import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[4]


class LocalReleaseContractTests(unittest.TestCase):
    def test_local_release_owns_local_release_surface(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: local-release", text)
        self.assertIn("READY_FOR_RELEASE", text)
        self.assertIn("Qualification strategy: LOCAL", text)
        self.assertIn("coferlandia-release-publisher", text)
        self.assertIn("exact release candidate", text)
        self.assertIn("release manifest", text)
        self.assertIn("RELEASE_REPAIR_REQUIRED", text)
        self.assertIn("must not deploy", text)

    def test_local_release_never_falls_back_to_github_native(self):
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("never falls back to `chat-release`", text)
        self.assertIn("must not invoke GitHub-native Qualification", text)

    def test_skill_is_listed_in_public_index(self):
        index = (ROOT / "skills" / "INDEX.md").read_text(encoding="utf-8")
        self.assertIn("[local-release](./engineering/local-release/)", index)


if __name__ == "__main__":
    unittest.main()
