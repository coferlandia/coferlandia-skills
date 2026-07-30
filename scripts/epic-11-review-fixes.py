#!/usr/bin/env python3
"""Apply code-review fixes for Epic #11."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


# Refine local->GitHub initialization and preserve legacy local v2 manifests.
path = "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/contract_initialization.py"
text = read(path)
text = replace_once(
    text,
    'generated_keys = ("source:", "repository:", "issue:", "epic:", "work_item:", "materialized_at:")',
    'generated_keys = ("snapshot:", "repository:", "issue:", "epic:", "work_item:", "materialized_at:")',
    path,
)
start = text.index("def _create_issue(")
end = text.index("\ndef _parent_matches", start)
text = text[:start] + '''def _ensure_issue(\n    service: GitHubService,\n    repository: str,\n    issues: list[dict[str, Any]],\n    *,\n    marker: str,\n    title: str,\n    body: str,\n    labels: list[str] | None = None,\n) -> tuple[dict[str, Any], bool]:\n    existing = _find_marked(issues, marker)\n    if existing:\n        return existing, False\n    created = service.create_issue(repository, title=title, body=body, labels=labels)\n    issues.append(created)\n    return created, True\n\n\n''' + text[end + 1:]
start = text.index("def _validate_existing_mapping(")
end = text.index("\ndef initialize_local_manifest", start)
text = text[:start] + '''def _validate_existing_mapping(repo: Path, manifest: dict[str, Any], service: GitHubService) -> None:\n    source = manifest.get("source") or {}\n    repository = str(source.get("repository") or "")\n    epic_number = source.get("epic_issue") or manifest.get("epic", {}).get("issue")\n    if not repository or epic_number is None:\n        raise ValidationError("GitHub-backed local manifest requires repository and Epic Issue identity")\n    epic_number = int(epic_number)\n    epic_issue = service.issue(IssueRef(repository, epic_number))\n    _read_contract(repo, manifest["epic"]["path"], "Epic")\n    origin = str(source.get("origin") or source.get("kind") or "github")\n    if origin == "local":\n        epic_marker = _marker("epic", str(manifest.get("epic", {}).get("id") or "EPIC"))\n        if epic_marker not in str(epic_issue.get("body") or ""):\n            raise ValidationError(f"Epic #{epic_number} does not carry the expected local contract marker")\n    for task in manifest["tasks"]:\n        _read_contract(repo, task["path"], f"task {task['id']}")\n        if task.get("id") == "DIRECT-PLAN":\n            continue\n        if task.get("issue") is None:\n            raise ValidationError(f"task {task['id']} is missing GitHub Issue identity")\n        issue_number = int(task["issue"])\n        issue = service.issue(IssueRef(repository, issue_number))\n        if not _parent_matches(issue, epic_number):\n            raise ValidationError(f"task {task['id']} Issue #{issue_number} is not linked to Epic #{epic_number}")\n        if origin == "local":\n            task_marker = _marker("task", str(task["id"]))\n            if task_marker not in str(issue.get("body") or ""):\n                raise ValidationError(f"task {task['id']} Issue #{issue_number} does not carry the expected contract marker")\n        elif str(task["id"]) != f"TASK-{issue_number}":\n            raise ValidationError(f"GitHub-origin task {task['id']} does not match Issue #{issue_number}")\n\n\n''' + text[end + 1:]
text = replace_once(
    text,
    '''    local = _validate_local_contracts(repo, manifest_path, manifest)\n    strategy = local["strategy"]\n''',
    '''    source = manifest.setdefault("source", {})\n    if not isinstance(manifest.get("execution_strategy"), dict):\n        try:\n            manifest["execution_strategy"] = _strategy(repo, manifest)\n        except ValidationError as exc:\n            if source.get("kind") == "local" and "missing required '## Execution Strategy' contract" in str(exc):\n                source.setdefault("origin", "local")\n                source.setdefault("tracking", "local")\n                source.setdefault("initial_materialization_complete", True)\n                return {"changed": False, "required": False, "tracking": "local", "legacy": True, "manifest": manifest}\n            raise\n\n    local = _validate_local_contracts(repo, manifest_path, manifest)\n    strategy = local["strategy"]\n''',
    path,
)
text = replace_once(
    text,
    '''    source = manifest.setdefault("source", {})\n    source.setdefault("origin", source.get("kind", "local"))\n''',
    '''    source.setdefault("origin", source.get("kind", "local"))\n''',
    path,
)
text = replace_once(text, "_try_native_parent(service, repository, epic_number, issue_number)", "service.try_add_sub_issue(repository, epic_number, issue_number)", path)
text = replace_once(
    text,
    '''        "created_epic": epic_created,\n        "created_tasks": created_tasks,''',
    '''        "created_epic": epic_created,\n        "created_analysis": analysis_created,\n        "created_tasks": created_tasks,''',
    path,
)
write(path, text)


# Remove the legacy refresh implementation entirely.
path = "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/materialization.py"
text = read(path)
start = text.index("\ndef _graph_signature(")
end = text.index("\ndef archive_delivered_tasks", start)
text = text[:start] + "\n" + text[end + 1:]
write(path, text)


# Update focused tests to the final no-refresh API and public GitHubService boundary.
path = "skills/ops/project-orchestrator/tests/test_contract_initialization.py"
text = read(path)
text = replace_once(
    text,
    "from project_orchestrator_cli.materialization import ANALYSIS_MARKER, materialize_github_epic, verify_github_freshness",
    "from project_orchestrator_cli.materialization import ANALYSIS_MARKER, materialize_github_epic",
    path,
)
text = replace_once(
    text,
    '''    def list_issues(self, repository: str) -> list[dict]:\n        return list(self.issues)\n\n''',
    '''    def list_issues(self, repository: str) -> list[dict]:\n        return list(self.issues)\n\n    def create_issue(self, repository: str, *, title: str, body: str, labels=None) -> dict:\n        item = {\n            "id": 1000 + self.next_number,\n            "number": self.next_number,\n            "title": title,\n            "body": body,\n            "state": "OPEN",\n            "url": f"https://github.test/{self.next_number}",\n            "parent": None,\n        }\n        self.next_number += 1\n        self.issues.append(item)\n        return item\n\n    def try_add_sub_issue(self, repository: str, epic_number: int, task_number: int) -> bool:\n        self.native_links.append((repository, epic_number, task_number))\n        return True\n\n''',
    path,
)
text = replace_once(
    text,
    '''        before = service.issue_calls\n        result = verify_github_freshness(repo, manifest)\n        self.assertEqual(service.issue_calls, before)\n        self.assertTrue(result["snapshot"])\n''',
    '''        self.assertEqual(service.issue_calls, 1)\n        self.assertNotIn("verify_github_freshness", read_materialization_source())\n''',
    path,
)
text = replace_once(
    text,
    '''DIRECT_GITHUB_STRATEGY = GITHUB_STRATEGY.replace("Decomposition: Analyst", "Decomposition: none").replace(\n    "Worker profile: Basic coding agents", "Worker profile: capable coding agent"\n)\n\n\nclass FakeGitHub:''',
    '''DIRECT_GITHUB_STRATEGY = GITHUB_STRATEGY.replace("Decomposition: Analyst", "Decomposition: none").replace(\n    "Worker profile: Basic coding agents", "Worker profile: capable coding agent"\n)\n\n\ndef read_materialization_source() -> str:\n    return (SKILL / "scripts/project_orchestrator_cli/materialization.py").read_text(encoding="utf-8")\n\n\nclass FakeGitHub:''',
    path,
)
write(path, text)


# Remove stale refresh-specific tests from the original suite; focused initialization tests replace them.
path = "skills/ops/project-orchestrator/tests/test_cli.py"
text = read(path)
pattern = re.compile(
    r"\n    def test_materialization_discovers_tasks_and_preserves_execution_metadata_on_refresh\(self\).*?"
    r"(?=\n    def test_git_staging_excludes_github_projection_files)",
    re.S,
)
text, count = pattern.subn("\n", text, count=1)
if count != 1:
    raise SystemExit(f"{path}: refresh test block not found")
write(path, text)


# Make the static assertion case-insensitive and assert the refresh API was removed.
path = "skills/ops/project-orchestrator/tests/test_initial_materialization_contract.py"
text = read(path)
text = replace_once(text, '            self.assertIn("frozen", text)', '            self.assertIn("frozen", text.lower())', path)
text = replace_once(
    text,
    '        self.assertNotIn("verify_github_freshness", engine)\n',
    '        materialization = self.read("skills/ops/project-orchestrator/scripts/project_orchestrator_cli/materialization.py")\n        self.assertNotIn("verify_github_freshness", engine)\n        self.assertNotIn("verify_github_freshness", materialization)\n',
    path,
)
write(path, text)

print("Epic #11 review fixes applied")
