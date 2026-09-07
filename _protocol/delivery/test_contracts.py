import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "skills" / "meta" / "coferlandia-ci-adapter" / "scripts" / "coferlandia_ci_adapter_cli" / "profile.py"
FIXTURE = ROOT / "skills" / "meta" / "coferlandia-ci-adapter" / "tests" / "fixtures" / "secretaria-profile.json"


def module():
    spec = importlib.util.spec_from_file_location("ci_profile", PROFILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class DeliveryContractTests(unittest.TestCase):
    def test_shared_handoffs_have_required_identity(self):
        ready_ci = (Path(__file__).parent / "READY_FOR_CI.md").read_text(encoding="utf-8")
        for field in ("Issue:", "PR:", "Branch:", "Candidate SHA:", "Base SHA studied:", "Review Critical: 0", "Review Important: 0"):
            self.assertIn(field, ready_ci)
        ready_merge = (Path(__file__).parent / "READY_FOR_MERGE.md").read_text(encoding="utf-8")
        for field in ("Candidate SHA:", "Qualified base SHA:", "Effective candidate:", "Qualification strategy: LOCAL | GITHUB_NATIVE", "CI profile fingerprint:"):
            self.assertIn(field, ready_merge)

    def test_requalification_matrix_is_fail_closed(self):
        text = (Path(__file__).parent / "REQUALIFICATION.md").read_text(encoding="utf-8")
        self.assertIn("PR head changes", text)
        self.assertIn("CI profile fingerprint changes", text)
        self.assertIn("Authoritative base changes", text)
        self.assertIn("Old/cancelled/superseded remote run", text)
        self.assertIn("merge.md` never performs requalification", text)

    def test_secretaria_fixture_is_representable_without_controller_hardcoding(self):
        mod = module()
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        mod.validate_profile(data)
        fp = mod.profile_fingerprint(data)
        self.assertEqual(len(fp), 64)
        generic_controller_text = "\n".join(
            (ROOT / "prompts" / f"{name}.md").read_text(encoding="utf-8")
            for name in ("chat-coder", "ci", "merge")
        ) + (ROOT / "skills" / "engineering" / "local-ci" / "SKILL.md").read_text(encoding="utf-8")
        for project_specific in ("scripts/validate-all.sh", ".github/workflows/fast-ci.yml", "docs/development/hotfix-lane.md"):
            self.assertNotIn(project_specific, generic_controller_text)
            self.assertIn(project_specific, FIXTURE.read_text(encoding="utf-8"))

    def test_material_profile_changes_change_fingerprint(self):
        mod = module()
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        base = mod.profile_fingerprint(data)
        changed = json.loads(json.dumps(data))
        changed["identity"]["base_sensitive"] = False
        self.assertNotEqual(base, mod.profile_fingerprint(changed))
        changed = json.loads(json.dumps(data))
        changed["github"]["gates"][0]["allowed_conclusions"].append("neutral")
        self.assertNotEqual(base, mod.profile_fingerprint(changed))

if __name__ == "__main__":
    unittest.main()
