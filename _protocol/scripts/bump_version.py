#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Manage the repo-wide plugin version for coferlandia-skills.

This tracks ONE release version for the plugin as a whole (declared in
.version-bump.json), separate from each skill's own `metadata.version` in its
SKILL.md frontmatter (see _protocol/NAMING_CONVENTIONS.md) — that one tracks a
single skill's instruction changes, this one tracks plugin releases.

Checks, per declared file:
  - the field exists and is readable
  - all declared files agree on the same version (drift detection)

--audit additionally greps the whole repo for the current version string and
flags any file NOT declared in .version-bump.json that still contains it, so a
missed manifest doesn't silently fall out of sync.

Output: JSON to stdout (parseable by an agent). Diagnostics to stderr.
Exit code: 0 on success, 1 on drift/failure.

Usage:
  python bump_version.py --check
  python bump_version.py --audit
  python bump_version.py <new-version>
  python bump_version.py --help

Examples:
  python _protocol/scripts/bump_version.py --check
  python _protocol/scripts/bump_version.py --audit
  python _protocol/scripts/bump_version.py 1.1.0
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config(root: Path) -> dict:
    config_path = root / ".version-bump.json"
    if not config_path.is_file():
        print(f"error: .version-bump.json not found at {config_path}", file=sys.stderr)
        raise SystemExit(1)
    return json.loads(config_path.read_text(encoding="utf-8"))


def get_field(data: Any, field: str) -> Any:
    node = data
    for part in field.split("."):
        if isinstance(node, list):
            node = node[int(part)]
        else:
            node = node[part]
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


def read_versions(root: Path, files: list[dict]) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    errors: list[str] = []
    for entry in files:
        path, field = entry["path"], entry["field"]
        full = root / path
        if not full.is_file():
            rows.append({"path": path, "field": field, "version": None, "missing": True})
            errors.append(f"Missing declared file: {path}")
            continue
        try:
            data = json.loads(full.read_text(encoding="utf-8"))
            version = get_field(data, field)
        except Exception as exc:  # noqa: BLE001 - surface any parse/lookup failure
            rows.append({"path": path, "field": field, "version": None, "missing": True})
            errors.append(f"Could not read {field} from {path}: {exc}")
            continue
        rows.append({"path": path, "field": field, "version": version, "missing": False})
    return rows, errors


def cmd_check(root: Path, config: dict) -> int:
    rows, errors = read_versions(root, config["files"])
    versions = {r["version"] for r in rows if not r["missing"]}
    drift = len(versions) > 1
    result = {
        "command": "check",
        "files": rows,
        "drift": drift,
        "errors": errors,
        "current_version": next(iter(versions)) if len(versions) == 1 else None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    for r in rows:
        tag = "MISSING" if r["missing"] else r["version"]
        print(f"  {r['path']} ({r['field']}): {tag}", file=sys.stderr)
    if drift:
        print("DRIFT DETECTED - declared files do not agree on a version.", file=sys.stderr)
    elif not errors:
        print(f"All declared files are in sync at {result['current_version']}.", file=sys.stderr)
    return 1 if (drift or errors) else 0


def cmd_audit(root: Path, config: dict) -> int:
    rows, errors = read_versions(root, config["files"])
    versions = [r["version"] for r in rows if not r["missing"]]
    if not versions:
        print(json.dumps({"command": "audit", "error": "no readable version found"}, indent=2))
        print("error: could not determine current version", file=sys.stderr)
        return 1
    current_version = max(set(versions), key=versions.count)

    declared_paths = {entry["path"] for entry in config["files"]}
    exclude = set(config.get("audit", {}).get("exclude", [])) | {".git"}

    undeclared: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(rel == ex or rel.startswith(ex.rstrip("/") + "/") for ex in exclude):
            continue
        if rel in declared_paths:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if current_version in text:
            undeclared.append(rel)

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
        for f in undeclared:
            print(f"  {f}", file=sys.stderr)
        print(
            "Review these - add them to .version-bump.json if they should be bumped, "
            "or to audit.exclude if they should be skipped.",
            file=sys.stderr,
        )
    else:
        print("No undeclared files contain the version string. All clear.", file=sys.stderr)
    return 1 if undeclared else 0


def cmd_bump(root: Path, config: dict, new_version: str) -> int:
    if not SEMVER_RE.match(new_version):
        print(f"error: '{new_version}' doesn't look like a version (expected X.Y.Z)", file=sys.stderr)
        return 1

    updates: list[dict] = []
    for entry in config["files"]:
        path, field = entry["path"], entry["field"]
        full = root / path
        if not full.is_file():
            updates.append({"path": path, "field": field, "status": "skipped-missing"})
            continue
        data = json.loads(full.read_text(encoding="utf-8"))
        old_version = get_field(data, field)
        set_field(data, field, new_version)
        full.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        updates.append({"path": path, "field": field, "from": old_version, "to": new_version})

    result = {"command": "bump", "new_version": new_version, "updates": updates}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    for u in updates:
        if u.get("status") == "skipped-missing":
            print(f"  SKIP (missing): {u['path']}", file=sys.stderr)
        else:
            print(f"  {u['path']} ({u['field']}): {u['from']} -> {u['to']}", file=sys.stderr)
    print("\nDon't forget: add a RELEASE-NOTES.md entry for this version.", file=sys.stderr)
    return cmd_audit(root, config)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the repo-wide plugin version for coferlandia-skills.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="Report current versions, detect drift")
    group.add_argument("--audit", action="store_true", help="Check + scan repo for undeclared version references")
    group.add_argument("new_version", nargs="?", default=None, help="Bump all declared files to this version")
    args = parser.parse_args()

    root = repo_root()
    config = load_config(root)

    if args.check:
        return cmd_check(root, config)
    if args.audit:
        return cmd_audit(root, config)
    if args.new_version:
        return cmd_bump(root, config, args.new_version)

    parser.print_help(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
