#!/usr/bin/env python3
"""Deterministic release maintenance for the coferlandia-skills repository."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

CLI_VERSION = "1.0.0"
README_START = "<!-- coferlandia-latest-release:start -->"
README_END = "<!-- coferlandia-latest-release:end -->"
RELEASE_HEADING_RE = re.compile(r"^## v(?P<version>\d+\.\d+\.\d+)\s*(?:\((?P<paren_date>\d{4}-\d{2}-\d{2})\)|[—-]\s*(?P<dash_date>\d{4}-\d{2}-\d{2}))\s*$", re.M)
UNRELEASED_RE = re.compile(r"^## Unreleased(?:\s*\([^\n]+\))?\s*$", re.M)
VERSION_RE = re.compile(r"(?ms)(^metadata:\s*\n(?:^[ \t]+.*\n)*?^[ \t]+version:\s*[\"']?)([^\"'\n]+)([\"']?\s*$)")
CHANGELOG_VERSION_RE = re.compile(r"^##\s+v?(?P<version>[^\s—-]+)\s*(?:[—-]|\()", re.M)


class ReleaseError(RuntimeError):
    pass


@dataclass(frozen=True)
class SkillInfo:
    name: str
    directory: Path
    skill_file: Path
    version: str
    changelog: Path


def emit(payload: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return code


def find_repo_root(start: Path | None = None) -> Path:
    env = os.environ.get("COFERLANDIA_REPO_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".claude-plugin" / "plugin.json").is_file() and (candidate / "skills").is_dir():
            return candidate
    script = Path(__file__).resolve()
    if len(script.parents) >= 5:
        candidate = script.parents[4]
        if (candidate / ".claude-plugin" / "plugin.json").is_file():
            return candidate
    raise ReleaseError("could not resolve repository root")


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, delete=False) as handle:
        handle.write(content)
        temp = Path(handle.name)
    temp.replace(path)


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if check and process.returncode != 0:
        raise ReleaseError(process.stderr.strip() or f"git {' '.join(args)} failed")
    return process


def plugin_version(root: Path) -> str:
    data = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    version = data.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ReleaseError(".claude-plugin/plugin.json has no valid semantic version")
    return version


def skill_version(text: str) -> str:
    match = VERSION_RE.search(text)
    if not match:
        raise ReleaseError("SKILL.md has no metadata.version")
    return match.group(2).strip()


def set_skill_version(text: str, version: str) -> str:
    if not VERSION_RE.search(text):
        raise ReleaseError("SKILL.md has no metadata.version")
    return VERSION_RE.sub(lambda m: f"{m.group(1)}{version}{m.group(3)}", text, count=1)


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


def changelog_version(path: Path) -> str | None:
    if not path.is_file():
        return None
    match = CHANGELOG_VERSION_RE.search(path.read_text(encoding="utf-8"))
    return match.group("version") if match else None


def release_sections(text: str) -> list[tuple[re.Match[str], str]]:
    matches = list(RELEASE_HEADING_RE.finditer(text))
    sections: list[tuple[re.Match[str], str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((match, text[match.end():end]))
    return sections


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
        if len(cells) != 4 or cells[0].lower() == "skill" or set(cells[0]) == {"-"}:
            continue
        rows.append({"name": cells[0].strip("`"), "previous": cells[1], "current": cells[2], "summary": cells[3]})
    return rows


def latest_release(root: Path) -> dict[str, Any]:
    path = root / "RELEASE-NOTES.md"
    text = path.read_text(encoding="utf-8")
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
    skills = release.get("skills") or []
    if skills:
        lines.extend([
            "| Changed skill | Version | Main change |",
            "|---|---:|---|",
        ])
        for row in skills:
            lines.append(f"| {row['name']} | {row['current']} | {row['summary']} |")
        lines.append("")
    lines.extend([
        "[Read the complete release notes](./RELEASE-NOTES.md)",
        README_END,
    ])
    return "\n".join(lines)


def apply_readme_block(text: str, block: str) -> str:
    if README_START in text or README_END in text:
        if text.count(README_START) != 1 or text.count(README_END) != 1:
            raise ReleaseError("README release markers are malformed")
        start = text.index(README_START)
        end = text.index(README_END, start) + len(README_END)
        return text[:start] + block + text[end:]
    heading = "## Releases"
    pos = text.find(heading)
    if pos < 0:
        raise ReleaseError("README.md has no '## Releases' heading")
    insert_at = text.find("\n", pos) + 1
    return text[:insert_at] + "\n" + block + "\n" + text[insert_at:]


def unreleased_body(text: str) -> str | None:
    match = UNRELEASED_RE.search(text)
    if not match:
        return None
    next_heading = re.search(r"^## ", text[match.end():], re.M)
    end = match.end() + (next_heading.start() if next_heading else len(text) - match.end())
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
            name = parts[2]
            result["skills"].setdefault(name, []).append(path)
        elif path.startswith(".claude-plugin/") or path in {".version-bump.json", "scripts/update-plugin.ps1"}:
            result["plugin"].append(path)
        elif path.startswith("_protocol/"):
            result["protocol"].append(path)
        elif path in {"README.md", "AGENTS.md", "RELEASE-NOTES.md", "SKILLS-GUIDE.md", "LICENSE"}:
            result["repository_docs"].append(path)
        elif path.startswith(".agents/") or path.startswith(".agent/"):
            result["local_only"].append(path)
        else:
            result["other"].append(path)
    return result


def command_inspect(root: Path, base: str) -> int:
    files = diff_files(root, base)
    classes = classify_paths(files)
    skills = {skill.name: skill for skill in discover_skills(root)}
    skill_rows = []
    for name, paths in sorted(classes["skills"].items()):
        current = skills.get(name)
        old_text = base_file(root, base, f"skills/{current.directory.parent.name}/{name}/SKILL.md") if current else None
        old_version = skill_version(old_text) if old_text else None
        skill_rows.append({"name": name, "paths": paths, "previous_version": old_version, "current_version": current.version if current else None})
    return emit({"command": "inspect", "base": base, "files": files, "classification": classes, "skills": skill_rows})


def check_bump_script(root: Path, errors: list[str], warnings: list[str]) -> None:
    script = root / "_protocol" / "scripts" / "bump_version.py"
    if not script.is_file():
        warnings.append("bump_version.py not present")
        return
    for flag in ("--check", "--audit"):
        process = subprocess.run([sys.executable, str(script), flag], cwd=root, text=True, capture_output=True, check=False)
        if process.returncode != 0:
            errors.append(f"bump_version.py {flag} failed: {process.stderr.strip() or process.stdout.strip()}")


def check_release(root: Path, base: str | None, release_ready: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    release = latest_release(root)
    current_plugin = plugin_version(root)
    if current_plugin != release["version"]:
        errors.append(f"plugin version {current_plugin} does not match latest release {release['version']}")

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    expected = apply_readme_block(readme, render_readme_block(release))
    if readme != expected:
        errors.append("README latest-release block is missing or stale")

    skills = discover_skills(root)
    by_name = {skill.name: skill for skill in skills}
    for skill in skills:
        top = changelog_version(skill.changelog)
        if top is None:
            errors.append(f"{skill.name}: missing or malformed CHANGELOG.md")
        elif top != skill.version:
            errors.append(f"{skill.name}: changelog {top} does not match metadata.version {skill.version}")

    release_rows = {row["name"]: row for row in release["skills"]}
    for name, row in release_rows.items():
        skill = by_name.get(name)
        if not skill:
            errors.append(f"release notes reference unknown skill {name}")
        elif row["current"] != skill.version:
            errors.append(f"release notes list {name} {row['current']} but SKILL.md is {skill.version}")

    notes = (root / "RELEASE-NOTES.md").read_text(encoding="utf-8")
    body = unreleased_body(notes)
    if release_ready and body:
        errors.append("release-ready state contains non-empty Unreleased content")

    changed_files: list[str] = []
    if base:
        try:
            changed_files = diff_files(root, base)
            classes = classify_paths(changed_files)
            for name, paths in classes["skills"].items():
                meaningful = [p for p in paths if not p.endswith("/CHANGELOG.md") and "/tests/" not in p]
                if not meaningful:
                    continue
                skill = by_name.get(name)
                if not skill:
                    continue
                old_text = base_file(root, base, skill.skill_file.relative_to(root).as_posix())
                old_version = skill_version(old_text) if old_text else None
                if old_version == skill.version:
                    errors.append(f"{name}: shipped behavior changed without metadata.version bump")
                if name not in release_rows:
                    errors.append(f"{name}: changed shipped behavior is absent from latest release notes")
                if skill.changelog.relative_to(root).as_posix() not in changed_files:
                    errors.append(f"{name}: changed shipped behavior without CHANGELOG.md update")
            shipped = bool(classes["skills"] or classes["plugin"] or classes["protocol"])
            old_plugin_text = base_file(root, base, ".claude-plugin/plugin.json")
            if shipped and old_plugin_text:
                old_plugin = json.loads(old_plugin_text).get("version")
                if old_plugin == current_plugin:
                    errors.append("shipped surface changed without repo/plugin version bump")
        except ReleaseError as exc:
            warnings.append(str(exc))

    check_bump_script(root, errors, warnings)
    return {
        "command": "check",
        "ok": not errors,
        "release_ready": release_ready,
        "plugin_version": current_plugin,
        "latest_release": {k: release[k] for k in ("version", "date", "skills")},
        "changed_files": changed_files,
        "errors": errors,
        "warnings": warnings,
    }


def prepend_changelog(path: Path, name: str, version: str, date: str, summary: str) -> None:
    entry = f"## {version} — {date}\n\n### Changed\n\n- {summary.strip()}\n\n"
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        heading = f"# Changelog — {name}"
        if not text.startswith(heading):
            raise ReleaseError(f"{path}: invalid changelog heading")
        rest = text[len(heading):].lstrip("\n")
        atomic_write(path, f"{heading}\n\n{entry}{rest}")
    else:
        atomic_write(path, f"# Changelog — {name}\n\n{entry}")


def render_release_section(plan: dict[str, Any]) -> str:
    lines = [f"## v{plan['release_version']} ({plan['release_date']})", ""]
    skills = plan.get("skills", [])
    if skills:
        lines.extend(["### Skills", "", "| Skill | Previous | Current | Summary |", "|---|---:|---:|---|"])
        for item in skills:
            lines.append(f"| {item['name']} | {item.get('previous_version', 'new')} | {item['new_version']} | {item['summary']} |")
        lines.append("")
    sections = [
        ("### Repository and protocol", plan.get("repository_changes", [])),
        ("### Plugin and packaging", plan.get("plugin_changes", [])),
        ("### Migration or compatibility", plan.get("migration_notes", [])),
    ]
    for heading, items in sections:
        if items:
            lines.extend([heading, ""] + [f"- {item}" for item in items] + [""])
    return "\n".join(lines).rstrip() + "\n"


def replace_unreleased_with_release(text: str, section: str) -> str:
    match = UNRELEASED_RE.search(text)
    if not match:
        return text.rstrip() + "\n\n## Unreleased\n\n" + section
    next_heading = re.search(r"^## ", text[match.end():], re.M)
    end = match.end() + (next_heading.start() if next_heading else len(text) - match.end())
    prefix = text[:match.start()]
    suffix = text[end:]
    return prefix + "## Unreleased\n\n" + section + "\n" + suffix.lstrip("\n")


def command_prepare(root: Path, plan_path: Path) -> int:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    required = {"schema_version", "release_version", "release_date", "impact", "skills"}
    missing = sorted(required - set(plan))
    if missing:
        raise ReleaseError(f"release plan missing fields: {', '.join(missing)}")
    if plan["schema_version"] != 1:
        raise ReleaseError("unsupported release-plan schema_version")
    if not re.fullmatch(r"\d+\.\d+\.\d+", plan["release_version"]):
        raise ReleaseError("release_version must be X.Y.Z")

    manifest_path = root / ".claude-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = plan["release_version"]
    atomic_write(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")

    skill_map = {skill.name: skill for skill in discover_skills(root)}
    updated: list[str] = []
    for item in plan["skills"]:
        skill = skill_map.get(item["name"])
        if not skill:
            raise ReleaseError(f"unknown skill in release plan: {item['name']}")
        text = skill.skill_file.read_text(encoding="utf-8")
        atomic_write(skill.skill_file, set_skill_version(text, item["new_version"]))
        prepend_changelog(skill.changelog, skill.name, item["new_version"], plan["release_date"], item["summary"])
        updated.append(skill.name)

    notes_path = root / "RELEASE-NOTES.md"
    notes = notes_path.read_text(encoding="utf-8")
    atomic_write(notes_path, replace_unreleased_with_release(notes, render_release_section(plan)))

    release = latest_release(root)
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    atomic_write(readme_path, apply_readme_block(readme, render_readme_block(release)))
    return emit({"command": "prepare", "release_version": plan["release_version"], "updated_skills": updated})


def iter_package_files(root: Path) -> Iterable[Path]:
    includes = [".claude-plugin", "skills", "_protocol", "README.md", "AGENTS.md", "SKILLS-GUIDE.md", "RELEASE-NOTES.md", "LICENSE"]
    for name in includes:
        path = root / name
        if not path.exists():
            continue
        if path.is_file():
            yield path
            continue
        for child in sorted(path.rglob("*")):
            if child.is_file() and "__pycache__" not in child.parts and child.suffix not in {".pyc", ".pyo"}:
                yield child


def command_package(root: Path, output: Path, verify: bool) -> int:
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(output.suffix + ".tmp")
    if temp.exists():
        temp.unlink()
    files = list(iter_package_files(root))
    with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
    temp.replace(output)

    errors: list[str] = []
    entries: list[str] = []
    if verify:
        with zipfile.ZipFile(output, "r") as archive:
            entries = sorted(archive.namelist())
            bad = archive.testzip()
            if bad:
                errors.append(f"corrupt archive entry: {bad}")
            required = {".claude-plugin/plugin.json", "README.md", "AGENTS.md", "RELEASE-NOTES.md", "LICENSE"}
            missing = sorted(required - set(entries))
            if missing:
                errors.append(f"missing package entries: {', '.join(missing)}")
            leaked = [entry for entry in entries if entry.startswith(".agents/") or entry.startswith(".agent/")]
            if leaked:
                errors.append("repository-local agent files leaked into package")
            manifest = json.loads(archive.read(".claude-plugin/plugin.json").decode("utf-8"))
            if manifest.get("version") != plugin_version(root):
                errors.append("packaged plugin version differs from repository")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    return emit({
        "command": "package",
        "ok": not errors,
        "output": str(output),
        "size": output.stat().st_size,
        "sha256": digest,
        "entries": len(entries) if verify else len(files),
        "errors": errors,
    }, 0 if not errors else 1)


def command_self_check(root: Path) -> int:
    required = [
        root / ".claude-plugin" / "plugin.json",
        root / "README.md",
        root / "RELEASE-NOTES.md",
        root / "skills" / "INDEX.md",
        root / "_protocol" / "scripts" / "validate_skill.py",
        root / "_protocol" / "scripts" / "bump_version.py",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    return emit({"command": "self-check", "ok": not missing, "repo_root": str(root), "missing": missing}, 0 if not missing else 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, help="repository root; otherwise auto-detected")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("version")
    sub.add_parser("capabilities")
    sub.add_parser("self-check")
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--base", required=True)
    prepare = sub.add_parser("prepare")
    prepare.add_argument("--input", required=True, type=Path)
    check = sub.add_parser("check")
    check.add_argument("--base")
    check.add_argument("--release-ready", action="store_true")
    render = sub.add_parser("render-readme")
    mode = render.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    package = sub.add_parser("package")
    package.add_argument("--output", required=True, type=Path)
    package.add_argument("--verify", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        root = args.repo.resolve() if args.repo else find_repo_root()
        if args.command == "version":
            return emit({"command": "version", "version": CLI_VERSION})
        if args.command == "capabilities":
            return emit({"command": "capabilities", "capabilities": ["inspect", "prepare", "check", "render-readme", "package"]})
        if args.command == "self-check":
            return command_self_check(root)
        if args.command == "inspect":
            return command_inspect(root, args.base)
        if args.command == "prepare":
            return command_prepare(root, args.input)
        if args.command == "check":
            result = check_release(root, args.base, args.release_ready)
            return emit(result, 0 if result["ok"] else 1)
        if args.command == "render-readme":
            release = latest_release(root)
            path = root / "README.md"
            current = path.read_text(encoding="utf-8")
            rendered = apply_readme_block(current, render_readme_block(release))
            if args.check:
                return emit({"command": "render-readme", "ok": current == rendered}, 0 if current == rendered else 1)
            atomic_write(path, rendered)
            return emit({"command": "render-readme", "ok": True, "updated": current != rendered})
        if args.command == "package":
            return command_package(root, args.output, args.verify)
    except (ReleaseError, OSError, ValueError, json.JSONDecodeError) as exc:
        return emit({"command": getattr(args, "command", None), "ok": False, "error": str(exc)}, 1)
    parser.error("unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
