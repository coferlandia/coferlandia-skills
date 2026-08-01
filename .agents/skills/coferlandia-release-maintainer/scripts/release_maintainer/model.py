from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

README_START = "<!-- coferlandia-latest-release:start -->"
README_END = "<!-- coferlandia-latest-release:end -->"
RELEASE_HEADING_RE = re.compile(
    r"^## v(?P<version>\d+\.\d+\.\d+)\s*"
    r"(?:\((?P<paren_date>\d{4}-\d{2}-\d{2})\)|[—-]\s*(?P<dash_date>\d{4}-\d{2}-\d{2}))\s*$",
    re.M,
)
UNRELEASED_RE = re.compile(r"^## Unreleased(?:\s*\([^\n]+\))?\s*$", re.M)
METADATA_VERSION_LINE_RE = re.compile(
    r"^(?P<indent>[ \t]+)version:\s*(?P<quote>[\"']?)(?P<version>[^\"'\n]+)(?P=quote)\s*$"
)
CHANGELOG_VERSION_RE = re.compile(
    r"^##\s+v?(?P<version>[^\s—-]+)\s*(?:[—-]|\()", re.M
)
INDEX_SKILL_RE = re.compile(r"\]\(\./(?P<category>[^/]+)/(?P<name>[^/]+)/\)")


class ReleaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class SkillInfo:
    name: str
    directory: Path
    skill_file: Path
    version: str
    changelog: Path


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", newline="", dir=path.parent, delete=False
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    temporary.replace(path)


def find_repo_root(start: Path | None = None) -> Path:
    configured = os.environ.get("COFERLANDIA_REPO_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".claude-plugin/plugin.json").is_file() and (
            candidate / "skills"
        ).is_dir():
            return candidate
    script = Path(__file__).resolve()
    candidate = script.parents[5]
    if (candidate / ".claude-plugin/plugin.json").is_file():
        return candidate
    raise ReleaseError("could not resolve repository root")


def run_git(
    root: Path, *arguments: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        ["git", "-C", str(root), *arguments],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and process.returncode != 0:
        raise ReleaseError(process.stderr.strip() or f"git {' '.join(arguments)} failed")
    return process


def plugin_version(root: Path) -> str:
    data = json.loads(
        (root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    version = data.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ReleaseError(".claude-plugin/plugin.json has no valid semantic version")
    return version


def _metadata_version_line(lines: list[str]) -> tuple[int, re.Match[str]]:
    metadata_index: int | None = None
    for index, line in enumerate(lines):
        if line.strip() == "metadata:" and not line.startswith((" ", "\t")):
            metadata_index = index
            break
    if metadata_index is None:
        raise ReleaseError("SKILL.md has no metadata block")

    for index in range(metadata_index + 1, len(lines)):
        line = lines[index].rstrip("\r\n")
        if line and not line.startswith((" ", "\t")):
            break
        match = METADATA_VERSION_LINE_RE.match(line)
        if match:
            return index, match
    raise ReleaseError("SKILL.md has no metadata.version")


def skill_version(text: str) -> str:
    _, match = _metadata_version_line(text.splitlines(keepends=True))
    return match.group("version").strip()


def set_skill_version(text: str, version: str) -> str:
    lines = text.splitlines(keepends=True)
    index, match = _metadata_version_line(lines)
    newline = "\r\n" if lines[index].endswith("\r\n") else "\n" if lines[index].endswith("\n") else ""
    quote = match.group("quote")
    lines[index] = f"{match.group('indent')}version: {quote}{version}{quote}{newline}"
    return "".join(lines)


def discover_skills(root: Path) -> list[SkillInfo]:
    result: list[SkillInfo] = []
    for skill_file in sorted((root / "skills").glob("*/*/SKILL.md")):
        directory = skill_file.parent
        result.append(
            SkillInfo(
                name=directory.name,
                directory=directory,
                skill_file=skill_file,
                version=skill_version(skill_file.read_text(encoding="utf-8")),
                changelog=directory / "CHANGELOG.md",
            )
        )
    return result


def index_skill_names(root: Path) -> set[str]:
    index = root / "skills/INDEX.md"
    if not index.is_file():
        raise ReleaseError("skills/INDEX.md is missing")
    return {
        match.group("name")
        for match in INDEX_SKILL_RE.finditer(index.read_text(encoding="utf-8"))
    }


def changelog_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    match = CHANGELOG_VERSION_RE.search(path.read_text(encoding="utf-8"))
    return match.group("version") if match else None


def release_sections(text: str) -> list[tuple[re.Match[str], str]]:
    matches = list(RELEASE_HEADING_RE.finditer(text))
    result: list[tuple[re.Match[str], str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        result.append((match, text[match.end():end]))
    return result


def parse_skill_table(section: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    in_skills = False
    for line in section.splitlines():
        if line.strip() == "### Skills":
            in_skills = True
            continue
        if in_skills and line.startswith("### "):
            break
        if not in_skills or not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if (
            len(cells) != 4
            or cells[0].lower() == "skill"
            or set(cells[0]) == {"-"}
        ):
            continue
        rows.append(
            {
                "name": cells[0].strip("`"),
                "previous": cells[1],
                "current": cells[2],
                "summary": cells[3],
            }
        )
    return rows


def latest_release(root: Path) -> dict[str, Any]:
    text = (root / "RELEASE-NOTES.md").read_text(encoding="utf-8")
    sections = release_sections(text)
    if not sections:
        raise ReleaseError("RELEASE-NOTES.md has no released version section")
    match, body = sections[0]
    return {
        "version": match.group("version"),
        "date": match.group("paren_date") or match.group("dash_date"),
        "skills": parse_skill_table(body),
        "body": body,
    }


def render_readme_block(release: dict[str, Any]) -> str:
    lines = [
        README_START,
        "## Latest release",
        "",
        f"**v{release['version']} — {release['date']}**",
        "",
    ]
    if release["skills"]:
        lines.extend(
            [
                "| Changed skill | Version | Main change |",
                "|---|---:|---|",
            ]
        )
        for row in release["skills"]:
            lines.append(f"| {row['name']} | {row['current']} | {row['summary']} |")
        lines.append("")
    lines.extend(
        [
            "[Read the complete release notes](./RELEASE-NOTES.md)",
            README_END,
        ]
    )
    return "\n".join(lines)


def apply_readme_block(text: str, block: str) -> str:
    if README_START in text or README_END in text:
        if text.count(README_START) != 1 or text.count(README_END) != 1:
            raise ReleaseError("README release markers are malformed")
        start = text.index(README_START)
        end = text.index(README_END, start) + len(README_END)
        return text[:start] + block + text[end:]
    heading = "## Releases"
    position = text.find(heading)
    if position < 0:
        raise ReleaseError("README.md has no '## Releases' heading")
    insertion = text.find("\n", position) + 1
    return text[:insertion] + "\n" + block + "\n" + text[insertion:]


def unreleased_body(text: str) -> str | None:
    match = UNRELEASED_RE.search(text)
    if not match:
        return None
    next_heading = re.search(r"^## ", text[match.end():], re.M)
    end = match.end() + (
        next_heading.start() if next_heading else len(text) - match.end()
    )
    return text[match.end():end].strip()


def diff_files(root: Path, base: str) -> list[str]:
    process = run_git(root, "diff", "--name-only", f"{base}...HEAD", check=False)
    if process.returncode != 0:
        process = run_git(root, "diff", "--name-only", base, "HEAD", check=False)
    if process.returncode != 0:
        raise ReleaseError(process.stderr.strip() or f"cannot diff against {base}")
    return [line.strip() for line in process.stdout.splitlines() if line.strip()]


def base_file(root: Path, base: str, path: str) -> str | None:
    process = run_git(root, "show", f"{base}:{path}", check=False)
    return process.stdout if process.returncode == 0 else None


def classify_paths(paths: Iterable[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "skills": {},
        "plugin": [],
        "protocol": [],
        "repository_docs": [],
        "local_only": [],
        "other": [],
    }
    for path in paths:
        parts = Path(path).parts
        if len(parts) >= 4 and parts[0] == "skills":
            result["skills"].setdefault(parts[2], []).append(path)
        elif path.startswith(".claude-plugin/") or path in {
            ".version-bump.json",
            "scripts/update-plugin.ps1",
        }:
            result["plugin"].append(path)
        elif path.startswith("_protocol/"):
            result["protocol"].append(path)
        elif path in {
            "README.md",
            "AGENTS.md",
            "RELEASE-NOTES.md",
            "SKILLS-GUIDE.md",
            "LICENSE",
        }:
            result["repository_docs"].append(path)
        elif path.startswith(".agents/") or path.startswith(".agent/"):
            result["local_only"].append(path)
        else:
            result["other"].append(path)
    return result


def upsert_changelog_entry(
    path: Path, name: str, version: str, date: str, summary: str
) -> None:
    entry = f"## {version} — {date}\n\n### Changed\n\n- {summary.strip()}\n"
    heading = f"# Changelog — {name}"
    if not path.is_file():
        atomic_write(path, f"{heading}\n\n{entry}")
        return
    text = path.read_text(encoding="utf-8")
    if not text.startswith(heading):
        raise ReleaseError(f"{path}: invalid changelog heading")
    version_heading = re.compile(rf"^##\s+v?{re.escape(version)}(?:\s|$).*?$", re.M)
    match = version_heading.search(text)
    if match:
        next_heading = re.search(r"^##\s+", text[match.end():], re.M)
        end = match.end() + (
            next_heading.start() if next_heading else len(text) - match.end()
        )
        updated = text[:match.start()] + entry + "\n" + text[end:].lstrip("\n")
    else:
        rest = text[len(heading):].lstrip("\n")
        updated = f"{heading}\n\n{entry}\n{rest}"
    atomic_write(path, updated.rstrip() + "\n")


def render_release_section(plan: dict[str, Any]) -> str:
    lines = [f"## v{plan['release_version']} ({plan['release_date']})", ""]
    if plan.get("skills"):
        lines.extend(
            [
                "### Skills",
                "",
                "| Skill | Previous | Current | Summary |",
                "|---|---:|---:|---|",
            ]
        )
        for item in plan["skills"]:
            lines.append(
                f"| {item['name']} | {item.get('previous_version', 'new')} | "
                f"{item['new_version']} | {item['summary']} |"
            )
        lines.append("")
    for heading, key in (
        ("### Repository and protocol", "repository_changes"),
        ("### Plugin and packaging", "plugin_changes"),
        ("### Migration or compatibility", "migration_notes"),
    ):
        if plan.get(key):
            lines.extend([heading, "", *[f"- {item}" for item in plan[key]], ""])
    return "\n".join(lines).rstrip() + "\n"


def upsert_release_section(text: str, version: str, section: str) -> str:
    release_heading = re.compile(rf"^## v{re.escape(version)}(?:\s|$).*?$", re.M)
    existing = release_heading.search(text)
    if existing:
        next_heading = re.search(r"^## ", text[existing.end():], re.M)
        end = existing.end() + (
            next_heading.start() if next_heading else len(text) - existing.end()
        )
        text = (
            text[:existing.start()]
            + section.rstrip()
            + "\n\n"
            + text[end:].lstrip("\n")
        )

    unreleased = UNRELEASED_RE.search(text)
    if not unreleased:
        return text.rstrip() + "\n\n## Unreleased\n\n" + ("" if existing else section)
    next_heading = re.search(r"^## ", text[unreleased.end():], re.M)
    end = unreleased.end() + (
        next_heading.start() if next_heading else len(text) - unreleased.end()
    )
    suffix = text[end:].lstrip("\n")
    if not existing:
        suffix = section.rstrip() + "\n\n" + suffix
    return text[:unreleased.start()] + "## Unreleased\n\n" + suffix


def iter_package_files(root: Path) -> Iterable[Path]:
    includes = [
        ".claude-plugin",
        "skills",
        "_protocol",
        "README.md",
        "AGENTS.md",
        "SKILLS-GUIDE.md",
        "RELEASE-NOTES.md",
        "LICENSE",
    ]
    for name in includes:
        path = root / name
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in sorted(path.rglob("*")):
            if child.is_symlink():
                continue
            if (
                child.is_file()
                and "__pycache__" not in child.parts
                and child.suffix not in {".pyc", ".pyo", ".plugin"}
            ):
                yield child
