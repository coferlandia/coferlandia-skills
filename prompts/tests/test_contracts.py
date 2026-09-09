import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "prompts"
VALIDATOR = ROOT / "_protocol" / "scripts" / "validate_prompt.py"

class PromptContractTests(unittest.TestCase):
    def test_registry_contract(self):
        registry = json.loads((PROMPTS / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["schema_version"], 1)
        ids = [item["id"] for item in registry["prompts"]]
        self.assertEqual(ids, ["chat-coder", "ci", "merge"])
        aliases = {alias: item["id"] for item in registry["prompts"] for alias in item["aliases"]}
        self.assertEqual(aliases["chat coder"], "chat-coder")
        self.assertEqual(aliases["gh ci"], "ci")
        self.assertEqual(aliases["merge"], "merge")
        external = {item["alias"]: item for item in registry["external_aliases"]}
        self.assertEqual(external["local ci"]["kind"], "skill")
        self.assertEqual(external["local ci"]["target"], "local-ci")
        self.assertEqual(registry["composition"]["order"], "left-to-right")
        self.assertFalse(registry["composition"]["implicit_stages"])
        self.assertFalse(registry["composition"]["automatic_fallback"])

    def test_validator_and_alias_resolution(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "validate", "--root", str(ROOT), "--json"],
            text=True, capture_output=True
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        resolved = subprocess.run(
            [sys.executable, str(VALIDATOR), "resolve", "chat coder + gh ci + merge", "--root", str(ROOT), "--json"],
            text=True, capture_output=True
        )
        self.assertEqual(resolved.returncode, 0, resolved.stderr or resolved.stdout)
        payload = json.loads(resolved.stdout)
        self.assertEqual([x["target"] for x in payload["sequence"]], ["chat-coder", "ci", "merge"])
        local = subprocess.run(
            [sys.executable, str(VALIDATOR), "resolve", "chat coder + local ci + merge", "--root", str(ROOT), "--json"],
            text=True, capture_output=True
        )
        self.assertEqual(local.returncode, 0, local.stderr or local.stdout)
        payload = json.loads(local.stdout)
        self.assertEqual(payload["sequence"][1], {"alias": "local ci", "kind": "skill", "target": "local-ci"})

    def test_prompts_are_generic_and_separated(self):
        banned = [
            "SecretarIA", "secretaria-ci-delivery", "scripts/validate-all.sh", "fast-ci.yml",
            "coferlandia-ci, docker", "projects/1", "projects/2"
        ]
        texts = {}
        for name in ("chat-coder", "ci", "merge"):
            text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
            texts[name] = text
            for token in banned:
                self.assertNotIn(token, text, f"{name}.md hardcodes {token}")
        self.assertIn("READY_FOR_CI", texts["chat-coder"])
        self.assertIn("must not perform Qualification", texts["chat-coder"])
        self.assertIn("GITHUB_NATIVE", texts["ci"])
        self.assertIn("must not merge", texts["ci"])
        self.assertIn("REQUALIFICATION_REQUIRED", texts["merge"])
        self.assertIn("must not execute CI", texts["merge"])

    def test_chat_coder_claims_unassigned_issue_for_authenticated_user(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        self.assertIn("first state-changing action", text)
        self.assertIn("MUST assign it to the authenticated GitHub user", text)
        self.assertIn("verify that assignment succeeded", text)
        self.assertIn("preserve the existing ownership and stop", text)
        self.assertIn("Assignee = <authenticated GitHub user>", text)

    def test_chat_coder_ready_for_ci_requires_complete_cheap_validation(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        self.assertIn("every applicable cheap deterministic development check", text)
        self.assertIn("canonical complete frontend unit-test suite", text)
        self.assertIn("failing, skipped, unknown, stale", text)
        self.assertIn("effective or synthetic merge candidate", ready)
        self.assertIn("focused iteration tests are not used as a substitute", ready)
        self.assertIn("no applicable required development check is failing, skipped, unknown", ready)
        self.assertIn("Never weaken, delete, bypass, or broaden an assertion merely to make CI green", text)

    def test_chat_coder_ready_for_ci_requires_versioned_derived_artifacts(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        self.assertIn("repository-owned versioned derived artifact", text)
        self.assertIn("repository-owned generation or synchronization mechanism", text)
        self.assertIn("no unexpected diff", text)
        self.assertIn("missing, stale, manually approximated", text)
        self.assertIn("repository-owned versioned derived artifact", ready)
        self.assertIn("freshness/idempotence/diff check", ready)
        self.assertIn("without unexpected diff", ready)

    def test_environment_change_contract_is_durable_and_qualified(self):
        chat = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ci = (PROMPTS / "ci.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        self.assertIn("Environment change: YES | NO", chat)
        self.assertIn("Environment action = <NONE or concise deployment/operator action>", chat)
        self.assertIn("Environment variables = <NONE or concise affected-variable list", chat)
        self.assertIn("Environment change: YES | NO", ready)
        self.assertIn("Environment evidence:", ready)
        self.assertIn("secret values are never included", ready)
        self.assertIn("fail closed", ci.lower())
        self.assertIn("contradicted by the candidate", ci)
        self.assertIn("repository-owned deterministic environment/configuration contract checker", ci)

    def test_bootstrap_is_small(self):
        bootstrap = (PROMPTS / "BOOTSTRAP.md").read_text(encoding="utf-8")
        full = sum(len((PROMPTS / f"{name}.md").read_text(encoding="utf-8")) for name in ("chat-coder", "ci", "merge"))
        self.assertLess(len(bootstrap), full // 3)

if __name__ == "__main__":
    unittest.main()
