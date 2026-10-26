"""External skill recommendation deduplication contract."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

from project_orchestrator_cli.external_recommendations import dedupe_external_recommendations


class ExternalRecommendationTests(unittest.TestCase):
    def test_controller_surfaces_same_provider_skill_only_once_per_run(self) -> None:
        state: dict = {}
        recommendation = {
            "provider_id": "addy-agent-skills",
            "skill_id": "source-driven-development",
            "level": "recommended",
            "reason": "Version-specific framework behavior",
        }

        first = dedupe_external_recommendations(
            state,
            [recommendation],
            work_item_id="TASK-1",
            role="coding-agent",
        )
        second = dedupe_external_recommendations(
            state,
            [recommendation],
            work_item_id="TASK-2",
            role="code-reviewer",
        )

        self.assertEqual(len(first), 1)
        self.assertEqual(second, [])
        self.assertEqual(
            state["external_skill_recommendations_reported"],
            ["addy-agent-skills:source-driven-development"],
        )
        self.assertEqual(len(state["external_skill_recommendations"]), 1)
        self.assertEqual(
            state["external_skill_recommendations"][0]["first_reported_by"],
            "coding-agent",
        )

    def test_optional_recommendations_remain_silent(self) -> None:
        state: dict = {}
        emitted = dedupe_external_recommendations(
            state,
            [{
                "provider_id": "addy-agent-skills",
                "skill_id": "documentation-and-adrs",
                "level": "optional",
                "reason": "Could help",
            }],
            work_item_id="TASK-1",
            role="coding-agent",
        )
        self.assertEqual(emitted, [])
        self.assertEqual(state["external_skill_recommendations_reported"], [])
        self.assertEqual(state["external_skill_recommendations"], [])

    def test_distinct_skills_are_independently_reported(self) -> None:
        state: dict = {}
        emitted = dedupe_external_recommendations(
            state,
            [
                {
                    "provider_id": "addy-agent-skills",
                    "skill_id": "security-and-hardening",
                    "level": "recommended",
                    "reason": "Trust boundary changed",
                },
                {
                    "provider_id": "addy-agent-skills",
                    "skill_id": "observability-and-instrumentation",
                    "level": "recommended",
                    "reason": "Production telemetry changed",
                },
            ],
            work_item_id="TASK-1",
            role="coding-agent",
        )
        self.assertEqual(len(emitted), 2)


if __name__ == "__main__":
    unittest.main()
