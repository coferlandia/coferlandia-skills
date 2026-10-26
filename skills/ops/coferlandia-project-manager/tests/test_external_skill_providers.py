from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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


def make_plugin(
    provider_root: Path,
    *,
    plugin_name: str,
    repository: str,
    version: str | None,
    skills: list[str],
    nested: str = "instance",
) -> Path:
    plugin = provider_root / nested
    manifest = plugin / ".codex-plugin" / "plugin.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": plugin_name,
        "repository": repository,
        "skills": "./skills/",
    }
    if version is not None:
        payload["version"] = version
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    for name in skills:
        make_skill(plugin / "skills", name)
    return plugin


class ExternalSkillProviderTests(unittest.TestCase):
    def run_cli(
        self,
        skill_root: Path,
        *,
        provider_root: Path | None = None,
        runtime: str = "codex",
    ) -> dict:
        args = [
            sys.executable,
            str(CLI),
            "--config",
            str(CONFIG),
            "--runtime",
            runtime,
            "--skill-root",
            str(skill_root),
        ]
        if provider_root is not None:
            args.extend(["--provider-root", str(provider_root)])
        args.append("--json")
        result = subprocess.run(args, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    @staticmethod
    def provider(payload: dict, provider_id: str) -> dict:
        return next(
            provider
            for provider in payload["providers"]
            if provider["provider_id"] == provider_id
        )

    def test_registry_keeps_external_projects_independent(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        providers = {provider["id"]: provider for provider in registry["providers"]}
        self.assertEqual(
            providers["superpowers"]["repository_url"],
            "https://github.com/obra/superpowers",
        )
        self.assertEqual(
            providers["addy-agent-skills"]["repository_url"],
            "https://github.com/addyosmani/agent-skills",
        )
        self.assertEqual(providers["superpowers"]["license"], "MIT")
        self.assertEqual(providers["addy-agent-skills"]["license"], "MIT")
        self.assertTrue(providers["superpowers"]["allow_legacy_flat_detection"])
        self.assertFalse(providers["addy-agent-skills"]["allow_legacy_flat_detection"])

    def test_addy_conflicting_lifecycle_skills_are_never_requested(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        addy = next(
            provider
            for provider in registry["providers"]
            if provider["id"] == "addy-agent-skills"
        )
        blocked = set(addy["default_policy"]["never_request"])
        self.assertIn("using-agent-skills", blocked)
        self.assertIn("test-driven-development", blocked)
        self.assertIn("git-workflow-and-versioning", blocked)
        self.assertNotIn(
            "test-driven-development",
            addy["default_policy"]["recommended"],
        )

    def test_missing_recommended_provider_is_non_blocking_and_has_install_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skills"
            provider_root = Path(tmp) / "providers"
            make_skill(skill_root, "brainstorming")
            make_skill(skill_root, "writing-plans")
            payload = self.run_cli(skill_root, provider_root=provider_root)

        superpowers = self.provider(payload, "superpowers")
        addy = self.provider(payload, "addy-agent-skills")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(superpowers["status"], "ok")
        self.assertEqual(superpowers["presence"], "legacy-flat-unverified")
        self.assertEqual(addy["status"], "missing")
        action = addy["install_action"]
        self.assertTrue(action["requires_user_approval"])
        self.assertIn(
            "codex plugin marketplace add addyosmani/agent-skills",
            action["commands"],
        )
        self.assertEqual(action["scope"], "provider")
        self.assertTrue(action["warnings"])
        self.assertIn("using-agent-skills", action["warnings"][0])
        self.assertEqual(
            addy["verify_action"],
            {
                "kind": "rerun-provider-resolution",
                "provider_id": "addy-agent-skills",
            },
        )
        self.assertTrue(payload["read_only"])

    def test_missing_required_superpowers_blocks_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = self.run_cli(
                Path(tmp) / "skills",
                provider_root=Path(tmp) / "providers",
            )
        superpowers = self.provider(payload, "superpowers")
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(superpowers["presence"], "missing")
        self.assertEqual(
            superpowers["skills"]["required_missing"],
            ["brainstorming", "writing-plans"],
        )

    def test_verified_addy_plugin_reports_provenance_version_and_skill_availability(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            providers = root / "providers"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            plugin = make_plugin(
                providers,
                plugin_name="agent-skills",
                repository="https://github.com/addyosmani/agent-skills",
                version="0.6.13",
                skills=["source-driven-development", "security-and-hardening"],
                nested="cache/addy/agent-skills/0.6.13",
            )
            payload = self.run_cli(skills, provider_root=providers)

        addy = self.provider(payload, "addy-agent-skills")
        self.assertEqual(addy["presence"], "verified")
        self.assertTrue(addy["present"])
        self.assertEqual(addy["installed"]["version"], "0.6.13")
        self.assertEqual(addy["installed"]["compatibility"], "same-as-tested")
        self.assertIn("source-driven-development", addy["skills"]["recommended_available"])
        self.assertIn("security-and-hardening", addy["skills"]["recommended_available"])
        self.assertEqual(Path(addy["instances"][0]["plugin_root"]), plugin)

    def test_unverified_recommended_name_does_not_identify_addy_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            make_skill(skills, "source-driven-development")
            payload = self.run_cli(skills, provider_root=root / "providers")

        addy = self.provider(payload, "addy-agent-skills")
        self.assertFalse(addy["present"])
        self.assertEqual(addy["presence"], "missing")
        self.assertEqual(addy["status"], "missing")
        self.assertNotIn(
            "source-driven-development",
            addy["skills"]["recommended_available"],
        )
        self.assertIn(
            "source-driven-development",
            addy["skills"]["unverified_name_matches"],
        )

    def test_wrong_repository_with_same_plugin_name_is_not_attributed_to_addy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            providers = root / "providers"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            make_plugin(
                providers,
                plugin_name="agent-skills",
                repository="https://example.com/not-addy/agent-skills",
                version="9.9.9",
                skills=["source-driven-development"],
            )
            payload = self.run_cli(skills, provider_root=providers)

        addy = self.provider(payload, "addy-agent-skills")
        self.assertFalse(addy["present"])
        self.assertEqual(addy["instances"], [])

    def test_same_named_conflicting_skill_does_not_identify_addy_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            make_skill(skills, "test-driven-development")
            payload = self.run_cli(skills, provider_root=root / "providers")
        addy = self.provider(payload, "addy-agent-skills")
        self.assertFalse(addy["present"])
        self.assertEqual(addy["status"], "missing")
        self.assertIn(
            "test-driven-development",
            addy["skills"]["ambiguous_conflicting_names_present"],
        )

    def test_installed_version_reports_older_newer_and_unknown_compatibility(self) -> None:
        cases = [
            ("0.6.12", "older-than-tested"),
            ("0.6.14", "newer-than-tested"),
            (None, "unknown"),
        ]
        for version, expected in cases:
            with self.subTest(version=version), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                providers = root / "providers"
                make_plugin(
                    providers,
                    plugin_name="agent-skills",
                    repository="https://github.com/addyosmani/agent-skills.git",
                    version=version,
                    skills=["source-driven-development"],
                )
                payload = self.run_cli(root / "skills", provider_root=providers)
                addy = self.provider(payload, "addy-agent-skills")
                self.assertEqual(addy["installed"]["version"], version)
                self.assertEqual(addy["installed"]["compatibility"], expected)

    def test_runtime_specific_recipe_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            payload = self.run_cli(
                skills,
                provider_root=root / "providers",
                runtime="claude",
            )
        addy = self.provider(payload, "addy-agent-skills")
        self.assertEqual(addy["install_action"]["execution"], "agent-ui")
        self.assertEqual(
            addy["install_action"]["commands"][0],
            "/plugin marketplace add addyosmani/agent-skills",
        )

    def test_fresh_rerun_detects_provider_after_install_materializes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            providers = root / "providers"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            before = self.run_cli(skills, provider_root=providers)
            self.assertFalse(self.provider(before, "addy-agent-skills")["present"])

            make_plugin(
                providers,
                plugin_name="agent-skills",
                repository="https://github.com/addyosmani/agent-skills",
                version="0.6.13",
                skills=["source-driven-development"],
            )
            after = self.run_cli(skills, provider_root=providers)
            self.assertTrue(self.provider(after, "addy-agent-skills")["present"])
            self.assertIn(
                "source-driven-development",
                self.provider(after, "addy-agent-skills")["skills"]["recommended_available"],
            )

    def test_cli_never_executes_install_actions_or_mutates_provider(self) -> None:
        text = CLI.read_text(encoding="utf-8")
        self.assertNotIn("os.system(", text)
        self.assertNotIn("shell=True", text)
        self.assertNotIn("subprocess.run(", text)
        self.assertNotIn("write_text(", text)
        self.assertNotIn("mkdir(", text)

    def test_legacy_wrappers_and_doctor_use_generic_resolver(self) -> None:
        bash = "bash"
        if os.name == "nt":
            git_executable = shutil.which("git")
            if git_executable:
                git_bash = Path(git_executable).with_name("bash.exe")
                if git_bash.is_file():
                    bash = str(git_bash)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            providers = root / "providers"
            make_skill(skills, "brainstorming")
            make_skill(skills, "writing-plans")
            env = os.environ.copy()
            env["COFERLANDIA_EXTERNAL_SKILL_ROOTS"] = str(skills)
            env["COFERLANDIA_EXTERNAL_PROVIDER_ROOTS"] = str(providers)
            env["COFERLANDIA_AGENT_RUNTIME"] = "codex"

            detect = subprocess.run(
                [
                    bash,
                    "skills/ops/coferlandia-project-manager/scripts/pm-detect-superpowers.sh",
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
            self.assertEqual(detect.returncode, 0, detect.stdout + detect.stderr)
            detect_payload = json.loads(detect.stdout)
            self.assertEqual(detect_payload["status"], "ok")
            self.assertEqual(detect_payload["presence"], "legacy-flat-unverified")

            legacy = subprocess.run(
                [
                    bash,
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
            self.assertEqual(json.loads(legacy.stdout)["status"], "ok")

            doctor = subprocess.run(
                [
                    bash,
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
            providers_by_id = {
                provider["provider_id"]: provider
                for provider in doctor_payload["external_skills"]["providers"]
            }
            self.assertEqual(providers_by_id["superpowers"]["status"], "ok")
            self.assertEqual(providers_by_id["addy-agent-skills"]["status"], "missing")
            self.assertTrue(
                providers_by_id["addy-agent-skills"]["install_action"]["requires_user_approval"]
            )

    def test_superpowers_detect_wrapper_is_not_fooled_by_unrelated_skill_root(self) -> None:
        bash = "bash"
        if os.name == "nt":
            git_executable = shutil.which("git")
            if git_executable:
                git_bash = Path(git_executable).with_name("bash.exe")
                if git_bash.is_file():
                    bash = str(git_bash)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skills = root / "skills"
            make_skill(skills, "unrelated-skill")
            env = os.environ.copy()
            env["COFERLANDIA_EXTERNAL_SKILL_ROOTS"] = str(skills)
            env["COFERLANDIA_EXTERNAL_PROVIDER_ROOTS"] = str(root / "providers")
            result = subprocess.run(
                [
                    bash,
                    "skills/ops/coferlandia-project-manager/scripts/pm-detect-superpowers.sh",
                    "--json",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "missing")

    def test_coferlandia_roles_keep_external_specialists_subordinate(self) -> None:
        software = (
            REPO_ROOT / "skills" / "engineering" / "software-development" / "SKILL.md"
        ).read_text(encoding="utf-8")
        architect = (
            REPO_ROOT / "skills" / "engineering" / "the-architect" / "SKILL.md"
        ).read_text(encoding="utf-8")
        project_manager = (
            REPO_ROOT / "skills" / "ops" / "coferlandia-project-manager" / "SKILL.md"
        ).read_text(encoding="utf-8")
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
