---
name: coferlandia-project-manager
description: >
  Use ONLY when the user explicitly wants Coferlandia portfolio/project management across
  an explicit projects.json registry, GitHub Issues/Projects reporting, project architecture,
  Archivist knowledge-health coordination, or Obsidian portfolio projection. Explicit invocation only.
license: Apache-2.0
compatibility: >
  Requires Bash, git, Python 3.11+, and GitHub CLI (`gh`) authenticated for managed GitHub
  repositories. GitHub Projects operations require a token with the `project` scope.
metadata:
  author: coferlandia
  version: "0.6.0"
  category: ops
  status: active
  tested: "2026-07-27 - Phase 1 GitHub-native project-management protocol."
---

## Context

This skill is the portfolio and project-architecture layer for Coferlandia.

It does not own a second task database. Operational work state belongs to GitHub Issues and
GitHub Projects. The repository contains implementation reality. Archivist owns durable
knowledge. Obsidian is an optional generated projection.

## PM responsibilities

### 1. Project architecture

Transform a conversation, rough idea, external document, bug cluster, or product requirement
into a coherent development initiative.

Relevant Superpowers remain intentionally available for design work, especially:

- `superpowers:brainstorming`
- `superpowers:writing-plans`
- `superpowers:preserving-productive-tensions` when applicable
- `superpowers:writing-skills` for skill projects when applicable

Execution-oriented Superpowers are not PM runtime dependencies merely for task tracking.
Development/execution remains delegated to the selected delivery workflow or development role.

### 2. Portfolio management

The PM home owns:

- `.coferlandia/project-manager/config.json`
- `.coferlandia/project-manager/projects.json`
- `.coferlandia/project-manager/reports/`
- `.coferlandia/project-manager/state.json`
- optional local Obsidian portfolio projection

`projects.json` is authoritative only for **portfolio membership and integration metadata**.
It must not duplicate Issue status or Project field values.

A project entry may contain:

```json
{
  "slug": "secretaria",
  "path": "C:/dev/secretaria",
  "repository": "diegocofre/secretaria",
  "github_project": {
    "owner": "diegocofre",
    "number": 4
  },
  "status": "active"
}
```

`repository` and `github_project` are optional during migration; repository identity can be
resolved from the local Git remote when possible.

## Source-of-truth boundaries

- GitHub Issues: requested/pending/active/blocked/completed work.
- GitHub Projects: workflow state, prioritization, iteration, and project-board fields.
- Git repository: implementation reality.
- Archivist: README/AGENTS/DECISIONS/RUNBOOK and knowledge traceability.
- PM `projects.json`: portfolio membership and GitHub Project coordinates only.
- Obsidian: human-readable projection only.

Never recreate TODO.md/HISTORY.md as PM state.

## Prerequisites

- Bash
- git
- Python 3.11+
- `gh`
- authenticated access to managed repositories
- `project` token scope when GitHub Project data is requested

Useful checks:

```bash
gh auth status
gh auth refresh -s project   # when Project access is missing
```

## Onboarding

1. Run `scripts/pm-onboard.sh --apply --json`.
2. Register projects with `scripts/pm-manage-projects.sh add <path>`.
3. Prefer storing the resolved GitHub repository and, when known, GitHub Project owner/number.
4. Run `scripts/pm-portfolio-report.sh --json`.
5. Migrate any repository still using Archivist v2 TODO/HISTORY before treating GitHub state as authoritative.

## GitHub-native reporting

The reporting layer should answer from GitHub and Git state:

- open Issues;
- Issues represented in the configured GitHub Project;
- blocked work using native `blockedBy`/`blocking` relationships when available;
- current Project status/priority fields when available;
- recently closed Issues;
- linked PR/implementation context where exposed;
- repository dirty/ahead/behind/staleness state;
- Archivist durable-knowledge health.

A repository that has not completed the GitHub-native migration may expose a migration warning,
but its TODO/HISTORY files must not be treated as authoritative portfolio state.

## Project status

Prefer configured GitHub Project `Status` values. Do not force all repositories into the old
18-state PM state machine.

For portfolio aggregation, normalize only broad categories when possible:

- `backlog`
- `in-progress`
- `review`
- `blocked`
- `done`
- `unknown`

Preserve the original Project status text in detailed output.

## Archivist integration

The PM reads:

- `README.md` for confirmed current state;
- `DECISIONS.md` for rationale;
- `RUNBOOK.md` for operations;
- `AGENTS.md` for agent-critical constraints;
- Archivist catalog health for processing status.

The PM reads GitHub directly for active/completed work. It does not ask Archivist for a TODO or HISTORY mirror.

## Obsidian projection

Obsidian pages are generated from GitHub/portfolio state.

Generated project sections may contain:

- repository and GitHub Project links;
- counts by status;
- Issues in progress/review/blocked;
- recently completed Issues;
- project priority/iteration when present;
- Archivist health;
- Git status.

Generated sections are disposable/rebuildable. Preserve human notes outside managed sections.
Generated per-Issue notes are allowed only as mechanically replaceable projections. They must never carry independent workflow state that can diverge from GitHub; preserve human notes outside managed sections.

## Git policy

The PM may inspect repositories and GitHub state. It does not automatically implement code,
create development branches, merge, or push. Delivery workflows own their own Git lifecycle.

## Migration boundary

Phase 1 requires every managed repository to migrate legacy operational files through
`project-documentation-archivist` before the repository is considered GitHub-native.

Expected migrated Archivist files are:

```text
README.md
AGENTS.md
DECISIONS.md
RUNBOOK.md
.agent/catalog/SOURCE_INDEX.md
.agent/catalog/PROCESSING_RUNS.md
```

`TODO.md`, `HISTORY.md`, and legacy `OPEN_QUESTIONS.md` are migration inputs only.

## Reporting commands

Existing read/report entry points remain stable:

- `pm-portfolio-report.sh`
- `pm-project-report.sh`
- `pm-task-report.sh` (task now means GitHub Issue)
- `pm-health-check.sh`
- `pm-clean-worktrees.sh`

`pm-task-report.sh --task` prefers `project-slug#number`; plain `#number` is accepted only when it resolves uniquely across the managed portfolio, and GitHub Issue URLs are also accepted.

## Safety

- GitHub and Git reads must fail visibly when authentication/repository resolution fails.
- Do not silently fall back to TODO/HISTORY for authoritative status.
- Writes to Obsidian/runtime projections remain approval-gated and dry-run-first where existing wrappers provide that behavior.
- Never claim a GitHub Project field was read when the project is not configured or access failed.
- Preserve manual user notes in Obsidian.

## Expected output

```text
PM coordination output:
- portfolio membership
- GitHub repository / Project state
- active, blocked, review, and recently completed Issues
- Git/Archivist health
- project architecture or next design action when requested
- migration warnings when a project has not completed GitHub-native cutover
```
