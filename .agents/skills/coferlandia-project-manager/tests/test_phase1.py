#!/usr/bin/env python3
import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SKILL_ROOT = ROOT / ".agents" / "skills" / "coferlandia-project-manager"
SCRIPTS_ROOT = Path(".agents/skills/coferlandia-project-manager/scripts")


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


@contextmanager
def make_repo_temp_config(name: str):
    (ROOT / ".test-tmp").mkdir(exist_ok=True)
    tempdir = tempfile.TemporaryDirectory(dir=ROOT / ".test-tmp")
    try:
        path = Path(tempdir.name) / name
        relative_path = path.relative_to(ROOT).as_posix()
        yield relative_path
    finally:
        tempdir.cleanup()


class Phase1Tests(unittest.TestCase):
    def test_generate_config_apply_copies_template(self) -> None:
        with make_repo_temp_config("config.json") as target:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-generate-config.sh").as_posix()),
                "--config",
                target,
                "--apply",
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            target_path = ROOT / target
            self.assertTrue(target_path.exists(), result.stdout)

            generated = json.loads(target_path.read_text(encoding="utf-8"))
            template = json.loads(
                (SKILL_ROOT / "templates" / "config.template.json").read_text(encoding="utf-8")
            )
            self.assertEqual(generated, template)

            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "applied")

    def test_validate_config_rejects_missing_required_sections(self) -> None:
        with make_repo_temp_config("invalid.json") as invalid_config:
            invalid_config_path = ROOT / invalid_config
            invalid_config_path.write_text('{"version": 1}', encoding="utf-8")

            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-validate-config.sh").as_posix()),
                "--config",
                invalid_config,
                "--json",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertIn("missing_keys", payload)
            self.assertIn("obsidian", payload["missing_keys"])

    def test_sample_config_matches_required_top_level_shape(self) -> None:
        template = json.loads(
            (SKILL_ROOT / "templates" / "config.template.json").read_text(encoding="utf-8")
        )
        sample = json.loads(
            (SKILL_ROOT / "examples" / "config.sample.json").read_text(encoding="utf-8")
        )

        self.assertEqual(set(sample.keys()), set(template.keys()))

    def test_default_config_path_points_to_template(self) -> None:
        command = (
            "source .agents/skills/coferlandia-project-manager/scripts/lib/config.sh; "
            "pm_config_default_path"
        )
        result = run_script("bash", "-lc", command)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            ".agents/skills/coferlandia-project-manager/templates/config.template.json",
        )

    def test_doctor_json_reports_real_sections(self) -> None:
        config_path = ".agents/skills/coferlandia-project-manager/examples/config.sample.json"
        result = run_script(
            "bash",
            str((SCRIPTS_ROOT / "pm-doctor.sh").as_posix()),
            "--config",
            config_path,
            "--json",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("config", payload)
        self.assertIn("environment", payload)
        self.assertIn("superpowers", payload)
        self.assertIn("git_capabilities", payload)
        self.assertIn("next_approved_action", payload)
        self.assertEqual(payload["config"]["status"], "ok")

    def test_onboard_json_wraps_readiness_report(self) -> None:
        config_path = ".agents/skills/coferlandia-project-manager/examples/config.sample.json"
        result = run_script(
            "bash",
            str((SCRIPTS_ROOT / "pm-onboard.sh").as_posix()),
            "--config",
            config_path,
            "--json",
            "--dry-run",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["mode"], "dry-run")
        self.assertIn("readiness", payload)


if __name__ == "__main__":
    if shutil.which("bash") is None:
        raise SystemExit("bash is required for phase 1 tests")
    unittest.main()
