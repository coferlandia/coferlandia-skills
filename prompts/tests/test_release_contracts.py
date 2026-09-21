import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "prompts"
VALIDATOR = ROOT / "_protocol" / "scripts" / "validate_prompt.py"


class ReleasePromptContractTests(unittest.TestCase):
    def test_registry_exposes_chat_release_without_implicit_composition(self):
        registry = json.loads((PROMPTS / "registry.json").read_text(encoding="utf-8"))
        release = next(item for item in registry["prompts"] if item["id"] == "chat-release")
        self.assertEqual(release["stage"], "release")
        self.assertIn("chat release", release["aliases"])
        external = {item["alias"]: item for item in registry["external_aliases"]}
        self.assertEqual(external["local release"]["kind"], "skill")
        self.assertEqual(external["local release"]["target"], "local-release")
        self.assertFalse(registry["composition"]["implicit_stages"])
        self.assertFalse(registry["composition"]["automatic_fallback"])

    def test_validator_accepts_release_stage_and_resolves_both_surfaces(self):
        validate = subprocess.run(
            [sys.executable, str(VALIDATOR), "validate", "--root", str(ROOT), "--json"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(validate.returncode, 0, validate.stderr or validate.stdout)

        chat = subprocess.run(
            [sys.executable, str(VALIDATOR), "resolve", "chat release", "--root", str(ROOT), "--json"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(chat.returncode, 0, chat.stderr or chat.stdout)
        self.assertEqual(json.loads(chat.stdout)["sequence"][0]["target"], "chat-release")

        local = subprocess.run(
            [sys.executable, str(VALIDATOR), "resolve", "local release", "--root", str(ROOT), "--json"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(local.returncode, 0, local.stderr or local.stdout)
        self.assertEqual(
            json.loads(local.stdout)["sequence"][0],
            {"alias": "local release", "kind": "skill", "target": "local-release"},
        )

    def test_chat_release_is_generic_github_native_and_reentrant(self):
        text = (PROMPTS / "chat-release.md").read_text(encoding="utf-8")
        for token in (
            "SecretarIA",
            "scripts/validate-all.sh",
            "fast-ci.yml",
            "Hotfix CI / Gate",
            "dev → main",
        ):
            self.assertNotIn(token, text)

        self.assertIn("GITHUB_NATIVE", text)
        self.assertIn("READY_FOR_RELEASE", text)
        self.assertIn("coferlandia-release-publisher", text)
        self.assertIn("must not deploy", text)
        self.assertIn("exact release candidate", text)
        self.assertIn("release manifest", text)
        self.assertIn("RELEASE_REPAIR_REQUIRED", text)
        self.assertIn("does not invoke `ci.md`", text)
        self.assertIn("does not fall back to `local-release`", text)

    def test_chat_release_initializes_or_reuses_release_work_surface(self):
        text = (PROMPTS / "chat-release.md").read_text(encoding="utf-8")
        self.assertIn("## Release candidate initialization", text)
        self.assertIn("search for an existing open release PR", text)
        self.assertIn("create the repository-approved release PR", text)
        self.assertIn("conflicting/ambiguous active release PR", text)
        self.assertIn("Build or currentize the release manifest", text)
        self.assertIn("source snapshot", text)
        self.assertIn("Materialized/frozen candidate", text)
        self.assertIn("Live-source candidate", text)
        self.assertIn("normal advancement of the source ref does **not** move", text)
        self.assertIn("source-ref advancement after initialization is ordinary concurrent development", text)
        self.assertIn("Candidate ref/SHA movement", text)
        self.assertIn("RELEASE_INITIALIZATION_BLOCKED", text)

    def test_chat_release_frozen_candidate_keeps_source_drift_non_authoritative(self):
        text = (PROMPTS / "chat-release.md").read_text(encoding="utf-8")
        self.assertIn("Source snapshot SHA:", text)
        self.assertIn("Candidate ref:", text)
        self.assertIn("do not require the mutable source ref to still point at the candidate SHA", text)
        self.assertIn("Source-ref advancement alone is not drift", text)
        self.assertIn("explicit new release candidate initialization", text)

    def test_chat_release_uses_repository_declared_github_native_publication_transport(self):
        text = (PROMPTS / "chat-release.md").read_text(encoding="utf-8")
        for token in (
            "publication.github",
            "issue-comment",
            "workflow-dispatch",
            "coferlandia-release-publication-request:v1",
            "target_sha",
            "merge_commit_sha",
            "version",
            "impact",
            "title",
            "notes",
            "causally triggered by that exact newly created comment/event",
            "annotated tag and GitHub Release",
            "RELEASE_PUBLICATION_BLOCKED",
        ):
            self.assertIn(token, text)
        self.assertIn("Do not fall back to LOCAL", text)
        self.assertIn("do not mutate publication identity directly from this prompt", text)
        self.assertIn("Publication evidence = <request comment + workflow/run identity>", text)
        self.assertNotIn("gh release create", text)
        self.assertNotIn("git tag -a", text)


if __name__ == "__main__":
    unittest.main()
