from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "_protocol" / "scripts" / "install_global_skills.py"


def run_installer(source: Path, destinations: list[Path]) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(INSTALLER), "--source", str(source)]
    for destination in destinations:
        command.extend(["--destination", str(destination)])
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_installer_overwrites_skills_and_removes_legacy_names(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source_skill = source / "engineering" / "software-development"
    source_skill.mkdir(parents=True)
    (source_skill / "SKILL.md").write_text("new", encoding="utf-8")
    (source_skill / "agents").mkdir()
    (source_skill / "agents" / "openai.yaml").write_text("ui", encoding="utf-8")

    destinations = [tmp_path / "agents" / "skills", tmp_path / "codex" / "skills"]
    for destination in destinations:
        old = destination / "coferlandia-software-dev"
        old.mkdir(parents=True)
        (old / "SKILL.md").write_text("old", encoding="utf-8")
        current = destination / "software-development"
        current.mkdir(parents=True)
        (current / "SKILL.md").write_text("stale", encoding="utf-8")

    result = run_installer(source, destinations)

    assert result.returncode == 0, result.stderr
    for destination in destinations:
        assert not (destination / "coferlandia-software-dev").exists()
        assert (destination / "software-development" / "SKILL.md").read_text(encoding="utf-8") == "new"
        assert (destination / "software-development" / "agents" / "openai.yaml").read_text(encoding="utf-8") == "ui"


def test_installer_rejects_missing_source(tmp_path: Path) -> None:
    result = run_installer(tmp_path / "missing", [tmp_path / "destination"])

    assert result.returncode != 0
    assert "source" in result.stderr.lower()
