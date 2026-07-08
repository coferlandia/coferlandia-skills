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


@contextmanager
def make_phase2_portfolio():
    (ROOT / ".test-tmp").mkdir(exist_ok=True)
    tempdir = tempfile.TemporaryDirectory(dir=ROOT / ".test-tmp")
    try:
        base = Path(tempdir.name)
        repos_root = base / "repos"
        repos_root.mkdir()

        clean_repo = repos_root / "repo-one"
        dirty_repo = repos_root / "repo-two"
        clean_repo.mkdir()
        dirty_repo.mkdir()

        for repo_path in (clean_repo, dirty_repo):
            repo_relative = repo_path.relative_to(ROOT).as_posix()
            init = subprocess.run(
                ["bash", "-lc", f"git init '{repo_relative}' >/dev/null"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if init.returncode != 0:
                raise RuntimeError(init.stderr)

            checkout = subprocess.run(
                ["bash", "-lc", f"git -C '{repo_relative}' checkout -b main >/dev/null"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            if checkout.returncode != 0:
                raise RuntimeError(checkout.stderr)

        (clean_repo / "tracked.txt").write_text("hello\n", encoding="utf-8")
        clean_relative = clean_repo.relative_to(ROOT).as_posix()
        add = subprocess.run(
            ["bash", "-lc", f"git -C '{clean_relative}' add tracked.txt"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if add.returncode != 0:
            raise RuntimeError(add.stderr)

        commit = subprocess.run(
            [
                "bash",
                "-lc",
                " ".join(
                    [
                        f"git -C '{clean_relative}'",
                        "-c user.name=Test",
                        "-c user.email=test@example.com",
                        "commit -m init >/dev/null",
                    ]
                ),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if commit.returncode != 0:
            raise RuntimeError(commit.stderr)

        (dirty_repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")

        config = json.loads(
            (SKILL_ROOT / "examples" / "config.sample.json").read_text(encoding="utf-8")
        )
        config["repos_root"] = repos_root.resolve().as_posix()

        config_path = base / "config.json"
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        relative_config = config_path.relative_to(ROOT).as_posix()
        yield {
            "config_path": relative_config,
            "repos_root": repos_root,
            "clean_repo": clean_repo,
            "dirty_repo": dirty_repo,
        }
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

    def test_config_helpers_read_repos_root_and_default_branch(self) -> None:
        config_path = ".agents/skills/coferlandia-project-manager/examples/config.sample.json"
        command = (
            "source .agents/skills/coferlandia-project-manager/scripts/lib/config.sh; "
            f"pm_config_repos_root '{config_path}' && "
            f"pm_config_default_branch '{config_path}'"
        )
        result = run_script("bash", "-lc", command)

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        self.assertGreaterEqual(len(lines), 2)
        self.assertEqual(lines[1], "main")

    def test_config_helper_normalizes_windows_style_repos_root_for_bash(self) -> None:
        with make_phase2_portfolio() as portfolio:
            command = (
                "source .agents/skills/coferlandia-project-manager/scripts/lib/config.sh; "
                f"pm_config_repos_root '{portfolio['config_path']}'"
            )
            result = run_script("bash", "-lc", command)

            self.assertEqual(result.returncode, 0, result.stderr)
            normalized = result.stdout.strip()
            self.assertTrue(normalized.startswith("/"))

    def test_git_helpers_detect_repo_and_branch(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / ".test-tmp") as tempdir_name:
            tempdir = Path(tempdir_name)
            tempdir_posix = tempdir.as_posix()
            result_init = run_script(
                "bash",
                "-lc",
                f"git init '{tempdir_posix}' >/dev/null && git -C '{tempdir_posix}' checkout -b main >/dev/null",
            )
            self.assertEqual(result_init.returncode, 0, result_init.stderr)

            command = (
                "source .agents/skills/coferlandia-project-manager/scripts/lib/git.sh; "
                f"pm_git_is_repo '{tempdir_posix}' && "
                f"pm_git_current_branch '{tempdir_posix}'"
            )
            result = run_script("bash", "-lc", command)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip().splitlines()[-1], "main")

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

    def test_state_template_has_phase2_runtime_shape(self) -> None:
        payload = json.loads(
            (SKILL_ROOT / "templates" / "state.template.json").read_text(encoding="utf-8")
        )

        self.assertEqual(payload["version"], 1)
        self.assertIn("last_scan_at", payload)
        self.assertIn("repos_root", payload)
        self.assertIn("projects_detected", payload)
        self.assertIn("maintenance", payload)
        self.assertIn("runtime", payload)
        self.assertEqual(payload["runtime"]["execution_mode"], "supervised_agentic")

    def test_project_map_template_has_project_entries(self) -> None:
        payload = json.loads(
            (SKILL_ROOT / "templates" / "project-map.template.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(payload["version"], 1)
        self.assertIn("projects", payload)
        self.assertEqual(len(payload["projects"]), 1)
        project = payload["projects"][0]
        self.assertIn("project_slug", project)
        self.assertIn("repo_path", project)
        self.assertIn("obsidian_project_note", project)
        self.assertIn("obsidian_tasks", project)
        self.assertIn("archivist_status", project)

    def test_phase2_scripts_advertise_read_only_discovery_contract(self) -> None:
        scripts = [
            SCRIPTS_ROOT / "pm-detect-projects.sh",
            SCRIPTS_ROOT / "pm-scan-repos.sh",
            SCRIPTS_ROOT / "pm-git-status-all.sh",
        ]

        for script in scripts:
            result = run_script("bash", str(script.as_posix()), "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Usage:", result.stdout)

    def test_sample_scan_output_parses_as_json(self) -> None:
        payload = json.loads(
            (SKILL_ROOT / "examples" / "sample-scan-output.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertIn("projects", payload)
        self.assertGreaterEqual(len(payload["projects"]), 1)
        self.assertIn("git", payload["projects"][0])

    def test_skill_docs_include_phase2_read_only_policy(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("## State Files", skill_text)
        self.assertIn("## Project Discovery Rules", skill_text)
        self.assertIn("## Git Policy", skill_text)

    def test_phase2_detect_and_scan_repositories_end_to_end(self) -> None:
        with make_phase2_portfolio() as portfolio:
            detect = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-detect-projects.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--json",
            )
            self.assertEqual(detect.returncode, 0, detect.stderr)
            detected_payload = json.loads(detect.stdout)
            self.assertEqual(detected_payload["projects_detected"], 2)

            scan = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-scan-repos.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--json",
                "--include-dirty",
                "--include-remotes",
            )
            self.assertEqual(scan.returncode, 0, scan.stderr)
            scan_payload = json.loads(scan.stdout)
            self.assertEqual(scan_payload["projects_detected"], 2)
            projects = {project["project_slug"]: project for project in scan_payload["projects"]}
            self.assertFalse(projects["repo-one"]["git"]["dirty"])
            self.assertTrue(projects["repo-two"]["git"]["untracked"])

    def test_phase2_text_status_includes_git_state(self) -> None:
        with make_phase2_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-git-status-all.sh").as_posix()),
                "--config",
                portfolio["config_path"],
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("projects_detected: 2", result.stdout)
            self.assertIn("repo-one: branch=main dirty=False untracked=False", result.stdout)
            self.assertIn("repo-two: branch=main dirty=False untracked=True", result.stdout)

    def test_phase2_fail_on_dirty_returns_nonzero(self) -> None:
        with make_phase2_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-git-status-all.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--fail-on-dirty",
            )

            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    if shutil.which("bash") is None:
        raise SystemExit("bash is required for phase 1 tests")
    unittest.main()
