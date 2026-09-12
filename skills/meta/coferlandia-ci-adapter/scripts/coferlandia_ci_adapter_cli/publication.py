from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_WORKFLOW_PATH = Path(".github/workflows/coferlandia-release-publish.yml")
DEFAULT_RUNS_ON: str = "ubuntu-latest"
RELEASE_POLICY_PATH = Path(".coferlandia/release/policy.json")
PUBLICATION_REQUEST_MARKER = "<!-- coferlandia-release-publication-request:v1 -->"


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


def _normalize_runs_on(value: Any) -> str | list[str]:
    if value is None:
        return DEFAULT_RUNS_ON
    if isinstance(value, str):
        normalized = value.strip()
        if not normalized or "\n" in normalized or "\r" in normalized:
            raise ValueError("publication.github.runs_on string must be non-empty and single-line")
        return normalized
    if isinstance(value, list):
        if not value:
            raise ValueError("publication.github.runs_on list must not be empty")
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("publication.github.runs_on labels must be strings")
            label = item.strip()
            if not label or "\n" in label or "\r" in label:
                raise ValueError("publication.github.runs_on labels must be non-empty and single-line")
            normalized.append(label)
        if len(normalized) != len(set(normalized)):
            raise ValueError("publication.github.runs_on contains duplicate labels")
        return normalized
    raise ValueError("publication.github.runs_on must be a string or non-empty list of strings")


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
    if mode not in {"issue-comment", "workflow-dispatch"}:
        raise ValueError("publication.github.mode must be none, issue-comment, or workflow-dispatch")
    allowed = {"mode", "workflow", "runs_on"}
    if not {"mode", "workflow"}.issubset(github) or not set(github).issubset(allowed):
        raise ValueError(f"{mode} publication requires mode/workflow and optionally runs_on")
    workflow = _safe_repo_path(str(github.get("workflow", "")), suffixes=(".yml", ".yaml"))
    if not workflow.startswith(".github/workflows/"):
        raise ValueError("publication.github.workflow must be under .github/workflows/")
    rendered = {"mode": mode, "workflow": workflow}
    if "runs_on" in github:
        rendered["runs_on"] = _normalize_runs_on(github["runs_on"])
    return rendered


def load_release_policy(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid release policy JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("release policy must be a JSON object")
    publication_github(raw)
    return raw


def render_workflow(*, publisher_path: str, runs_on: Any = None) -> str:
    publisher = _safe_repo_path(publisher_path, suffixes=(".py",))
    rendered_runs_on = json.dumps(_normalize_runs_on(runs_on), separators=(",", ":"))
    return f'''name: Coferlandia Release Publish

on:
  issue_comment:
    types: [created]

permissions:
  contents: write
  issues: read
  pull-requests: read

concurrency:
  group: coferlandia-release-${{{{ github.event.issue.number }}}}
  cancel-in-progress: false

jobs:
  publish:
    name: Publish exact release
    if: >-
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '{PUBLICATION_REQUEST_MARKER}')
    runs-on: {rendered_runs_on}
    env:
      GH_TOKEN: ${{{{ github.token }}}}
    steps:
      - name: Require release authority
        shell: bash
        run: |
          set -euo pipefail
          permission="$(gh api "repos/$GITHUB_REPOSITORY/collaborators/$GITHUB_ACTOR/permission" --jq .permission)"
          case "$permission" in
            admin|maintain) ;;
            *) echo "actor $GITHUB_ACTOR has insufficient release permission: $permission" >&2; exit 2 ;;
          esac
          merged_at="$(gh api "repos/$GITHUB_REPOSITORY/pulls/${{{{ github.event.issue.number }}}}" --jq '.merged_at // empty')"
          test -n "$merged_at"

      - name: Parse immutable publication request
        id: request
        shell: bash
        run: |
          python - <<'PY'
          import json
          import os
          import re
          from pathlib import Path

          marker = {PUBLICATION_REQUEST_MARKER!r}
          event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
          body = event['comment']['body']
          if body.count(marker) != 1:
              raise SystemExit('publication request must contain exactly one marker')
          tail = body.split(marker, 1)[1]
          matches = re.findall(r'```json\\s*(\\{{.*?\\}})\\s*```', tail, re.S)
          if len(matches) != 1:
              raise SystemExit('publication request must contain exactly one JSON block')
          request = json.loads(matches[0])
          expected = {{'schema', 'target_sha', 'version', 'impact', 'title', 'notes'}}
          if set(request) != expected or request['schema'] != 1:
              raise SystemExit('invalid publication request schema')
          if not re.fullmatch(r'[0-9a-f]{{40}}', request['target_sha']):
              raise SystemExit('target_sha must be an exact 40-character lowercase SHA')
          if not re.fullmatch(r'[0-9]+\\.[0-9]+\\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?', request['version']):
              raise SystemExit('version must be explicit SemVer without tag prefix')
          if request['impact'] not in {{'patch', 'minor', 'major'}}:
              raise SystemExit('impact must be patch, minor, or major')
          if not isinstance(request['title'], str) or not request['title'].strip():
              raise SystemExit('title must be non-empty')
          if not isinstance(request['notes'], str) or not request['notes'].strip():
              raise SystemExit('notes must be non-empty')
          with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
              output.write(f"target_sha={{request['target_sha']}}\\n")
              output.write(f"version={{request['version']}}\\n")
          PY

      - name: Bind request to release PR integration
        env:
          TARGET_SHA: ${{{{ steps.request.outputs.target_sha }}}}
        shell: bash
        run: |
          set -euo pipefail
          merge_sha="$(gh api "repos/$GITHUB_REPOSITORY/pulls/${{{{ github.event.issue.number }}}}" --jq '.merge_commit_sha // empty')"
          test -n "$merge_sha"
          test "$merge_sha" = "$TARGET_SHA"

      - name: Check out exact publication target
        uses: actions/checkout@v4
        with:
          ref: ${{{{ steps.request.outputs.target_sha }}}}
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
        env:
          TARGET_SHA: ${{{{ steps.request.outputs.target_sha }}}}
        shell: bash
        run: |
          set -euo pipefail
          test "$(git rev-parse HEAD)" = "$TARGET_SHA"
          git fetch --tags --force origin
          test "$(git rev-parse HEAD)" = "$TARGET_SHA"

      - name: Materialize request and deterministic release plan
        shell: bash
        run: |
          python - <<'PY'
          import json
          import os
          import re
          import subprocess
          from pathlib import Path

          marker = {PUBLICATION_REQUEST_MARKER!r}
          event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
          body = event['comment']['body']
          if body.count(marker) != 1:
              raise SystemExit('publication request must contain exactly one marker')
          tail = body.split(marker, 1)[1]
          matches = re.findall(r'```json\\s*(\\{{.*?\\}})\\s*```', tail, re.S)
          if len(matches) != 1:
              raise SystemExit('publication request must contain exactly one JSON block')
          request = json.loads(matches[0])
          root = Path('.agent/release-publisher')
          root.mkdir(parents=True, exist_ok=True)
          notes = root / 'release-notes.md'
          notes.write_text(request['notes'], encoding='utf-8')
          plan = root / 'release-plan.json'
          subprocess.run([
              'python', {publisher!r},
              '--repository', os.environ['GITHUB_REPOSITORY'],
              '--policy', '.coferlandia/release/policy.json',
              'plan',
              '--target', request['target_sha'],
              '--impact', request['impact'],
              '--version', request['version'],
              '--title', request['title'],
              '--notes-file', str(notes),
              '--output', str(plan),
          ], check=True)
          PY

      - name: Publish through Coferlandia release publisher
        shell: bash
        run: |
          python {publisher} \
            --repository "$GITHUB_REPOSITORY" \
            --policy .coferlandia/release/policy.json \
            publish \
            --input .agent/release-publisher/release-plan.json
'''


def render_publication_policy(
    policy: dict[str, Any], *, workflow_path: str, runs_on: Any = None
) -> dict[str, Any]:
    workflow = _safe_repo_path(workflow_path, suffixes=(".yml", ".yaml"))
    if not workflow.startswith(".github/workflows/"):
        raise ValueError("publication workflow must be under .github/workflows/")
    rendered = json.loads(json.dumps(policy))
    publication = rendered.setdefault("publication", {})
    if not isinstance(publication, dict):
        raise ValueError("publication must be an object")
    existing_github = publication.get("github")
    inherited_runs_on = existing_github.get("runs_on") if isinstance(existing_github, dict) else None
    resolved_runs_on = _normalize_runs_on(runs_on if runs_on is not None else inherited_runs_on)
    publication["github"] = {
        "mode": "issue-comment",
        "workflow": workflow,
        "runs_on": resolved_runs_on,
    }
    publication_github(rendered)
    return rendered


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(value, encoding="utf-8")
    temp.replace(path)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")
