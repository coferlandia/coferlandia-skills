"""Deterministic GitHub CLI adapter owned by project-orchestrator."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import DependencyError, OrchestratorError, ValidationError

ISSUE_URL_RE = re.compile(r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<number>\d+)(?:/.*)?$")


@dataclass(frozen=True)
class IssueRef:
    repository: str
    number: int


class GitHubService:
    def __init__(self, repo: Path):
        self.repo = repo.resolve()

    def available(self) -> bool:
        return shutil.which("gh") is not None

    def _run(self, *args: str) -> str:
        if not self.available():
            raise DependencyError("GitHub CLI (gh) is required for GitHub-backed orchestrator mode")
        result = subprocess.run(
            ["gh", *args],
            cwd=self.repo,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            message = (result.stderr or result.stdout).strip() or f"gh {' '.join(args)} failed"
            lowered = message.lower()
            if "auth" in lowered or "token" in lowered or "login" in lowered:
                raise DependencyError(message)
            raise OrchestratorError(message)
        return result.stdout.strip()

    def _json(self, *args: str) -> Any:
        raw = self._run(*args)
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"gh returned invalid JSON for {' '.join(args)}") from exc

    def repository_name(self) -> str:
        value = self._json("repo", "view", "--json", "nameWithOwner")
        name = value.get("nameWithOwner") if isinstance(value, dict) else None
        if not name:
            raise ValidationError("could not resolve GitHub repository from current checkout")
        return str(name)

    def resolve_issue_ref(self, raw: str) -> IssueRef:
        match = ISSUE_URL_RE.match(raw.strip())
        if match:
            return IssueRef(f"{match.group('owner')}/{match.group('repo')}", int(match.group("number")))
        token = raw.strip().lstrip("#")
        if token.isdigit():
            return IssueRef(self.repository_name(), int(token))
        if "#" in token:
            repo, number = token.rsplit("#", 1)
            if "/" in repo and number.isdigit():
                return IssueRef(repo, int(number))
        raise ValidationError(f"unsupported GitHub Issue reference: {raw}")

    def issue(self, ref: IssueRef) -> dict[str, Any]:
        fields = "number,title,body,state,stateReason,url,createdAt,updatedAt,closedAt,labels,assignees,parent,subIssuesSummary,blockedBy,blocking,projectItems"
        value = self._json("issue", "view", str(ref.number), "--repo", ref.repository, "--json", fields)
        if not isinstance(value, dict):
            raise ValidationError(f"GitHub Issue {ref.repository}#{ref.number} did not return an object")
        return value

    def comments(self, ref: IssueRef) -> list[dict[str, Any]]:
        value = self._json(
            "api",
            f"repos/{ref.repository}/issues/{ref.number}/comments",
            "--paginate",
        )
        return value if isinstance(value, list) else []

    def list_issues(self, repository: str) -> list[dict[str, Any]]:
        fields = "number,title,body,state,stateReason,url,createdAt,updatedAt,closedAt,labels,assignees,parent,subIssuesSummary,blockedBy,blocking,projectItems"
        value = self._json("issue", "list", "--repo", repository, "--state", "all", "--limit", "1000", "--json", fields)
        return value if isinstance(value, list) else []

    def child_issues(self, epic: IssueRef) -> list[dict[str, Any]]:
        issues = self.list_issues(epic.repository)
        native = [item for item in issues if isinstance(item.get("parent"), dict) and item["parent"].get("number") == epic.number]
        if native:
            return sorted(native, key=lambda item: int(item["number"]))
        fallback_re = re.compile(rf"(?mi)^\s*(?:Parent\s+Epic|Epic)\s*:\s*#?{epic.number}\s*$")
        fallback = [item for item in issues if item.get("number") != epic.number and fallback_re.search(str(item.get("body") or ""))]
        return sorted(fallback, key=lambda item: int(item["number"]))

    def add_issue_comment(self, ref: IssueRef, body: str) -> dict[str, Any]:
        value = self._json("api", f"repos/{ref.repository}/issues/{ref.number}/comments", "-f", f"body={body}")
        return value if isinstance(value, dict) else {}

    def existing_comment_with_marker(self, ref: IssueRef, marker: str) -> dict[str, Any] | None:
        for comment in self.comments(ref):
            if marker in str(comment.get("body") or ""):
                return comment
        return None

    def ensure_issue_comment(self, ref: IssueRef, marker: str, body: str) -> dict[str, Any]:
        existing = self.existing_comment_with_marker(ref, marker)
        if existing:
            return existing
        return self.add_issue_comment(ref, f"{marker}\n\n{body}")
