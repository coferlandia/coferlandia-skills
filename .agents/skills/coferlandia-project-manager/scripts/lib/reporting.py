#!/usr/bin/env python3
"""Reporting and observation surface for coferlandia-project-manager.

This module is the single source of truth for all report generation commands
the PM exposes: ``portfolio-report``, ``project-report``, ``task-report``,
``health-check``, and ``worktree-cleanup``.

All commands are read-only. They aggregate data from existing PM scan/conflict/
archivist infrastructure and present it as structured JSON or human-readable
Markdown. The write path (sync-to-obsidian, backup-pm-db) is not implemented
here.

A lightweight TODO.md parser extracts task-level data so the portfolio report
can answer the Reporting Questions defined in SKILL.md.
"""
import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Canonical archivist artifacts — mirrors archivist.py.
EXPECTED_ARTIFACTS = (
    "README.md",
    "TODO.md",
    "HISTORY.md",
    "DECISIONS.md",
    "RUNBOOK.md",
    "AGENTS.md",
)

# All valid task statuses from SKILL.md.
VALID_TASK_STATUSES = (
    "intake",
    "needs-brainstorming",
    "spec-writing",
    "spec-review",
    "planning",
    "plan-review",
    "ready-for-agent",
    "worktree-prep",
    "implementing",
    "debugging",
    "code-review",
    "changes-requested",
    "verification",
    "branch-finishing",
    "syncing-docs",
    "done",
    "blocked",
    "cancelled",
)

# Statuses considered "active" (not terminal).
ACTIVE_STATUSES = {
    "intake",
    "needs-brainstorming",
    "spec-writing",
    "spec-review",
    "planning",
    "plan-review",
    "ready-for-agent",
    "worktree-prep",
    "implementing",
    "debugging",
    "code-review",
    "changes-requested",
    "verification",
    "branch-finishing",
    "syncing-docs",
    "blocked",
}

# Statuses considered "in review".
REVIEW_STATUSES = {"code-review", "spec-review", "plan-review", "changes-requested"}

# Statuses needing brainstorming.
BRAINSTORM_STATUSES = {"needs-brainstorming"}

# Statuses waiting for plan approval.
PLAN_WAIT_STATUSES = {"planning", "plan-review"}

# Statuses waiting for code review.
CODE_REVIEW_STATUSES = {"code-review", "changes-requested"}


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _is_git_repo(path: Path) -> bool:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip()


def _iter_git_projects(repos_root: Path):
    """Yield project Paths that are git repos, sorted."""
    if not repos_root.is_dir():
        return
    for p in sorted(p for p in repos_root.iterdir() if p.is_dir()):
        if _is_git_repo(p):
            yield p


def _missing_artifacts(project_path: Path) -> list:
    return [name for name in EXPECTED_ARTIFACTS if not (project_path / name).is_file()]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


# ---------------------------------------------------------------------------
# TODO.md parser
# ---------------------------------------------------------------------------

_TODO_TASK_RE = re.compile(
    r"^\s*[-*]\s+\[(?P<status>[ xX])\]\s+"
    r"(?P<line>.*)",
    re.MULTILINE,
)

# Regex to detect explicit status tags like [status: planning] or [ready-for-agent].
# Must be checked AFTER checkbox pattern to avoid false matches.
_TODO_EXPLICIT_STATUS_RE = re.compile(
    r"\[\s*(?:status\s*:\s*)?(?P<status>[a-z-]+)\s*\]",
    re.IGNORECASE,
)

_TODO_ID_RE = re.compile(
    r"(?P<id>TASK-[a-zA-Z0-9_-]+|PM-[0-9]+|task[-_]?[a-zA-Z0-9_-]+)",
    re.IGNORECASE,
)


def parse_todo_tasks(todo_path: Path) -> list:
    """Parse an archivist TODO.md and extract tasks with status."""
    if not todo_path.is_file():
        return []
    text = todo_path.read_text(encoding="utf-8")
    tasks = []
    for m in _TODO_TASK_RE.finditer(text):
        checkbox_status = m.group("status").lower()
        line = m.group("line").strip()
        if not line:
            continue

        # Detect explicit status tags like [status: planning] or [ready-for-agent].
        status_match = _TODO_EXPLICIT_STATUS_RE.search(line)
        detected_status = None
        if status_match:
            candidate = status_match.group("status").strip().lower()
            if candidate in VALID_TASK_STATUSES:
                detected_status = candidate

        # Derive status from checkbox if no explicit tag.
        if detected_status is None:
            if checkbox_status == "x":
                detected_status = "done"
            else:
                detected_status = "intake"

        # Detect task ID.
        id_match = _TODO_ID_RE.search(line)
        task_id = id_match.group("id") if id_match else None

        tasks.append({
            "task_id": task_id,
            "title": line,
            "status": detected_status,
            "checkbox_done": checkbox_status == "x",
        })
    return tasks


# ---------------------------------------------------------------------------
# HISTORY.md parser (lightweight — looks for recent completions)
# ---------------------------------------------------------------------------

_HISTORY_ENTRY_RE = re.compile(
    r"^\s*[-*]\s+(?P<line>.+)",
    re.MULTILINE,
)


def parse_history_entries(history_path: Path, since_days: int = 7) -> list:
    """Parse HISTORY.md and return entries that might represent recent completions."""
    if not history_path.is_file():
        return []
    text = history_path.read_text(encoding="utf-8")
    entries = []
    now = datetime.now(timezone.utc)
    for m in _HISTORY_ENTRY_RE.finditer(text):
        line = m.group("line").strip()
        if not line:
            continue
        entries.append({"line": line})
    return entries


# ---------------------------------------------------------------------------
# Git extended state (worktrees, remotes, staleness)
# ---------------------------------------------------------------------------

def _build_git_state(project_path: Path, default_branch: str = "main") -> dict:
    branch = _git(project_path, "branch", "--show-current")
    detached = branch == ""
    last_sha = _git(project_path, "rev-parse", "--short=7", "HEAD")

    # Dirty / untracked.
    porcelain = _git(project_path, "status", "--porcelain").splitlines()
    dirty = any(not line.startswith("??") for line in porcelain if line)
    untracked = any(line.startswith("??") for line in porcelain)

    # Remote state.
    remote_url = _git(project_path, "remote", "get-url", "origin")
    ahead_behind = {"ahead": 0, "behind": 0}
    tracking = _git(
        project_path, "rev-parse", "--abbrev-ref", f"{branch}@{{upstream}}"
    )
    if tracking and not detached:
        ab = _git(project_path, "rev-list", "--left-right", "--count", f"HEAD...{tracking}")
        parts = ab.split()
        if len(parts) == 2:
            ahead_behind["ahead"] = int(parts[0])
            ahead_behind["behind"] = int(parts[1])

    # Last commit date (for staleness).
    last_date_iso = _git(project_path, "log", "-1", "--format=%cI")
    last_commit_dt = None
    days_since_commit = None
    if last_date_iso:
        try:
            last_commit_dt = datetime.fromisoformat(last_date_iso)
            now_dt = datetime.now(timezone.utc)
            days_since_commit = (now_dt - last_commit_dt).days
        except (ValueError, OSError):
            pass

    return {
        "branch": branch,
        "detached_head": detached,
        "default_branch": default_branch,
        "last_commit_sha": last_sha,
        "dirty": dirty,
        "untracked": untracked,
        "remote_url": remote_url,
        "ahead": ahead_behind["ahead"],
        "behind": ahead_behind["behind"],
        "last_commit_date": last_date_iso,
        "days_since_commit": days_since_commit,
    }


# ---------------------------------------------------------------------------
# Worktree helpers
# ---------------------------------------------------------------------------

def _list_worktrees(project_path: Path) -> list:
    """Return a list of worktree dicts for a project."""
    output = _git(project_path, "worktree", "list", "--porcelain")
    worktrees = []
    current = {}
    for line in output.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[len("worktree "):].strip()}
        elif line.startswith("branch "):
            ref = line[len("branch "):].strip()
            current["branch"] = ref.replace("refs/heads/", "")
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):].strip()
        elif line == "":
            pass
        elif line.startswith("bare") or line.startswith("detached"):
            current["is_" + line.split()[0]] = True
    if current:
        worktrees.append(current)
    return worktrees


def _classify_worktree(wt: dict, main_path: Path) -> dict:
    """Classify a worktree as main, clean-linked, dirty-linked, or orphaned."""
    wt_path = Path(wt.get("path", "")).resolve()
    is_main = wt_path == main_path.resolve()

    wt_state = {
        "path": wt.get("path", ""),
        "branch": wt.get("branch", "(detached)"),
        "is_main": is_main,
        "classification": "main",
    }

    if is_main:
        return wt_state

    dirty = False
    if wt_path.is_dir():
        result = subprocess.run(
            ["git", "-C", str(wt_path), "status", "--porcelain"],
            capture_output=True, text=True, check=False,
        )
        dirty = bool(result.stdout.strip())

    wt_state["dirty"] = dirty
    if dirty:
        wt_state["classification"] = "dirty-linked"
    else:
        wt_state["classification"] = "clean-linked"

    return wt_state


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_portfolio_report(args: argparse.Namespace) -> dict:
    """Generate a portfolio-wide report answering all 14 Reporting Questions."""
    repos_root = args.repos_root
    default_branch = args.default_branch or "main"

    projects_data = []
    all_tasks = []
    conflicts = []
    stale_threshold = args.stale_days

    total_active = 0
    total_blocked = 0
    ready_for_agent = 0
    in_review = 0
    completed_this_week = 0
    uncommitted = 0
    ahead_or_behind = 0
    missing_archivist = 0
    sync_conflicts_count = 0
    no_recent_activity = 0
    needs_brainstorming = 0
    waiting_plan_approval = 0
    waiting_code_review = 0
    needs_maintenance = 0

    for project_path in _iter_git_projects(repos_root):
        slug = project_path.name
        git_state = _build_git_state(project_path, default_branch)
        missing = _missing_artifacts(project_path)

        archivist_ok = not missing
        todo_tasks = parse_todo_tasks(project_path / "TODO.md")
        history_entries = parse_history_entries(project_path / "HISTORY.md", since_days=7)

        project_entry = {
            "project_slug": slug,
            "repo_path": project_path.as_posix(),
            "git": git_state,
            "archivist_initialized": archivist_ok,
            "missing_artifacts": missing,
            "tasks": todo_tasks,
            "recent_history_entries": len(history_entries),
        }
        projects_data.append(project_entry)

        # Classify tasks.
        for task in todo_tasks:
            all_tasks.append({**task, "project": slug, "repo_path": project_path.as_posix()})
            if task["status"] == "done":
                completed_this_week += 1
            if task["status"] == "blocked":
                total_blocked += 1
            if task["status"] in REVIEW_STATUSES:
                in_review += 1
            if task["status"] == "ready-for-agent":
                ready_for_agent += 1
            if task["status"] in BRAINSTORM_STATUSES:
                needs_brainstorming += 1
            if task["status"] in PLAN_WAIT_STATUSES:
                waiting_plan_approval += 1
            if task["status"] in CODE_REVIEW_STATUSES:
                waiting_code_review += 1

        # Active projects: those with at least one non-terminal task.
        has_active = any(t["status"] in ACTIVE_STATUSES for t in todo_tasks)
        if has_active or not todo_tasks:
            # If no tasks at all, still count as active if it's a discovered repo.
            total_active += 1

        # Git conditions.
        if git_state["dirty"] or git_state["untracked"]:
            uncommitted += 1
        if git_state["ahead"] > 0 or git_state["behind"] > 0:
            ahead_or_behind += 1

        # Archivist coverage.
        if not archivist_ok:
            missing_archivist += 1
            conflicts.append({
                "project_slug": slug,
                "type": "missing_archivist_artifact",
                "missing_artifacts": missing,
            })

        # Staleness.
        days = git_state.get("days_since_commit")
        if days is not None and days > stale_threshold:
            no_recent_activity += 1

        # Maintenance needs.
        if not archivist_ok or git_state["dirty"] or git_state["ahead"] > 0 or git_state["behind"] > 0:
            needs_maintenance += 1

    sync_conflicts_count = len(conflicts)

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "repos_root": repos_root.as_posix(),
        "summary": {
            "active_projects": total_active,
            "blocked_projects": total_blocked,
            "ready_for_agent_tasks": ready_for_agent,
            "projects_in_review": in_review,
            "tasks_completed_this_week": completed_this_week,
            "repos_with_uncommitted_changes": uncommitted,
            "repos_ahead_or_behind_remote": ahead_or_behind,
            "projects_lacking_archivist_artifacts": missing_archivist,
            "projects_with_sync_conflicts": sync_conflicts_count,
            "projects_without_recent_activity": no_recent_activity,
            "tasks_needing_brainstorming": needs_brainstorming,
            "tasks_waiting_for_plan_approval": waiting_plan_approval,
            "tasks_waiting_for_code_review": waiting_code_review,
            "projects_needing_maintenance": needs_maintenance,
        },
        "projects": projects_data,
        "tasks": all_tasks,
        "conflicts": conflicts,
    }


def cmd_project_report(args: argparse.Namespace) -> dict:
    """Generate a report for one managed project."""
    repos_root = args.repos_root
    default_branch = args.default_branch or "main"
    project_slug = args.project

    project_path = repos_root / project_slug
    if not project_path.is_dir() or not _is_git_repo(project_path):
        return {
            "status": "error",
            "error": f"Project '{project_slug}' not found or not a Git repository under repos_root.",
        }

    git_state = _build_git_state(project_path, default_branch)
    missing = _missing_artifacts(project_path)
    tasks = parse_todo_tasks(project_path / "TODO.md")
    history_count = len(parse_history_entries(project_path / "HISTORY.md", since_days=7))

    blocked_tasks = [t for t in tasks if t["status"] == "blocked"]
    ready_tasks = [t for t in tasks if t["status"] == "ready-for-agent"]
    active_tasks = [t for t in tasks if t["status"] in ACTIVE_STATUSES]

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "project_slug": project_slug,
        "repo_path": project_path.as_posix(),
        "git": git_state,
        "archivist": {
            "initialized": not missing,
            "missing_artifacts": missing,
        },
        "tasks": {
            "total": len(tasks),
            "active": len(active_tasks),
            "ready_for_agent": len(ready_tasks),
            "blocked": len(blocked_tasks),
            "items": tasks,
        },
        "recent_history_entries": history_count,
    }


def cmd_task_report(args: argparse.Namespace) -> dict:
    """Generate a report for one managed task."""
    repos_root = args.repos_root
    task_id = args.task.lower()

    found = None
    for project_path in _iter_git_projects(repos_root):
        tasks = parse_todo_tasks(project_path / "TODO.md")
        for task in tasks:
            tid = (task.get("task_id") or "").lower()
            if tid and tid == task_id:
                found = {**task, "project": project_path.name, "repo_path": project_path.as_posix()}
                break
        if found:
            break

    if not found:
        # Broaden search: look for task_id as a substring in task titles.
        for project_path in _iter_git_projects(repos_root):
            tasks = parse_todo_tasks(project_path / "TODO.md")
            for task in tasks:
                if task_id in task["title"].lower():
                    found = {**task, "project": project_path.name, "repo_path": project_path.as_posix()}
                    break
            if found:
                break

    if not found:
        return {
            "status": "error",
            "error": f"Task '{args.task}' not found in any project TODO.md under repos_root.",
        }

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "task": found,
    }


def cmd_health_check(args: argparse.Namespace) -> dict:
    """Summarize portfolio health, sync gaps, and maintenance needs."""
    repos_root = args.repos_root
    default_branch = args.default_branch or "main"
    stale_threshold = args.stale_days

    health_issues = []
    projects_summary = []
    total_projects = 0
    healthy_count = 0

    for project_path in _iter_git_projects(repos_root):
        total_projects += 1
        slug = project_path.name
        git_state = _build_git_state(project_path, default_branch)
        missing = _missing_artifacts(project_path)

        issues = []
        if missing:
            issues.append({"type": "missing_archivist_artifact", "details": missing})
        if git_state["dirty"]:
            issues.append({"type": "dirty_repo"})
        if git_state["untracked"]:
            issues.append({"type": "untracked_files"})
        if git_state["ahead"] > 0:
            issues.append({"type": "ahead_of_remote", "ahead": git_state["ahead"]})
        if git_state["behind"] > 0:
            issues.append({"type": "behind_remote", "behind": git_state["behind"]})

        days = git_state.get("days_since_commit")
        if days is not None and days > stale_threshold:
            issues.append({"type": "stale", "days_since_commit": days})

        is_healthy = not issues
        if is_healthy:
            healthy_count += 1

        project_summary = {
            "project_slug": slug,
            "healthy": is_healthy,
            "issues": issues,
        }
        projects_summary.append(project_summary)

        for issue in issues:
            health_issues.append({"project_slug": slug, **issue})

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "repos_root": repos_root.as_posix(),
        "summary": {
            "total_projects": total_projects,
            "healthy_projects": healthy_count,
            "projects_with_issues": total_projects - healthy_count,
            "total_issues": len(health_issues),
            "maintenance_due": len(health_issues) > 0,
        },
        "issues": health_issues,
        "projects": projects_summary,
    }


def cmd_worktree_cleanup(args: argparse.Namespace) -> dict:
    """Enumerate worktrees, classify them, and suggest safe removals."""
    repos_root = args.repos_root
    suggestions = []

    for project_path in _iter_git_projects(repos_root):
        slug = project_path.name
        worktrees = _list_worktrees(project_path)

        for wt in worktrees:
            classified = _classify_worktree(wt, project_path)
            entry = {
                "project_slug": slug,
                **classified,
            }
            suggestions.append(entry)

    # Filter to non-main worktrees only for actionable suggestions.
    actionable = [s for s in suggestions if not s["is_main"]]
    clean_removable = [s for s in actionable if s["classification"] == "clean-linked"]
    dirty_caution = [s for s in actionable if s["classification"] == "dirty-linked"]

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "repos_root": repos_root.as_posix(),
        "mode": args.mode or "dry-run",
        "summary": {
            "total_worktrees": len(suggestions),
            "main_worktrees": len([s for s in suggestions if s["is_main"]]),
            "linked_worktrees": len(actionable),
            "clean_suggesting_removal": len(clean_removable),
            "dirty_caution": len(dirty_caution),
        },
        "worktrees": suggestions,
        "clean_removable": clean_removable,
        "dirty_caution": dirty_caution,
    }


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------

def _render_portfolio_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Portfolio Report",
        "",
        f"- Active projects: {s['active_projects']}",
        f"- Blocked projects: {s['blocked_projects']}",
        f"- Ready-for-agent tasks: {s['ready_for_agent_tasks']}",
        f"- Projects in review: {s['projects_in_review']}",
        f"- Tasks completed this week: {s['tasks_completed_this_week']}",
        f"- Repos with uncommitted changes: {s['repos_with_uncommitted_changes']}",
        f"- Repos ahead or behind remote: {s['repos_ahead_or_behind_remote']}",
        f"- Projects lacking archivist artifacts: {s['projects_lacking_archivist_artifacts']}",
        f"- Projects with sync conflicts: {s['projects_with_sync_conflicts']}",
        f"- Projects without recent activity: {s['projects_without_recent_activity']}",
        f"- Tasks needing brainstorming: {s['tasks_needing_brainstorming']}",
        f"- Tasks waiting for plan approval: {s['tasks_waiting_for_plan_approval']}",
        f"- Tasks waiting for code review: {s['tasks_waiting_for_code_review']}",
        f"- Projects needing maintenance: {s['projects_needing_maintenance']}",
        "",
    ]

    # Project details.
    for project in payload.get("projects", []):
        git = project.get("git", {})
        slug = project["project_slug"]
        task_count = len(project.get("tasks", []))
        lines.append(f"## {slug}")
        lines.append(f"- Branch: {git.get('branch', 'unknown')}")
        lines.append(f"- Dirty: {git.get('dirty', False)}")
        lines.append(f"- Ahead/behind: {git.get('ahead', 0)}/{git.get('behind', 0)}")
        lines.append(f"- Archivist: {'initialized' if project.get('archivist_initialized') else 'missing: ' + ', '.join(project.get('missing_artifacts', []))}")
        lines.append(f"- Tasks: {task_count}")
        lines.append("")

    return "\n".join(lines)


def _render_project_markdown(payload: dict) -> str:
    if payload.get("status") == "error":
        return f"# Project Report\n\nError: {payload.get('error', '')}\n"

    git = payload.get("git", {})
    arch = payload.get("archivist", {})
    tasks = payload.get("tasks", {})
    lines = [
        "# Project Report",
        "",
        f"- Project: {payload.get('project_slug', '')}",
        f"- Repo path: {payload.get('repo_path', '')}",
        f"- Git status: branch={git.get('branch', '')} dirty={git.get('dirty', False)} untracked={git.get('untracked', False)}",
        f"- Archivist status: {'initialized' if arch.get('initialized') else 'missing: ' + ', '.join(arch.get('missing_artifacts', []))}",
        f"- PM status: {git.get('branch', '')}",
        f"- Ready tasks: {tasks.get('ready_for_agent', 0)}",
        f"- Blockers: {tasks.get('blocked', 0)}",
        "",
    ]

    for task in tasks.get("items", []):
        lines.append(f"- [{task['status']}] {task.get('task_id', '—')}: {task['title']}")

    return "\n".join(lines)


def _render_task_markdown(payload: dict) -> str:
    if payload.get("status") == "error":
        return f"# Task Report\n\nError: {payload.get('error', '')}\n"

    task = payload.get("task", {})
    lines = [
        "# Task Report",
        "",
        f"- Task: {task.get('task_id', '—')}",
        f"- Project: {task.get('project', '')}",
        f"- Source: TODO.md",
        f"- Status: {task.get('status', '')}",
        f"- Owner: coferlandia-project-manager",
        f"- Review state: {'in review' if task.get('status') in REVIEW_STATUSES else 'not in review'}",
        f"- Verification state: {'verified' if task.get('status') == 'done' else 'pending'}",
        "",
    ]
    return "\n".join(lines)


def _render_health_check_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Health Check Report",
        "",
        f"- Total projects: {s['total_projects']}",
        f"- Healthy projects: {s['healthy_projects']}",
        f"- Projects with issues: {s['projects_with_issues']}",
        f"- Total issues: {s['total_issues']}",
        f"- Maintenance due: {s['maintenance_due']}",
        "",
    ]

    if payload.get("issues"):
        lines.append("## Issues")
        for issue in payload["issues"]:
            slug = issue.get("project_slug", "unknown")
            itype = issue.get("type", "unknown")
            details = ""
            if itype == "missing_archivist_artifact":
                details = f"missing: {', '.join(issue.get('details', []))}"
            elif itype == "ahead_of_remote":
                details = f"ahead by {issue.get('ahead', 0)} commits"
            elif itype == "behind_remote":
                details = f"behind by {issue.get('behind', 0)} commits"
            elif itype == "stale":
                details = f"{issue.get('days_since_commit', '?')} days since last commit"
            else:
                details = itype.replace("_", " ")
            lines.append(f"- {slug}: {details}")
        lines.append("")

    return "\n".join(lines)


def _render_worktree_cleanup_markdown(payload: dict) -> str:
    s = payload["summary"]
    lines = [
        "# Worktree Cleanup Report",
        "",
        f"- Total worktrees: {s['total_worktrees']}",
        f"- Main worktrees: {s['main_worktrees']}",
        f"- Linked worktrees: {s['linked_worktrees']}",
        f"- Clean (suggesting removal): {s['clean_suggesting_removal']}",
        f"- Dirty (caution): {s['dirty_caution']}",
        "",
    ]

    if payload.get("clean_removable"):
        lines.append("## Clean linked worktrees (safe to remove)")
        for wt in payload["clean_removable"]:
            lines.append(f"- {wt['project_slug']}: {wt['branch']} at {wt['path']}")
        lines.append("")

    if payload.get("dirty_caution"):
        lines.append("## Dirty linked worktrees (do not remove)")
        for wt in payload["dirty_caution"]:
            lines.append(f"- {wt['project_slug']}: {wt['branch']} at {wt['path']}")
        lines.append("")

    return "\n".join(lines)


_RENDERERS = {
    "portfolio-report": _render_portfolio_markdown,
    "project-report": _render_project_markdown,
    "task-report": _render_task_markdown,
    "health-check": _render_health_check_markdown,
    "worktree-cleanup": _render_worktree_cleanup_markdown,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_COMMANDS = {
    "portfolio-report": cmd_portfolio_report,
    "project-report": cmd_project_report,
    "task-report": cmd_task_report,
    "health-check": cmd_health_check,
    "worktree-cleanup": cmd_worktree_cleanup,
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reporting and observation surface for coferlandia-project-manager.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p):
        p.add_argument("--repos-root", required=True, type=Path)
        p.add_argument("--format", choices=("json", "markdown"), default="markdown")
        p.add_argument("--default-branch", default="main")
        p.add_argument("--stale-days", type=int, default=30)

    # portfolio-report
    p = sub.add_parser("portfolio-report", help=cmd_portfolio_report.__doc__)
    add_common(p)

    # project-report
    p = sub.add_parser("project-report", help=cmd_project_report.__doc__)
    add_common(p)
    p.add_argument("--project", required=True, help="Project slug (directory name under repos_root).")

    # task-report
    p = sub.add_parser("task-report", help=cmd_task_report.__doc__)
    add_common(p)
    p.add_argument("--task", required=True, help="Task ID to search for across all project TODO.md files.")

    # health-check
    p = sub.add_parser("health-check", help=cmd_health_check.__doc__)
    add_common(p)

    # worktree-cleanup
    p = sub.add_parser("worktree-cleanup", help=cmd_worktree_cleanup.__doc__)
    add_common(p)
    p.add_argument("--mode", choices=("dry-run", "suggest"), default="dry-run")

    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    payload = _COMMANDS[args.command](args)

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        renderer = _RENDERERS.get(args.command)
        if renderer:
            print(renderer(payload))
        else:
            print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
