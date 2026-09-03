from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from project_orchestrator_cli.integration import _gate_state
from project_orchestrator_cli.integration_gates import (
    FAILED,
    GREEN,
    PENDING,
    evaluate_required_gates,
    integration_github_config,
    validate_integration_config,
)
from project_orchestrator_cli.state import RunStore, TRANSITIONS


class IntegrationGateConfigTests(unittest.TestCase):
    def test_missing_integration_config_is_backward_compatible_and_generic(self) -> None:
        github = integration_github_config({})
        self.assertEqual(github["required_gates"], [])
        self.assertEqual(github["wait_seconds"], 30)
        self.assertIsNone(github["max_wait_cycles"])
        self.assertNotIn("Fast CI", repr(github))

    def test_validate_config_rejects_duplicate_gate_ids(self) -> None:
        config = {"integration": {"github": {"required_gates": [
            {"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]},
            {"id": "ci", "kind": "check_run", "name": "Quality", "allowed_conclusions": ["success"]},
        ], "wait_seconds": 30, "max_wait_cycles": None}}}
        with self.assertRaisesRegex(Exception, "duplicate integration gate id"):
            validate_integration_config(config)

    def test_validate_config_rejects_unsupported_gate_kind(self) -> None:
        config = {"integration": {"github": {"required_gates": [
            {"id": "ci", "kind": "magic", "name": "CI", "allowed_conclusions": ["success"]},
        ], "wait_seconds": 30, "max_wait_cycles": None}}}
        with self.assertRaisesRegex(Exception, "unsupported integration gate kind"):
            validate_integration_config(config)

    def test_integration_states_are_recoverable_without_provider_wait_semantics(self) -> None:
        self.assertIn("WAITING_FOR_INTEGRATION_CHECKS", TRANSITIONS["PR_OPEN_AWAITING_MERGE_APPROVAL"])
        self.assertIn("INTEGRATION_CHECKS_FAILED", TRANSITIONS["PR_OPEN_AWAITING_MERGE_APPROVAL"])
        self.assertIn("INTEGRATING", TRANSITIONS["WAITING_FOR_INTEGRATION_CHECKS"])
        self.assertIn("INTEGRATING", TRANSITIONS["INTEGRATION_CHECKS_FAILED"])
        self.assertNotIn("WAITING_FOR_PROVIDER", TRANSITIONS["WAITING_FOR_INTEGRATION_CHECKS"])

    def test_non_green_gate_persists_state_and_stops_integration_call(self) -> None:
        common_dir = Path(tempfile.mkdtemp()) / ".git"
        common_dir.mkdir()
        store = RunStore(common_dir, "run-gate")
        store.create({"run_id": "run-gate", "state": "PR_OPEN_AWAITING_MERGE_APPROVAL"})
        candidate = {"kind": "pr_head", "gate_sha": "a" * 40, "pr_head_sha": "a" * 40, "base_sha": "b" * 40, "pr_number": 1}
        with self.assertRaisesRegex(Exception, "integration checks are not green"):
            _gate_state(store, PENDING, candidate, phase="initial")
        self.assertEqual(store.load()["state"], "WAITING_FOR_INTEGRATION_CHECKS")


class IntegrationGateEvaluationTests(unittest.TestCase):
    SHA = "a" * 40

    def test_all_exact_sha_gates_success_is_green(self) -> None:
        gates = [
            {"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]},
            {"id": "quality", "kind": "check_run", "name": "Quality Gate", "app": "github-actions", "allowed_conclusions": ["success"]},
        ]
        observations = [
            {"kind": "workflow", "workflow": ".github/workflows/ci.yml", "sha": self.SHA, "status": "completed", "conclusion": "success", "event": "pull_request"},
            {"kind": "check_run", "name": "Quality Gate", "app": "github-actions", "sha": self.SHA, "status": "completed", "conclusion": "success"},
        ]
        self.assertEqual(evaluate_required_gates(gates, observations, self.SHA).decision, GREEN)

    def test_pending_exact_sha_gate_is_pending(self) -> None:
        gates = [{"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]}]
        observations = [{"kind": "workflow", "workflow": ".github/workflows/ci.yml", "sha": self.SHA, "status": "in_progress", "conclusion": None, "event": "pull_request"}]
        self.assertEqual(evaluate_required_gates(gates, observations, self.SHA).decision, PENDING)

    def test_missing_required_gate_is_failed(self) -> None:
        gates = [{"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]}]
        self.assertEqual(evaluate_required_gates(gates, [], self.SHA).decision, FAILED)

    def test_old_sha_green_does_not_satisfy_current_candidate(self) -> None:
        gates = [{"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]}]
        observations = [{"kind": "workflow", "workflow": ".github/workflows/ci.yml", "sha": "b" * 40, "status": "completed", "conclusion": "success", "event": "pull_request"}]
        self.assertEqual(evaluate_required_gates(gates, observations, self.SHA).decision, FAILED)

    def test_neutral_and_skipped_are_not_implicitly_green(self) -> None:
        for conclusion in ("neutral", "skipped"):
            with self.subTest(conclusion=conclusion):
                gates = [{"id": "quality", "kind": "check_run", "name": "Quality", "allowed_conclusions": ["success"]}]
                observations = [{"kind": "check_run", "name": "Quality", "sha": self.SHA, "status": "completed", "conclusion": conclusion}]
                self.assertEqual(evaluate_required_gates(gates, observations, self.SHA).decision, FAILED)

    def test_neutral_or_skipped_can_be_explicitly_allowed(self) -> None:
        gates = [{"id": "quality", "kind": "check_run", "name": "Quality", "allowed_conclusions": ["success", "neutral", "skipped"]}]
        for conclusion in ("neutral", "skipped"):
            with self.subTest(conclusion=conclusion):
                observations = [{"kind": "check_run", "name": "Quality", "sha": self.SHA, "status": "completed", "conclusion": conclusion}]
                self.assertEqual(evaluate_required_gates(gates, observations, self.SHA).decision, GREEN)

    def test_duplicate_authoritative_matches_fail_closed(self) -> None:
        gates = [{"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]}]
        observations = [
            {"kind": "workflow", "workflow": ".github/workflows/ci.yml", "sha": self.SHA, "status": "completed", "conclusion": "success", "event": "pull_request"},
            {"kind": "workflow", "workflow": ".github/workflows/ci.yml", "sha": self.SHA, "status": "completed", "conclusion": "success", "event": "pull_request"},
        ]
        self.assertEqual(evaluate_required_gates(gates, observations, self.SHA).decision, FAILED)


if __name__ == "__main__":
    unittest.main()
