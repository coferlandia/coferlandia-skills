from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"expected text not found in {path}: {old[:140]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


service = "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/github_service.py"
integration = "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/integration.py"
tests = "skills/ops/project-orchestrator/tests/test_integration_gates.py"

replace_once(
    service,
    '''    def _commit_contains_base(self, repository: str, base_sha: str, head_sha: str) -> bool:\n        value = self._json("api", f"repos/{repository}/compare/{base_sha}...{head_sha}")\n        status = value.get("status") if isinstance(value, dict) else None\n        return status in {"ahead", "identical"}\n\n    def merge_group_candidate(self, repository: str, pr_number: int, pr_head_sha: str, base_sha: str) -> dict[str, Any] | None:\n''',
    '''    def merge_queue_entry(self, repository: str, pr_number: int) -> dict[str, Any] | None:\n        owner, name = repository.split("/", 1)\n        query = """\n        query($owner: String!, $name: String!, $number: Int!) {\n          repository(owner: $owner, name: $name) {\n            pullRequest(number: $number) {\n              mergeQueueEntry {\n                id\n                state\n                enqueuedAt\n                position\n                baseCommit { oid }\n                headCommit { oid }\n              }\n            }\n          }\n        }\n        """\n        value = self._json(\n            "api", "graphql",\n            "-f", f"query={query}",\n            "-f", f"owner={owner}",\n            "-f", f"name={name}",\n            "-F", f"number={pr_number}",\n        )\n        repository_value = value.get("data", {}).get("repository") if isinstance(value, dict) else None\n        pull = repository_value.get("pullRequest") if isinstance(repository_value, dict) else None\n        entry = pull.get("mergeQueueEntry") if isinstance(pull, dict) else None\n        return entry if isinstance(entry, dict) else None\n\n    def _commit_contains_base(self, repository: str, base_sha: str, head_sha: str) -> bool:\n        value = self._json("api", f"repos/{repository}/compare/{base_sha}...{head_sha}")\n        status = value.get("status") if isinstance(value, dict) else None\n        return status in {"ahead", "identical"}\n\n    def merge_group_candidate(\n        self, repository: str, pr_number: int, pr_head_sha: str, base_sha: str, *, enqueued_at: str | None = None\n    ) -> dict[str, Any] | None:\n''',
)
replace_once(
    service,
    '''            if not isinstance(run, dict) or not run.get("head_sha"):\n                continue\n            prs = run.get("pull_requests") or []\n''',
    '''            if not isinstance(run, dict) or not run.get("head_sha"):\n                continue\n            if enqueued_at and str(run.get("created_at") or "") < enqueued_at:\n                continue\n            prs = run.get("pull_requests") or []\n''',
)

replace_once(
    integration,
    '''    base_sha = service.branch_sha(repository, base_branch)\n    merge_group = service.merge_group_candidate(repository, pr_number, pr_head_sha, base_sha)\n    if merge_group:\n        return merge_group\n    return {\n''',
    '''    base_sha = service.branch_sha(repository, base_branch)\n    queue_entry = service.merge_queue_entry(repository, pr_number)\n    if queue_entry:\n        queue_base = ((queue_entry.get("baseCommit") or {}).get("oid"))\n        queue_head = ((queue_entry.get("headCommit") or {}).get("oid"))\n        pending_reason = None\n        if queue_base and str(queue_base) != base_sha:\n            pending_reason = "merge queue entry has not reconciled to the current remote base"\n        elif queue_head and str(queue_head) != pr_head_sha:\n            pending_reason = "merge queue entry does not represent the current PR head"\n        merge_group = None if pending_reason else service.merge_group_candidate(\n            repository, pr_number, pr_head_sha, base_sha, enqueued_at=str(queue_entry.get("enqueuedAt") or "") or None\n        )\n        if merge_group:\n            merge_group["merge_queue_entry_id"] = queue_entry.get("id")\n            return merge_group\n        return {\n            "kind": "merge_group",\n            "gate_sha": None,\n            "pr_head_sha": pr_head_sha,\n            "base_sha": base_sha,\n            "pr_number": pr_number,\n            "merge_queue_entry_id": queue_entry.get("id"),\n            "pending_reason": pending_reason or "merge queue entry exists but no current merge_group candidate is available yet",\n        }\n    return {\n''',
)
replace_once(
    integration,
    '''    candidate = _resolve_github_candidate(service, repository, pr_number, state)\n    if candidate["base_sha"] != state["base_commit"]:\n        return candidate, "BASE_MOVED"\n    gate_config = integration_github_config(config)\n''',
    '''    candidate = _resolve_github_candidate(service, repository, pr_number, state)\n    if candidate["base_sha"] != state["base_commit"]:\n        return candidate, "BASE_MOVED"\n    if candidate.get("pending_reason"):\n        state = store.load()\n        _record_gate_evidence(store, state, candidate, [], PENDING, ({"decision": PENDING, "reason": candidate["pending_reason"]},), phase)\n        return candidate, PENDING\n    gate_config = integration_github_config(config)\n''',
)

replace_once(
    tests,
    "from project_orchestrator_cli.integration import _gate_state\n",
    "from project_orchestrator_cli.integration import _gate_state, _resolve_github_candidate\n",
)
insert_before = '''\n\nclass ConditionalMergeTests(unittest.TestCase):\n'''
new_tests = '''\n\nclass MergeQueueAuthorityTests(unittest.TestCase):\n    def test_active_queue_without_current_merge_group_never_falls_back_to_pr_head(self) -> None:\n        class FakeService:\n            def pull_request(self, repository: str, number: int) -> dict[str, object]:\n                return {"state": "OPEN", "headRefOid": "a" * 40, "baseRefName": "main"}\n\n            def branch_sha(self, repository: str, branch: str) -> str:\n                return "b" * 40\n\n            def merge_queue_entry(self, repository: str, number: int) -> dict[str, object]:\n                return {\n                    "id": "MQE_1",\n                    "enqueuedAt": "2026-09-03T17:00:00Z",\n                    "baseCommit": {"oid": "b" * 40},\n                    "headCommit": {"oid": "a" * 40},\n                }\n\n            def merge_group_candidate(self, repository: str, number: int, pr_head_sha: str, base_sha: str, *, enqueued_at: str | None = None) -> None:\n                return None\n\n        state = {"final_reviewed_sha": "a" * 40, "base_branch": "main"}\n        candidate = _resolve_github_candidate(FakeService(), "owner/repo", 7, state)\n        self.assertEqual(candidate["kind"], "merge_group")\n        self.assertIsNone(candidate["gate_sha"])\n        self.assertIn("no current merge_group", candidate["pending_reason"])\n\n    def test_not_queued_uses_current_pr_head_candidate(self) -> None:\n        class FakeService:\n            def pull_request(self, repository: str, number: int) -> dict[str, object]:\n                return {"state": "OPEN", "headRefOid": "a" * 40, "baseRefName": "main"}\n\n            def branch_sha(self, repository: str, branch: str) -> str:\n                return "b" * 40\n\n            def merge_queue_entry(self, repository: str, number: int) -> None:\n                return None\n\n        state = {"final_reviewed_sha": "a" * 40, "base_branch": "main"}\n        candidate = _resolve_github_candidate(FakeService(), "owner/repo", 7, state)\n        self.assertEqual(candidate["kind"], "pr_head")\n        self.assertEqual(candidate["gate_sha"], "a" * 40)\n''' + insert_before
replace_once(tests, insert_before, new_tests)

print("active merge queue authority fix applied")
