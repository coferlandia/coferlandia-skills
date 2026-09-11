import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts" / "hotfix.md"
CONTRACT = ROOT / "_protocol" / "delivery" / "HOTFIX.md"


class HotfixContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prompt = PROMPT.read_text(encoding="utf-8")
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_invocation_is_explicit_and_supports_issue_or_free_form_report(self):
        self.assertIn("hotfix #123", self.prompt)
        self.assertIn("hotfix: <free-form bug report>", self.prompt)
        self.assertIn("only from an explicit `hotfix` invocation", self.prompt)
        self.assertIn("does not by itself authorize the exceptional hotfix path", self.prompt)

    def test_prompt_creates_or_reuses_primary_issue_without_inventing_facts(self):
        self.assertIn("search current open/recent work", self.prompt)
        self.assertIn("reuse an existing matching Issue only when identity is clear", self.prompt)
        self.assertIn("otherwise create one primary bug Issue", self.prompt)
        self.assertIn("Do not fabricate reproduction steps, impact, root cause or certainty", self.prompt)

    def test_resolution_strategy_is_explicit(self):
        for token in ("PERMANENT", "TEMPORARY_MITIGATION", "HOTFIX_BLOCKED"):
            self.assertIn(token, self.prompt)
            self.assertIn(token, self.contract)
        self.assertIn("Urgency alone is not justification for an unsafe workaround", self.prompt)

    def test_temporary_mitigation_requires_permanent_follow_up(self):
        self.assertIn("not allowed to become `HOTFIX_READY` until a distinct permanent-fix Issue exists", self.prompt)
        self.assertIn("Permanent fix issue", self.contract)
        self.assertIn("Reason temporary", self.contract)
        self.assertIn("Temporary surfaces", self.contract)
        self.assertIn("Removal criteria", self.contract)
        self.assertIn("known or probable root cause", self.contract)
        self.assertIn("regression/prevention coverage", self.contract)

    def test_permanent_hotfix_does_not_create_artificial_follow_up(self):
        self.assertIn("Do not create this second Issue for a genuinely `PERMANENT` hotfix", self.prompt)
        self.assertIn("Permanent fix issue: NONE", self.contract)

    def test_controller_delegates_development_and_publication(self):
        self.assertIn("Do not reimplement TDD, implementation", self.prompt)
        self.assertIn("generic `chat-coder`", self.prompt)
        self.assertIn("coferlandia-release-publisher", self.prompt)
        self.assertIn("do not duplicate its SemVer/tag/GitHub Release logic", self.prompt)

    def test_hotfix_ready_is_bound_to_exact_candidate(self):
        self.assertIn("HOTFIX_READY", self.contract)
        self.assertIn("Candidate SHA", self.contract)
        self.assertIn("READY_FOR_CI evidence", self.contract)
        self.assertIn("Any later PR-head change", self.contract)

    def test_generic_prompt_does_not_hardcode_consumer_topology(self):
        for token in (
            "SecretarIA",
            "scripts/validate-all.sh",
            "fast-ci.yml",
            "Hotfix CI / Gate",
            "hotfix-authorized",
            "branch desde main",
            "main -> dev",
        ):
            self.assertNotIn(token, self.prompt)
            self.assertNotIn(token, self.contract)

    def test_temporary_completion_does_not_claim_structural_resolution(self):
        self.assertIn("production stabilization is complete **while permanent resolution remains open**", self.prompt)
        self.assertIn("Permanent resolution = PENDING", self.prompt)
        self.assertIn("production is mitigated, not that the structural cause is resolved", self.contract)


if __name__ == "__main__":
    unittest.main()
