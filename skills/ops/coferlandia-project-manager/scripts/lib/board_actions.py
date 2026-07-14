#!/usr/bin/env python3
"""Board-driven action validation for coferlandia-project-manager."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reporting import VALID_TASK_STATUSES, iter_managed_project_entries, _is_git_repo, _missing_artifacts, parse_todo_tasks


ACTIONABLE_STATES = {
    "needs-brainstorming": {
        "suggested_next_action": "prepare a brainstorming brief",
        "required_next_skill": "superpowers:brainstorming",
    },
    "planning": {
        "suggested_next_action": "prepare a writing-plans brief",
        "required_next_skill": "superpowers:writing-plans",
    },
    "ready-for-agent": {
        "suggested_next_action": "prepare an execution brief",
        "required_next_skill": "superpowers:executing-plans",
    },
    "code-review": {
        "suggested_next_action": "prepare a review handoff brief",
        "required_next_skill": "superpowers:requesting-code-review",
    },
    "verification": {
        "suggested_next_action": "prepare a verification checklist",
        "required_next_skill": "superpowers:verification-before-completion",
    },
}


def _find_task(projects_file: Path, task_id: str) -> dict | None:
    task_id_lower = task_id.lower()
    for project_slug, project_path in iter_managed_project_entries(projects_file):
        if not _is_git_repo(project_path):
            continue
        for task in parse_todo_tasks(project_path / "TODO.md"):
            candidate = (task.get("task_id") or "").lower()
            if candidate == task_id_lower:
                return {
                    **task,
                    "project_slug": project_slug,
                    "repo_path": project_path.as_posix(),
                }
    return None


def cmd_validate_task_transition(args: argparse.Namespace) -> dict:
    task = _find_task(args.projects_file, args.task)
    if task is None:
        return {
            "status": "error",
            "authorized": False,
            "blocking_reason": f"Task '{args.task}' was not found in managed projects.",
        }

    target_status = args.target_status.strip().lower()
    if target_status not in VALID_TASK_STATUSES:
        return {
            "status": "error",
            "authorized": False,
            "blocking_reason": f"Unknown target status: {args.target_status}",
        }

    if task["status"] != target_status:
        return {
            "status": "ok",
            "task_id": task.get("task_id"),
            "project_slug": task["project_slug"],
            "current_status": task["status"],
            "target_status": target_status,
            "authorized": False,
            "blocking_reason": "Current task status does not match the requested board state.",
            "required_approval": "no",
            "suggested_next_action": None,
        }

    missing = _missing_artifacts(Path(task["repo_path"]))
    if missing:
        action = ACTIONABLE_STATES.get(target_status)
        return {
            "status": "ok",
            "task_id": task.get("task_id"),
            "project_slug": task["project_slug"],
            "current_status": task["status"],
            "target_status": target_status,
            "authorized": False,
            "blocking_reason": "Unresolved sync conflict blocks board-driven action preparation.",
            "required_approval": "yes",
            "suggested_next_action": action["suggested_next_action"] if action else None,
            "missing_artifacts": missing,
        }

    action = ACTIONABLE_STATES.get(target_status)
    if action is None:
        return {
            "status": "ok",
            "task_id": task.get("task_id"),
            "project_slug": task["project_slug"],
            "current_status": task["status"],
            "target_status": target_status,
            "authorized": False,
            "blocking_reason": "Target task status is not board-actionable in Phase 6.",
            "required_approval": "no",
            "suggested_next_action": None,
        }

    return {
        "status": "ok",
        "task_id": task.get("task_id"),
        "project_slug": task["project_slug"],
        "current_status": task["status"],
        "target_status": target_status,
        "authorized": True,
        "blocking_reason": None,
        "required_approval": "no",
        "suggested_next_action": action["suggested_next_action"],
    }


def cmd_generate_execution_brief(args: argparse.Namespace) -> dict:
    task = _find_task(args.projects_file, args.task)
    if task is None:
        return {
            "status": "error",
            "error": f"Task '{args.task}' was not found in managed projects.",
        }

    current_status = task["status"]
    actionable = ACTIONABLE_STATES.get(current_status)
    if actionable is None:
        return {
            "status": "error",
            "task_id": task.get("task_id"),
            "error": f"Task status '{current_status}' is not board-actionable in Phase 6.",
        }

    validation = cmd_validate_task_transition(
        argparse.Namespace(
            projects_file=args.projects_file,
            task=task.get("task_id") or args.task,
            target_status=current_status,
        )
    )
    if not validation.get("authorized"):
        return {
            "status": "error",
            "task_id": task.get("task_id"),
            "current_status": current_status,
            "blocking_reason": validation.get("blocking_reason"),
            "required_approval": validation.get("required_approval", "yes"),
            "executes_work": False,
        }

    return {
        "status": "ok",
        "task_id": task.get("task_id"),
        "project_slug": task["project_slug"],
        "repo_path": task["repo_path"],
        "title": task["title"],
        "current_status": current_status,
        "required_next_skill": actionable["required_next_skill"],
        "suggested_next_action": actionable["suggested_next_action"],
        "required_approval": "plan approval before implementation",
        "blocking_conflicts": [],
        "executes_work": False,
        "mode": "dry-run" if args.dry_run else "describe-only",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Board-driven action tooling.")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-task-transition")
    validate.add_argument("--projects-file", required=True, type=Path)
    validate.add_argument("--task", required=True)
    validate.add_argument("--target-status", required=True)

    brief = sub.add_parser("generate-execution-brief")
    brief.add_argument("--projects-file", required=True, type=Path)
    brief.add_argument("--task", required=True)
    brief.add_argument("--dry-run", action="store_true")
    brief.add_argument("--current-status-override")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "validate-task-transition":
        payload = cmd_validate_task_transition(args)
    else:
        payload = cmd_generate_execution_brief(args)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
