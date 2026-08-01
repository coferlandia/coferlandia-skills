from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_skill_contract_and_cases(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cases = json.loads((ROOT / "tests/cases.json").read_text(encoding="utf-8"))
        self.assertIn("name: coferlandia-release-maintainer", text)
        self.assertIn("final-delivery gate", text.lower())
        self.assertIn("superpowers:writing-skills", text)
        self.assertIn("coferlandia-release-maintainer-cli.py", text)
        self.assertIn("Do not activate", text)
        self.assertGreaterEqual(len(cases["positive"]), 4)
        self.assertGreaterEqual(len(cases["negative"]), 4)
        for reference in ("release-model.md", "change-classification.md", "final-delivery-checklist.md"):
            self.assertIn(reference, text)
            self.assertTrue((ROOT / "references" / reference).is_file())


if __name__ == "__main__":
    unittest.main()
