#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Manage the repo-wide plugin version for coferlandia-skills.

The plugin release version is independent from each public skill's
`metadata.version`. Declared manifest fields live in `.version-bump.json`.

Commands:
  python _protocol/scripts/bump_version.py --check
  python _protocol/scripts/bump_version.py --audit
  python _protocol/scripts/bump_version.py X.Y.Z

Output is JSON on stdout, diagnostics on stderr, and exit code 1 on drift/failure.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(root: Path) -> dict[str, Any]:
    path = root / ".version-bump.json"
    if not path.is_file():
        print(f"error: .version-bump.json not found at {path}", file=sys.stderr)
        raise SystemExit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def get_field(data: Any, field: str) -> Any:
    node = data
    for part in field.split("."):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def set_field(data: Any, field: str, value: str) -> None:
    parts = field.split(".")
    node = data
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    last = parts[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value


def read_versions(
    root: Path, files: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    for entry in files:
        path, field = entry["path"], entry["field"]
        full = root / path
        if not full.is_file():
            rows.append(
                {"path": path, "field": field, "version": None, "missing": True}
            )
            errors.append(f"Missing declared file: {path}")
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
            version = get_field(data, field)
        except Exception as error:  # noqa: BLE001 - report malformed declared files
            rows.append(
                {"path": path, "field": field, "version": None, "missing": True}
            )
            errors.append(f"Could not read {field} from {path}: {error}")
            continue
        rows.append(
            {"path": path, "field": field, "version": version, "missing": False}
        )
    return rows, errors


def print_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        tag = "MISSING" if row["missing"] else row["version"]
        print(f"  {row['path']} ({row['field']}): {tag}", file=sys.stderr)


def cmd_check(root: Path, config: dict[str, Any]) -> int:
    rows, errors = read_versions(root, config["files"])
    versions = {row["version"] for row in rows if not row["missing"]}
    drift = len(versions) > 1
    result = {
        "command": "check",
        "files": rows,
        "drift": drift,
        "errors": errors,
        "current_version": next(iter(versions)) if len(versions) == 1 else None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print_rows(rows)
    if drift:
        print("DRIFT DETECTED - declared files do not agree on a version.", file=sys.stderr)
    elif not errors:
        print(
            f"All declared files are in sync at {result['current_version']}.",
            file=sys.stderr,
        )
    return 1 if drift or errors else 0


def is_excluded(relative: str, exclusions: set[str]) -> bool:
    return any(
        relative == excluded or relative.startswith(excluded.rstrip("/") + "/")
        for excluded in exclusions
    )


def audit_files(root: Path, exclusions: set[str]) -> Iterable[Path]:
    """Yield candidate files without descending into excluded directories."""
    for current, directories, filenames in os.walk(root):
        current_path = Path(current)
        relative_dir = current_path.relative_to(root).as_posix()
        if relative_dir == ".":
            relative_dir = ""

        kept: list[str] = []
        for directory in directories:
            relative = f"{relative_dir}/{directory}".strip("/")
            if not is_excluded(relative, exclusions):
                kept.append(directory)
        directories[:] = kept

        for filename in filenames:
            path = current_path / filename
            relative = path.relative_to(root).as_posix()
            if not is_excluded(relative, exclusions):
                yield path


def cmd_audit(root: Path, config: dict[str, Any]) -> int:
    rows, errors = read_versions(root, config["files"])
    versions = [row["version"] for row in rows if not row["missing"]]
    if not versions:
        print(
            json.dumps(
                {"command": "audit", "error": "no readable version found"}, indent=2
            )
        )
        print("error: could not determine current version", file=sys.stderr)
        return 1

    current_version = max(set(versions), key=versions.count)
    declared = {entry["path"] for entry in config["files"]}
    exclusions = set(config.get("audit", {}).get("exclude", [])) | {".git"}
    undeclared: list[str] = []

    for path in audit_files(root, exclusions):
        relative = path.relative_to(root).as_posix()
        if relative in declared:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if current_version in text:
            undeclared.append(relative)

    undeclared.sort()
    result = {
        "command": "audit",
        "current_version": current_version,
        "drift": len(set(versions)) > 1,
        "undeclared_files_with_version_string": undeclared,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if undeclared:
        print("UNDECLARED files containing the current version string:", file=sys.stderr)
        for path in undeclared:
            print(f"  {path}", file=sys.stderr)
        print(
            "Add version-bearing files to .version-bump.json or exclude intentional references.",
            file=sys.stderr,
        )
    else:
        print("No undeclared files contain the version string. All clear.", file=sys.stderr)
    return 1 if undeclared or errors or len(set(versions)) > 1 else 0


def cmd_bump(root: Path, config: dict[str, Any], new_version: str) -> int:
    if not SEMVER_RE.fullmatch(new_version):
        print(
            f"error: '{new_version}' doesn't look like a version (expected X.Y.Z)",
            file=sys.stderr,
        )
        return 1

    updates: list[dict[str, Any]] = []
    for entry in config["files"]:
        path, field = entry["path"], entry["field"]
        full = root / path
        if not full.is_file():
            updates.append(
                {"path": path, "field": field, "status": "skipped-missing"}
            )
            continue
        data = json.loads(full.read_text(encoding="utf-8"))
        previous = get_field(data, field)
        set_field(data, field, new_version)
        full.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        updates.append(
            {"path": path, "field": field, "from": previous, "to": new_version}
        )

    print(
        json.dumps(
            {"command": "bump", "new_version": new_version, "updates": updates},
            indent=2,
            ensure_ascii=False,
        )
    )
    for update in updates:
        if update.get("status") == "skipped-missing":
            print(f"  SKIP (missing): {update['path']}", file=sys.stderr)
        else:
            print(
                f"  {update['path']} ({update['field']}): "
                f"{update['from']} -> {update['to']}",
                file=sys.stderr,
            )
    print("\nDon't forget: add a RELEASE-NOTES.md entry.", file=sys.stderr)
    return cmd_audit(root, config)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the repo-wide plugin version for coferlandia-skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--check", action="store_true")
    commands.add_argument("--audit", action="store_true")
    commands.add_argument("new_version", nargs="?", default=None)
    arguments = parser.parse_args()

    root = repo_root()
    config = load_config(root)
    if arguments.check:
        return cmd_check(root, config)
    if arguments.audit:
        return cmd_audit(root, config)
    if arguments.new_version:
        return cmd_bump(root, config, arguments.new_version)
    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
