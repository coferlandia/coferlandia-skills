import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
CLI = SKILL_ROOT / "scripts" / "coferlandia-ci-adapter-cli.py"
PKG = SKILL_ROOT / "scripts" / "coferlandia_ci_adapter_cli" / "profile.py"


def load_profile_module():
    spec = importlib.util.spec_from_file_location("profile_module", PKG)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdapterCLITests(unittest.TestCase):
    def sample(self):
        return {
            "schema_version": 1,
            "profile_version": "1.0.0",
            "repository": "example/repo",
            "documentation": ["AGENTS.md"],
            "local": {
                "working_directory": ".",
                "qualification_commands": [
                    {"id": "canonical", "command": "python -m unittest", "purpose": "canonical qualification"}
                ],
                "required_services": [],
                "environment": []
            },
            "github": {
                "submission": {"mode": "existing-pr-events", "workflow": ".github/workflows/ci.yml"},
                "gates": [
                    {"id": "ci", "kind": "workflow", "workflow": ".github/workflows/ci.yml", "allowed_conclusions": ["success"]}
                ],
                "merge_group": {"supported": False, "authoritative_when_present": False}
            },
            "identity": {"base_sensitive": True, "profile_sensitive": True},
            "exceptions": []
        }

    def test_validation_and_fingerprint_are_deterministic(self):
        module = load_profile_module()
        profile = self.sample()
        module.validate_profile(profile)
        fp1 = module.profile_fingerprint(profile)
        reordered = json.loads(json.dumps(profile, sort_keys=True))
        fp2 = module.profile_fingerprint(reordered)
        self.assertEqual(fp1, fp2)
        with_fingerprint = dict(profile, fingerprint=fp1)
        module.validate_profile(with_fingerprint, verify_fingerprint=True)

    def test_rejects_unsafe_or_ambiguous_profiles(self):
        module = load_profile_module()
        profile = self.sample()
        profile["token"] = "abc"
        with self.assertRaises(ValueError):
            module.validate_profile(profile)
        profile = self.sample()
        profile["github"]["gates"][0]["allowed_conclusions"] = []
        with self.assertRaises(ValueError):
            module.validate_profile(profile)
        profile = self.sample()
        profile["local"]["qualification_commands"] = []
        with self.assertRaises(ValueError):
            module.validate_profile(profile)

    def test_cli_validate_fingerprint_and_render(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "plan.json"
            source.write_text(json.dumps(self.sample()), encoding="utf-8")
            validate = subprocess.run([sys.executable, str(CLI), "profile", "validate", "--profile", str(source), "--json"], text=True, capture_output=True)
            self.assertEqual(validate.returncode, 0, validate.stderr or validate.stdout)
            fp = subprocess.run([sys.executable, str(CLI), "profile", "fingerprint", "--profile", str(source), "--json"], text=True, capture_output=True)
            self.assertEqual(fp.returncode, 0, fp.stderr or fp.stdout)
            fingerprint = json.loads(fp.stdout)["fingerprint"]
            dry = subprocess.run([sys.executable, str(CLI), "profile", "render", "--input", str(source), "--target-root", str(root), "--dry-run", "--json"], text=True, capture_output=True)
            self.assertEqual(dry.returncode, 0, dry.stderr or dry.stdout)
            target = root / ".coferlandia" / "ci" / "profile.json"
            self.assertFalse(target.exists())
            apply = subprocess.run([sys.executable, str(CLI), "profile", "render", "--input", str(source), "--target-root", str(root), "--json"], text=True, capture_output=True)
            self.assertEqual(apply.returncode, 0, apply.stderr or apply.stdout)
            self.assertTrue(target.exists())
            stored = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(stored["fingerprint"], fingerprint)

if __name__ == "__main__":
    unittest.main()
