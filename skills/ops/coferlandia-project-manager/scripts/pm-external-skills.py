#!/usr/bin/env python3
"""Read-only external Agent Skill provider resolver for Coferlandia Project Manager."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = SKILL_ROOT / "references" / "external-skill-providers.json"
CONFIG_TEMPLATE = SKILL_ROOT / "templates" / "config.template.json"

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def split_override_roots(value: str | None) -> list[Path]:
    if not value:
        return []
    return [Path(item).expanduser() for item in value.split(os.pathsep) if item.strip()]

def default_skill_roots() -> list[Path]:
    home = Path.home()
    candidates = [
        home / ".codex" / "skills",
        home / ".agents" / "skills",
        home / ".claude" / "skills",
        home / ".config" / "opencode" / "skills",
    ]
    return [path for path in candidates if path.is_dir()]

def resolve_skill_roots(cli_roots: list[str] | None) -> list[Path]:
    if cli_roots:
        candidates = [Path(item).expanduser() for item in cli_roots]
    else:
        env_roots = split_override_roots(os.environ.get("COFERLANDIA_EXTERNAL_SKILL_ROOTS"))
        candidates = env_roots if env_roots else default_skill_roots()
    seen: set[str] = set()
    result: list[Path] = []
    for path in candidates:
        resolved = str(path.resolve()) if path.exists() else str(path.absolute())
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(path)
    return result

def discover_skills(roots: list[Path]) -> tuple[set[str], dict[str, list[str]]]:
    available: set[str] = set()
    locations: dict[str, list[str]] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if not child.is_dir() or not (child / "SKILL.md").is_file():
                continue
            available.add(child.name)
            locations.setdefault(child.name, []).append(str(child))
    return available, locations

def detect_runtime(config: dict[str, Any], explicit: str) -> str:
    if explicit != "auto":
        return explicit
    configured = (
        config.get("agent_runtime", {}).get("current_runtime", "auto")
        if isinstance(config.get("agent_runtime"), dict)
        else "auto"
    )
    if configured and configured != "auto":
        return str(configured).lower()
    env_runtime = os.environ.get("COFERLANDIA_AGENT_RUNTIME", "").strip().lower()
    if env_runtime:
        return env_runtime
    env_hints = [
        ("codex", bool(os.environ.get("CODEX_HOME"))),
        ("claude", bool(os.environ.get("CLAUDE_CONFIG_DIR") or os.environ.get("CLAUDECODE"))),
        ("gemini", bool(os.environ.get("GEMINI_CLI_HOME"))),
    ]
    hinted = [name for name, present in env_hints if present]
    if len(hinted) == 1:
        return hinted[0]
    binaries = [name for name in ("codex", "claude", "gemini") if shutil.which(name)]
    if len(binaries) == 1:
        return binaries[0]
    return "unknown"

def provider_policy(provider: dict[str, Any], config: dict[str, Any]) -> dict[str, list[str]]:
    policy = {
        key: list(provider.get("default_policy", {}).get(key, []))
        for key in ("required", "recommended", "optional", "never_request")
    }
    if provider["id"] == "superpowers":
        legacy = config.get("superpowers")
        if isinstance(legacy, dict):
            policy["required"] = list(legacy.get("required_skills", policy["required"]))
            policy["optional"] = list(legacy.get("optional_skills", policy["optional"]))
    return policy

def recipe_for(provider: dict[str, Any], runtime: str) -> dict[str, Any] | None:
    recipes = provider.get("install_recipes", {})
    recipe = recipes.get(runtime)
    if recipe is None and runtime != "unknown":
        recipe = recipes.get("generic")
    return recipe

def build_provider_result(
    provider: dict[str, Any],
    config: dict[str, Any],
    runtime: str,
    roots: list[Path],
    available_skills: set[str],
    skill_locations: dict[str, list[str]],
) -> dict[str, Any]:
    policy = provider_policy(provider, config)
    tracked = set(provider.get("sentinel_skills", []))
    for names in policy.values():
        tracked.update(names)
    available = sorted(tracked & available_skills)
    required_missing = sorted(set(policy["required"]) - available_skills)
    recommended_missing = sorted(set(policy["recommended"]) - available_skills)
    optional_missing = sorted(set(policy["optional"]) - available_skills)

    identity_names = set(provider.get("sentinel_skills", []))
    identity_names.update(policy["required"])
    identity_names.update(policy["recommended"])
    identity_names.update(policy["optional"])
    identity_names.difference_update(policy["never_request"])
    provider_present = bool(identity_names & available_skills)

    if required_missing:
        status = "partial" if provider_present else "missing"
    elif policy["recommended"] and recommended_missing:
        status = "partial" if provider_present else "missing"
    else:
        status = "ok" if provider_present or not policy["required"] else "missing"

    selected_recipe = recipe_for(provider, runtime)
    install_action: dict[str, Any] | None = None
    if status != "ok" and selected_recipe:
        install_action = {
            "requires_user_approval": True,
            "execution": selected_recipe["execution"],
        }
        if "commands" in selected_recipe:
            install_action["commands"] = selected_recipe["commands"]
        if "steps" in selected_recipe:
            install_action["steps"] = selected_recipe["steps"]

    return {
        "provider_id": provider["id"],
        "display_name": provider["display_name"],
        "status": status,
        "present": provider_present,
        "repository_url": provider["repository_url"],
        "documentation_url": provider.get("documentation_url", provider["repository_url"]),
        "license": provider.get("license"),
        "tested": provider.get("tested", {}),
        "installed": {"version": None, "revision": None},
        "runtime": runtime,
        "roots": [str(path) for path in roots if path.is_dir()],
        "policy": policy,
        "skills": {
            "available": available,
            "locations": {name: skill_locations[name] for name in available if name in skill_locations},
            "required_available": sorted(set(policy["required"]) & available_skills),
            "required_missing": required_missing,
            "recommended_available": sorted(set(policy["recommended"]) & available_skills),
            "recommended_missing": recommended_missing,
            "optional_available": sorted(set(policy["optional"]) & available_skills),
            "optional_missing": optional_missing,
            "ambiguous_conflicting_names_present": sorted(
                set(policy["never_request"]) & available_skills
            ),
        },
        "install_action": install_action,
        "verification": selected_recipe.get("verification") if selected_recipe else None,
    }

def aggregate_counts(providers: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for level in ("required", "recommended", "optional"):
        total = 0
        available = 0
        for provider in providers:
            policy = provider["policy"][level]
            total += len(policy)
            available += len(provider["skills"][f"{level}_available"])
        summary[level] = {
            "available": available,
            "total": total,
            "missing": total - available,
        }
    return summary

def build_payload(config_path: Path, runtime_arg: str, roots_arg: list[str] | None) -> dict[str, Any]:
    config = load_json(config_path)
    registry = load_json(REGISTRY_PATH)
    runtime = detect_runtime(config, runtime_arg)
    roots = resolve_skill_roots(roots_arg)
    available_skills, skill_locations = discover_skills(roots)
    providers = [
        build_provider_result(provider, config, runtime, roots, available_skills, skill_locations)
        for provider in registry["providers"]
    ]
    return {
        "schema_version": registry["schema_version"],
        "status": "ok" if all(not p["skills"]["required_missing"] for p in providers) else "partial",
        "runtime": runtime,
        "roots": [str(path) for path in roots if path.is_dir()],
        "summary": aggregate_counts(providers),
        "providers": providers,
        "read_only": True,
    }

def select_provider(payload: dict[str, Any], provider_id: str) -> dict[str, Any]:
    for provider in payload["providers"]:
        if provider["provider_id"] == provider_id:
            return provider
    raise SystemExit(f"Unknown provider: {provider_id}")

def print_human(payload: dict[str, Any]) -> None:
    print("External skills:")
    print(f"- runtime: {payload['runtime']}")
    for provider in payload["providers"]:
        print(f"- {provider['display_name']}: {provider['status']}")
        print(f"  repository: {provider['repository_url']}")
        if provider["tested"]:
            tested = provider["tested"]
            print(
                "  tested: "
                f"{tested.get('version', 'unknown')} "
                f"({tested.get('revision', 'unknown')})"
            )
        missing = provider["skills"]["recommended_missing"]
        if missing:
            print(f"  recommended missing: {', '.join(missing)}")
        action = provider.get("install_action")
        if action:
            print("  install: explicit user approval required")
            for command in action.get("commands", []):
                print(f"    {command}")
            for step in action.get("steps", []):
                print(f"    {step}")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(CONFIG_TEMPLATE))
    parser.add_argument("--runtime", default="auto")
    parser.add_argument("--skill-root", action="append", dest="skill_roots")
    parser.add_argument("--provider")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_payload(Path(args.config), args.runtime.lower(), args.skill_roots)
    result: dict[str, Any] = select_provider(payload, args.provider) if args.provider else payload
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.provider:
        print(f"{result['display_name']}: {result['status']}")
        print(f"repository: {result['repository_url']}")
        print(f"runtime: {result['runtime']}")
    else:
        print_human(payload)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
