from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"expected text not found in {path}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_section(path: str, heading: str, body: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if heading in text:
        return
    target.write_text(text.rstrip() + "\n\n" + heading + "\n\n" + body.strip() + "\n", encoding="utf-8")


# engine.py: integration policy is part of config v2 and validate-config.
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/engine.py",
    "from .git_service import GitService\nfrom .materialization import materialize_github_epic\n",
    "from .git_service import GitService\nfrom .integration_gates import validate_integration_config\nfrom .materialization import materialize_github_epic\n",
)
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/engine.py",
    "    \"roles\": {\n",
    "    \"integration\": {\n        \"github\": {\n            \"required_gates\": [],\n            \"wait_seconds\": 30,\n            \"max_wait_cycles\": None,\n        }\n    },\n    \"roles\": {\n",
)
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/engine.py",
    '    for key in ("git", "roles", "providers", "retry", "timeouts", "loops", "protocol"):\n',
    '    for key in ("git", "integration", "roles", "providers", "retry", "timeouts", "loops", "protocol"):\n',
)
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/engine.py",
    '        if role not in value["roles"]:\n            raise ValidationError(f"configuration requires role: {role}")\n\n\ndef _resolve_manifest',
    '        if role not in value["roles"]:\n            raise ValidationError(f"configuration requires role: {role}")\n    validate_integration_config(value)\n\n\ndef _resolve_manifest',
)

# claims.py: completion hooks are permitted only after verified PROJECT_COMPLETED.
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/claims.py",
    '    else:\n        state = integrate_run(repo, run_id, config)\n    _project_all(repo, state, config, "done")\n',
    '    else:\n        state = integrate_run(repo, run_id, config)\n    if state.get("state") != "PROJECT_COMPLETED":\n        return state\n    _project_all(repo, state, config, "done")\n',
)

# github_service.py: do not classify arbitrary merge-policy permission text as auth;
# verify current base is an ancestor of a merge-group candidate, not necessarily a direct parent.
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/github_service.py",
    '            if "auth" in lowered or "token" in lowered or "login" in lowered or "scope" in lowered or "permission" in lowered:\n',
    '            if "auth" in lowered or "token" in lowered or "login" in lowered or "scope" in lowered:\n',
)
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/github_service.py",
    '''    def _commit_parent_shas(self, repository: str, sha: str) -> list[str]:\n        value = self._json("api", f"repos/{repository}/commits/{sha}")\n        parents = value.get("parents") if isinstance(value, dict) else None\n        return [str(item.get("sha")) for item in (parents or []) if isinstance(item, dict) and item.get("sha")]\n\n''',
    '''    def _commit_contains_base(self, repository: str, base_sha: str, head_sha: str) -> bool:\n        value = self._json("api", f"repos/{repository}/compare/{base_sha}...{head_sha}")\n        status = value.get("status") if isinstance(value, dict) else None\n        return status in {"ahead", "identical"}\n\n''',
)
replace_once(
    "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/github_service.py",
    '            parents = self._commit_parent_shas(repository, head_sha)\n            if base_sha not in parents:\n                continue\n',
    '            if not self._commit_contains_base(repository, base_sha, head_sha):\n                continue\n',
)

# Tests: assert public validate-config behavior, not only the pure helper.
replace_once(
    "skills/ops/project-orchestrator/tests/test_integration_gates.py",
    "import sys\nimport tempfile\nimport unittest\n",
    "import copy\nimport sys\nimport tempfile\nimport unittest\n",
)
replace_once(
    "skills/ops/project-orchestrator/tests/test_integration_gates.py",
    "from project_orchestrator_cli.github_service import GitHubService\n",
    "from project_orchestrator_cli.engine import DEFAULT_CONFIG, validate_config\nfrom project_orchestrator_cli.github_service import GitHubService\n",
)
needle = '''    def test_validate_config_rejects_duplicate_gate_ids(self) -> None:\n'''
insert = '''    def test_default_config_exposes_generic_integration_policy(self) -> None:\n        github = DEFAULT_CONFIG["integration"]["github"]\n        self.assertEqual(github["required_gates"], [])\n        self.assertEqual(github["wait_seconds"], 30)\n        self.assertIsNone(github["max_wait_cycles"])\n\n    def test_public_validate_config_rejects_invalid_integration_policy(self) -> None:\n        config = copy.deepcopy(DEFAULT_CONFIG)\n        config["integration"]["github"]["required_gates"] = [\n            {"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]},\n            {"id": "ci", "kind": "check_run", "name": "Quality", "allowed_conclusions": ["success"]},\n        ]\n        with self.assertRaisesRegex(Exception, "duplicate integration gate id"):\n            validate_config(config)\n\n''' + needle
replace_once(
    "skills/ops/project-orchestrator/tests/test_integration_gates.py",
    needle,
    insert,
)

# Public skill contract.
skill = "skills/ops/project-orchestrator/SKILL.md"
replace_once(
    skill,
    '  tested: "2026-07-31 - Durable Epic/task claims, duplicate-run exclusion, cancellation release, and In Progress Project projection covered."',
    '  tested: "2026-09-03 - Exact-candidate integration gates, durable CI states, rerun selection, remote-base validation, and conditional squash merge covered across repository CI."',
)
append_section(
    skill,
    "## GitHub integration gates",
    '''For GitHub-backed final integration, repository configuration may declare deterministic required gates under `integration.github.required_gates`. The controller evaluates only authoritative observations for the exact current integration candidate: normally the current PR head SHA, or the current merge-group SHA when a valid Merge Queue candidate exists. A green older SHA, comment, local test, or human assertion never satisfies the gate.\n\nMissing required gates and disallowed terminal conclusions fail closed. Pending states use `WAITING_FOR_INTEGRATION_CHECKS`; terminal gate failures use `INTEGRATION_CHECKS_FAILED`. `neutral` and `skipped` count only when that gate explicitly lists them in `allowed_conclusions`. Transient observation errors never imply GREEN. Claims and Project `Done` projection remain active/incomplete until verified `PROJECT_COMPLETED`.\n\nImmediately before merge, re-read PR head, remote base, candidate identity, and all configured gates. Only an unchanged GREEN candidate may enter `INTEGRATING`. The squash merge itself must carry the expected PR head SHA so GitHub atomically rejects a race-window head change. Remote base movement preserves the existing base-reconciliation/review requirement. Read `references/configuration.md`, `references/state-machine.md`, and `references/recovery.md` before changing these semantics.''',
)

append_section(
    "skills/ops/project-orchestrator/references/configuration.md",
    "## GitHub integration gates",
    '''GitHub-backed integration may configure required gates independently of GitHub branch-protection availability:\n\n```json\n{\n  "integration": {\n    "github": {\n      "required_gates": [\n        {\n          "id": "primary-ci",\n          "kind": "workflow",\n          "workflow": ".github/workflows/ci.yml",\n          "allowed_conclusions": ["success"],\n          "events": ["pull_request", "merge_group"]\n        }\n      ],\n      "wait_seconds": 30,\n      "max_wait_cycles": null\n    }\n  }\n}\n```\n\n`workflow` gates match a workflow path or numeric workflow id. `check_run` gates match an exact check name and optional app slug/name. Gate IDs must be unique. `allowed_conclusions` is explicit; `neutral` and `skipped` are not successful unless listed. An absent `integration` section or an empty `required_gates` list is backward-compatible and declares no orchestrator-owned remote CI requirement.\n\nThe policy is validated by `validate-config`. Gate observations are evaluated only for the exact integration-candidate SHA and never inferred from local validation, comments, or historical runs.''',
)
append_section(
    "skills/ops/project-orchestrator/references/architecture.md",
    "## Integration gate boundary",
    '''Final GitHub integration is intentionally split into three layers: `GitHubService` acquires authoritative GitHub evidence and performs the head-conditional merge; `integration_gates.py` is a pure deterministic policy evaluator with no I/O; `integration.py` owns run-state transitions, double revalidation, and the final merge decision.\n\nThe authoritative candidate is the current PR head unless a valid current `merge_group` candidate for that PR contains the current remote base. The controller uses the remote base SHA, not a possibly stale local `main` ref, at this boundary. No semantic worker or model may decide that CI is green.''',
)
append_section(
    "skills/ops/project-orchestrator/references/state-machine.md",
    "## GitHub integration-check states",
    '''The GitHub integration path is:\n\n```text\nPR_OPEN_AWAITING_MERGE_APPROVAL\n  -> WAITING_FOR_INTEGRATION_CHECKS\n  -> INTEGRATION_CHECKS_FAILED\n  -> INTEGRATING\n  -> INTEGRATED\n  -> ARCHIVING\n  -> PROJECT_COMPLETED\n```\n\n`WAITING_FOR_INTEGRATION_CHECKS` represents pending or temporarily unavailable authoritative CI evidence and is separate from provider availability. `INTEGRATION_CHECKS_FAILED` represents a missing required gate or a terminal non-allowed conclusion. Both preserve claims and are re-evaluable by a later integration attempt. `INTEGRATING` means review identity, remote base, exact-candidate gates, and the second pre-merge revalidation have all passed and the controller is executing the merge side effect.''',
)
append_section(
    "skills/ops/project-orchestrator/references/recovery.md",
    "## Integration-check recovery",
    '''Queued, requested, waiting, pending, and in-progress integration checks are recoverable asynchronous states. Persist `WAITING_FOR_INTEGRATION_CHECKS` and retry by re-reading the current PR/candidate; never reuse an older green SHA. A terminal required-gate failure persists `INTEGRATION_CHECKS_FAILED`; fix or legitimately rerun the failing gate, then re-evaluate the newest authoritative observation.\n\nTransient GitHub/API observation errors fail closed and never become GREEN. Permanent authentication/scope failures transition through the integration wait boundary into `BLOCKED_BY_AUTHENTICATION`. Base movement remains `BLOCKED_BY_BASE_MOVED` and requires the existing reconciliation/fresh-review path. Claims are not released from any of these states.''',
)
append_section(
    "skills/ops/project-orchestrator/references/candidate-commit-lifecycle.md",
    "## Integration candidate authority",
    '''The reviewed Epic HEAD and the CI integration candidate are related but distinct authorities. Direct PR integration uses the current PR head SHA for both review identity and gate identity. Merge Queue may introduce a `merge_group` SHA whose CI is authoritative for the queued candidate while the merge side effect still requires the expected PR head SHA.\n\nA green run for any superseded PR SHA is historical evidence only. Any material change that changes the reviewed PR head invalidates the old review and must pass the existing fresh-review lifecycle before its own exact-candidate CI can authorize integration.''',
)

print("issue 28 final reconciliation complete")
