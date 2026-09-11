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
        self.assertIn("bind it to the exact source candidate and target/base identity", text)
        self.assertIn("source changes while a release PR/manifest already exists", text)
        self.assertIn("previous qualification evidence stale", text)
        self.assertIn("RELEASE_INITIALIZATION_BLOCKED", text)


if __name__ == "__main__":
    unittest.main()
