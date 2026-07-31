"""Regression tests for the optional pre-execution Architecture Gate."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from project_orchestrator_cli.contracts import ValidationError  # noqa: E402
from project_orchestrator_cli import work_items as module  # noqa: E402


class ArchitectureGateTests(unittest.TestCase):
    def contract(self, gate: str = "") -> str:
        return f"""# Plan

## Execution Strategy
Tracking: local fallback
Decomposition: none
Execution: Project Orchestrator
Worker profile: capable coding agent
Review: final independent review
Integration: Single PR / squash merge

{gate}
"""

    def test_absent_gate_is_backward_compatible(self) -> None:
        self.assertEqual("not-required", module.validate_architecture_gate("")["status"])

    def test_not_required_and_passed_gate_continue(self) -> None:
        not_required = "## Architecture Gate\n\nMode: none\nStatus: not-required\n"
        passed = "## Architecture Gate\n\nMode: the-architect\nStatus: passed\nBlocker: none\n"
        self.assertEqual("not-required", module.validate_architecture_gate(not_required)["status"])
        self.assertEqual("passed", module.validate_architecture_gate(passed)["status"])

    def test_required_or_blocked_architect_gate_stops_execution(self) -> None:
        for status in ("required", "blocked"):
            text = f"## Architecture Gate\n\nMode: the-architect\nStatus: {status}\nBlocker: preflight pending\n"
            with self.assertRaisesRegex(ValidationError, "Architecture Gate blocks execution"):
                module.validate_architecture_gate(text)

    def test_direct_plan_is_blocked_before_runtime_preparation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(self.contract("## Architecture Gate\n\nMode: the-architect\nStatus: required\nBlocker: run preflight\n"), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "Architecture Gate blocks execution"):
                module.direct_plan_manifest(path)

    def test_passed_direct_plan_carries_normalized_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "plan.md"
            path.write_text(self.contract("## Architecture Gate\n\nMode: the-architect\nStatus: passed\nAssessment reference: ENG-demo\nBlocker: none\n"), encoding="utf-8")
            manifest = module.direct_plan_manifest(path)
            self.assertEqual("passed", manifest["architecture_gate"]["status"])

    def test_local_manifest_reads_epic_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            epic = root / "EPIC.md"
            epic.write_text(self.contract("## Architecture Gate\n\nMode: the-architect\nStatus: blocked\nBlocker: unresolved risk\n"), encoding="utf-8")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps({
                "schema_version": 2,
                "execution_mode": "direct-plan",
                "source": {"kind": "local", "tracking": "local"},
                "epic": {"id": "EPIC-demo", "path": str(epic)},
                "tasks": [{"id": "DIRECT-PLAN", "path": str(epic), "depends_on": []}],
            }), encoding="utf-8")
            with self.assertRaisesRegex(ValidationError, "unresolved risk"):
                module.load_manifest(manifest)

    def test_addendum_stays_inside_epic_contract(self) -> None:
        reference = (Path(__file__).resolve().parents[3] / "engineering" / "the-architect" / "references" / "architecture-gate.md").read_text(encoding="utf-8")
        self.assertIn("Architect Addendum", reference)
        self.assertIn("ARCHITECTURE.md", reference)


if __name__ == "__main__":
    unittest.main()
