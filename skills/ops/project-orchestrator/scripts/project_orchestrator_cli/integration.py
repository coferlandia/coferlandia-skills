"""Final traceability, PR/integration, archival, and cleanup for project-orchestrator v2."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from .contracts import DependencyError, ValidationError
from .git_service import GitService
from .github_service import GitHubService, IssueRef
from .materialization import archive_delivered_tasks
from .state import RunStore, atomic_json
from .work_items import task_by_id


def _project_cfg(config: dict[str, Any]) -> dict[str, Any] | None:
    value = config.get("github_project")
    return value if isinstance(value, dict) and value.get("owner") and value.get("number") is not None else None


def _status_name(config: dict[str, Any], logical: str) -> str:
    mapping = {
        "pending": "Todo",
        "in_progress": "In Progress",
        "review": "Review",
        "blocked": "Blocked",
        "done": "Done",
    }
    mapping.update(config.get("github_project", {}).get("status_mapping", {}))
    return str(mapping[logical])


def _github_refs(state: dict[str, Any]) -> tuple[str, int]:
    source = state.get("manifest", {}).get("source", {})
    repository = source.get("repository")
    epic = source.get("epic_issue")
    if not repository or epic is None:
        raise ValidationError("GitHub-backed run is missing repository/Epic identity")
    return str(repository), int(epic)


def _ensure_task_traceability(repo: Path, state: dict[str, Any], config: dict[str, Any]) -> None:
    if state.get("manifest", {}).get("source", {}).get("kind") != "github":
        return
    service = GitHubService(repo)
    repository, epic_number = _github_refs(state)
    project = _project_cfg(config)
    for task in state["manifest"].get("tasks", []):
        issue_number = task.get("issue")
        if issue_number is None:
            continue
        ref = IssueRef(repository, int(issue_number))
        for commit in task.get("commits", []):
            sha = str(commit["sha"])
            kind = str(commit.get("kind") or "candidate")
            marker = f"<!-- coferlandia-orchestrator:{state['run_id']}:commit:{sha} -->"
            body = (
                "## Orchestrator commit evidence\n\n"
                f"- Epic: #{epic_number}\n"
                f"- Task: #{issue_number}\n"
                f"- Commit: `{sha}`\n"
                f"- Kind: `{kind}`\n"
            )
            if commit.get("review_round") is not None:
                body += f"- Review round: {commit['review_round']}\n"
            service.ensure_issue_comment(ref, marker, body)

        reviews = state.get("task_reviews", {}).get(task["id"], [])
        for index, review in enumerate(reviews, start=1):
            candidate = str(review.get("candidate_commit") or "")
            marker = f"<!-- coferlandia-orchestrator:{state['run_id']}:review:{task['id']}:{index}:{candidate} -->"
            findings = review.get("findings") or []
            body = (
                "## Independent review evidence\n\n"
                f"- Candidate: `{candidate}`\n"
                f"- Round: {index}\n"
                f"- Result: `{review.get('status')}`\n"
                f"- Findings: {len(findings)}\n"
            )
            service.ensure_issue_comment(ref, marker, body)

        marker = f"<!-- coferlandia-orchestrator:{state['run_id']}:ready:{task['id']} -->"
        service.ensure_issue_comment(
            ref,
            marker,
            "## Task lifecycle\n\nStatus: `ready_for_merge`\n\nThe task remains open until the final Epic PR reaches the default branch.",
        )

        if project:
            issue = service.issue(ref)
            service.set_project_status(str(project["owner"]), int(project["number"]), issue, _status_name(config, "review"))


def _pr_body(state: dict[str, Any]) -> str:
    manifest = state["manifest"]
    source = manifest.get("source", {})
    epic_number = source.get("epic_issue")
    lines = [
        "## Summary",
        "",
        "Implements the reviewed Coferlandia Epic execution branch.",
        "",
        f"Final reviewed SHA: `{state['final_reviewed_sha']}`",
        "",
        "## Delivered work items",
        "",
    ]
    for task_id in manifest.get("execution_order", []):
        task = task_by_id(manifest, task_id)
        if task.get("issue") is not None:
            lines.append(f"- Closes #{task['issue']} — {task.get('title', task_id)}")
        else:
            lines.append(f"- {task_id} — {task.get('title', task_id)}")
    if epic_number is not None:
        lines.extend(["", "## Epic", "", f"Closes #{epic_number}"])
    lines.extend([
        "",
        "## Review",
        "",
        f"Task reviews: {sum(len(value) for value in state.get('task_reviews', {}).values())}",
        f"Holistic Epic reviews: {len(state.get('holistic_reviews', []))}",
        "",
        "Integration is intentionally separate from PR creation and requires an explicit orchestrator `integrate` action.",
    ])
    return "\n".join(lines) + "\n"


def prepare_final_pr(repo: Path, run_id: str, config: dict[str, Any]) -> dict[str, Any]:
    git = GitService(repo)
    store = RunStore(git.common_dir(), run_id)
    with store.lock():
        state = store.load()
        if state["state"] == "PR_OPEN_AWAITING_MERGE_APPROVAL":
            return state
        if state["state"] != "EPIC_READY_FOR_INTEGRATION":
            raise ValidationError(f"run is not ready for PR creation: {state['state']}")
        branch = state["resources"]["epic_branch"]
        if git.head(branch) != state.get("final_reviewed_sha"):
            raise ValidationError("Epic branch HEAD no longer matches the final reviewed SHA")
        if git.head(state["base_branch"]) != state["base_commit"]:
            raise ValidationError("base branch advanced after Epic execution; rerun holistic review against the new base")
        if state["manifest"].get("source", {}).get("kind") != "github":
            return state

        _ensure_task_traceability(repo, state, config)
        repository, epic_number = _github_refs(state)
        git.push_branch(branch)
        service = GitHubService(repo)
        title = f"Epic #{epic_number}: {state['manifest'].get('epic', {}).get('title', 'orchestrated implementation')}"
        pr = service.ensure_pull_request(repository, branch, state["base_branch"], title, _pr_body(state))
        state["manifest"]["final_pr"] = int(pr["number"])
        state["final_pr_url"] = pr.get("url")
        atomic_json(store.state_file, state)
        state = store.transition("PR_OPEN_AWAITING_MERGE_APPROVAL", {"pr": pr.get("number"), "url": pr.get("url")})
        return state


def _archive_execution_contracts(store: RunStore, state: dict[str, Any]) -> None:
    worktree = Path(state["resources"]["implementation_worktree"])
    manifest = state["manifest"]
    for task in manifest.get("tasks", []):
        if task.get("status") == "ready_for_merge":
            task["status"] = "done"
    archive_delivered_tasks(worktree, manifest)
    local_manifest_path = manifest.get("local_manifest_path")
    if local_manifest_path:
        atomic_json(Path(local_manifest_path), manifest)

    evidence = store.root / "work-items"
    if evidence.exists():
        shutil.rmtree(evidence)
    source_root = None
    epic_path = manifest.get("epic", {}).get("path")
    if epic_path:
        source = worktree / epic_path
        if source.exists():
            source_root = source.parent
    if source_root and source_root.exists():
        shutil.copytree(source_root, evidence)


def _sync_done(repo: Path, state: dict[str, Any], config: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if state["manifest"].get("source", {}).get("kind") != "github":
        return warnings
    service = GitHubService(repo)
    repository, _ = _github_refs(state)
    project = _project_cfg(config)
    for task in state["manifest"].get("tasks", []):
        if task.get("issue") is None:
            continue
        issue = service.issue(IssueRef(repository, int(task["issue"])))
        if str(issue.get("state", "OPEN")).upper() != "CLOSED":
            warnings.append(f"Issue #{task['issue']} did not close after final PR merge")
        if project:
            service.set_project_status(str(project["owner"]), int(project["number"]), issue, _status_name(config, "done"))
    return warnings


def integrate_run(repo: Path, run_id: str, config: dict[str, Any]) -> dict[str, Any]:
    git = GitService(repo)
    store = RunStore(git.common_dir(), run_id)
    with store.lock():
        state = store.load()
        kind = state["manifest"].get("source", {}).get("kind")
        allowed = {"EPIC_READY_FOR_INTEGRATION"} if kind != "github" else {"PR_OPEN_AWAITING_MERGE_APPROVAL"}
        if state["state"] not in allowed:
            raise ValidationError(f"run is not awaiting explicit integration: {state['state']}")
        branch = state["resources"]["epic_branch"]
        if git.head(branch) != state.get("final_reviewed_sha"):
            raise ValidationError("Epic branch HEAD changed after holistic review")
        if git.head(state["base_branch"]) != state["base_commit"]:
            raise ValidationError("base branch advanced after holistic review")

        state = store.transition("INTEGRATING", {"branch": branch, "reviewed_sha": state["final_reviewed_sha"]})
        if kind == "github":
            repository, _ = _github_refs(state)
            pr_number = int(state["manifest"]["final_pr"])
            merged = GitHubService(repo).merge_pull_request_squash(repository, pr_number)
            merge_commit = merged.get("mergeCommit") or {}
            final_sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
            if not final_sha:
                raise ValidationError("merged PR did not expose a final merge/squash SHA")
        else:
            git.merge_squash(branch, cwd=repo)
            epic_title = state["manifest"].get("epic", {}).get("title", "orchestrated implementation")
            final_sha = git.commit(f"feat: integrate {epic_title}", repo)

        state["manifest"]["squash_sha"] = final_sha
        state["final_integration_sha"] = final_sha
        atomic_json(store.state_file, state)
        state = store.transition("INTEGRATED", {"sha": final_sha})
        state = store.transition("ARCHIVING")
        _archive_execution_contracts(store, state)
        state = store.load()
        state["integration_warnings"] = _sync_done(repo, state, config)
        atomic_json(store.state_file, state)

        implementation = Path(state["resources"]["implementation_worktree"])
        if implementation.exists() and config["git"].get("remove_implementation_worktree_after_integration", True):
            git.remove_worktree(implementation)
        if config["git"].get("delete_epic_branch_after_integration", True) and kind != "github":
            git.remove_branch(branch)
        state = store.transition("PROJECT_COMPLETED", {"sha": final_sha, "warnings": state.get("integration_warnings", [])})
        state["state_path"] = str(store.root)
        atomic_json(store.state_file, state)
        return state
