"""Contract-store initialization tests for project-orchestrator v2."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from project_orchestrator_cli.contract_initialization import initialize_local_manifest, initialize_local_spec
from project_orchestrator_cli.contracts import ValidationError
from project_orchestrator_cli.github_service import IssueRef
from project_orchestrator_cli.materialization import ANALYSIS_MARKER, materialize_github_epic, verify_github_freshness

GITHUB_STRATEGY = """## Execution Strategy

Tracking: GitHub
Decomposition: Analyst
Execution: Project Orchestrator
Worker profile: Basic coding agents
Review: Per-task + final Epic review
Integration: Single PR / squash merge
"""

LOCAL_STRATEGY = GITHUB_STRATEGY.replace("Tracking: GitHub", "Tracking: local fallback")
DIRECT_GITHUB_STRATEGY = GITHUB_STRATEGY.replace("Decomposition: Analyst", "Decomposition: none").replace(
    "Worker profile: Basic coding agents", "Worker profile: capable coding agent"
)


class FakeGitHub:
    def __init__(self) -> None:
        self.issues: list[dict] = []
        self.comments_by_issue: dict[int, list[dict]] = {}
        self.next_number = 40
        self.native_links: list[tuple] = []
        self.project_items: list[int] = []
        self.issue_calls = 0
        self.repository_calls = 0

    def repository_name(self) -> str:
        self.repository_calls += 1
        return "acme/repo"

    def resolve_issue_ref(self, raw: str) -> IssueRef:
        return IssueRef("acme/repo", 1)

    def issue(self, ref: IssueRef) -> dict:
        self.issue_calls += 1
        if ref.number == 1 and not self.issues:
            return {"number": 1, "title": "Epic", "body": GITHUB_STRATEGY, "state": "OPEN", "updatedAt": "t1"}
        for item in self.issues:
            if item["number"] == ref.number:
                return item
        raise AssertionError(ref)

    def comments(self, ref: IssueRef) -> list[dict]:
        return self.comments_by_issue.get(ref.number, [])

    def child_issues(self, ref: IssueRef) -> list[dict]:
        if ref.number == 1 and not self.issues:
            return [{"number": 2, "title": "Task", "body": "## Dependencies\nNone.\n", "state": "OPEN", "updatedAt": "t1"}]
        return [item for item in self.issues if f"Parent Epic: #{ref.number}" in str(item.get("body") or "")]

    def list_issues(self, repository: str) -> list[dict]:
        return list(self.issues)

    def existing_comment_with_marker(self, ref: IssueRef, marker: str) -> dict | None:
        return next((comment for comment in self.comments(ref) if marker in str(comment.get("body") or "")), None)

    def ensure_issue_comment(self, ref: IssueRef, marker: str, body: str) -> dict:
        existing = self.existing_comment_with_marker(ref, marker)
        if existing:
            return existing
        value = {"id": len(self.comments(ref)) + 1, "body": f"{marker}\n\n{body}"}
        self.comments_by_issue.setdefault(ref.number, []).append(value)
        return value

    def ensure_project_item(self, owner: str, number: int, url: str, issue_number: int) -> dict:
        self.project_items.append(issue_number)
        return {}

    def _json(self, *args: str):
        if args[:2] == ("api", "--method"):
            self.native_links.append(args)
            return {}
        endpoint = next((arg for arg in args if isinstance(arg, str) and arg.startswith("repos/")), "")
        if endpoint.endswith("/issues"):
            title = next(arg[6:] for arg in args if arg.startswith("title="))
            body = next(arg[5:] for arg in args if arg.startswith("body="))
            item = {
                "id": 1000 + self.next_number,
                "number": self.next_number,
                "title": title,
                "body": body,
                "state": "OPEN",
                "url": f"https://github.test/{self.next_number}",
                "parent": None,
            }
            self.next_number += 1
            self.issues.append(item)
            return item
        if "/issues/" in endpoint:
            number = int(endpoint.rsplit("/", 1)[1])
            item = next(issue for issue in self.issues if issue["number"] == number)
            return {"id": item["id"]}
        return {}


def write_local(root: Path, *, strategy: str = GITHUB_STRATEGY, task_count: int = 1) -> Path:
    work = root / ".agent" / "work-items" / "demo"
    (work / "tasks").mkdir(parents=True)
    (work / "EPIC.md").write_text(f"# Demo Epic\n\n{strategy}", encoding="utf-8")
    (work / "ANALYSIS.md").write_text("# Analysis\n\nUse existing boundaries.\n", encoding="utf-8")
    tasks = []
    for index in range(1, task_count + 1):
        task_id = f"TASK-{index:03d}"
        task_path = work / "tasks" / f"{task_id}.md"
        task_path.write_text(f"# Implement thing {index}\n\n## Dependencies\nNone.\n", encoding="utf-8")
        tasks.append({"id": task_id, "title": f"Implement thing {index}", "path": str(task_path.relative_to(root)), "depends_on": []})
    tracking = "GitHub" if "Tracking: GitHub" in strategy else "local fallback"
    decomposition = "none" if "Decomposition: none" in strategy else "Analyst"
    mode = "direct-plan" if decomposition == "none" else "task-execution"
    if mode == "direct-plan":
        tasks = [{"id": "DIRECT-PLAN", "title": "Demo Epic", "path": str((work / "EPIC.md").relative_to(root)), "depends_on": []}]
    manifest = {
        "schema_version": 2,
        "execution_mode": mode,
        "execution_strategy": {
            "tracking": tracking,
            "decomposition": decomposition,
            "execution": "Project Orchestrator",
            "worker_profile": "capable coding agent" if decomposition == "none" else "Basic coding agents",
            "review": "Per-task + final Epic review",
            "integration": "Single PR / squash merge",
        },
        "source": {"kind": "local"},
        "epic": {"id": "EPIC-demo", "title": "Demo Epic", "path": str((work / "EPIC.md").relative_to(root))},
        "tasks": tasks,
    }
    path = work / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class ContractInitializationTests(unittest.TestCase):
    def test_github_to_local_includes_canonical_analysis_and_freezes_snapshot(self) -> None:
        repo = Path(tempfile.mkdtemp())
        service = FakeGitHub()
        service.comments_by_issue[1] = [{"id": 9, "body": f"{ANALYSIS_MARKER}\n\n# Findings"}]
        manifest = materialize_github_epic(repo, "#1", service)
        self.assertTrue((repo / ".agent/work-items/epic-1/ANALYSIS.md").is_file())
        self.assertEqual(manifest["source"]["origin"], "github")
        self.assertTrue(manifest["source"]["initial_materialization_complete"])
        before = service.issue_calls
        result = verify_github_freshness(repo, manifest)
        self.assertEqual(service.issue_calls, before)
        self.assertTrue(result["snapshot"])

    def test_local_to_github_creates_marked_contracts_and_analysis(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo)
        service = FakeGitHub()
        result = initialize_local_manifest(repo, path, service=service)
        value = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(value["source"]["kind"], "github")
        self.assertEqual(value["source"]["origin"], "local")
        self.assertEqual(len(service.issues), 2)
        self.assertIn("coferlandia-contract-id: epic:EPIC-demo", service.issues[0]["body"])
        self.assertIn("Parent Epic: #40", service.issues[1]["body"])
        self.assertIsNotNone(service.existing_comment_with_marker(IssueRef("acme/repo", 40), ANALYSIS_MARKER))
        self.assertTrue(result["performed"])

    def test_second_initialization_reuses_issue_mapping_without_new_writes(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo)
        service = FakeGitHub()
        initialize_local_manifest(repo, path, service=service)
        issue_count = len(service.issues)
        comment_count = sum(len(comments) for comments in service.comments_by_issue.values())
        result = initialize_local_manifest(repo, path, service=service)
        self.assertEqual(len(service.issues), issue_count)
        self.assertEqual(sum(len(comments) for comments in service.comments_by_issue.values()), comment_count)
        self.assertFalse(result["performed"])

    def test_partial_retry_recovers_marked_epic_and_creates_only_missing_task(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo, task_count=2)
        service = FakeGitHub()
        epic_marker = "<!-- coferlandia-contract-id: epic:EPIC-demo -->"
        service.issues.append({"id": 1040, "number": 40, "title": "Demo Epic", "body": epic_marker, "state": "OPEN", "url": "https://github.test/40", "parent": None})
        service.next_number = 41
        result = initialize_local_manifest(repo, path, service=service)
        self.assertFalse(result["created_epic"])
        self.assertEqual(result["created_tasks"], [41, 42])
        self.assertEqual(len(service.issues), 3)

    def test_dry_run_performs_no_external_or_manifest_writes(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo)
        service = FakeGitHub()
        before = path.read_text(encoding="utf-8")
        result = initialize_local_manifest(repo, path, service=service, dry_run=True)
        self.assertTrue(result["required"])
        self.assertEqual(service.issues, [])
        self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_marker_collision_blocks_before_creating_more_issues(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo)
        service = FakeGitHub()
        marker = "<!-- coferlandia-contract-id: epic:EPIC-demo -->"
        service.issues = [{"number": 1, "body": marker}, {"number": 2, "body": marker}]
        with self.assertRaises(ValidationError):
            initialize_local_manifest(repo, path, service=service)
        self.assertEqual(len(service.issues), 2)

    def test_existing_mapping_requires_parent_linkage(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo)
        service = FakeGitHub()
        initialize_local_manifest(repo, path, service=service)
        task = next(item for item in service.issues if "task:TASK-001" in item["body"])
        task["body"] = task["body"].replace("Parent Epic: #40\n", "")
        with self.assertRaises(ValidationError):
            initialize_local_manifest(repo, path, service=service)

    def test_local_fallback_never_resolves_or_writes_github(self) -> None:
        repo = Path(tempfile.mkdtemp())
        path = write_local(repo, strategy=LOCAL_STRATEGY)
        service = FakeGitHub()
        result = initialize_local_manifest(repo, path, service=service)
        self.assertEqual(result["tracking"], "local")
        self.assertEqual(service.repository_calls, 0)
        self.assertEqual(service.issues, [])

    def test_direct_spec_dry_run_reports_required_initialization_without_issue_ids(self) -> None:
        repo = Path(tempfile.mkdtemp())
        spec = repo / "plan.md"
        spec.write_text(f"# Direct plan\n\n{DIRECT_GITHUB_STRATEGY}", encoding="utf-8")
        manifest_path, result = initialize_local_spec(repo, spec, dry_run=True, service=FakeGitHub())
        self.assertIsNone(manifest_path)
        self.assertTrue(result["required"])
        self.assertNotIn("epic_issue", result["manifest"]["source"])
        self.assertFalse((repo / ".agent").exists())


if __name__ == "__main__":
    unittest.main()
