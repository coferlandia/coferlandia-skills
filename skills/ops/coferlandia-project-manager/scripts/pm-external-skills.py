#!/usr/bin/env python3
"""Read-only external Agent Skill provider resolver for Coferlandia Project Manager."""

from __future__ import annotations

import argparse
import json
import os
import re
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


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    result: list[Path] = []
    for path in paths:
        try:
            resolved = str(path.resolve())
        except OSError:
            resolved = str(path.absolute())
        if resolved in seen:
            continue
        seen.add(resolved)
        result.append(path)
    return result


def default_skill_roots() -> list[Path]:
    home = Path.home()
    cwd = Path.cwd()
    candidates = [
        cwd / ".codex" / "skills",
        cwd / ".agents" / "skills",
        cwd / ".claude" / "skills",
        home / ".codex" / "skills",
        home / ".agents" / "skills",
        home / ".claude" / "skills",
        home / ".config" / "opencode" / "skills",
    ]
    return [path for path in _dedupe_paths(candidates) if path.is_dir()]


def default_provider_roots() -> list[Path]:
    """Roots that can contain provider/plugin manifests.

    Codex installs cached plugins below ~/.codex/plugins/cache/<marketplace>/<plugin>/<version>/.
    Repo/personal marketplaces may also point at arbitrary plugin folders, so callers can extend
    discovery with --provider-root or COFERLANDIA_EXTERNAL_PROVIDER_ROOTS.
    """

    home = Path.home()
    cwd = Path.cwd()
    candidates = [
        cwd / "plugins",
        cwd / ".codex" / "plugins",
        cwd / ".claude" / "plugins",
        home / ".codex" / "plugins",
        home / ".claude" / "plugins",
    ]
    return [path for path in _dedupe_paths(candidates) if path.is_dir()]


def resolve_roots(
    cli_roots: list[str] | None,
    env_name: str,
    defaults: list[Path],
) -> list[Path]:
    if cli_roots:
        candidates = [Path(item).expanduser() for item in cli_roots]
    else:
        env_roots = split_override_roots(os.environ.get(env_name))
        candidates = env_roots if env_roots else defaults
    return _dedupe_paths(candidates)


def discover_flat_skills(roots: list[Path]) -> dict[str, list[str]]:
    locations: dict[str, list[str]] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for child in root.iterdir():
            if not child.is_dir() or not (child / "SKILL.md").is_file():
                continue
            locations.setdefault(child.name, []).append(str(child))
    return locations


def _manifest_plugin_root(manifest: Path) -> Path:
    if manifest.parent.name in {".codex-plugin", ".claude-plugin"}:
        return manifest.parent.parent
    return manifest.parent


def _manifest_repository(payload: dict[str, Any]) -> str | None:
    value = payload.get("repository")
    if isinstance(value, str):
        return value.rstrip("/")
    if isinstance(value, dict):
        url = value.get("url")
        return str(url).rstrip("/") if url else None
    homepage = payload.get("homepage")
    return str(homepage).rstrip("/") if homepage else None


def _normalize_repository(value: str | None) -> str | None:
    if not value:
        return None
    result = value.strip().rstrip("/")
    if result.endswith(".git"):
        result = result[:-4]
    return result.lower()


def _read_git_revision(plugin_root: Path) -> str | None:
    """Read a local Git HEAD without invoking Git or mutating the provider."""

    git = plugin_root / ".git"
    if git.is_file():
        try:
            text = git.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if text.startswith("gitdir:"):
            git = (plugin_root / text.split(":", 1)[1].strip()).resolve()
    head = git / "HEAD"
    if not head.is_file():
        return None
    try:
        value = head.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not value.startswith("ref:"):
        return value or None
    ref = value.split(":", 1)[1].strip()
    ref_file = git / ref
    if ref_file.is_file():
        try:
            return ref_file.read_text(encoding="utf-8").strip() or None
        except OSError:
            return None
    packed = git / "packed-refs"
    if packed.is_file():
        try:
            for line in packed.read_text(encoding="utf-8").splitlines():
                if line.startswith("#") or line.startswith("^") or " " not in line:
                    continue
                revision, name = line.split(" ", 1)
                if name.strip() == ref:
                    return revision.strip()
        except OSError:
            pass
    return None


def _skill_root_from_manifest(plugin_root: Path, payload: dict[str, Any]) -> Path:
    raw = payload.get("skills", "./skills")
    if isinstance(raw, list):
        raw = raw[0] if raw else "./skills"
    if not isinstance(raw, str):
        raw = "./skills"
    return (plugin_root / raw).resolve()


def discover_provider_instances(provider_roots: list[Path]) -> list[dict[str, Any]]:
    """Discover plugin instances with provenance-preserving manifests."""

    manifests: list[Path] = []
    seen: set[str] = set()
    for root in provider_roots:
        if not root.is_dir():
            continue
        patterns = ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json")
        for pattern in patterns:
            for manifest in root.rglob(pattern):
                if not manifest.is_file():
                    continue
                key = str(manifest.resolve())
                if key in seen:
                    continue
                seen.add(key)
                manifests.append(manifest)

    instances: list[dict[str, Any]] = []
    for manifest in sorted(manifests):
        try:
            payload = load_json(manifest)
        except (OSError, json.JSONDecodeError):
            continue
        name = payload.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        plugin_root = _manifest_plugin_root(manifest)
        skill_root = _skill_root_from_manifest(plugin_root, payload)
        skill_names: list[str] = []
        if skill_root.is_dir():
            for child in skill_root.iterdir():
                if child.is_dir() and (child / "SKILL.md").is_file():
                    skill_names.append(child.name)
        instances.append(
            {
                "name": name.strip(),
                "repository": _manifest_repository(payload),
                "version": str(payload.get("version")) if payload.get("version") is not None else None,
                "revision": _read_git_revision(plugin_root),
                "manifest": str(manifest),
                "plugin_root": str(plugin_root),
                "skill_root": str(skill_root),
                "skills": sorted(skill_names),
            }
        )
    return instances


def provider_matches_instance(provider: dict[str, Any], instance: dict[str, Any]) -> bool:
    identity = provider.get("manifest_identity", {})
    names = {str(name).lower() for name in identity.get("names", [])}
    repositories = {
        normalized
        for value in identity.get("repositories", [])
        if (normalized := _normalize_repository(str(value)))
    }
    if names and str(instance.get("name", "")).lower() not in names:
        return False
    instance_repo = _normalize_repository(instance.get("repository"))
    if repositories:
        if instance_repo is None or instance_repo not in repositories:
            return False
    return bool(names or repositories)


def _version_tuple(value: str | None) -> tuple[int, ...] | None:
    if not value:
        return None
    match = re.match(r"^v?(\d+(?:\.\d+)*)", value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def compatibility_relation(installed: str | None, tested: str | None) -> str:
    left = _version_tuple(installed)
    right = _version_tuple(tested)
    if left is None or right is None:
        return "unknown"
    width = max(len(left), len(right))
    left += (0,) * (width - len(left))
    right += (0,) * (width - len(right))
    if left == right:
        return "same-as-tested"
    return "newer-than-tested" if left > right else "older-than-tested"


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
    return recipes.get(runtime) or recipes.get("generic")


def build_provider_result(
    provider: dict[str, Any],
    config: dict[str, Any],
    runtime: str,
    flat_locations: dict[str, list[str]],
    instances: list[dict[str, Any]],
) -> dict[str, Any]:
    policy = provider_policy(provider, config)
    matching_instances = [item for item in instances if provider_matches_instance(provider, item)]
    verified_skills = {
        skill
        for instance in matching_instances
        for skill in instance.get("skills", [])
    }

    tracked: set[str] = set(provider.get("sentinel_skills", []))
    for names in policy.values():
        tracked.update(names)
    flat_matches = sorted(tracked & set(flat_locations))

    presence = "verified" if matching_instances else "missing"
    available_skills = set(verified_skills)

    legacy_available: set[str] = set()
    if not matching_instances and provider.get("allow_legacy_flat_detection"):
        legacy_names = set(policy["required"]) | set(policy["optional"]) | set(provider.get("sentinel_skills", []))
        legacy_available = legacy_names & set(flat_locations)
        if legacy_available:
            presence = "legacy-flat-unverified"
            available_skills.update(legacy_available)

    discovery_roots = {
        str(Path(instance["skill_root"]))
        for instance in matching_instances
        if instance.get("skill_root")
    }
    if presence == "legacy-flat-unverified":
        for name in legacy_available:
            for location in flat_locations.get(name, []):
                discovery_roots.add(str(Path(location).parent))

    unverified_matches = sorted((tracked & set(flat_locations)) - available_skills)
    required_missing = sorted(set(policy["required"]) - available_skills)
    recommended_missing = sorted(set(policy["recommended"]) - available_skills)
    optional_missing = sorted(set(policy["optional"]) - available_skills)

    provider_present = presence != "missing"
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
            "scope": "provider",
            "execution": selected_recipe["execution"],
        }
        if policy["never_request"]:
            install_action["warnings"] = [
                "Provider installation also exposes lifecycle skills that Coferlandia "
                "will never auto-request: " + ", ".join(sorted(policy["never_request"]))
            ]
        if "commands" in selected_recipe:
            install_action["commands"] = selected_recipe["commands"]
        if "steps" in selected_recipe:
            install_action["steps"] = selected_recipe["steps"]

    primary = matching_instances[0] if matching_instances else None
    tested = provider.get("tested", {})
    installed_version = primary.get("version") if primary else None
    installed_revision = primary.get("revision") if primary else None

    return {
        "provider_id": provider["id"],
        "display_name": provider["display_name"],
        "status": status,
        "present": provider_present,
        "presence": presence,
        "repository_url": provider["repository_url"],
        "documentation_url": provider.get("documentation_url", provider["repository_url"]),
        "license": provider.get("license"),
        "tested": tested,
        "installed": {
            "version": installed_version,
            "revision": installed_revision,
            "compatibility": compatibility_relation(installed_version, tested.get("version")),
        },
        "instances": matching_instances,
        "roots": sorted(discovery_roots),
        "runtime": runtime,
        "policy": policy,
        "skills": {
            "available": sorted(available_skills & tracked),
            "locations": {
                name: flat_locations.get(name, [])
                for name in sorted(available_skills & set(flat_locations))
            },
            "required_available": sorted(set(policy["required"]) & available_skills),
            "required_missing": required_missing,
            "recommended_available": sorted(set(policy["recommended"]) & available_skills),
            "recommended_missing": recommended_missing,
            "optional_available": sorted(set(policy["optional"]) & available_skills),
            "optional_missing": optional_missing,
            "unverified_name_matches": unverified_matches,
            "ambiguous_conflicting_names_present": sorted(
                set(policy["never_request"]) & set(flat_locations)
            ),
        },
        "install_action": install_action,
        "verification": selected_recipe.get("verification") if selected_recipe else None,
        "verify_action": {
            "kind": "rerun-provider-resolution",
            "provider_id": provider["id"],
        },
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


def build_payload(
    config_path: Path,
    runtime_arg: str,
    skill_roots_arg: list[str] | None,
    provider_roots_arg: list[str] | None,
) -> dict[str, Any]:
    config = load_json(config_path)
    registry = load_json(REGISTRY_PATH)
    runtime = detect_runtime(config, runtime_arg)
    skill_roots = resolve_roots(
        skill_roots_arg,
        "COFERLANDIA_EXTERNAL_SKILL_ROOTS",
        default_skill_roots(),
    )
    provider_roots = resolve_roots(
        provider_roots_arg,
        "COFERLANDIA_EXTERNAL_PROVIDER_ROOTS",
        default_provider_roots(),
    )
    flat_locations = discover_flat_skills(skill_roots)
    instances = discover_provider_instances(provider_roots)
    providers = [
        build_provider_result(provider, config, runtime, flat_locations, instances)
        for provider in registry["providers"]
    ]
    return {
        "schema_version": registry["schema_version"],
        "status": "ok" if all(not p["skills"]["required_missing"] for p in providers) else "partial",
        "runtime": runtime,
        "skill_roots": [str(path) for path in skill_roots if path.is_dir()],
        "provider_roots": [str(path) for path in provider_roots if path.is_dir()],
        "summary": aggregate_counts(providers),
        "providers": providers,
        "unowned_skill_names": sorted(flat_locations),
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
        print(f"- {provider['display_name']}: {provider['status']} ({provider['presence']})")
        print(f"  repository: {provider['repository_url']}")
        installed = provider.get("installed", {})
        if installed.get("version"):
            print(
                "  installed: "
                f"{installed['version']} ({installed.get('compatibility', 'unknown')})"
            )
        if provider["tested"]:
            tested = provider["tested"]
            print(
                "  tested: "
                f"{tested.get('version', 'unknown')} "
                f"({tested.get('revision', 'unknown')})"
            )
        unverified = provider["skills"]["unverified_name_matches"]
        if unverified:
            print(f"  unverified name matches: {', '.join(unverified)}")
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
            for warning in action.get("warnings", []):
                print(f"    warning: {warning}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(CONFIG_TEMPLATE))
    parser.add_argument("--runtime", default="auto")
    parser.add_argument("--skill-root", action="append", dest="skill_roots")
    parser.add_argument("--provider-root", action="append", dest="provider_roots")
    parser.add_argument("--provider")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_payload(
        Path(args.config),
        args.runtime.lower(),
        args.skill_roots,
        args.provider_roots,
    )
    result: dict[str, Any] = select_provider(payload, args.provider) if args.provider else payload
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.provider:
        print(f"{result['display_name']}: {result['status']} ({result['presence']})")
        print(f"repository: {result['repository_url']}")
        print(f"runtime: {result['runtime']}")
    else:
        print_human(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
