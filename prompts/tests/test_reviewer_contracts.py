import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "prompts"


class ChatReviewerContractTests(unittest.TestCase):
    def setUp(self):
        self.text = (PROMPTS / "chat-reviewer.md").read_text(encoding="utf-8")
        self.registry = json.loads((PROMPTS / "registry.json").read_text(encoding="utf-8"))
        self.contract = (ROOT / "_protocol" / "delivery" / "INDEPENDENT_REVIEW.md").read_text(encoding="utf-8")

    def test_reviewer_is_registered_as_explicit_review_stage(self):
        reviewer = next(item for item in self.registry["prompts"] if item["id"] == "chat-reviewer")
        self.assertEqual(reviewer["stage"], "review")
        self.assertEqual(reviewer["aliases"], ["chat reviewer", "chat-reviewer"])
        self.assertNotIn("chat reviewer", self.registry["composition"]["standalone_defaults"])
        self.assertNotIn("chat-reviewer", self.registry["composition"]["standalone_defaults"])

    def test_reviewer_is_read_only_and_does_not_create_validation_evidence(self):
        self.assertIn("Operate read-only on repository contents and Git state", self.text)
        self.assertIn("The only allowed side effect is publishing the review", self.text)
        self.assertIn("does not create new validation evidence", self.text)
        self.assertIn("Do not modify code, documentation, Git state, or implementation artifacts", self.text)

    def test_reviewer_binds_verdict_to_exact_delta_and_contract(self):
        self.assertIn("authoritative work contract", self.text)
        self.assertIn("exact head and base identities", self.text)
        for token in (
            "<!-- independent-review:v1 -->",
            "Head reviewed:",
            "Base reviewed:",
            "Critical:",
            "Important:",
            "Completeness: COMPLETE | INCOMPLETE",
            "Ready: YES | NO",
        ):
            self.assertIn(token, self.contract)

    def test_reviewer_requires_zero_blockers_and_complete_scope(self):
        self.assertIn("Critical = 0", self.text)
        self.assertIn("Important = 0", self.text)
        self.assertIn("complete for its declared scope", self.text)
        self.assertIn("no contradiction with the current authoritative contract", self.text)
        self.assertIn("Missing evidence required to establish completeness", self.text)

    def test_reviewer_stays_generic(self):
        for token in ("SecretarIA", "Flow Platform", "Sim-native", "cofer-vm-admin", "projects/2"):
            self.assertNotIn(token, self.text)


if __name__ == "__main__":
    unittest.main()
