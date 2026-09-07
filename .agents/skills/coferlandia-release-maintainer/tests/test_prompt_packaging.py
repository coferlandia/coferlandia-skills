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


class PromptPackagingTests(unittest.TestCase):
    def test_package_includes_public_prompt_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            repo = Path(temp)
            (repo / ".claude-plugin").mkdir()
            (repo / "skills/meta/sample-skill").mkdir(parents=True)
            (repo / "_protocol").mkdir()
            (repo / "prompts").mkdir()

            (repo / ".claude-plugin/plugin.json").write_text(
                json.dumps({"name": "demo", "version": "1.0.0"}) + "\n",
                encoding="utf-8",
            )
            (repo / "skills/meta/sample-skill/SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: sample\nmetadata:\n"
                "  version: \"1.0\"\n  category: meta\n  status: active\n---\n",
                encoding="utf-8",
            )
            (repo / "prompts/INDEX.md").write_text("# Prompts\n", encoding="utf-8")
            for name in ("chat-coder.md", "ci.md", "merge.md", "registry.json"):
                (repo / "prompts" / name).write_text(name + "\n", encoding="utf-8")
            for name in ("README.md", "AGENTS.md", "SKILLS-GUIDE.md", "RELEASE-NOTES.md", "LICENSE"):
                (repo / name).write_text(name + "\n", encoding="utf-8")

            output = repo / "dist/demo.plugin"
            result = run_cli(repo, "package", "--output", str(output), "--verify")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())

            self.assertIn("prompts/INDEX.md", names)
            self.assertIn("prompts/chat-coder.md", names)
            self.assertIn("prompts/ci.md", names)
            self.assertIn("prompts/merge.md", names)
            self.assertIn("prompts/registry.json", names)


if __name__ == "__main__":
    unittest.main()
