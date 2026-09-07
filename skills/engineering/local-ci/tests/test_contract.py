import json
import re
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]

class LocalCIContractTests(unittest.TestCase):
    def test_skill_contract(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"name:\s*local-ci")
        self.assertRegex(text, r"category:\s*engineering")
        self.assertIn("READY_FOR_CI", text)
        self.assertIn("READY_FOR_MERGE", text)
        self.assertIn(".coferlandia/ci/profile.json", text)
        self.assertIn("LOCAL", text)
        self.assertIn("must not run GitHub-native CI", text)
        self.assertIn("must not merge", text)
        for token in ("SecretarIA", "scripts/validate-all.sh", "fast-ci.yml"):
            self.assertNotIn(token, text)

    def test_changelog_matches_version(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        changelog = (SKILL_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        version = re.search(r'version:\s*["\']([^"\']+)', skill).group(1)
        self.assertIn(f"## {version} —", changelog)

    def test_activation_cases_have_positive_and_negative(self):
        cases = json.loads((SKILL_ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases["positive"]), 4)
        self.assertGreaterEqual(len(cases["negative"]), 4)

if __name__ == "__main__":
    unittest.main()
