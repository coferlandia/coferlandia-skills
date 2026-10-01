import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT = ROOT / "prompts" / "chat-coder.md"
REGISTRY = ROOT / "prompts" / "registry.json"
READY_FOR_CI = ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md"


class ChatCoderTestImpactContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = PROMPT.read_text(encoding="utf-8")

    def test_test_impact_is_frozen_during_study_before_implementation(self):
        self.assertIn("## Test Impact", self.text)
        self.assertIn("Affected invariants", self.text)
        self.assertIn("Existing canonical coverage", self.text)
        self.assertIn("Coverage changes", self.text)
        self.assertIn("Selected test level per invariant", self.text)
        self.assertIn("Heavy-test justification", self.text)
        self.assertIn("Expected validation surface", self.text)
        self.assertIn("Repository-owned performance budget/tooling", self.text)
        self.assertIn("Expected performance impact", self.text)
        self.assertLess(self.text.index("## Test Impact"), self.text.index("## Implementation"))
        self.assertIn("before production edits", self.text)

    def test_coverage_is_owned_by_invariant_and_canonical_authority_not_test_count(self):
        self.assertIn("canonical authority", self.text)
        self.assertIn("existing regression", self.text)
        self.assertIn("parameterizable variants", self.text)
        self.assertIn("duplicate semantic coverage", self.text)
        self.assertIn("Test-count growth is not a goal", self.text)
        self.assertIn("same invariant", self.text)

    def test_cheapest_valid_test_level_preserves_complete_invariant(self):
        self.assertIn("cheapest", self.text.lower())
        self.assertIn("preserves the complete invariant", self.text)
        self.assertIn("Tier 0", self.text)
        self.assertIn("Tier 4", self.text)
        self.assertIn("expensive/heavy", self.text)
        self.assertIn("why a cheaper level would lose semantics", self.text)

    def test_cost_never_authorizes_downgrading_real_semantics(self):
        for semantic in (
            "database",
            "authentication",
            "tenancy",
            "locks",
            "transactions",
            "migrations",
            "network",
            "side effects",
        ):
            with self.subTest(semantic=semantic):
                self.assertIn(semantic, self.text.lower())
        self.assertIn("must not replace", self.text.lower())
        self.assertIn("complete invariant", self.text)

    def test_consolidated_coverage_maps_to_retained_authority(self):
        self.assertIn("retained canonical authority", self.text)
        self.assertIn("old coverage", self.text)
        self.assertIn("protected invariant", self.text)
        self.assertIn("reconstruct", self.text.lower())

    def test_repository_owned_performance_policy_is_used_without_invented_thresholds(self):
        self.assertIn("repository-owned performance", self.text.lower())
        self.assertIn("timings", self.text.lower())
        self.assertIn("budgets", self.text.lower())
        self.assertIn("regression checks", self.text.lower())
        self.assertIn("must not invent", self.text.lower())
        self.assertIn("repository budget not defined", self.text.lower())
        self.assertIn("does not block", self.text.lower())

    def test_performance_regression_is_development_finding_not_coverage_weakening(self):
        self.assertIn("Development finding", self.text)
        self.assertIn("investigate", self.text.lower())
        self.assertIn("waiver", self.text.lower())
        self.assertIn("do not reduce coverage", self.text.lower())
        self.assertIn("READY_FOR_CI", self.text)

    def test_terminal_development_evidence_summarizes_test_cost_impact(self):
        self.assertIn("Test impact =", self.text)
        self.assertIn("Heavy test impact = YES | NO", self.text)
        self.assertIn("Performance evidence =", self.text)
        self.assertIn("NOT DEFINED", self.text)

    def test_scenarios_keep_the_cheapest_level_semantically_honest(self):
        self.assertIn("pure/unit", self.text)
        self.assertIn("service/component", self.text)
        self.assertIn("persistence/integration", self.text)
        self.assertIn("real concurrency/external-system semantics", self.text)
        self.assertIn("migration/history/E2E/full-stack", self.text)
        self.assertIn("distinct boundary", self.text)

    def test_controller_remains_generic_and_delivery_boundaries_stay_unchanged(self):
        for forbidden in (
            "SecretarIA",
            "pytest",
            "Alembic",
            "PostgreSQL",
            "Fast CI",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, self.text)
        self.assertIn("must not perform Qualification", self.text)
        self.assertIn("must not merge", self.text)
        self.assertIn("Qualification remains owned by", self.text)
        self.assertIn('"schema_version": 1', REGISTRY.read_text(encoding="utf-8"))
        self.assertIn("Schema: 1", READY_FOR_CI.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
