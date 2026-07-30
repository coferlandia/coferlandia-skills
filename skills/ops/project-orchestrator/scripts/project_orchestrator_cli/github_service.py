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
        result = subprocess.run(["gh", *args], cwd=self.repo, text=True, capture_output=True, check=False)
        if result.returncode:
            message = (result.stderr or result.stdout).strip() or f"gh {' '.join(args)} failed"
            lowered = message.lower()
            if "auth" in lowered or "token" in lowered or "login" in lowered or "scope" in lowered:
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
        pages = self._json("api", f"repos/{ref.repository}/issues/{ref.number}/comments", "--paginate", "--slurp")
        if not isinstance(pages, list):
            return []
        if pages and all(isinstance(page, list) for page in pages):
            return [comment for page in pages for comment in page if isinstance(comment, dict)]
        return [comment for comment in pages if isinstance(comment, dict)]

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

    def create_issue(
        self,
        repository: str,
        *,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create exactly one Issue, then apply optional labels without retrying creation."""
        value = self._json(
            "api",
            f"repos/{repository}/issues",
            "-f",
            f"title={title}",
            "-f",
            f"body={body}",
        )
        if not isinstance(value, dict) or not value.get("number"):
            raise OrchestratorError("GitHub did not return a created Issue")
        ref = IssueRef(repository, int(value["number"]))
        for label in labels or []:
            self.try_add_issue_label(ref, label)
        return self.issue(ref)

    def try_add_issue_label(self, ref: IssueRef, label: str) -> bool:
        try:
            self._run("issue", "edit", str(ref.number), "--repo", ref.repository, "--add-label", label)
            return True
        except DependencyError:
            raise
        except OrchestratorError as exc:
            lowered = str(exc).lower()
            if "label" in lowered and any(token in lowered for token in ("not found", "does not exist", "could not resolve")):
                return False
            raise

    def issue_database_id(self, repository: str, number: int) -> int:
        value = self._json("api", f"repos/{repository}/issues/{number}")
        if not isinstance(value, dict) or value.get("id") is None:
            raise ValidationError(f"GitHub Issue {repository}#{number} has no database id")
        return int(value["id"])

    def try_add_sub_issue(self, repository: str, epic_number: int, task_number: int) -> bool:
        task_id = self.issue_database_id(repository, task_number)
        try:
            self._json(
                "api",
                "--method",
                "POST",
                f"repos/{repository}/issues/{epic_number}/sub_issues",
                "-F",
                f"sub_issue_id={task_id}",
            )
            return True
        except DependencyError:
            raise
        except OrchestratorError:
            return False

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

    def pull_requests_for_head(self, repository: str, branch: str) -> list[dict[str, Any]]:
        value = self._json("pr", "list", "--repo", repository, "--head", branch, "--state", "all", "--json", "number,url,state,title,headRefName,baseRefName")
        return value if isinstance(value, list) else []

    def ensure_pull_request(self, repository: str, branch: str, base: str, title: str, body: str) -> dict[str, Any]:
        existing = self.pull_requests_for_head(repository, branch)
        if existing:
            return self.pull_request(repository, int(existing[0]["number"]))
        value = self._json(
            "api",
            f"repos/{repository}/pulls",
            "-f", f"title={title}",
            "-f", f"head={branch}",
            "-f", f"base={base}",
            "-f", f"body={body}",
        )
        if not isinstance(value, dict) or not value.get("number"):
            raise OrchestratorError("GitHub did not return a created pull request")
        return self.pull_request(repository, int(value["number"]))

    def pull_request(self, repository: str, number: int) -> dict[str, Any]:
        value = self._json("pr", "view", str(number), "--repo", repository, "--json", "number,url,state,mergeCommit,headRefName,baseRefName,title,body")
        if not isinstance(value, dict):
            raise ValidationError(f"GitHub PR {repository}#{number} did not return an object")
        return value

    def merge_pull_request_squash(self, repository: str, number: int) -> dict[str, Any]:
        self._run("pr", "merge", str(number), "--repo", repository, "--squash", "--delete-branch=false")
        return self.pull_request(repository, number)

    def project_view(self, owner: str, number: int) -> dict[str, Any]:
        value = self._json("project", "view", str(number), "--owner", owner, "--format", "json")
        if not isinstance(value, dict):
            raise ValidationError(f"GitHub Project {owner}/{number} did not return an object")
        return value

    def project_fields(self, owner: str, number: int) -> list[dict[str, Any]]:
        value = self._json("project", "field-list", str(number), "--owner", owner, "--format", "json")
        if isinstance(value, dict):
            value = value.get("fields")
        return value if isinstance(value, list) else []

    def project_items(self, owner: str, number: int) -> list[dict[str, Any]]:
        value = self._json("project", "item-list", str(number), "--owner", owner, "--limit", "1000", "--format", "json")
        if isinstance(value, dict):
            value = value.get("items")
        return value if isinstance(value, list) else []

    def ensure_project_item(self, owner: str, number: int, issue_url: str, issue_number: int) -> dict[str, Any]:
        for item in self.project_items(owner, number):
            content = item.get("content") or {}
            if content.get("number") == issue_number:
                return item
        value = self._json("project", "item-add", str(number), "--owner", owner, "--url", issue_url, "--format", "json")
        if isinstance(value, dict):
            return value.get("item") if isinstance(value.get("item"), dict) else value
        raise OrchestratorError(f"failed to add Issue #{issue_number} to GitHub Project")

    def set_project_status(self, owner: str, number: int, issue: dict[str, Any], status_name: str) -> None:
        project = self.project_view(owner, number)
        project_id = project.get("id")
        if not project_id:
            raise ValidationError("GitHub Project id is missing")
        status_field = next((field for field in self.project_fields(owner, number) if str(field.get("name", "")).lower() == "status"), None)
        if not status_field:
            raise ValidationError("GitHub Project has no Status field")
        option = next((item for item in status_field.get("options") or [] if str(item.get("name", "")).lower() == status_name.lower()), None)
        if not option:
            raise ValidationError(f"GitHub Project Status option not found: {status_name}")
        item = self.ensure_project_item(owner, number, str(issue["url"]), int(issue["number"]))
        item_id = item.get("id")
        if not item_id:
            raise ValidationError("GitHub Project item id is missing")
        self._run(
            "project", "item-edit",
            "--id", str(item_id),
            "--project-id", str(project_id),
            "--field-id", str(status_field["id"]),
            "--single-select-option-id", str(option["id"]),
        )
