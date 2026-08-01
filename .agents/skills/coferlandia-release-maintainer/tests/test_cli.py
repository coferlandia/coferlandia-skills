from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "coferlandia-release-maintainer-cli.py"
)


def run_cli(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(repo), *args],
        text=True,
        capture_output=True,
        check=False,
        timeout=20,
    )


class ReleaseMaintainerCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        (self.repo / ".claude-plugin").mkdir()
        (self.repo / "skills/meta/sample-skill").mkdir(parents=True)
        (self.repo / "_protocol/scripts").mkdir(parents=True)
        (self.repo / ".agents/skills/private").mkdir(parents=True)
        (self.repo / ".claude-plugin/plugin.json").write_text(
            json.dumps({"name": "demo", "version": "1.2.0"}) + "\n",
            encoding="utf-8",
        )
        (self.repo / "skills/INDEX.md").write_text(
            "# Index\n\n| [sample-skill](./meta/sample-skill/) | Sample | active |\n",
            encoding="utf-8",
        )
        (self.repo / "skills/meta/sample-skill/SKILL.md").write_text(
            "---\nname: sample-skill\ndescription: sample\nmetadata:\n"
            "  version: \"1.1.0\"\n  category: meta\n  status: active\n---\n\n# Sample\n",
            encoding="utf-8",
        )
        (self.repo / "skills/meta/sample-skill/CHANGELOG.md").write_text(
            "# Changelog — sample-skill\n\n## 1.1.0 — 2026-08-01\n\n"
            "### Changed\n\n- Improved behavior.\n",
            encoding="utf-8",
        )
        (self.repo / "RELEASE-NOTES.md").write_text(
            "# Releases\n\n## Unreleased\n\n## v1.2.0 (2026-08-01)\n\n"
            "### Skills\n\n| Skill | Previous | Current | Summary |\n"
            "|---|---:|---:|---|\n"
            "| sample-skill | 1.0.0 | 1.1.0 | Improved behavior. |\n",
            encoding="utf-8",
        )
        (self.repo / "README.md").write_text(
            "# Demo\n\n## Releases\n\nOld text.\n", encoding="utf-8"
        )
        for name in ("AGENTS.md", "SKILLS-GUIDE.md", "LICENSE"):
            (self.repo / name).write_text(name + "\n", encoding="utf-8")
        for script in ("validate_skill.py", "bump_version.py"):
            (self.repo / "_protocol/scripts" / script).write_text(
                "raise SystemExit(0)\n", encoding="utf-8"
            )
        (self.repo / ".agents/skills/private/secret.txt").write_text(
            "private\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_render_readme_preserves_human_content(self) -> None:
        result = run_cli(self.repo, "render-readme", "--write")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        text = (self.repo / "README.md").read_text(encoding="utf-8")
        self.assertIn("# Demo", text)
        self.assertIn("<!-- coferlandia-latest-release:start -->", text)
        self.assertIn("| sample-skill | 1.1.0 | Improved behavior. |", text)
        self.assertIn("Old text.", text)
        check = run_cli(self.repo, "render-readme", "--check")
        self.assertEqual(check.returncode, 0, check.stdout)

    def test_check_rejects_changelog_version_drift(self) -> None:
        run_cli(self.repo, "render-readme", "--write")
        path = self.repo / "skills/meta/sample-skill/CHANGELOG.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("1.1.0", "1.0.0", 1),
            encoding="utf-8",
        )
        result = run_cli(self.repo, "check", "--release-ready")
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertTrue(
            any("does not match metadata.version" in error for error in payload["errors"])
        )

    def test_release_ready_rejects_nonempty_unreleased(self) -> None:
        run_cli(self.repo, "render-readme", "--write")
        notes = self.repo / "RELEASE-NOTES.md"
        notes.write_text(
            notes.read_text(encoding="utf-8").replace(
                "## Unreleased\n\n", "## Unreleased\n\n- pending\n\n"
            ),
            encoding="utf-8",
        )
        result = run_cli(self.repo, "check", "--release-ready")
        self.assertEqual(result.returncode, 1)
        self.assertIn("non-empty Unreleased", result.stdout)

    def test_package_contains_release_notes_and_excludes_local_skill(self) -> None:
        output = self.repo / "dist/demo.plugin"
        result = run_cli(
            self.repo, "package", "--output", str(output), "--verify"
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
        self.assertIn("RELEASE-NOTES.md", names)
        self.assertIn("SKILLS-GUIDE.md", names)
        self.assertIn("skills/meta/sample-skill/SKILL.md", names)
        self.assertFalse(any(name.startswith(".agents/") for name in names))

    def test_prepare_is_idempotent(self) -> None:
        plan = self.repo / "plan.json"
        plan.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "release_version": "1.3.0",
                    "release_date": "2026-08-02",
                    "impact": "minor",
                    "skills": [
                        {
                            "name": "sample-skill",
                            "previous_version": "1.1.0",
                            "new_version": "1.2.0",
                            "impact": "minor",
                            "summary": "Adds a deterministic release gate.",
                        }
                    ],
                    "repository_changes": ["Adds release protocol."],
                    "plugin_changes": ["Adds verified packaging."],
                    "migration_notes": [],
                }
            ),
            encoding="utf-8",
        )
        for _ in range(2):
            result = run_cli(self.repo, "prepare", "--input", str(plan))
            self.assertEqual(result.returncode, 0, result.stdout)
        manifest = json.loads(
            (self.repo / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["version"], "1.3.0")
        skill_text = (self.repo / "skills/meta/sample-skill/SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn('version: "1.2.0"', skill_text)
        changelog = (
            self.repo / "skills/meta/sample-skill/CHANGELOG.md"
        ).read_text(encoding="utf-8")
        notes = (self.repo / "RELEASE-NOTES.md").read_text(encoding="utf-8")
        self.assertEqual(changelog.count("## 1.2.0 — 2026-08-02"), 1)
        self.assertEqual(notes.count("## v1.3.0 (2026-08-02)"), 1)
        self.assertIn(
            "**v1.3.0 — 2026-08-02**",
            (self.repo / "README.md").read_text(encoding="utf-8"),
        )

    def test_check_rejects_index_inventory_drift(self) -> None:
        run_cli(self.repo, "render-readme", "--write")
        (self.repo / "skills/INDEX.md").write_text("# Index\n", encoding="utf-8")
        result = run_cli(self.repo, "check", "--release-ready")
        self.assertEqual(result.returncode, 1)
        self.assertIn("INDEX.md is missing public skill sample-skill", result.stdout)

    def test_large_skill_body_is_checked_without_backtracking(self) -> None:
        run_cli(self.repo, "render-readme", "--write")
        skill = self.repo / "skills/meta/sample-skill/SKILL.md"
        skill.write_text(
            skill.read_text(encoding="utf-8")
            + "\n".join(f"Instruction line {index}" for index in range(20_000)),
            encoding="utf-8",
        )
        result = run_cli(self.repo, "check", "--release-ready")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
