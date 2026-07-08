#!/usr/bin/env python3
"""Read-only archivist-state helpers for coferlandia-project-manager.

This module is the single source of truth for the set of archivist-managed
artifacts a project repository is expected to contain, and for the read-only
inspection commands the PM exposes: ``status``, ``sync-plan``, ``conflicts``,
and ``maintenance``.

No write path is implemented here. The ``--apply`` flag is rejected by the
calling scripts (see ``pm-sync-from-repos.sh`` and ``pm-weekly-maintenance.sh``)
with a "not implemented yet" error, consistent with the Phase 3 approval-gated
placeholders. This keeps the read-only contract honest: a caller cannot mistake
a reported no-op for a successful write.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

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
    projects = []
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
        entry = _project_entry(project_path)
        projects.append(entry)
        if not entry["archivist_initialized"]:
            conflicts.append(
                {
                    "project_slug": project_path.name,
                    "repo_path": project_path.as_posix(),
                    "type": "missing_archivist_artifact",
                    "missing_artifacts": entry["missing_artifacts"],
                }
            )

    initialized = sum(1 for p in projects if p["archivist_initialized"])
    return {
        "status": "ok",
        "mode": "dry-run",
        "maintenance_due": bool(conflicts),
        "archivist": {
            "projects_detected": len(projects),
            "initialized_projects": initialized,
            "initialized_all": (initialized == len(projects)) if projects else True,
        },
        "conflicts": {
            "conflict_count": len(conflicts),
            "items": conflicts,
        },
        "write_performed": False,
    }


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
    "conflicts": cmd_conflicts,
    "maintenance": cmd_maintenance,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read-only archivist-state helpers for the PM.")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p):
        p.add_argument("--repos-root", required=True, type=Path)
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
