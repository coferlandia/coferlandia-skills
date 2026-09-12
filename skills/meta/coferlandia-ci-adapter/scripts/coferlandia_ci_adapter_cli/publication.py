from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

DEFAULT_WORKFLOW_PATH = Path(".github/workflows/coferlandia-release-publish.yml")
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
    if set(github) != {"mode", "workflow"}:
        raise ValueError(f"{mode} publication requires exactly mode and workflow")
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
    runs-on: ubuntu-latest
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
          if marker not in body:
              raise SystemExit('missing publication request marker')
          tail = body.split(marker, 1)[1]
          match = re.search(r'```json\\s*(\\{{.*?\\}})\\s*```', tail, re.S)
          if not match:
              raise SystemExit('missing publication request JSON block')
          request = json.loads(match.group(1))
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
          tail = event['comment']['body'].split(marker, 1)[1]
          request = json.loads(re.search(r'```json\\s*(\\{{.*?\\}})\\s*```', tail, re.S).group(1))
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


def render_publication_policy(policy: dict[str, Any], *, workflow_path: str) -> dict[str, Any]:
    workflow = _safe_repo_path(workflow_path, suffixes=(".yml", ".yaml"))
    if not workflow.startswith(".github/workflows/"):
        raise ValueError("publication workflow must be under .github/workflows/")
    rendered = json.loads(json.dumps(policy))
    publication = rendered.setdefault("publication", {})
    if not isinstance(publication, dict):
        raise ValueError("publication must be an object")
    publication["github"] = {"mode": "issue-comment", "workflow": workflow}
    publication_github(rendered)
    return rendered


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(value, encoding="utf-8")
    temp.replace(path)


def atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")
