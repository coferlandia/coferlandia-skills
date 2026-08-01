from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

from .model import (
    ReleaseError,
    apply_readme_block,
    atomic_write,
    base_file,
    changelog_version,
    classify_paths,
    diff_files,
    discover_skills,
    index_skill_names,
    iter_package_files,
    latest_release,
    plugin_version,
    render_readme_block,
    render_release_section,
    set_skill_version,
    skill_version,
    unreleased_body,
    upsert_changelog_entry,
    upsert_release_section,
)


def inspect_release(root: Path, base: str) -> dict[str, Any]:
    files = diff_files(root, base)
    classes = classify_paths(files)
    skills = {skill.name: skill for skill in discover_skills(root)}
    rows: list[dict[str, Any]] = []
    for name, paths in sorted(classes["skills"].items()):
        current = skills.get(name)
        skill_path = next((path for path in paths if path.endswith("/SKILL.md")), None)
        if skill_path is None and current is not None:
            skill_path = current.skill_file.relative_to(root).as_posix()
        old_text = base_file(root, base, skill_path) if skill_path else None
        rows.append(
            {
                "name": name,
                "paths": paths,
                "previous_version": skill_version(old_text) if old_text else None,
                "current_version": current.version if current else "removed",
            }
        )
    return {
        "command": "inspect",
        "base": base,
        "files": files,
        "classification": classes,
        "skills": rows,
    }


def check_release(root: Path, base: str | None, release_ready: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    release = latest_release(root)
    current_plugin = plugin_version(root)
    if current_plugin != release["version"]:
        errors.append(
            f"plugin version {current_plugin} does not match latest release {release['version']}"
        )

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    if readme != apply_readme_block(readme, render_readme_block(release)):
        errors.append("README latest-release block is missing or stale")

    skills = discover_skills(root)
    by_name = {skill.name: skill for skill in skills}
    indexed = index_skill_names(root)
    discovered = set(by_name)
    for missing in sorted(discovered - indexed):
        errors.append(f"skills/INDEX.md is missing public skill {missing}")
    for unknown in sorted(indexed - discovered):
        errors.append(f"skills/INDEX.md references unknown public skill {unknown}")

    for skill in skills:
        top = changelog_version(skill.changelog)
        if top is None:
            errors.append(f"{skill.name}: missing or malformed CHANGELOG.md")
        elif top != skill.version:
            errors.append(
                f"{skill.name}: changelog {top} does not match metadata.version {skill.version}"
            )

    release_rows = {row["name"]: row for row in release["skills"]}
    for name, row in release_rows.items():
        skill = by_name.get(name)
        if skill is None and row["current"].lower() != "removed":
            errors.append(f"release notes reference unknown skill {name}")
        elif skill is not None and row["current"] != skill.version:
            errors.append(
                f"release notes list {name} {row['current']} but SKILL.md is {skill.version}"
            )

    notes = (root / "RELEASE-NOTES.md").read_text(encoding="utf-8")
    if release_ready and unreleased_body(notes):
        errors.append("release-ready state contains non-empty Unreleased content")

    changed_files: list[str] = []
    if base:
        try:
            changed_files = diff_files(root, base)
            classes = classify_paths(changed_files)
            for name, paths in classes["skills"].items():
                meaningful = [
                    path
                    for path in paths
                    if not path.endswith("/CHANGELOG.md") and "/tests/" not in path
                ]
                if not meaningful:
                    continue
                skill = by_name.get(name)
                skill_path = next(
                    (path for path in paths if path.endswith("/SKILL.md")), None
                )
                if skill_path is None and skill is not None:
                    skill_path = skill.skill_file.relative_to(root).as_posix()
                old_text = base_file(root, base, skill_path) if skill_path else None
                old_version = skill_version(old_text) if old_text else None
                row = release_rows.get(name)
                if skill is None:
                    if row is None or row["current"].lower() != "removed":
                        errors.append(
                            f"{name}: removed public skill is absent from latest release notes"
                        )
                    continue
                if old_version == skill.version:
                    errors.append(
                        f"{name}: shipped behavior changed without metadata.version bump"
                    )
                if row is None:
                    errors.append(
                        f"{name}: changed shipped behavior is absent from latest release notes"
                    )
                changelog_path = skill.changelog.relative_to(root).as_posix()
                if changelog_path not in changed_files:
                    errors.append(
                        f"{name}: changed shipped behavior without CHANGELOG.md update"
                    )

            shipped = bool(
                classes["skills"] or classes["plugin"] or classes["protocol"]
            )
            old_plugin_text = base_file(root, base, ".claude-plugin/plugin.json")
            if shipped and old_plugin_text:
                if json.loads(old_plugin_text).get("version") == current_plugin:
                    errors.append("shipped surface changed without repo/plugin version bump")
        except ReleaseError as error:
            warnings.append(str(error))

    return {
        "command": "check",
        "ok": not errors,
        "release_ready": release_ready,
        "plugin_version": current_plugin,
        "latest_release": {
            key: release[key] for key in ("version", "date", "skills")
        },
        "changed_files": changed_files,
        "errors": errors,
        "warnings": warnings,
        "version_tools": "run separately via bump_version.py --check and --audit",
    }


def prepare_release(root: Path, plan_path: Path) -> dict[str, Any]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    required = {"schema_version", "release_version", "release_date", "impact", "skills"}
    missing = sorted(required - set(plan))
    if missing:
        raise ReleaseError(f"release plan missing fields: {', '.join(missing)}")
    if plan["schema_version"] != 1:
        raise ReleaseError("unsupported release-plan schema_version")
    if not re.fullmatch(r"\d+\.\d+\.\d+", plan["release_version"]):
        raise ReleaseError("release_version must be X.Y.Z")

    manifest_path = root / ".claude-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = plan["release_version"]
    atomic_write(
        manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )

    skill_map = {skill.name: skill for skill in discover_skills(root)}
    updated: list[str] = []
    for item in plan["skills"]:
        skill = skill_map.get(item["name"])
        new_version = str(item["new_version"])
        if new_version.lower() == "removed":
            if skill is not None:
                raise ReleaseError(
                    f"release plan marks existing skill as removed: {item['name']}"
                )
            updated.append(item["name"])
            continue
        if skill is None:
            raise ReleaseError(f"unknown skill in release plan: {item['name']}")
        text = skill.skill_file.read_text(encoding="utf-8")
        atomic_write(skill.skill_file, set_skill_version(text, new_version))
        upsert_changelog_entry(
            skill.changelog,
            skill.name,
            new_version,
            plan["release_date"],
            item["summary"],
        )
        updated.append(skill.name)

    notes_path = root / "RELEASE-NOTES.md"
    notes = notes_path.read_text(encoding="utf-8")
    section = render_release_section(plan)
    atomic_write(
        notes_path,
        upsert_release_section(notes, plan["release_version"], section),
    )

    release = latest_release(root)
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    atomic_write(readme_path, apply_readme_block(readme, render_readme_block(release)))
    return {
        "command": "prepare",
        "release_version": plan["release_version"],
        "updated_skills": updated,
    }


def build_package(root: Path, output: Path, verify: bool) -> tuple[dict[str, Any], int]:
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    if temporary.exists():
        temporary.unlink()
    files = list(iter_package_files(root))
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
    temporary.replace(output)

    errors: list[str] = []
    entries: list[str] = []
    if verify:
        with zipfile.ZipFile(output, "r") as archive:
            entries = sorted(archive.namelist())
            corrupted = archive.testzip()
            if corrupted:
                errors.append(f"corrupt archive entry: {corrupted}")
            required = {
                ".claude-plugin/plugin.json",
                "README.md",
                "AGENTS.md",
                "RELEASE-NOTES.md",
                "SKILLS-GUIDE.md",
                "LICENSE",
            }
            missing = sorted(required - set(entries))
            if missing:
                errors.append(f"missing package entries: {', '.join(missing)}")
            leaked = [
                entry
                for entry in entries
                if entry.startswith(".agents/") or entry.startswith(".agent/")
            ]
            if leaked:
                errors.append("repository-local agent files leaked into package")
            packaged_manifest = json.loads(
                archive.read(".claude-plugin/plugin.json").decode("utf-8")
            )
            if packaged_manifest.get("version") != plugin_version(root):
                errors.append("packaged plugin version differs from repository")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    result = {
        "command": "package",
        "ok": not errors,
        "output": str(output),
        "size": output.stat().st_size,
        "sha256": digest,
        "entries": len(entries) if verify else len(files),
        "errors": errors,
    }
    return result, 0 if not errors else 1


def self_check(root: Path) -> tuple[dict[str, Any], int]:
    required = [
        root / ".claude-plugin/plugin.json",
        root / "README.md",
        root / "RELEASE-NOTES.md",
        root / "skills/INDEX.md",
        root / "_protocol/scripts/validate_skill.py",
        root / "_protocol/scripts/bump_version.py",
    ]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    return (
        {
            "command": "self-check",
            "ok": not missing,
            "repo_root": str(root),
            "missing": missing,
        },
        0 if not missing else 1,
    )
