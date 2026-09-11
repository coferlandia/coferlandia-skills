#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = {"name", "description", "version", "stage", "status"}
STAGES = {"development", "qualification", "integration", "release"}
STATUSES = {"active", "deprecated"}
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter")
    try:
        block = text.split("---\n", 2)[1]
    except IndexError as exc:
        raise ValueError(f"{path}: malformed frontmatter") from exc
    data: dict[str, str] = {}
    for raw in block.splitlines():
        if not raw.strip():
            continue
        if ":" not in raw:
            raise ValueError(f"{path}: unsupported frontmatter line: {raw}")
        key, value = raw.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key.strip()] = value
    missing = REQUIRED - data.keys()
    if missing:
        raise ValueError(f"{path}: missing frontmatter keys: {sorted(missing)}")
    return data


def load_registry(root: Path) -> dict:
    path = root / "prompts" / "registry.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("registry schema_version must be 1")
    prompts = data.get("prompts")
    if not isinstance(prompts, list) or not prompts:
        raise ValueError("registry prompts must be a non-empty list")
    aliases: dict[str, tuple[str, str]] = {}
    for item in prompts:
        for key in ("id", "path", "stage", "aliases"):
            if key not in item:
                raise ValueError(f"registry prompt missing {key}")
        if item["stage"] not in STAGES:
            raise ValueError(f"invalid stage: {item['stage']}")
        for alias in item["aliases"]:
            normalized = normalize_alias(alias)
            if normalized in aliases:
                raise ValueError(f"duplicate alias: {alias}")
            aliases[normalized] = ("prompt", item["id"])
    for item in data.get("external_aliases", []):
        normalized = normalize_alias(item["alias"])
        if normalized in aliases:
            raise ValueError(f"duplicate alias: {item['alias']}")
        aliases[normalized] = (item["kind"], item["target"])
    composition = data.get("composition", {})
    if composition.get("order") != "left-to-right":
        raise ValueError("composition order must be left-to-right")
    if composition.get("implicit_stages") is not False:
        raise ValueError("implicit stages must be disabled")
    if composition.get("automatic_fallback") is not False:
        raise ValueError("automatic fallback must be disabled")
    return data


def normalize_alias(value: str) -> str:
    return " ".join(value.strip().lower().split())


def validate(root: Path) -> dict:
    registry = load_registry(root)
    errors: list[str] = []
    seen_ids: set[str] = set()
    for item in registry["prompts"]:
        prompt_id = item["id"]
        if prompt_id in seen_ids:
            errors.append(f"duplicate prompt id: {prompt_id}")
            continue
        seen_ids.add(prompt_id)
        path = root / item["path"]
        if not path.is_file():
            errors.append(f"missing prompt: {item['path']}")
            continue
        try:
            meta = parse_frontmatter(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if meta["name"] != prompt_id:
            errors.append(f"{item['path']}: name does not match registry id")
        if path.stem != prompt_id:
            errors.append(f"{item['path']}: filename does not match prompt id")
        if meta["stage"] != item["stage"]:
            errors.append(f"{item['path']}: stage does not match registry")
        if meta["stage"] not in STAGES:
            errors.append(f"{item['path']}: invalid stage")
        if meta["status"] not in STATUSES:
            errors.append(f"{item['path']}: invalid status")
        if not VERSION_RE.match(meta["version"]):
            errors.append(f"{item['path']}: version must be MAJOR.MINOR.PATCH")
        if len(meta["description"]) < 20:
            errors.append(f"{item['path']}: description too short")
    return {"ok": not errors, "errors": errors, "prompt_count": len(registry["prompts"])}


def resolve(root: Path, expression: str) -> dict:
    registry = load_registry(root)
    table: dict[str, dict] = {}
    for item in registry["prompts"]:
        for alias in item["aliases"]:
            table[normalize_alias(alias)] = {"kind": "prompt", "target": item["id"]}
    for item in registry.get("external_aliases", []):
        table[normalize_alias(item["alias"])] = {"kind": item["kind"], "target": item["target"]}
    sep = registry["composition"]["separator"]
    parts = [normalize_alias(part) for part in expression.split(sep)]
    if any(not part for part in parts):
        raise ValueError("empty stage in composition")
    sequence = []
    for part in parts:
        target = table.get(part)
        if target is None:
            raise ValueError(f"unknown delivery alias: {part}")
        sequence.append({"alias": part, **target})
    return {"ok": True, "sequence": sequence}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and resolve Coferlandia Chat prompts")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_p = sub.add_parser("validate")
    validate_p.add_argument("--root", default=".")
    validate_p.add_argument("--json", action="store_true")
    resolve_p = sub.add_parser("resolve")
    resolve_p.add_argument("expression")
    resolve_p.add_argument("--root", default=".")
    resolve_p.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            result = validate(Path(args.root).resolve())
            if args.json:
                print(json.dumps(result, sort_keys=True))
            elif result["ok"]:
                print(f"PASS: {result['prompt_count']} prompts")
            else:
                for error in result["errors"]:
                    print(f"ERROR: {error}", file=sys.stderr)
            return 0 if result["ok"] else 1
        result = resolve(Path(args.root).resolve(), args.expression)
        print(json.dumps(result, sort_keys=True) if args.json else " -> ".join(item["target"] for item in result["sequence"]))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {"ok": False, "error": str(exc)}
        if getattr(args, "json", False):
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
