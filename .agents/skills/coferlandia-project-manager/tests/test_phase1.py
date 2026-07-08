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


@contextmanager
def make_phase4_portfolio():
    (ROOT / ".test-tmp").mkdir(exist_ok=True)
    tempdir = tempfile.TemporaryDirectory(dir=ROOT / ".test-tmp")
    try:
        base = Path(tempdir.name)
        repos_root = base / "repos"
        repos_root.mkdir()

        complete_repo = repos_root / "repo-complete"
        incomplete_repo = repos_root / "repo-incomplete"
        complete_repo.mkdir()
        incomplete_repo.mkdir()

        for repo_path in (complete_repo, incomplete_repo):
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

        for filename in ("README.md", "TODO.md", "HISTORY.md", "DECISIONS.md", "RUNBOOK.md", "AGENTS.md"):
            (complete_repo / filename).write_text(f"# {filename}\n", encoding="utf-8")

        (incomplete_repo / "README.md").write_text("# README.md\n", encoding="utf-8")

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
            "complete_repo": complete_repo,
            "incomplete_repo": incomplete_repo,
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

    def test_phase3_obsidian_templates_include_required_fields(self) -> None:
        project_template = (SKILL_ROOT / "templates" / "obsidian-project.template.md").read_text(
            encoding="utf-8"
        )
        task_template = (SKILL_ROOT / "templates" / "obsidian-task.template.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("pm-project: true", project_template)
        self.assertIn("coferlandia-project-id: \"\"", project_template)
        self.assertIn("tags: [\"coferlandia\", \"repo\", \"agentic-dev\"]", project_template)
        self.assertIn("pm-task: true", task_template)
        self.assertIn("execution_policy: supervised_agentic", task_template)
        self.assertIn("requires_archivist_sync: true", task_template)

    def test_phase3_obsidian_helper_returns_expected_paths(self) -> None:
        command = (
            "source .agents/skills/coferlandia-project-manager/scripts/lib/obsidian-pm.sh; "
            "pm_obsidian_project_path /vault Projects demo-project && "
            "pm_obsidian_task_path /vault Tasks task-001"
        )
        result = run_script("bash", "-lc", command)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip().splitlines(),
            ["/vault/Projects/demo-project.md", "/vault/Tasks/task-001.md"],
        )

    def test_phase3_entry_points_advertise_usage(self) -> None:
        scripts = [
            SCRIPTS_ROOT / "pm-backup-pm-db.sh",
            SCRIPTS_ROOT / "pm-sync-to-obsidian.sh",
        ]

        for script in scripts:
            result = run_script("bash", str(script.as_posix()), "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Usage:", result.stdout)
            self.assertIn("Description:", result.stdout)

    def test_phase3_entry_points_reject_non_help_invocation_until_implemented(self) -> None:
        config_path = ".agents/skills/coferlandia-project-manager/examples/config.sample.json"
        scripts = [
            SCRIPTS_ROOT / "pm-backup-pm-db.sh",
            SCRIPTS_ROOT / "pm-sync-to-obsidian.sh",
        ]

        for script in scripts:
            result = run_script(
                "bash",
                str(script.as_posix()),
                "--config",
                config_path,
                "--dry-run",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not implemented yet", result.stderr.lower())

    def test_phase3_examples_and_skill_docs_include_sync_vocabulary(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        project_note = (SKILL_ROOT / "examples" / "sample-project-note.md").read_text(
            encoding="utf-8"
        )
        task_note = (SKILL_ROOT / "examples" / "sample-task-note.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("## Required Task Statuses", skill_text)
        self.assertIn("## Sync Rules", skill_text)
        self.assertIn("## Phase Boundary", skill_text)
        self.assertIn("entry points remain approval-gated placeholders", skill_text.lower())
        self.assertIn("preserve unknown frontmatter fields", skill_text.lower())
        self.assertIn("status: active", project_note)
        self.assertIn("status: planning", task_note)

    def test_phase3_shell_scripts_are_syntax_clean(self) -> None:
        scripts = [
            SCRIPTS_ROOT / "pm-backup-pm-db.sh",
            SCRIPTS_ROOT / "pm-sync-to-obsidian.sh",
            SCRIPTS_ROOT / "lib" / "obsidian-pm.sh",
        ]

        for script in scripts:
            result = run_script("bash", "-n", str(script.as_posix()))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_phase4_sample_archivist_status_document_is_valid_json(self) -> None:
        payload = json.loads(
            (SKILL_ROOT / "examples" / "sample-archivist-status.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertIn("projects", payload)
        self.assertGreaterEqual(len(payload["projects"]), 1)
        project = payload["projects"][0]
        self.assertIn("project_slug", project)
        self.assertIn("archivist_initialized", project)
        self.assertIn("expected_artifacts", project)
        self.assertNotIn("maintenance_overdue", project)

    def test_phase4_archivist_check_reports_repo_artifacts(self) -> None:
        with make_phase4_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-check-archivist.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["projects_detected"], 2)
            projects = {project["project_slug"]: project for project in payload["projects"]}
            self.assertTrue(projects["repo-complete"]["archivist_initialized"])
            self.assertFalse(projects["repo-incomplete"]["archivist_initialized"])
            for project in payload["projects"]:
                self.assertNotIn("maintenance_overdue", project)

    def test_phase4_sync_from_repos_reports_read_only_summary(self) -> None:
        with make_phase4_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-sync-from-repos.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--json",
                "--dry-run",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertEqual(payload["mode"], "dry-run")
            self.assertEqual(payload["projects_detected"], 2)
            self.assertEqual(payload["syncable_projects"], 1)

    def test_phase4_conflict_detector_flags_missing_archivist_files(self) -> None:
        with make_phase4_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-detect-conflicts.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertGreaterEqual(payload["conflict_count"], 1)
            conflict_types = {conflict["type"] for conflict in payload["conflicts"]}
            self.assertIn("missing_archivist_artifact", conflict_types)

    def test_phase4_weekly_maintenance_reports_due_state(self) -> None:
        with make_phase4_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-weekly-maintenance.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--json",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertIn("archivist", payload)
            self.assertIn("conflicts", payload)
            self.assertIn("maintenance_due", payload)

    def test_phase4_conflict_example_mentions_required_action(self) -> None:
        example = (SKILL_ROOT / "examples" / "sample-sync-conflict.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Sync Conflict Example", example)
        self.assertIn("Required action", example)
        self.assertIn("`TODO.md` still lists the task as open", example)

    def test_phase4_skill_docs_include_archivist_integration(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("## Archivist Integration", skill_text)
        self.assertIn("TODO.md", skill_text)
        self.assertIn("HISTORY.md", skill_text)
        self.assertIn("## Weekly Maintenance", skill_text)
        self.assertIn("does not run in the background by itself", skill_text)

    def test_phase4_archivist_scripts_are_syntax_clean(self) -> None:
        scripts = [
            SCRIPTS_ROOT / "pm-check-archivist.sh",
            SCRIPTS_ROOT / "pm-sync-from-repos.sh",
            SCRIPTS_ROOT / "pm-detect-conflicts.sh",
            SCRIPTS_ROOT / "pm-weekly-maintenance.sh",
        ]

        for script in scripts:
            result = run_script("bash", "-n", str(script.as_posix()))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_phase4_archivist_python_module_is_syntax_clean(self) -> None:
        result = run_script(
            "python", "-m", "py_compile",
            str((SCRIPTS_ROOT / "lib" / "archivist.py").as_posix()),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_phase4_sync_script_rejects_apply_until_implemented(self) -> None:
        with make_phase4_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-sync-from-repos.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--apply",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not implemented yet", result.stderr.lower())

    def test_phase4_weekly_maintenance_rejects_apply_until_implemented(self) -> None:
        with make_phase4_portfolio() as portfolio:
            result = run_script(
                "bash",
                str((SCRIPTS_ROOT / "pm-weekly-maintenance.sh").as_posix()),
                "--config",
                portfolio["config_path"],
                "--apply",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not implemented yet", result.stderr.lower())

    def test_phase4_conflict_report_only_advertises_implemented_classes(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        # The two classes the PM actually detects must be documented as a contract.
        self.assertIn("`repo_path_missing`", skill_text)
        self.assertIn("`missing_archivist_artifact`", skill_text)
        # Classes that are not implemented must be framed as future work, not promises.
        self.assertIn("candidates for later phases", skill_text.lower())

    def test_phase5_report_templates_carry_required_headings(self) -> None:
        portfolio = (
            (SKILL_ROOT / "templates" / "portfolio-report.template.md")
            .read_text(encoding="utf-8")
        )
        project = (
            (SKILL_ROOT / "templates" / "project-report.template.md")
            .read_text(encoding="utf-8")
        )
        task = (
            (SKILL_ROOT / "templates" / "task-report.template.md")
            .read_text(encoding="utf-8")
        )

        for required in (
            "Active projects:",
            "Ready-for-agent tasks:",
            "Repos with uncommitted changes:",
            "Projects with sync conflicts:",
        ):
            self.assertIn(required, portfolio)
        for required in ("Git status:", "Archivist status:", "Blockers:"):
            self.assertIn(required, project)
        for required in ("Review state:", "Verification state:"):
            self.assertIn(required, task)

    def test_phase5_examples_cover_portfolio_questions(self) -> None:
        portfolio = (
            (SKILL_ROOT / "examples" / "sample-portfolio-report.md")
            .read_text(encoding="utf-8")
        )
        project = (
            (SKILL_ROOT / "examples" / "sample-project-report.md")
            .read_text(encoding="utf-8")
        )

        self.assertIn("Ready-for-agent tasks:", portfolio)
        self.assertIn("Projects with sync conflicts:", portfolio)
        self.assertIn("Tasks completed this week:", portfolio)
        self.assertIn("Archivist status:", project)

    def test_phase5_reporting_scripts_advertise_usage(self) -> None:
        scripts = [
            SCRIPTS_ROOT / "pm-portfolio-report.sh",
            SCRIPTS_ROOT / "pm-project-report.sh",
            SCRIPTS_ROOT / "pm-task-report.sh",
            SCRIPTS_ROOT / "pm-health-check.sh",
            SCRIPTS_ROOT / "pm-clean-worktrees.sh",
        ]

        for script in scripts:
            result = run_script("bash", str(script.as_posix()), "--help")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Usage:", result.stdout)
            self.assertIn("Description:", result.stdout)

    def test_phase5_scripts_are_syntax_clean(self) -> None:
        scripts = [
            SCRIPTS_ROOT / "pm-portfolio-report.sh",
            SCRIPTS_ROOT / "pm-project-report.sh",
            SCRIPTS_ROOT / "pm-task-report.sh",
            SCRIPTS_ROOT / "pm-health-check.sh",
            SCRIPTS_ROOT / "pm-clean-worktrees.sh",
        ]

        for script in scripts:
            result = run_script("bash", "-n", str(script.as_posix()))
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_phase5_entry_points_reject_invocation_until_implemented(self) -> None:
        config_path = ".agents/skills/coferlandia-project-manager/examples/config.sample.json"
        scripts = [
            SCRIPTS_ROOT / "pm-portfolio-report.sh",
            SCRIPTS_ROOT / "pm-project-report.sh",
            SCRIPTS_ROOT / "pm-task-report.sh",
            SCRIPTS_ROOT / "pm-health-check.sh",
            SCRIPTS_ROOT / "pm-clean-worktrees.sh",
        ]

        for script in scripts:
            result = run_script(
                "bash",
                str(script.as_posix()),
                "--config",
                config_path,
            )
            self.assertNotEqual(result.returncode, 0, script.name)
            self.assertIn("not implemented yet", result.stderr.lower())

    def test_phase5_skill_docs_include_reporting_policy(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("## Reporting Output", skill_text)
        self.assertIn(".coferlandia/project-manager/reports/", skill_text)
        self.assertIn("## Reporting Questions", skill_text)
        self.assertIn("which projects have ready-for-agent tasks", skill_text.lower())
        self.assertIn("which repos have uncommitted changes", skill_text.lower())

    def test_phase5_skill_docs_include_worktree_cleanup_rules(self) -> None:
        skill_text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("## Worktree Cleanup Rules", skill_text)
        # Conservative guardrails must be explicit.
        self.assertIn("delete dirty worktrees", skill_text.lower())
        self.assertIn("force-delete anything", skill_text.lower())
        self.assertIn("bypass superpowers branch finishing rules", skill_text.lower())


if __name__ == "__main__":
    if shutil.which("bash") is None:
        raise SystemExit("bash is required for phase 1 tests")
    unittest.main()
