from __future__ import annotations
import json
import subprocess
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote
from .model import ReleaseError

Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]

def _default_runner(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], text=True, capture_output=True, check=False)

class GitHubService:
    def __init__(self, runner: Runner | None = None) -> None:
        self.runner = runner or _default_runner

    def _call(self, args: list[str], *, allow_not_found: bool = False) -> subprocess.CompletedProcess[str]:
        result = self.runner(args)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            if allow_not_found and ("404" in stderr or "not found" in stderr.lower()):
                return result
            raise ReleaseError(stderr or f"gh {' '.join(args)} failed")
        return result

    def _json(self, args: list[str], *, allow_not_found: bool = False) -> Any:
        result = self._call(args, allow_not_found=allow_not_found)
        if result.returncode != 0 and allow_not_found:
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"gh returned invalid JSON for {' '.join(args)}") from exc

    @staticmethod
    def _split(repository: str) -> tuple[str, str]:
        parts = repository.split("/", 1)
        if len(parts) != 2 or not all(parts):
            raise ReleaseError(f"invalid GitHub repository: {repository}")
        return parts[0], parts[1]

    def repository_info(self, repository: str) -> dict[str, Any]:
        owner, repo = self._split(repository)
        data = self._json(["api", f"repos/{owner}/{repo}"])
        default = data.get("default_branch") or (data.get("defaultBranchRef") or {}).get("name")
        full = data.get("full_name") or data.get("nameWithOwner") or repository
        return {"repository": full, "default_branch": default}

    @staticmethod
    def _normalize_asset(asset: dict[str, Any]) -> dict[str, Any]:
        digest = asset.get("digest")
        if isinstance(digest, str) and digest.startswith("sha256:"):
            digest = digest.removeprefix("sha256:")
        return {"id": asset.get("id"), "name": asset.get("name"), "size": asset.get("size"), "sha256": digest, "url": asset.get("browser_download_url")}

    @classmethod
    def _normalize_release(cls, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": data.get("id"), "tag": data.get("tag_name") or data.get("tag"),
            "title": data.get("name") or data.get("title") or "", "body": data.get("body") or "",
            "draft": bool(data.get("draft")), "prerelease": bool(data.get("prerelease")),
            "immutable": data.get("immutable"), "created_at": data.get("created_at"),
            "published_at": data.get("published_at"), "html_url": data.get("html_url"),
            "assets": [cls._normalize_asset(item) for item in data.get("assets", [])],
        }

    def list_releases(self, repository: str) -> list[dict[str, Any]]:
        owner, repo = self._split(repository)
        data = self._json(["api", "--paginate", "--slurp", f"repos/{owner}/{repo}/releases?per_page=100"])
        flat = [item for page in data for item in page] if data and isinstance(data[0], list) else (data or [])
        return [self._normalize_release(item) for item in flat]

    def release_by_tag(self, repository: str, tag: str) -> dict[str, Any] | None:
        owner, repo = self._split(repository)
        data = self._json(["api", f"repos/{owner}/{repo}/releases/tags/{quote(tag, safe='')}"], allow_not_found=True)
        return self._normalize_release(data) if data else None

    def release_by_id(self, repository: str, release_id: int) -> dict[str, Any]:
        owner, repo = self._split(repository)
        return self._normalize_release(self._json(["api", f"repos/{owner}/{repo}/releases/{release_id}"]))

    def checks_for_commit(self, repository: str, sha: str) -> list[dict[str, Any]]:
        owner, repo = self._split(repository)
        data = self._json(["api", f"repos/{owner}/{repo}/commits/{sha}/check-runs?per_page=100"])
        return [{"name": item.get("name"), "status": item.get("status"), "conclusion": item.get("conclusion"), "url": item.get("html_url") or item.get("details_url")} for item in data.get("check_runs", [])]

    def immutable_releases_status(self, repository: str) -> dict[str, Any]:
        owner, repo = self._split(repository)
        data = self._json(["api", f"repos/{owner}/{repo}/immutable-releases"], allow_not_found=True)
        if data is None:
            return {"enabled": False, "enforced_by_owner": False}
        return {"enabled": bool(data.get("enabled")), "enforced_by_owner": bool(data.get("enforced_by_owner"))}

    def create_draft_release(self, repository: str, tag: str, title: str, body: str, prerelease: bool) -> dict[str, Any]:
        owner, repo = self._split(repository)
        data = self._json(["api", "--method", "POST", f"repos/{owner}/{repo}/releases", "-f", f"tag_name={tag}", "-f", f"name={title}", "-f", f"body={body}", "-F", "draft=true", "-F", f"prerelease={'true' if prerelease else 'false'}"])
        return self._normalize_release(data)

    def upload_asset(self, repository: str, release_id: int, path: Path, name: str | None = None) -> dict[str, Any]:
        owner, repo = self._split(repository)
        asset_name = quote(name or path.name, safe="")
        data = self._json(["api", "--hostname", "uploads.github.com", "--method", "POST", "-H", "Content-Type: application/octet-stream", "--input", str(path), f"repos/{owner}/{repo}/releases/{release_id}/assets?name={asset_name}"])
        return self._normalize_asset(data)

    def publish_release(self, repository: str, release_id: int) -> dict[str, Any]:
        owner, repo = self._split(repository)
        data = self._json(["api", "--method", "PATCH", f"repos/{owner}/{repo}/releases/{release_id}", "-F", "draft=false"])
        return self._normalize_release(data)

    def download_text_asset(self, repository: str, asset_id: int) -> str:
        owner, repo = self._split(repository)
        return self._call(["api", "-H", "Accept: application/octet-stream", f"repos/{owner}/{repo}/releases/assets/{asset_id}"]).stdout
