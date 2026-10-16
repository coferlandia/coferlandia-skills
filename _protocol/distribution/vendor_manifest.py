#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

HEX40_RE = re.compile(r"^[0-9a-f]{40}$")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def manifest_fingerprint(manifest: dict[str, Any]) -> str:
    payload = dict(manifest)
    payload.pop("manifest_fingerprint", None)
    return _sha256_bytes(_canonical_bytes(payload))


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        (path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts),
        key=lambda path: path.as_posix(),
    )


def _entry(family: str, source_path: str, consumer_path: str, data: bytes) -> dict[str, str]:
    return {
        "family": family,
        "source_path": source_path,
        "consumer_path": consumer_path,
        "sha256": _sha256_bytes(data),
    }


def build_manifest(root: Path, *, release_version: str, source_revision: str) -> dict[str, Any]:
    root = root.resolve()
    if not HEX40_RE.fullmatch(source_revision):
        raise ValueError("source_revision must be a lowercase 40-character Git SHA")

    entries: list[dict[str, str]] = []

    prompts = root / "prompts"
    for path in _iter_files(prompts):
        rel = path.relative_to(prompts).as_posix()
        entries.append(_entry("prompts", f"prompts/{rel}", f".agents/prompts/{rel}", path.read_bytes()))

    delivery = root / "_protocol" / "delivery"
    for path in _iter_files(delivery):
        rel = path.relative_to(delivery).as_posix()
        entries.append(_entry("delivery", f"_protocol/delivery/{rel}", f"_protocol/delivery/{rel}", path.read_bytes()))

    skills = root / "skills"
    if skills.exists():
        for category in sorted(path for path in skills.iterdir() if path.is_dir()):
            for skill in sorted(path for path in category.iterdir() if path.is_dir()):
                family = f"skill:{skill.name}"
                for path in _iter_files(skill):
                    rel = path.relative_to(skill).as_posix()
                    source = path.relative_to(root).as_posix()
                    consumer = f".agents/skills/{skill.name}/{rel}"
                    entries.append(_entry(family, source, consumer, path.read_bytes()))

    entries.sort(key=lambda item: (item["family"], item["consumer_path"], item["source_path"]))
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "source_repository": "coferlandia/coferlandia-skills",
        "source_release_version": release_version,
        "source_revision": source_revision,
        "entries": entries,
    }
    manifest["manifest_fingerprint"] = manifest_fingerprint(manifest)
    return manifest


def check_consumer(root: Path, manifest: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    missing: list[str] = []
    modified: list[str] = []

    for key in ("source_repository", "source_release_version", "source_revision"):
        if provenance.get(key) != manifest.get(key):
            errors.append(key)

    expected_fingerprint = manifest_fingerprint(manifest)
    if manifest.get("manifest_fingerprint") != expected_fingerprint:
        errors.append("manifest_fingerprint")
    declared_manifest_fingerprint = provenance.get("manifest_fingerprint")
    if declared_manifest_fingerprint is not None and declared_manifest_fingerprint != expected_fingerprint:
        errors.append("provenance_manifest_fingerprint")

    families = provenance.get("families")
    if not isinstance(families, list) or not families or not all(isinstance(item, str) and item for item in families):
        errors.append("families")
        families = []

    available_families = {entry.get("family") for entry in manifest.get("entries", [])}
    for family in families:
        if family not in available_families:
            errors.append(f"family:{family}")

    selected = [entry for entry in manifest.get("entries", []) if entry.get("family") in set(families)]
    for entry in selected:
        consumer_path = entry["consumer_path"]
        path = root / consumer_path
        if not path.is_file():
            missing.append(consumer_path)
            continue
        if _sha256_bytes(path.read_bytes()) != entry["sha256"]:
            modified.append(consumer_path)

    result = {
        "status": "ok" if not errors and not missing and not modified else "error",
        "provenance_errors": sorted(set(errors)),
        "missing": sorted(missing),
        "modified": sorted(modified),
        "checked": len(selected),
    }
    return result


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _cmd_generate(args: argparse.Namespace) -> int:
    manifest = build_manifest(Path(args.root), release_version=args.release_version, source_revision=args.source_revision)
    _write_json(Path(args.output), manifest)
    print(json.dumps({"status": "ok", "output": args.output, "entries": len(manifest["entries"]), "manifest_fingerprint": manifest["manifest_fingerprint"]}))
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    result = check_consumer(Path(args.root), _load_json(Path(args.manifest)), _load_json(Path(args.provenance)))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "ok" else 1


def _cmd_check_source(args: argparse.Namespace) -> int:
    manifest = _load_json(Path(args.manifest))
    rebuilt = build_manifest(
        Path(args.root),
        release_version=str(manifest.get("source_release_version")),
        source_revision=str(manifest.get("source_revision")),
    )
    same = rebuilt == manifest
    result = {
        "status": "ok" if same else "error",
        "expected_fingerprint": manifest.get("manifest_fingerprint"),
        "actual_fingerprint": rebuilt.get("manifest_fingerprint"),
        "entries": len(rebuilt["entries"]),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if same else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and verify Coferlandia public vendor manifests.")
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate")
    generate.add_argument("--root", required=True)
    generate.add_argument("--release-version", required=True)
    generate.add_argument("--source-revision", required=True)
    generate.add_argument("--output", required=True)

    check = sub.add_parser("check")
    check.add_argument("--root", required=True)
    check.add_argument("--manifest", required=True)
    check.add_argument("--provenance", required=True)

    source = sub.add_parser("check-source")
    source.add_argument("--root", required=True)
    source.add_argument("--manifest", required=True)

    args = parser.parse_args()
    if args.command == "generate":
        return _cmd_generate(args)
    if args.command == "check":
        return _cmd_check(args)
    return _cmd_check_source(args)


if __name__ == "__main__":
    raise SystemExit(main())
