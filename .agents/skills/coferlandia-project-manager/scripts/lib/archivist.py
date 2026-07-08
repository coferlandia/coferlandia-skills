#!/usr/bin/env python3
"""Archivist-state helpers for coferlandia-project-manager.

This module is the single source of truth for the set of archivist-managed
artifacts a project repository is expected to contain, and for the read-only
inspection commands the PM exposes: ``status``, ``sync-plan``, ``conflicts``,
and ``maintenance``.

Read-only inspection remains the default, but the ``--apply`` paths now persist
runtime backups, PM state, and Obsidian notes when the calling script enables
them with explicit approval. The scripts keep dry-run as the default so a caller
cannot mistake a requested preview for a successful write.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from reporting import (
    _TODO_EXPLICIT_STATUS_RE,
    _TODO_ID_RE,
    _build_git_state,
    _derive_project_pm_status,
    _git,
    parse_todo_tasks,
)

# Canonical set of artifacts the project-documentation-archivist manages.
# Every direct-child git repo under repos_root is expected to contain these.
# This tuple is the one source of truth — the bash layer and every PM
# archivist command read from it.
EXPECTED_ARTIFACTS = (
    "README.md",
    "TODO.md",
    "HISTORY.md",
    "DECISIONS.md",
    "RUNBOOK.md",
    "AGENTS.md",
)

RUNTIME_ROOT = Path(".coferlandia/project-manager")


def _is_git_repo(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def iter_projects(repos_root: Path):
    """Yield ``(project_path, is_git_repo)`` for each direct child dir, sorted."""
    if not repos_root.is_dir():
        return
    for project_path in sorted(p for p in repos_root.iterdir() if p.is_dir()):
        yield project_path, _is_git_repo(project_path)


def missing_artifacts(project_path: Path) -> list:
    return [name for name in EXPECTED_ARTIFACTS if not (project_path / name).is_file()]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _runtime_root() -> Path:
    return RUNTIME_ROOT


def _normalize_path_text(value: str) -> str:
    match = re.match(r"^([A-Za-z]):[\\/](.*)$", value)
    if not match:
        return value
    drive_letter = match.group(1).lower()
    remainder = match.group(2).replace("\\", "/")
    return f"/mnt/{drive_letter}/{remainder}"


def _config_value(config: dict, *keys, default=None):
    value = config
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return default if value is None else value


def _load_config(config_path: Path) -> dict:
    if not config_path:
        return {}
    if not config_path.is_file():
        raise FileNotFoundError(f"Config not found: {config_path}")
    return _load_json(config_path)


def _obsidian_settings(config: dict) -> dict:
    vault_root = _config_value(config, "obsidian", "vault_root", default="")
    if isinstance(vault_root, str):
        vault_root = _normalize_path_text(vault_root)
    return {
        "vault_root": vault_root,
        "pm_projects_folder": _config_value(
            config, "obsidian", "pm_projects_folder", default="Projects"
        ),
        "pm_tasks_folder": _config_value(
            config, "obsidian", "pm_tasks_folder", default="Projects/tasks"
        ),
    }


def _project_display_title(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def _clean_task_title(raw_title: str) -> str:
    title = raw_title
    if ":" in title:
        prefix, remainder = title.split(":", 1)
        if _TODO_ID_RE.search(prefix):
            title = remainder.strip()
    title = _TODO_EXPLICIT_STATUS_RE.sub("", title).strip()
    return re.sub(r"\s+", " ", title).strip(" -:")


def _task_progress(status: str) -> int:
    progress_map = {
        "intake": 0,
        "needs-brainstorming": 5,
        "spec-writing": 15,
        "spec-review": 20,
        "planning": 25,
        "plan-review": 35,
        "ready-for-agent": 40,
        "worktree-prep": 50,
        "implementing": 60,
        "debugging": 65,
        "code-review": 80,
        "changes-requested": 85,
        "verification": 90,
        "branch-finishing": 95,
        "syncing-docs": 98,
        "done": 100,
        "blocked": 0,
        "cancelled": 0,
    }
    return progress_map.get(status, 0)


def _task_type_for_title(title: str) -> str:
    lowered = title.lower()
    if any(word in lowered for word in ("bug", "fix", "regress", "error")):
        return "bugfix"
    if any(word in lowered for word in ("doc", "write", "spec", "report", "note")):
        return "documentation"
    return "feature"


def _frontmatter_scalar(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return json.dumps(str(value), ensure_ascii=False)


def _parse_frontmatter_value(raw: str):
    value = raw.strip()
    if value.lower() == "null":
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def _parse_markdown_frontmatter(text: str) -> tuple[dict, str, bool]:
    if not text.startswith("---\n"):
        return {}, text, False

    lines = text.splitlines()
    try:
        end_index = lines.index("---", 1)
    except ValueError:
        return {}, text, False

    fm_lines = lines[1:end_index]
    body = "\n".join(lines[end_index + 1 :])
    if body:
        body += "\n"

    payload = OrderedDict()
    for line in fm_lines:
        if not line.strip() or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        payload[key.strip()] = _parse_frontmatter_value(raw_value)
    return dict(payload), body, True


def _merge_frontmatter(existing: dict, updates: dict) -> dict:
    merged = OrderedDict(existing)
    for key, value in updates.items():
        merged[key] = value
    return merged


def _render_frontmatter(payload: dict, preferred_order: list[str]) -> str:
    lines = ["---"]
    seen = set()
    for key in preferred_order:
        if key in payload:
            lines.append(f"{key}: {_frontmatter_scalar(payload[key])}")
            seen.add(key)
    for key, value in payload.items():
        if key in seen:
            continue
        lines.append(f"{key}: {_frontmatter_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def _write_markdown_note(path: Path, updates: dict, preferred_order: list[str]) -> None:
    existing_payload = {}
    existing_body = ""
    if path.is_file():
        existing_payload, existing_body, _ = _parse_markdown_frontmatter(
            path.read_text(encoding="utf-8")
        )

    merged = _merge_frontmatter(existing_payload, updates)
    note_text = _render_frontmatter(merged, preferred_order)
    if existing_body:
        note_text += "\n" + existing_body.lstrip("\n")
        if not note_text.endswith("\n"):
            note_text += "\n"
    else:
        note_text += "\n"

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(note_text, encoding="utf-8")


def _project_note_path(vault_root: str, projects_folder: str, slug: str) -> Path:
    return Path(vault_root) / projects_folder / f"{slug}.md"


def _task_note_path(vault_root: str, tasks_folder: str, task_id: str) -> Path:
    return Path(vault_root) / tasks_folder / f"{task_id}.md"


def _project_note_updates(project_snapshot: dict, config: dict) -> dict:
    git_state = project_snapshot["git"]
    return {
        "pm-project": True,
        "title": _project_display_title(project_snapshot["project_slug"]),
        "coferlandia-project-id": project_snapshot["project_slug"],
        "repo_path": project_snapshot["repo_path"],
        "repo_remote": git_state.get("remote_url", ""),
        "default_branch": _config_value(config, "git", "default_branch", default="main"),
        "pm_owner": "coferlandia-project-manager",
        "archivist_initialized": project_snapshot["archivist_initialized"],
        "archivist_last_sync": _now_iso(),
        "last_seen_commit": git_state.get("last_commit_sha", ""),
        "status": project_snapshot["pm_status"],
        "tags": ["coferlandia", "repo", "agentic-dev"],
    }


def _task_note_updates(project_snapshot: dict, task: dict) -> dict:
    cleaned_title = _clean_task_title(task["title"])
    return {
        "pm-task": True,
        "title": cleaned_title,
        "coferlandia-task-id": task.get("task_id") or "",
        "project": project_snapshot["project_slug"],
        "repo_path": project_snapshot["repo_path"],
        "source": "TODO.md",
        "source_anchor": cleaned_title,
        "status": task["status"],
        "priority": "normal",
        "type": _task_type_for_title(cleaned_title),
        "progress": _task_progress(task["status"]),
        "assignees": ["coferlandia-project-manager"],
        "tags": [],
        "dependencies": [],
        "estimated_hours": None,
        "requires_tdd": True,
        "requires_code_review": True,
        "requires_archivist_sync": True,
        "execution_policy": "supervised_agentic",
    }


def _project_note_order() -> list[str]:
    return [
        "pm-project",
        "title",
        "coferlandia-project-id",
        "repo_path",
        "repo_remote",
        "default_branch",
        "pm_owner",
        "archivist_initialized",
        "archivist_last_sync",
        "last_seen_commit",
        "status",
        "tags",
    ]


def _task_note_order() -> list[str]:
    return [
        "pm-task",
        "title",
        "coferlandia-task-id",
        "project",
        "repo_path",
        "source",
        "source_anchor",
        "status",
        "priority",
        "type",
        "progress",
        "assignees",
        "tags",
        "dependencies",
        "estimated_hours",
        "requires_tdd",
        "requires_code_review",
        "requires_archivist_sync",
        "execution_policy",
    ]


def _project_snapshots(repos_root: Path, config: dict) -> list[dict]:
    snapshots = []
    default_branch = _config_value(config, "git", "default_branch", default="main")
    for project_path, is_git in iter_projects(repos_root):
        if not is_git:
            continue
        tasks = parse_todo_tasks(project_path / "TODO.md")
        snapshot = {
            "project_slug": project_path.name,
            "repo_path": project_path.as_posix(),
            "git": _build_git_state(project_path, default_branch),
            "tasks": tasks,
            "archivist_initialized": not missing_artifacts(project_path),
            "pm_status": _derive_project_pm_status(tasks),
        }
        snapshot["git"]["remote_url"] = _git(project_path, "remote", "get-url", "origin")
        snapshots.append(snapshot)
    return snapshots


def _sync_conflicts_from_snapshots(projects: list[dict]) -> list[dict]:
    conflicts = []
    for project in projects:
        if not project["archivist_initialized"]:
            conflicts.append(
                {
                    "project_slug": project["project_slug"],
                    "repo_path": project["repo_path"],
                    "type": "missing_archivist_artifact",
                    "missing_artifacts": missing_artifacts(Path(project["repo_path"])),
                }
            )
    return conflicts


def _read_existing_state(state_path: Path) -> dict:
    if not state_path.is_file():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _runtime_state_payload(
    repos_root: Path, config_path: Path, projects: list[dict], existing_state: dict | None = None
) -> dict:
    maintenance = (existing_state or {}).get("maintenance") or {}
    return {
        "version": 1,
        "last_scan_at": _now_iso(),
        "repos_root": repos_root.as_posix(),
        "projects_detected": len(projects),
        "maintenance": {
            "last_run_at": maintenance.get("last_run_at"),
            "next_due_at": maintenance.get("next_due_at"),
        },
        "runtime": {
            "config_path": config_path.as_posix(),
            "execution_mode": "supervised_agentic",
        },
    }


def _project_map_payload(projects: list[dict], config: dict) -> dict:
    settings = _obsidian_settings(config)
    mapped_projects = []
    for project in projects:
        task_ids = [task.get("task_id") for task in project["tasks"] if task.get("task_id")]
        mapped_projects.append(
            {
                "project_slug": project["project_slug"],
                "repo_path": project["repo_path"],
                "obsidian_project_note": _project_note_path(
                    settings["vault_root"], settings["pm_projects_folder"], project["project_slug"]
                ).as_posix()
                if settings["vault_root"]
                else None,
                "obsidian_tasks": [
                    _task_note_path(settings["vault_root"], settings["pm_tasks_folder"], task_id).as_posix()
                    for task_id in task_ids
                ]
                if settings["vault_root"]
                else [],
                "archivist_status": "initialized"
                if project["archivist_initialized"]
                else "missing_artifacts",
            }
        )
    return {"version": 1, "projects": mapped_projects}


def _write_runtime_artifacts(config_path: Path, repos_root: Path, projects: list[dict], *, apply: bool) -> dict:
    config = _load_config(config_path)
    runtime_root = _runtime_root()
    state_path = runtime_root / "state.json"
    project_map_path = runtime_root / "project-map.json"
    sync_log_path = runtime_root / "sync-log.md"
    sync_conflicts_path = runtime_root / "sync-conflicts.md"

    existing_state = _read_existing_state(state_path)
    state_payload = _runtime_state_payload(repos_root, config_path, projects, existing_state)
    project_map_payload = _project_map_payload(projects, config)
    conflicts = _sync_conflicts_from_snapshots(projects)

    if apply:
        _write_json(state_path, state_payload)
        _write_json(project_map_path, project_map_payload)
        sync_log_path.parent.mkdir(parents=True, exist_ok=True)
        sync_log_path.write_text(
            "\n".join(
                [
                    "# Sync Log",
                    "",
                    f"- Generated at: {state_payload['last_scan_at']}",
                    f"- Repos root: {repos_root.as_posix()}",
                    f"- Projects detected: {len(projects)}",
                    f"- Conflicts detected: {len(conflicts)}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        if conflicts:
            lines = ["# Sync Conflicts", ""]
            for conflict in conflicts:
                detail = ", ".join(conflict.get("missing_artifacts", [])) or conflict.get("details", "")
                lines.append(
                    f"- {conflict['project_slug']}: {conflict['type']} ({detail})"
                )
            sync_conflicts_path.parent.mkdir(parents=True, exist_ok=True)
            sync_conflicts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        elif sync_conflicts_path.exists():
            sync_conflicts_path.unlink()

    return {
        "state_path": state_path.as_posix(),
        "project_map_path": project_map_path.as_posix(),
        "sync_log_path": sync_log_path.as_posix(),
        "sync_conflicts_path": sync_conflicts_path.as_posix(),
        "conflicts": conflicts,
        "state_payload": state_payload,
        "project_map_payload": project_map_payload,
    }


def _backup_runtime_tree(*, apply: bool) -> dict:
    runtime_root = _runtime_root()
    backup_root = runtime_root / "backups"
    backup_name = _now_iso()
    backup_path = backup_root / backup_name
    copied = []
    manifest = {
        "status": "ok",
        "generated_at": backup_name,
        "source_root": runtime_root.as_posix(),
        "copied_files": copied,
    }

    if apply:
        backup_path.mkdir(parents=True, exist_ok=True)
        for rel_name in ("state.json", "project-map.json", "sync-log.md", "sync-conflicts.md"):
            source = runtime_root / rel_name
            if source.is_file():
                destination = backup_path / rel_name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                copied.append(destination.as_posix())
        _write_json(backup_path / "backup-manifest.json", manifest)

    return {
        "status": "ok",
        "mode": "apply" if apply else "dry-run",
        "backup_path": backup_path.as_posix(),
        "backup_root": backup_root.as_posix(),
        "copied_files": copied,
        "manifest": manifest,
    }


def _backup_before_apply_enabled(config: dict) -> bool:
    return bool(_config_value(config, "scripts", "backup_before_apply", default=True))


def _require_conflict_free_apply(projects: list[dict], *, operation: str) -> list[dict]:
    conflicts = _sync_conflicts_from_snapshots(projects)
    if conflicts:
        affected = ", ".join(conflict["project_slug"] for conflict in conflicts)
        raise SystemExit(
            f"Refusing to {operation}: unresolved sync conflicts affect {affected}. "
            "Resolve the conflicts before running --apply."
        )
    return conflicts


def _write_obsidian_notes(config_path: Path, repos_root: Path, projects: list[dict], *, apply: bool) -> dict:
    config = _load_config(config_path)
    settings = _obsidian_settings(config)
    if not settings["vault_root"]:
        raise ValueError("obsidian.vault_root is required in config")

    backup_payload = None
    if apply:
        _require_conflict_free_apply(projects, operation="sync Obsidian notes")
        if _backup_before_apply_enabled(config):
            backup_payload = _backup_runtime_tree(apply=True)

    project_paths = []
    task_paths = []
    written_projects = 0
    written_tasks = 0

    for project in projects:
        project_note = _project_note_path(
            settings["vault_root"], settings["pm_projects_folder"], project["project_slug"]
        )
        project_paths.append(project_note.as_posix())
        if apply:
            _write_markdown_note(project_note, _project_note_updates(project, config), _project_note_order())
            written_projects += 1

        for task in project["tasks"]:
            task_id = task.get("task_id")
            if not task_id:
                continue
            task_note = _task_note_path(
                settings["vault_root"], settings["pm_tasks_folder"], task_id
            )
            task_paths.append(task_note.as_posix())
            if apply:
                _write_markdown_note(task_note, _task_note_updates(project, task), _task_note_order())
                written_tasks += 1

    if apply:
        _write_runtime_artifacts(config_path, repos_root, projects, apply=True)

    payload = {
        "status": "ok",
        "mode": "apply" if apply else "dry-run",
        "vault_root": settings["vault_root"],
        "projects_written": written_projects if apply else len(project_paths),
        "tasks_written": written_tasks if apply else len(task_paths),
        "project_notes": project_paths,
        "task_notes": task_paths,
    }
    if backup_payload is not None:
        payload["backup"] = backup_payload
    return payload


def _update_maintenance_state(config_path: Path, repos_root: Path, projects: list[dict], *, apply: bool) -> dict:
    config = _load_config(config_path)
    runtime_root = _runtime_root()
    state_path = runtime_root / "state.json"
    report_path = runtime_root / "reports" / f"weekly-maintenance-{_now_iso()}.md"
    interval_days = int(_config_value(config, "archivist", "maintenance_interval_days", default=7))
    next_due = (datetime.now(timezone.utc) + timedelta(days=interval_days)).strftime(
        "%Y-%m-%dT%H%M%SZ"
    )
    conflicts = _sync_conflicts_from_snapshots(projects)

    payload = {
        "status": "ok",
        "mode": "apply" if apply else "dry-run",
        "maintenance_due": bool(conflicts),
        "archivist": {
            "projects_detected": len(projects),
            "initialized_projects": sum(1 for p in projects if p["archivist_initialized"]),
            "initialized_all": all(p["archivist_initialized"] for p in projects) if projects else True,
        },
        "conflicts": {
            "conflict_count": len(conflicts),
            "items": conflicts,
        },
        "write_performed": apply,
    }

    if apply:
        existing_state = _read_existing_state(state_path)
        state_payload = _runtime_state_payload(repos_root, config_path, projects, existing_state)
        state_payload["maintenance"] = {
            "last_run_at": _now_iso(),
            "next_due_at": next_due,
        }
        _write_json(state_path, state_payload)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            "\n".join(
                [
                    "# Weekly Maintenance Report",
                    "",
                    f"- Repos root: {repos_root.as_posix()}",
                    f"- Projects detected: {len(projects)}",
                    f"- Conflicts detected: {len(conflicts)}",
                    f"- Next due at: {next_due}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        payload["state_path"] = state_path.as_posix()
        payload["report_path"] = report_path.as_posix()
        payload["state"] = state_payload

    return payload


def _project_entry(project_path: Path) -> dict:
    missing = missing_artifacts(project_path)
    return {
        "project_slug": project_path.name,
        "repo_path": project_path.as_posix(),
        "archivist_initialized": not missing,
        "expected_artifacts": {
            name: name not in missing for name in EXPECTED_ARTIFACTS
        },
        "missing_artifacts": missing,
    }


def cmd_status(args: argparse.Namespace) -> dict:
    """Report archivist artifact presence per project (git repos only)."""
    projects = [
        _project_entry(project_path)
        for project_path, is_git in iter_projects(args.repos_root)
        if is_git
    ]
    return {"status": "ok", "projects_detected": len(projects), "projects": projects}


def cmd_sync_plan(args: argparse.Namespace) -> dict:
    """Map repo documentation into PM state without writing (dry-run only)."""
    projects = [
        _project_entry(project_path)
        for project_path, is_git in iter_projects(args.repos_root)
        if is_git
    ]
    syncable = sum(1 for p in projects if p["archivist_initialized"])
    return {
        "status": "ok",
        "mode": "dry-run",
        "projects_detected": len(projects),
        "syncable_projects": syncable,
        "projects": projects,
        "write_performed": False,
    }


def cmd_sync_from_repos(args: argparse.Namespace) -> dict:
    """Map repo documentation into PM state and optionally persist the PM files."""
    config_path = args.config
    if config_path is None:
        raise SystemExit("Missing required --config <path>")
    config = _load_config(config_path)
    projects = _project_snapshots(args.repos_root, config)
    syncable = sum(1 for p in projects if p["archivist_initialized"])
    payload = {
        "status": "ok",
        "mode": "apply" if args.apply else "dry-run",
        "projects_detected": len(projects),
        "syncable_projects": syncable,
        "projects": [
            {
                "project_slug": p["project_slug"],
                "repo_path": p["repo_path"],
                "archivist_initialized": p["archivist_initialized"],
                "missing_artifacts": missing_artifacts(Path(p["repo_path"])),
            }
            for p in projects
        ],
        "write_performed": args.apply,
    }
    if args.apply:
        _require_conflict_free_apply(projects, operation="sync PM state from repos")
        if _backup_before_apply_enabled(config):
            payload["backup"] = _backup_runtime_tree(apply=True)
        artifacts = _write_runtime_artifacts(config_path, args.repos_root, projects, apply=True)
        payload["state_path"] = artifacts["state_path"]
        payload["project_map_path"] = artifacts["project_map_path"]
        payload["sync_log_path"] = artifacts["sync_log_path"]
        payload["sync_conflicts_path"] = artifacts["sync_conflicts_path"]
        payload["conflicts"] = artifacts["conflicts"]
    return payload


def cmd_sync_to_obsidian(args: argparse.Namespace) -> dict:
    """Create or update Obsidian PM project and task notes from repo state."""
    config_path = args.config
    if config_path is None:
        raise SystemExit("Missing required --config <path>")
    config = _load_config(config_path)
    projects = _project_snapshots(args.repos_root, config)
    payload = _write_obsidian_notes(config_path, args.repos_root, projects, apply=args.apply)
    payload["projects_detected"] = len(projects)
    payload["syncable_projects"] = sum(1 for p in projects if p["archivist_initialized"])
    return payload


def cmd_backup(args: argparse.Namespace) -> dict:
    """Create a backup of the PM runtime tree."""
    config_path = args.config
    if config_path is None:
        raise SystemExit("Missing required --config <path>")
    _load_config(config_path)
    payload = _backup_runtime_tree(apply=args.apply)
    payload["config_path"] = config_path.as_posix()
    return payload


def cmd_conflicts(args: argparse.Namespace) -> dict:
    """Identify repo-level coverage gaps that require review.

    Phase 4 detects two conflict classes:
      - ``repo_path_missing``: a child dir of repos_root is not a git repo.
      - ``missing_archivist_artifact``: a git repo lacks one or more expected
        archivist files.

    Richer PM-vs-repo conflict detection (done/open drift, duplicates, manual
    edits, archival mismatches) is future work and intentionally not promised.
    """
    conflicts = []
    for project_path, is_git in iter_projects(args.repos_root):
        if not is_git:
            conflicts.append(
                {
                    "project_slug": project_path.name,
                    "repo_path": project_path.as_posix(),
                    "type": "repo_path_missing",
                    "details": "Project path is not a Git repository.",
                }
            )
            continue
        missing = missing_artifacts(project_path)
        if missing:
            conflicts.append(
                {
                    "project_slug": project_path.name,
                    "repo_path": project_path.as_posix(),
                    "type": "missing_archivist_artifact",
                    "missing_artifacts": missing,
                }
            )
    return {
        "status": "ok",
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
    }


def cmd_maintenance(args: argparse.Namespace) -> dict:
    """Aggregate archivist coverage and conflicts into a host-invoked report."""
    config_path = args.config
    if config_path is None:
        raise SystemExit("Missing required --config <path>")
    config = _load_config(config_path)
    projects = _project_snapshots(args.repos_root, config)
    return _update_maintenance_state(config_path, args.repos_root, projects, apply=args.apply)


def _render_text(command: str, payload: dict) -> str:
    if command == "status":
        lines = ["Archivist status report:", f"- projects_detected: {payload['projects_detected']}"]
        for project in payload["projects"]:
            missing = project["missing_artifacts"]
            missing_text = ", ".join(missing) if missing else "none"
            init = project["archivist_initialized"]
            lines.append(
                f"- {project['project_slug']}: archivist_initialized={init} missing={missing_text}"
            )
        return "\n".join(lines)

    if command == "sync-plan":
        lines = [
            "Repo-to-PM sync report:",
            f"- mode: {payload['mode']}",
            f"- projects_detected: {payload['projects_detected']}",
            f"- syncable_projects: {payload['syncable_projects']}",
            "- write_performed: false",
        ]
        return "\n".join(lines)

    if command == "sync-from-repos":
        lines = [
            "Repo-to-PM sync report:",
            f"- mode: {payload['mode']}",
            f"- projects_detected: {payload['projects_detected']}",
            f"- syncable_projects: {payload['syncable_projects']}",
            f"- write_performed: {payload['write_performed']}",
        ]
        return "\n".join(lines)

    if command == "sync-to-obsidian":
        lines = [
            "Obsidian sync report:",
            f"- mode: {payload['mode']}",
            f"- vault_root: {payload['vault_root']}",
            f"- projects_written: {payload['projects_written']}",
            f"- tasks_written: {payload['tasks_written']}",
        ]
        return "\n".join(lines)

    if command == "backup":
        lines = [
            "PM backup report:",
            f"- mode: {payload['mode']}",
            f"- backup_path: {payload['backup_path']}",
            f"- copied_files: {len(payload['copied_files'])}",
        ]
        return "\n".join(lines)

    if command == "conflicts":
        lines = ["Sync conflict report:", f"- conflict_count: {payload['conflict_count']}"]
        for conflict in payload["conflicts"]:
            detail = ", ".join(conflict.get("missing_artifacts", [])) or conflict.get("details", "")
            lines.append(f"- {conflict['project_slug']}: {conflict['type']} ({detail})")
        return "\n".join(lines)

    # maintenance
    return "\n".join(
        [
            "Weekly maintenance report:",
            f"- mode: {payload['mode']}",
            f"- maintenance_due: {payload['maintenance_due']}",
            f"- archivist_projects_detected: {payload['archivist']['projects_detected']}",
            f"- initialized_projects: {payload['archivist']['initialized_projects']}",
            f"- conflict_count: {payload['conflicts']['conflict_count']}",
            "- write_performed: false",
        ]
    )


_COMMANDS = {
    "status": cmd_status,
    "sync-plan": cmd_sync_plan,
    "sync-from-repos": cmd_sync_from_repos,
    "sync-to-obsidian": cmd_sync_to_obsidian,
    "backup": cmd_backup,
    "conflicts": cmd_conflicts,
    "maintenance": cmd_maintenance,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only archivist-state helpers for the PM.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p):
        p.add_argument("--repos-root", required=True, type=Path)
        p.add_argument("--config", type=Path)
        p.add_argument("--apply", action="store_true")
        p.add_argument(
            "--format",
            choices=("json", "text"),
            default="text",
            help="Output format (default: text).",
        )

    for name, func in _COMMANDS.items():
        sp = sub.add_parser(name, help=func.__doc__)
        add_common(sp)

    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _COMMANDS[args.command](args)
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(_render_text(args.command, payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
