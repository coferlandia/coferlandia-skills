from __future__ import annotations
import copy
import json
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "schema_version": 1,
    "versioning": {"scheme": "semver", "tag_prefix": "v"},
    "release_refs": [],
    "tag": {"type": "annotated", "signing": "optional"},
    "validation": {"required_github_checks": []},
    "github_release": {"enabled": True, "immutability": "observe"},
    "provenance": {"manifest": "optional"},
}

def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result

def validate_policy(policy: dict[str, Any]) -> dict[str, Any]:
    if policy.get("schema_version") != 1:
        raise ValueError("unsupported release policy schema_version")
    if policy.get("versioning", {}).get("scheme") != "semver":
        raise ValueError("generic release publisher v1 supports only semver")
    prefix = policy["versioning"].get("tag_prefix")
    if not isinstance(prefix, str):
        raise ValueError("versioning.tag_prefix must be a string")
    refs = policy.get("release_refs")
    if not isinstance(refs, list) or not all(isinstance(item, str) and item for item in refs):
        raise ValueError("release_refs must be a list of non-empty strings")
    tag = policy.get("tag", {})
    if tag.get("type") != "annotated":
        raise ValueError("release tags must be annotated")
    if tag.get("signing") not in {"optional", "required", "disabled"}:
        raise ValueError("tag.signing must be optional, required, or disabled")
    checks = policy.get("validation", {}).get("required_github_checks")
    if not isinstance(checks, list) or not all(isinstance(item, str) and item for item in checks):
        raise ValueError("validation.required_github_checks must be a list of names")
    if len(checks) != len(set(checks)):
        raise ValueError("validation.required_github_checks contains duplicates")
    gh = policy.get("github_release", {})
    if gh.get("enabled") is not True:
        raise ValueError("generic release publisher v1 requires GitHub Releases")
    if gh.get("immutability") not in {"observe", "required", "disabled"}:
        raise ValueError("github_release.immutability must be observe, required, or disabled")
    if policy.get("provenance", {}).get("manifest") not in {"optional", "required", "disabled"}:
        raise ValueError("provenance.manifest must be optional, required, or disabled")
    return policy

def load_policy(root: Path, explicit: Path | None = None) -> dict[str, Any]:
    path = explicit if explicit is not None else root / ".coferlandia/release/policy.json"
    if not path.is_file():
        return copy.deepcopy(DEFAULT_POLICY)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid release policy JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("release policy must be a JSON object")
    return validate_policy(_merge(DEFAULT_POLICY, raw))
