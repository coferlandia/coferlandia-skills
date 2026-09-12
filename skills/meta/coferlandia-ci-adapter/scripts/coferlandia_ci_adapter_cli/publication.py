from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_WORKFLOW_PATH = Path(".github/workflows/coferlandia-release-publish.yml")
RELEASE_POLICY_PATH = Path(".coferlandia/release/policy.json")


def _safe_repo_path(value: str, *, suffixes: tuple[str, ...] | None = None) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("repository path must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value.startswith("./"):
        raise ValueError("repository path must be relative and must not escape the repository")
    normalized = path.as_posix()
    if suffixes and not normalized.endswith(suffixes):
        raise ValueError(f"repository path must end with one of: {', '.join(suffixes)}")
    return normalized


def publication_github(policy: dict[str, Any]) -> dict[str, Any] | None:
    publication = policy.get("publication")
    if publication is None:
        return None
    if not isinstance(publication, dict):
        raise ValueError("publication must be an object")
    github = publication.get("github")
    if github is None:
        return None
    if not isinstance(github, dict):
        raise ValueError("publication.github must be an object")
    mode = github.get("mode")
    if mode == "none":
        if set(github) != {"mode"}:
            raise ValueError("publication.github mode=none accepts no additional fields")
        return github
    if mode != "workflow-dispatch":
        raise ValueError("publication.github.mode must be none or workflow-dispatch")
    if set(github) != {"mode", "workflow"}:
        raise ValueError("workflow-dispatch publication requires exactly mode and workflow")
    workflow = _safe_repo_path(str(github.get("workflow", "")), suffixes=(".yml", ".yaml"))
    if not workflow.startswith(".github/workflows/"):
        raise ValueError("publication.github.workflow must be under .github/workflows/")
    return {"mode": mode, "workflow": workflow}


def load_release_policy(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid release policy JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("release policy must be a JSON object")
    publication_github(raw)
    return raw


def render_workflow(*, publisher_path: str) -> str:
    publisher = _safe_repo_path(publisher_path, suffixes=(".py",))
    return f'''name: Coferlandia Release Publish

on:
  workflow_dispatch:
    inputs:
      target_sha:
        description: Exact integrated commit SHA to publish
        required: true
        type: string
      version:
        description: Explicit SemVer without tag prefix
        required: true
        type: string
      impact:
        description: Semantic impact approved for this release
        required: true
        type: choice
        options:
          - patch
          - minor
          - major
      title:
        description: GitHub Release title
        required: true
        type: string
      notes:
        description: Final release notes
        required: true
        type: string

permissions:
  contents: write

concurrency:
  group: coferlandia-release-${{{{ inputs.version }}}}
  cancel-in-progress: false

jobs:
  publish:
    name: Publish exact release
    runs-on: ubuntu-latest
    env:
      GH_TOKEN: ${{{{ github.token }}}}
      TARGET_SHA: ${{{{ inputs.target_sha }}}}
      VERSION: ${{{{ inputs.version }}}}
      IMPACT: ${{{{ inputs.impact }}}}
      RELEASE_TITLE: ${{{{ inputs.title }}}}
      RELEASE_NOTES: ${{{{ inputs.notes }}}}
    steps:
      - name: Validate immutable dispatch inputs
        shell: bash
        run: |
          set -euo pipefail
          [[ "$TARGET_SHA" =~ ^[0-9a-f]{{40}}$ ]]
          [[ "$VERSION" =~ ^[0-9]+\\.[0-9]+\\.[0-9]+([+-][0-9A-Za-z.-]+)?$ ]]
          case "$IMPACT" in patch|minor|major) ;; *) exit 2 ;; esac

      - name: Check out exact publication target
        uses: actions/checkout@v4
        with:
          ref: ${{{{ inputs.target_sha }}}}
          fetch-depth: 0
          persist-credentials: true

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Configure release identity
        shell: bash
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

      - name: Revalidate exact checkout
        shell: bash
        run: |
          set -euo pipefail
          test "$(git rev-parse HEAD)" = "$TARGET_SHA"
          git fetch --tags --force origin
          test "$(git rev-parse HEAD)" = "$TARGET_SHA"

      - name: Materialize release notes safely
        shell: bash
        run: |
          python - <<'PY'
          import os
          from pathlib import Path
          path = Path('.agent/release-publisher/release-notes.md')
          path.parent.mkdir(parents=True, exist_ok=True)
          path.write_text(os.environ['RELEASE_NOTES'], encoding='utf-8')
          PY

      - name: Build deterministic release plan
        shell: bash
        run: |
          set -euo pipefail
          python {publisher} \
            --repository "$GITHUB_REPOSITORY" \
            --policy .coferlandia/release/policy.json \
            plan \
            --target "$TARGET_SHA" \
            --impact "$IMPACT" \
            --version "$VERSION" \
            --title "$RELEASE_TITLE" \
            --notes-file .agent/release-publisher/release-notes.md \
            --output .agent/release-publisher/release-plan.json

      - name: Publish through Coferlandia release publisher
        shell: bash
        run: |
          set -euo pipefail
          python {publisher} \
            --repository "$GITHUB_REPOSITORY" \
            --policy .coferlandia/release/policy.json \
            publish \
            --input .agent/release-publisher/release-plan.json
'''


def render_publication_policy(policy: dict[str, Any], *, workflow_path: str) -> dict[str, Any]:
    workflow = _safe_repo_path(workflow_path, suffixes=(".yml", ".yaml"))
    if not workflow.startswith(".github/workflows/"):
        raise ValueError("publication workflow must be under .github/workflows/")
    rendered = json.loads(json.dumps(policy))
    publication = rendered.setdefault("publication", {})
    if not isinstance(publication, dict):
        raise ValueError("publication must be an object")
    publication["github"] = {"mode": "workflow-dispatch", "workflow": workflow}
    publication_github(rendered)
    return rendered


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(value, encoding="utf-8")
    temp.replace(path)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")
