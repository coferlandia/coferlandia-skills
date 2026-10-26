from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
CLI = SKILL_ROOT / "scripts" / "pm-external-skills.py"
REGISTRY = SKILL_ROOT / "references" / "external-skill-providers.json"
CONFIG = SKILL_ROOT / "templates" / "config.template.json"
REPO_ROOT = SKILL_ROOT.parents[2]

def make_skill(root: Path, name: str) -> None:
    skill = root / name
    skill.mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n", encoding="utf-8")

class ExternalSkillProviderTests(unittest.TestCase):
    def run_cli(self, root: Path, runtime: str = "codex") -> dict:
        result = subprocess.run(
            [
                "python",
                str(CLI),
                "--config",
                str(CONFIG),
                "--runtime",
                runtime,
                "--skill-root",
                str(root),
                "--json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_registry_keeps_external_projects_independent(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        providers = {provider["id"]: provider for provider in registry["providers"]}
        self.assertEqual(providers["superpowers"]["repository_url"], "https://github.com/obra/superpowers")
        self.assertEqual(
            providers["addy-agent-skills"]["repository_url"],
            "https://github.com/addyosmani/agent-skills",
        )
        self.assertEqual(providers["superpowers"]["license"], "MIT")
        self.assertEqual(providers["addy-agent-skills"]["license"], "MIT")

    def test_addy_conflicting_lifecycle_skills_are_never_requested(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        addy = next(provider for provider in registry["providers"] if provider["id"] == "addy-agent-skills")
        blocked = set(addy["default_policy"]["never_request"])
        self.assertIn("using-agent-skills", blocked)
        self.assertIn("test-driven-development", blocked)
        self.assertIn("git-workflow-and-versioning", blocked)
        self.assertNotIn("test-driven-development", addy["default_policy"]["recommended"])

    def test_missing_recommended_provider_is_non_blocking_and_has_install_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "brainstorming")
            make_skill(root, "writing-plans")
            payload = self.run_cli(root)
        providers = {provider["provider_id"]: provider for provider in payload["providers"]}
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(providers["superpowers"]["status"], "ok")
        self.assertEqual(providers["addy-agent-skills"]["status"], "missing")
        action = providers["addy-agent-skills"]["install_action"]
        self.assertTrue(action["requires_user_approval"])
        self.assertIn("codex plugin marketplace add addyosmani/agent-skills", action["commands"])
        self.assertEqual(action["scope"], "provider")
        self.assertTrue(action["warnings"])
        self.assertIn("using-agent-skills", action["warnings"][0])
        self.assertIn("test-driven-development", action["warnings"][0])
        self.assertTrue(payload["read_only"])

    def test_missing_required_superpowers_blocks_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = self.run_cli(Path(tmp))
        providers = {provider["provider_id"]: provider for provider in payload["providers"]}
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(
            providers["superpowers"]["skills"]["required_missing"],
            ["brainstorming", "writing-plans"],
        )

    def test_partial_addy_install_reports_only_real_availability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "brainstorming")
            make_skill(root, "writing-plans")
            make_skill(root, "source-driven-development")
            payload = self.run_cli(root)
        addy = next(provider for provider in payload["providers"] if provider["provider_id"] == "addy-agent-skills")
        self.assertEqual(addy["status"], "partial")
        self.assertIn("source-driven-development", addy["skills"]["recommended_available"])
        self.assertIn("security-and-hardening", addy["skills"]["recommended_missing"])

    def test_same_named_conflicting_skill_does_not_identify_addy_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "brainstorming")
            make_skill(root, "writing-plans")
            make_skill(root, "test-driven-development")
            payload = self.run_cli(root)
        addy = next(provider for provider in payload["providers"] if provider["provider_id"] == "addy-agent-skills")
        self.assertFalse(addy["present"])
        self.assertEqual(addy["status"], "missing")
        self.assertIn(
            "test-driven-development",
            addy["skills"]["ambiguous_conflicting_names_present"],
        )

    def test_runtime_specific_recipe_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "brainstorming")
            make_skill(root, "writing-plans")
            payload = self.run_cli(root, runtime="claude")
        addy = next(provider for provider in payload["providers"] if provider["provider_id"] == "addy-agent-skills")
        self.assertEqual(addy["install_action"]["execution"], "agent-ui")
        self.assertEqual(
            addy["install_action"]["commands"][0],
            "/plugin marketplace add addyosmani/agent-skills",
        )

    def test_cli_never_executes_install_actions(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        self.assertNotIn("os.system(", text)
        self.assertNotIn("shell=True", text)
        self.assertNotIn("subprocess.run(", text)

    def test_legacy_wrappers_and_doctor_use_generic_resolver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "brainstorming")
            make_skill(root, "writing-plans")
            env = os.environ.copy()
            env["COFERLANDIA_EXTERNAL_SKILL_ROOTS"] = str(root)
            env["COFERLANDIA_AGENT_RUNTIME"] = "codex"

            legacy = subprocess.run(
                [
                    "bash",
                    "skills/ops/coferlandia-project-manager/scripts/pm-check-superpowers-skills.sh",
                    "--config",
                    "skills/ops/coferlandia-project-manager/templates/config.template.json",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(legacy.returncode, 0, legacy.stdout + legacy.stderr)
            legacy_payload = json.loads(legacy.stdout)
            self.assertEqual(legacy_payload["status"], "ok")
            self.assertEqual(
                legacy_payload["repository_url"],
                "https://github.com/obra/superpowers",
            )

            doctor = subprocess.run(
                [
                    "bash",
                    "skills/ops/coferlandia-project-manager/scripts/pm-doctor.sh",
                    "--config",
                    "skills/ops/coferlandia-project-manager/templates/config.template.json",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
            doctor_payload = json.loads(doctor.stdout)
            self.assertIn("external_skills", doctor_payload)
            providers = {
                provider["provider_id"]: provider
                for provider in doctor_payload["external_skills"]["providers"]
            }
            self.assertEqual(providers["superpowers"]["status"], "ok")
            self.assertEqual(providers["addy-agent-skills"]["status"], "missing")
            self.assertTrue(
                providers["addy-agent-skills"]["install_action"]["requires_user_approval"]
            )

    def test_coferlandia_roles_keep_external_specialists_subordinate(self) -> None:
        software = (REPO_ROOT / "skills" / "engineering" / "software-development" / "SKILL.md").read_text(encoding="utf-8")
        architect = (REPO_ROOT / "skills" / "engineering" / "the-architect" / "SKILL.md").read_text(encoding="utf-8")
        project_manager = (REPO_ROOT / "skills" / "ops" / "coferlandia-project-manager" / "SKILL.md").read_text(encoding="utf-8")
        specialist_reference = (
            REPO_ROOT
            / "skills"
            / "engineering"
            / "software-development"
            / "references"
            / "external-specialists.md"
        ).read_text(encoding="utf-8")
        normalized_software = " ".join(software.split())
        self.assertIn("External specialist skills", software)
        self.assertIn("references/external-specialists.md", software)
        self.assertIn("never increases scope", normalized_software)
        self.assertIn("source-driven-development", specialist_reference)
        self.assertIn("security-and-hardening", specialist_reference)
        self.assertIn("test-driven-development", specialist_reference)
        self.assertIn("External specialist skills", architect)
        self.assertIn("doubt-driven-development", architect)
        self.assertIn("External skill providers", project_manager)
        self.assertIn("read-only", project_manager.lower())

if __name__ == "__main__":
    unittest.main()
