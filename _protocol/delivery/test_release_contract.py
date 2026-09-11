import unittest
from pathlib import Path


class ReadyForReleaseContractTests(unittest.TestCase):
    def test_ready_for_release_has_exact_candidate_and_strategy_identity(self):
        text = (Path(__file__).parent / "READY_FOR_RELEASE.md").read_text(encoding="utf-8")
        for field in (
            "State: READY_FOR_RELEASE",
            "Source ref:",
            "Target ref:",
            "Release candidate SHA:",
            "Qualified base SHA:",
            "Effective candidate:",
            "Qualification strategy: LOCAL | GITHUB_NATIVE",
            "CI profile fingerprint:",
            "Qualification evidence:",
            "Included work:",
            "Review Critical: 0",
            "Review Important: 0",
            "Next stage: Release integration",
        ):
            self.assertIn(field, text)

    def test_ready_for_release_is_not_publication_or_deployment_authority(self):
        text = (Path(__file__).parent / "READY_FOR_RELEASE.md").read_text(encoding="utf-8")
        self.assertIn("not publication authority", text)
        self.assertIn("does not create a tag", text)
        self.assertIn("deployment", text)
        self.assertIn("stale", text)


if __name__ == "__main__":
    unittest.main()
