---
name: coferlandia-project-manager
description: >
  Use ONLY when the user explicitly wants to set up the current repository as a
  project-manager home that tracks an explicit list of projects (projects.json),
  reports portfolio health, coordinates archivist sync, and governs approval-gated
  multi-project execution from `skills/ops/coferlandia-project-manager/`. Do NOT
  activate automatically based on a folder containing many repos, the presence of a
  `.coferlandia/` directory, portfolio-style reporting requests, or an opportunity to
  manage, scan, or report on multiple repositories: this skill is explicit-invocation
  only.
license: Apache-2.0
compatibility: >
  Requires Bash, git, and Python 3.11+ for validation. Write access is allowed only
  when the active control authority approves local skill updates or PM artifact
  synchronization.
metadata:
  author: coferlandia
  version: "0.5.1"
  category: ops
  status: active
  tested: "2026-07-14 - ProjectsJsonTests passes: custom slug preservation, projects_file guards, onboarding, and project management lifecycle."
---

## Context

This is a project-local skill for conservative portfolio management across multiple
repositories. It has evolved through the current implementation phases from
onboarding and diagnostics into approval-gated orchestration for planning,
implementation handoff, review, verification, and documentation sync.

## PM Home

The repository from which the skill is invoked is the PM home repository.

- Default config path: `.coferlandia/project-manager/config.json`
- Managed-projects list: `.coferlandia/project-manager/projects.json`
- Runtime root: `.coferlandia/project-manager/`
- Report output root: `.coferlandia/project-manager/reports/`
- Backup root: `.coferlandia/project-manager/backups/`
- Default local Obsidian vault: `obsidian/`

`projects.json` lists the managed projects explicitly (one entry per project:
`slug`, `path`, `status`). A project path may point anywhere on the filesystem,
including outside the PM home repository. The PM home repository is the controller
repo, not one of the managed project repositories. Projects can be added or removed
at any time via `scripts/pm-manage-projects.sh`.

The PM coordinates development workflows through explicit briefs, delegated
Superpowers skills, and approval gates. It does not replace the implementing roles
or execute repository changes autonomously.

## Prerequisites

- Bash
- git
- Python 3.11+ for the validator
- Optional: `jq` for richer JSON inspection in later phases

## Steps

1. Onboard the PM home: run `scripts/pm-onboard.sh --apply` to generate `config.json` and seed `projects.json`.
2. Add projects one at a time with `scripts/pm-manage-projects.sh add <path>` until the portfolio is complete (see Onboarding).
3. Validate the environment and portfolio state with the diagnostic and reporting scripts in `scripts/`.
4. Determine the next approved action from PM board state, repo state, and sync state.
5. Delegate planning, implementation, review, verification, and branch lifecycle work through the documented Superpowers pipelines.
6. Keep all write-capable consequences approval-gated and advisory until the delegated role executes them.

## Onboarding

When the user explicitly asks to set up the current repository as a project-manager
home, run an interactive add-one-at-a-time loop:

1. Run `scripts/pm-onboard.sh --apply --json` and confirm `config_exists` is true and
   `projects_status` is `empty` (it seeds an empty `projects.json`).
2. Ask the user for the absolute path of the first project to manage.
3. Run `scripts/pm-manage-projects.sh add <path>` (optionally with `--slug <slug>`);
   surface the JSON result. The script validates the path is a git repo and rejects
   active duplicates.
4. Ask whether to add another project; repeat until the user declines.
5. Run `scripts/pm-portfolio-report.sh --json` to show the initial portfolio state.

Projects can be added or removed at any later time with `pm-manage-projects.sh
add|remove|list`. Removing a project archives it (`status: archived`); it is not
deleted, so it can be reactivated.

## Gotchas

- **Do not skip approval gates:** write-capable operations remain dry-run-first and
  require explicit authority.
- **Do not claim background execution:** weekly or scheduled checks only run when
  explicitly invoked.
- **Do not treat coordination as implementation:** the PM may prepare briefs,
  validations, and sync actions, but it does not replace the developer, debugger,
  reviewer, or branch-finisher roles.
- **Do not follow obsolete phase text:** later sections define the current
  orchestration behavior; Phase 1 readiness is only one entry point, not the whole
  skill contract.

## Expected Output

```text
PM coordination output:
- config and environment status
- portfolio or project status
- sync or conflict status
- next approved action
- required delegated skill or approval gate
```

## Output Location

All artifacts generated by this skill go to `.coferlandia/project-manager/`.

## State Files

- `.coferlandia/project-manager/projects.json` - explicit list of managed projects (source of truth)
- `.coferlandia/project-manager/state.json` - runtime metadata and maintenance checkpoints
- `.coferlandia/project-manager/project-map.json` - mapping between managed projects and PM-visible artifacts
- `.coferlandia/project-manager/sync-log.md` - later sync history
- `.coferlandia/project-manager/sync-conflicts.md` - later sync ambiguity log

## Repo-Local Home Acceptance

- the PM is invoked from its own controller repository
- PM config defaults to `.coferlandia/project-manager/config.json`
- the managed-projects list defaults to `.coferlandia/project-manager/projects.json`
- PM runtime artifacts stay under `.coferlandia/project-manager/`
- the default Obsidian vault is local to the PM home repository
- managed project paths may live anywhere on the filesystem, including outside the PM home repository
- versioning policy for the PM home repository is left to the user

## Managed Projects Rules

1. A managed project is an entry in `projects.json` with a `slug`, an absolute `path`, and a `status` (`active` | `archived`).
2. Only `active` projects are scanned, reported, and acted upon.
3. Inspection is read-only: `.git`, branch state, remotes, and worktree status.
4. The PM may not create branches, worktrees, PRs, or modify repository files.
5. Projects are added or removed with `scripts/pm-manage-projects.sh`; removing archives (it does not delete).
6. Development branch lifecycle remains delegated to Superpowers.

## Git Policy

The PM may inspect Git state directly.
The PM must not manage development branches manually.
The PM must delegate worktree and branch lifecycle actions to:
- `superpowers:using-git-worktrees`
- `superpowers:finishing-a-development-branch`

## Required Task Statuses

intake
needs-brainstorming
spec-writing
spec-review
planning
plan-review
ready-for-agent
worktree-prep
implementing
debugging
code-review
changes-requested
verification
branch-finishing
syncing-docs
done
blocked
cancelled

## Sync Rules

- Preserve unknown frontmatter fields.
- Preserve manual user notes below frontmatter.
- Create backups before bulk writes when configured.
- Log ambiguous merges to `.coferlandia/project-manager/sync-conflicts.md`.

## Archivist Integration

The PM reads:
- `TODO.md` for active tasks
- `HISTORY.md` for completed work
- `DECISIONS.md` for architectural context
- `RUNBOOK.md` for executable commands
- `AGENTS.md` for high-priority agent instructions

The PM must not replace `coferlandia-project-archivist`.

## Phase Boundary

The reporting surface remains available through the five read-only report
generators (`pm-portfolio-report.sh`, `pm-project-report.sh`,
`pm-task-report.sh`, `pm-health-check.sh`, `pm-clean-worktrees.sh`) backed by
`scripts/lib/reporting.py`.

Phase 6 adds board-driven action validation and execution-brief generation:
- `pm-validate-task-transition.sh`
- `pm-generate-execution-brief.sh`

These Phase 6 actions prepare guidance only. They do not start development,
create branches or worktrees, or write into repositories automatically.
The `pm-backup-pm-db.sh` and `pm-sync-to-obsidian.sh` entry points now carry
approval-gated write paths for PM backups and Obsidian note sync.

## Repo Sync Safety

- Preserve manual Obsidian fields.
- Default to `--dry-run`.
- Reject `--apply` unless the active control authority approved the write; never report a write that did not happen.
- Stop when unresolved sync conflicts affect the target project.
- Do not duplicate archivist responsibilities.

## Weekly Maintenance

Weekly maintenance does not run in the background by itself.
It only runs when invoked by:
- user
- host process
- scheduler
- supervising agent
- explicit PM command

## Conflict Classes

Phase 4 detects two repo-level conflict classes only:

- `repo_path_missing` - an active project listed in `projects.json` is not a Git repository (or its path no longer exists)
- `missing_archivist_artifact` - a Git repository lacks one or more expected archivist files

Richer PM-vs-repository conflict detection is future work and intentionally not promised. The following classes are candidates for later phases, not a Phase 4 contract:

- PM task done but TODO still open
- TODO task not represented in PM
- duplicate tasks
- project note pointing to a non-existing repo
- dirty Git repo with no corresponding HISTORY entry
- Obsidian task changed manually and TODO changed simultaneously
- project archived in PM but still listed as active in projects.json
- repo removed but project still active in PM

## Reporting Output

Default report location:
- `.coferlandia/project-manager/reports/`

Report formats:
- Markdown for humans (default)
- JSON for agents (`--json` flag)

Report output behavior:
- With `--json`, reports print to stdout.
- With `--output-dir <dir>`, reports are written to timestamped files in the
  specified directory and are not echoed to stdout (ignored when `--json` is used).
- Without either flag, reports print Markdown to stdout.

## Reporting Questions

The PM must answer:
- how many active projects exist
- which projects are blocked
- which projects have ready-for-agent tasks
- which projects are in review
- which tasks were completed this week
- which repos have uncommitted changes
- which repos are ahead or behind remote
- which repos lack archivist artifacts
- which projects have sync conflicts
- which projects have not had recent activity
- which tasks need brainstorming
- which tasks are waiting for plan approval
- which tasks are waiting for code review
- which projects need weekly maintenance

## Worktree Cleanup Rules

The PM may:
- list worktrees
- identify worktrees related to completed tasks
- identify dirty worktrees
- suggest cleanup

The PM must not:
- delete dirty worktrees
- delete worktrees it cannot associate safely
- bypass Superpowers branch finishing rules
- remove branches
- force-delete anything

## Board-Driven Actions

Board changes may become actionable PM events only when:
- configuration is valid
- the task state authorizes the action
- control authority approval exists for write-capable follow-up
- no unresolved sync conflict affects the target project

## Actionable States

- `needs-brainstorming` -> prepare a brainstorming brief
- `planning` -> prepare a writing-plans brief
- `ready-for-agent` -> prepare an execution brief
- `code-review` -> prepare a review handoff brief
- `verification` -> prepare a verification checklist

## Transition Validation Output

The validator must report:
- authorized: true | false
- blocking_reason: <message or null>
- required_approval: yes | no
- suggested_next_action: <brief>

## Non-Autonomous Execution Rule

Board-driven actions may prepare:
- briefs
- checklists
- approvals needed
- next-step recommendations

They may not:
- start development automatically
- create branches or worktrees
- edit repositories without explicit authority

## Action Preflight

Before generating an actionable brief:
1. validate config
2. validate target task state
3. validate project sync state
4. validate git cleanliness for any repo-scoped action

## Phase 6 Acceptance

- board status can be validated
- next action can be described
- no development work is started automatically
- all write-capable consequences remain approval-gated

## Superpowers Dependency Matrix

- `brainstorming` - required when requirements or options are unclear
- `writing-plans` - mandatory before implementation planning
- `executing-plans` - used for inline approved plan execution
- `using-git-worktrees` - required before branch/worktree implementation setup
- `finishing-a-development-branch` - required after verified implementation
- `test-driven-development` - mandatory for features, fixes, and refactors
- `systematic-debugging` - mandatory for bugs, regressions, and unexplained behavior
- `verification-before-completion` - mandatory before marking work verified or done
- `subagent-driven-development` - used for independent approved implementation tasks
- `dispatching-parallel-agents` - used for independent read-only or isolated streams
- `requesting-code-review` - mandatory before merge or task closure
- `receiving-code-review` - mandatory when review feedback exists
- `writing-skills` - mandatory for skill design and skill implementation work
- `preserving-productive-tensions` - optional for architectural decisions with competing valid paths

## Feature Pipeline

1. Detect task from PM board.
2. Validate config and environment.
3. Generate project report.
4. Read AGENTS.md, RUNBOOK.md, TODO.md, HISTORY.md and DECISIONS.md.
5. If requirements are unclear, invoke brainstorming.
6. Invoke writing-plans.
7. Wait for plan approval from control authority.
8. Invoke using-git-worktrees.
9. Execute with executing-plans or subagent-driven-development.
10. Enforce test-driven-development.
11. Request code review.
12. Receive and process code review feedback.
13. Run verification-before-completion.
14. Invoke finishing-a-development-branch.
15. Update archivist-managed documentation.
16. Sync Obsidian PM.
17. Generate execution record and final report.

## Bug Pipeline

1. Detect bug task from PM board.
2. Validate config and environment.
3. Read HISTORY.md for possible regressions.
4. Read AGENTS.md and RUNBOOK.md.
5. Invoke systematic-debugging.
6. Reproduce the bug.
7. Create a failing regression test.
8. Apply the smallest correct fix.
9. Enforce test-driven-development.
10. Run verification-before-completion.
11. Request code review.
12. Process review feedback with receiving-code-review.
13. Invoke finishing-a-development-branch.
14. Update HISTORY.md and TODO.md through archivist conventions.
15. Sync Obsidian PM.
16. Generate final report.

## Review Pipeline

No meaningful code change may be closed without:
- requesting code review
- processing review feedback
- re-running verification-before-completion

## Git Delegation Policy

The Project Manager may inspect Git state directly.
The Project Manager must not manage development branches manually.
The Project Manager must delegate branch/worktree creation to `superpowers:using-git-worktrees`.
The Project Manager must delegate branch completion, merge, PR or cleanup to `superpowers:finishing-a-development-branch`.
The Project Manager must not force-push, rewrite history, delete branches or delete dirty worktrees.

## PM Role Boundary

The PM coordinates work selection, reporting, approvals, and artifact synchronization.
It does not replace the developer, debugger, reviewer, or branch finisher roles.

## Phase 7 Acceptance

- Superpowers usage matrix is documented
- feature pipeline is documented
- bug pipeline is documented
- review pipeline is documented
- Git delegation policy is explicit
- PM role boundaries are explicit

## Scripts Available

- `scripts/pm-onboard.sh` - orchestrates onboarding, seeds config.json and projects.json, reports readiness
- `scripts/pm-manage-projects.sh` - add/remove/list managed projects in projects.json (idempotent, non-interactive)
- `scripts/pm-generate-config.sh` - creates a config only with explicit apply approval
- `scripts/pm-validate-config.sh` - validates structural completeness of a config
- `scripts/pm-doctor.sh` - summarizes environment readiness
- `scripts/pm-detect-superpowers.sh` - detects Superpowers installation details
- `scripts/pm-check-superpowers-skills.sh` - checks required and optional skills
- `scripts/pm-detect-git-capabilities.sh` - checks git, worktree, identity, and related tooling
- `scripts/pm-detect-projects.sh` - lists active projects registered in `projects.json`
- `scripts/pm-scan-repos.sh` - emits read-only portfolio repository state
- `scripts/pm-git-status-all.sh` - reports Git status for all discovered projects
- `scripts/pm-check-archivist.sh` - reports archivist artifact coverage and maintenance status
- `scripts/pm-sync-from-repos.sh` - maps repo documentation into PM state without writing
- `scripts/pm-detect-conflicts.sh` - identifies sync mismatches that need review
- `scripts/pm-weekly-maintenance.sh` - runs host-invoked weekly maintenance checks
- `scripts/pm-portfolio-report.sh` - generates a portfolio-wide report in Markdown or JSON
- `scripts/pm-project-report.sh` - generates a report for one managed project
- `scripts/pm-task-report.sh` - generates a report for one managed task
- `scripts/pm-health-check.sh` - summarizes portfolio health, sync gaps, and maintenance needs
- `scripts/pm-clean-worktrees.sh` - lists and classifies worktrees, suggests safe cleanup (approval-gated)
- `scripts/lib/reporting.py` - Python module backing all Phase 6 report generators
- `scripts/lib/reporting.sh` - bash helpers for report output directory and file writing
- `scripts/pm-validate-task-transition.sh` - validates whether a board state is actionable and safe
- `scripts/pm-generate-execution-brief.sh` - generates advisory Superpowers handoff briefs without executing work
- `scripts/lib/board_actions.py` - Python module backing Phase 6 board-action validation and brief generation
