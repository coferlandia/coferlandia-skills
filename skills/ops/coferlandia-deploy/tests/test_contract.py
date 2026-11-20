from __future__ import annotations

import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[4]


class CoferlandiaDeployContractTests(unittest.TestCase):
    def test_public_catalog_registers_generic_deployment_skill(self) -> None:
        index = (REPO_ROOT / "skills" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn(
            "[coferlandia-deploy](./ops/coferlandia-deploy/)",
            index,
        )

    def test_skill_binds_immutable_release_to_expected_sha_and_terminal_outcome(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        lowered = text.lower()
        for token in (
            "immutable release",
            "expected sha",
            "resolved sha",
            "healthy",
            "failed",
            "blocked",
            "deployment evidence",
            "repository-declared",
        ):
            self.assertIn(token, lowered)
        self.assertIn("arbitrary command", lowered)
        self.assertIn("cofer-vm-admin", lowered)

    def test_skill_preserves_provider_state_ownership_and_reentry_idempotency(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("PREPARING", text)
        self.assertIn("DEPLOYING", text)
        self.assertIn("CHECKING", text)
        self.assertIn("must not mirror", text)
        self.assertIn("already HEALTHY", text)
        self.assertIn("no-op", text)

    def test_pressure_cases_cover_fail_closed_boundaries(self) -> None:
        cases = json.loads((SKILL_ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases["positive"]), 5)
        self.assertGreaterEqual(len(cases["negative"]), 5)
        self.assertGreaterEqual(len(cases["pressure"]), 5)


if __name__ == "__main__":
    unittest.main()
