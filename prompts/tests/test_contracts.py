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

    def test_bootstrap_is_small(self):
        bootstrap = (PROMPTS / "BOOTSTRAP.md").read_text(encoding="utf-8")
        full = sum(len((PROMPTS / f"{name}.md").read_text(encoding="utf-8")) for name in ("chat-coder", "ci", "merge"))
        self.assertLess(len(bootstrap), full // 3)

if __name__ == "__main__":
    unittest.main()
