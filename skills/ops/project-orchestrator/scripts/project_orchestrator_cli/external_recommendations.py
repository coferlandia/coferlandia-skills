"""Deduplicate external skill recommendations at the orchestration controller boundary."""
from __future__ import annotations

from typing import Any


def recommendation_key(value: dict[str, Any]) -> str:
    return f"{value.get('provider_id', '').strip()}:{value.get('skill_id', '').strip()}"


def dedupe_external_recommendations(
    state: dict[str, Any],
    incoming: list[dict[str, Any]] | None,
    *,
    work_item_id: str,
    role: str,
) -> list[dict[str, Any]]:
    """Return only first-seen non-optional recommendations and persist durable evidence in state."""

    seen = set(state.setdefault("external_skill_recommendations_reported", []))
    history = state.setdefault("external_skill_recommendations", [])
    emitted: list[dict[str, Any]] = []

    for raw in incoming or []:
        item = dict(raw)
        level = str(item.get("level", "recommended"))
        if level == "optional":
            continue
        key = recommendation_key(item)
        if key == ":" or key in seen:
            continue
        seen.add(key)
        item["key"] = key
        item["first_reported_by"] = role
        item["work_item_id"] = work_item_id
        history.append(item)
        emitted.append(item)

    state["external_skill_recommendations_reported"] = sorted(seen)
    return emitted
