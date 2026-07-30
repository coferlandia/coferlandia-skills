"""One-time GitHub/local work-contract materialization for project-orchestrator v2."""
from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import ValidationError
from .github_service import GitHubService
from .work_items import execution_mode_from_strategy, parse_execution_strategy, sha256_text, validate_manifest

ANALYSIS_MARKER = "<!-- coferlandia-analysis-contract -->"
FRONTMATTER_REV_RE = re.compile(r"(?mi)^\s*Contract revision\s*:\s*(\d+)\s*$")
HEADING_RE_TEMPLATE = r"(?ms)^##\s+{heading}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _section(text: str, heading: str) -> str:
    match = re.search(HEADING_RE_TEMPLATE.format(heading=re.escape(heading)), text)
    return match.group("body").strip() if match else ""


def _contract_revision(text: str) -> int:
    match = FRONTMATTER_REV_RE.search(text)
    return int(match.group(1)) if match else 1


def _dependency_numbers(text: str) -> list[int]:
    body = _section(text, "Dependencies")
    return sorted({int(value) for value in re.findall(r"#(\d+)", body)})


def _latest_strategy(epic_body: str, comments: list[dict[str, Any]]) -> dict[str, str]:
    try:
        return parse_execution_strategy(epic_body)
    except ValidationError as body_error:
        for comment in reversed(comments):
            text = str(comment.get("body") or "")
            try:
                return parse_execution_strategy(text)
            except ValidationError:
                continue
        raise body_error


def _canonical_analysis(comments: list[dict[str, Any]]) -> tuple[str, Any] | None:
    for comment in reversed(comments):
        body = str(comment.get("body") or "")
        if ANALYSIS_MARKER not in body:
            continue
        analysis = body.split(ANALYSIS_MARKER, 1)[1].strip()
        if analysis:
            return analysis, comment.get("id")
    return None


def _frontmatter(meta: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in meta.items():
        encoded = json.dumps(value, ensure_ascii=False) if value is not None else "null"
        lines.append(f"{key}: {encoded}")
    lines.append("---")
    return "\n".join(lines)


def github_materialization_root(repo: Path, epic_number: int) -> Path:
    return repo / ".agent" / "work-items" / f"epic-{epic_number}"


def materialize_github_epic(repo: Path, raw_epic: str, service: GitHubService | None = None) -> dict[str, Any]:
    """Materialize a GitHub Epic into one frozen local execution snapshot."""
    service = service or GitHubService(repo)
    ref = service.resolve_issue_ref(raw_epic)
    epic = service.issue(ref)
    comments = service.comments(ref)
    strategy = _latest_strategy(str(epic.get("body") or ""), comments)
    mode = execution_mode_from_strategy(strategy)
    children = service.child_issues(ref) if mode == "task-execution" else []
    if mode == "task-execution" and not children:
        raise ValidationError(f"Epic {ref.repository}#{ref.number} selected Analyst decomposition but has no task Issues")

    initialized_at = now()
    root = github_materialization_root(repo, ref.number)
    tasks_dir = root / "tasks"
    archive_dir = root / "archive"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    epic_body = str(epic.get("body") or "")
    epic_hash = sha256_text(epic_body)
    epic_meta = {
        "source": "github",
        "origin": "github",
        "snapshot": True,
        "repository": ref.repository,
        "issue": ref.number,
        "epic": ref.number,
        "source_updated_at": epic.get("updatedAt"),
        "source_hash": epic_hash,
        "materialized_at": initialized_at,
        "contract_revision": _contract_revision(epic_body),
    }
    epic_path = root / "EPIC.md"
    _atomic_text(epic_path, f"{_frontmatter(epic_meta)}\n\n# {epic.get('title', f'Epic #{ref.number}')}\n\n{epic_body.strip()}\n")

    analysis_row: dict[str, Any] | None = None
    analysis = _canonical_analysis(comments)
    if analysis is not None:
        analysis_text, comment_id = analysis
        analysis_path = root / "ANALYSIS.md"
        analysis_hash = sha256_text(analysis_text)
        analysis_meta = {
            "source": "github",
            "origin": "github",
            "snapshot": True,
            "repository": ref.repository,
            "epic": ref.number,
            "comment_id": comment_id,
            "source_hash": analysis_hash,
            "materialized_at": initialized_at,
        }
        _atomic_text(analysis_path, f"{_frontmatter(analysis_meta)}\n\n{analysis_text.rstrip()}\n")
        analysis_row = {
            "path": str(analysis_path.relative_to(repo)).replace("\\", "/"),
            "marker": ANALYSIS_MARKER,
            "comment_id": comment_id,
            "source_hash": analysis_hash,
        }

    task_rows: list[dict[str, Any]] = []
    child_numbers = {int(item["number"]) for item in children}
    for item in children:
        number = int(item["number"])
        body = str(item.get("body") or "")
        task_hash = sha256_text(body)
        task_id = f"TASK-{number}"
        task_path = tasks_dir / f"TASK-{number}.md"
        meta = {
            "work_item": task_id,
            "source": "github",
            "origin": "github",
            "snapshot": True,
            "repository": ref.repository,
            "issue": number,
            "epic": ref.number,
            "source_updated_at": item.get("updatedAt"),
            "source_hash": task_hash,
            "materialized_at": initialized_at,
            "contract_revision": _contract_revision(body),
        }
        _atomic_text(task_path, f"{_frontmatter(meta)}\n\n# {item.get('title', task_id)}\n\n{body.strip()}\n")
        deps = [f"TASK-{dep}" for dep in _dependency_numbers(body) if dep in child_numbers]
        task_rows.append({
            "id": task_id,
            "issue": number,
            "title": item.get("title") or task_id,
            "depends_on": deps,
            "status": "pending" if str(item.get("state", "OPEN")).upper() == "OPEN" else "done",
            "path": str(task_path.relative_to(repo)).replace("\\", "/"),
            "contract_revision": _contract_revision(body),
            "source_hash": task_hash,
            "source_updated_at": item.get("updatedAt"),
            "commits": [],
        })

    if mode == "direct-plan":
        task_rows = [{
            "id": "DIRECT-PLAN",
            "issue": None,
            "title": epic.get("title") or f"Epic #{ref.number}",
            "depends_on": [],
            "status": "pending",
            "path": str(epic_path.relative_to(repo)).replace("\\", "/"),
            "contract_revision": _contract_revision(epic_body),
            "source_hash": epic_hash,
            "source_updated_at": epic.get("updatedAt"),
            "commits": [],
        }]

    manifest_value: dict[str, Any] = {
        "schema_version": 2,
        "execution_mode": mode,
        "execution_strategy": strategy,
        "source": {
            "kind": "github",
            "origin": "github",
            "tracking": "github",
            "repository": ref.repository,
            "epic_issue": ref.number,
            "source_updated_at": epic.get("updatedAt"),
            "source_hash": epic_hash,
            "contract_revision": _contract_revision(epic_body),
            "initialized_at": initialized_at,
            "initial_materialization_complete": True,
        },
        "epic": {
            "id": f"EPIC-{ref.number}",
            "issue": ref.number,
            "title": epic.get("title") or f"Epic #{ref.number}",
            "path": str(epic_path.relative_to(repo)).replace("\\", "/"),
        },
        "tasks": task_rows,
        "final_pr": None,
        "squash_sha": None,
    }
    if analysis_row is not None:
        manifest_value["analysis"] = analysis_row
    manifest = validate_manifest(manifest_value)
    _atomic_text(root / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return manifest


def _graph_signature(manifest: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    return {
        task["id"]: tuple(sorted(str(dep) for dep in task.get("depends_on") or []))
        for task in manifest.get("tasks", [])
    }


def _preserve_execution_metadata(previous: dict[str, Any], refreshed: dict[str, Any]) -> dict[str, Any]:
    """Compatibility support for explicit/manual refresh callers only."""
    previous_by_id = {task["id"]: task for task in previous.get("tasks", [])}
    for task in refreshed.get("tasks", []):
        old = previous_by_id.get(task["id"])
        if not old:
            continue
        task["status"] = old.get("status", task.get("status", "pending"))
        task["commits"] = list(old.get("commits") or [])
        for key in ("completed_at", "ready_for_merge_at", "final_review_sha"):
            if key in old:
                task[key] = old[key]
    refreshed["final_pr"] = previous.get("final_pr")
    refreshed["squash_sha"] = previous.get("squash_sha")
    if previous.get("local_manifest_path"):
        refreshed["local_manifest_path"] = previous["local_manifest_path"]
    return validate_manifest(refreshed)


def verify_github_freshness(
    repo: Path,
    manifest: dict[str, Any],
    service: GitHubService | None = None,
    *,
    in_progress_task: str | None = None,
) -> dict[str, Any]:
    """Return the frozen snapshot during normal orchestration.

    The engine calls this compatibility entry point without an injected service, so no GitHub read,
    comparison, refresh, or merge occurs after initialization. An injected service preserves the
    old explicit/manual verification behavior for compatibility and migration tooling.
    """
    source = manifest.get("source") or {}
    if source.get("kind") != "github" or service is None:
        return {"fresh": True, "refreshed": False, "snapshot": True, "manifest": manifest}

    repository = str(source["repository"])
    epic_number = int(source["epic_issue"])
    from .github_service import IssueRef
    epic_ref = IssueRef(repository, epic_number)
    epic = service.issue(epic_ref)
    remote_epic_hash = sha256_text(str(epic.get("body") or ""))
    stale = remote_epic_hash != source.get("source_hash")

    children = service.child_issues(epic_ref)
    child_by_number = {int(item["number"]): item for item in children}
    known_numbers = {int(task["issue"]) for task in manifest.get("tasks", []) if task.get("issue") is not None}
    remote_numbers = set(child_by_number)
    changed_tasks: list[str] = []
    if remote_numbers != known_numbers:
        stale = True
        changed_tasks.extend(f"TASK-{number}" for number in sorted(remote_numbers ^ known_numbers))

    for task in manifest.get("tasks", []):
        if task.get("issue") is None:
            continue
        remote = child_by_number.get(int(task["issue"]))
        if remote is None or sha256_text(str(remote.get("body") or "")) != task.get("source_hash"):
            stale = True
            if task["id"] not in changed_tasks:
                changed_tasks.append(task["id"])

    if not stale:
        return {"fresh": True, "refreshed": False, "manifest": manifest}
    if in_progress_task and in_progress_task in changed_tasks:
        raise ValidationError(f"authoritative GitHub contract changed while {in_progress_task} is in progress")

    refreshed = materialize_github_epic(repo, f"{repository}#{epic_number}", service)
    if _graph_signature(refreshed) != _graph_signature(manifest):
        raise ValidationError("authoritative GitHub execution graph changed; re-resolve the Epic before assigning more work")
    refreshed = _preserve_execution_metadata(manifest, refreshed)
    return {"fresh": False, "refreshed": True, "changed_tasks": changed_tasks, "manifest": refreshed}


def archive_delivered_tasks(repo: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    for task in manifest.get("tasks", []):
        if task.get("status") != "done" or task.get("id") == "DIRECT-PLAN":
            continue
        current = repo / task["path"]
        if "/tasks/" not in "/" + task["path"].replace("\\", "/"):
            continue
        archive = current.parent.parent / "archive" / current.name
        archive.parent.mkdir(parents=True, exist_ok=True)
        if current.exists():
            os.replace(current, archive)
        task["path"] = str(archive.relative_to(repo)).replace("\\", "/")
    return manifest
