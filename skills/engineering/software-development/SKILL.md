---
name: software-development
description: >
  Use when a task needs a development role: a feature request, bug, detailed executable
  implementation plan, or request to review an implementation against its plan. Applies
  to code changes in Git repositories, including concurrent agent work and local integration.
license: Apache-2.0
compatibility: >
  Requires read/write access to the target repository, git, and its relevant validation
  commands. Falls back without worktree isolation only when the target is not a Git repository.
metadata:
  author: community
  version: "3.3.0"
  category: engineering
  status: active
  tested: "2026-07-12 - RED/GREEN role-routing, worktree, mandatory-TDD, and mandatory-debugging pressure scenarios; validated with validate_skill.py."
---

## Context

This skill governs development work in any Git repository. It routes a request to one concrete
development role and keeps implementation, independent review, commit, and local
integration as distinct stages. A direct human instruction is the active control
authority within its stated scope; do not invent another approval gate for a detailed,
executable implementation plan.

## Role Routing

Select exactly one role before changing files. A request can name a role; otherwise
apply this order:

| Request signal | Role |
|---|---|
| Review, validate, or compare an implementation/diff with its plan | `code-reviewer` |
| Detailed, executable implementation plan with ordered work or acceptance criteria | `coding-agent` |
| Bug, regression, failing test, exception, or incorrect behavior | `debugger` |
| Feature, functional improvement, new implementation, or approved refactor | `developer` |

Use **development role** for the collective term. Reserve `coding-agent` and
`code-reviewer` for their concrete responsibilities.

## Shared Worktree and Traceability Rules

Every development role that can modify code in a Git repository must use an isolated,
task-specific Git worktree. This is mandatory for `developer`, `debugger`,
`coding-agent`, `code-reviewer`, and any future code-modifying development role.

1. Inspect the repository, existing worktrees, branches, and current status before
   changing files. Never edit implementation files in the primary/main working tree.
2. Record the task's base commit, branch name, and absolute worktree path. Detect an
   existing branch or worktree with the intended name/path and choose a non-colliding
   task-specific name instead of reusing or overwriting another agent's work.
3. Create the branch and linked worktree from the recorded base commit at
   `{repository-root}/.worktrees/{task-name}`. Before creation, verify that
   `.worktrees/` is ignored. If it is not, add `.worktrees/` to the repository-root
   `.gitignore`, verify it with `git check-ignore -q --no-index .worktrees/.probe`,
   and only then create the worktree. Do not use a global worktree directory when a
   repository-local worktree is possible.
4. Reuse an existing linked task worktree rather than nesting another worktree inside
   it. Do not alter uncommitted changes belonging to another agent. Concurrent
   implementations use different local worktree paths and branches.
5. Standalone reviewers reuse the implementation worktree and branch. Orchestrated
   reviewers use only the explicitly assigned detached review worktree and immutable
   candidate commit. If the directory is not a Git repository, continue without a
   worktree and state that exception explicitly in the handoff.
6. Preserve the worktree until reviewed integration and verification succeed. Remove
   it only after the merge is verified; never remove a worktree that another agent owns.

### Assigned-worktree precedence

An explicitly assigned existing worktree from the user, supervisor, or
`project-orchestrator` overrides default worktree creation. Before modifying files,
verify the current directory is inside that assigned worktree and its active branch
matches the assignment. On either mismatch, stop and report it: do not create/select
another worktree, change branch, or change working directory as a workaround.

Use these process states in task records and handoffs:

```text
planned -> approved -> ready -> in_progress -> awaiting_review -> review_in_progress -> completed
```

Record, where the project has phase or task metadata: implementation agent, review
agent, control authority, worktree path, worktree branch, base commit, implementation
completion time, review completion time, review commit, and merge commit. Preserve
existing traceability fields; explicitly migrate or redefine ambiguous ones rather
than silently dropping them.

## Role: developer

Use `developer` for a feature, functional improvement, new implementation, or approved
refactor that is not already a detailed executable plan.

1. Study the issue, architecture, related code, tests, conventions, and documentation
   without modifying files. Report material inconsistencies to the control authority.
2. Prepare a concise plan covering scope, affected areas, implementation, validation,
   risks, and documentation. Obtain explicit approval from the active control authority.
3. Create the isolated worktree unless one was explicitly assigned, then implement the approved scope. **REQUIRED:** use
   `superpowers:test-driven-development` before writing implementation code when it is
   available. If it is unavailable, still follow its RED-GREEN-REFACTOR discipline and
   record that the Superpowers skill was unavailable in the handoff. Reuse existing
   patterns, avoid duplication and unrelated refactors, and match the repository's
   source-code language.
4. Run relevant tests and validation; update only documentation and traceability
   artifacts affected by the approved change. If the required work materially deviates
   from the approved scope or plan, stop and obtain fresh approval before expanding it.
   Hand off the uncommitted implementation to a reviewer distinct from the implementing
   agent in `awaiting_review` state.

## Role: debugger

Use `debugger` for a bug, regression, failing test, exception, data inconsistency, or
unexpected behavior.

1. Study the issue without modifying files. Separate facts, symptoms, hypotheses, and
   missing evidence; inspect reproduction steps, logs, failing tests, and `HISTORY.md`
   when it exists.
2. Prepare a root-cause plan and obtain explicit approval from the control authority.
   **REQUIRED:** use `superpowers:systematic-debugging` before proposing a fix when it
   is available. If it is unavailable, still separate facts from hypotheses, reproduce
   or pinpoint the failure, and identify the root cause before proposing a correction;
   record the unavailable skill in the handoff.
3. Create the isolated worktree unless one was explicitly assigned. Reproduce or pinpoint the failure, make the smallest
   approved correction, add or update regression tests, and verify related behavior.
   If the required correction materially deviates from the approved scope or plan, stop
   and obtain fresh approval before expanding it. Match the repository's source-code
   language.
4. Update relevant documentation or traceability and hand off uncommitted changes to
   a reviewer distinct from the implementing agent in `awaiting_review` state.

## Role: coding-agent

Activate `coding-agent` whenever the user supplies a sufficiently detailed executable
implementation plan. A separate statement that the plan is approved is unnecessary.

1. Read the complete plan and every referenced document. Inspect the repository
   structure, architecture, conventions, tests, and current code; confirm the plan is
   compatible with the actual state.
2. Create and record the isolated worktree before modifying code unless one was
   explicitly assigned. Ask only when the
   plan has a material contradiction, omits a required decision, or the repository
   state makes it unsafe or impossible to execute as written.
3. **REQUIRED:** use `superpowers:test-driven-development` before writing
   implementation code when it is available. If it is unavailable, follow its
   RED-GREEN-REFACTOR discipline and record the unavailable skill in the handoff.
   Implement the plan in its specified order and keep every change within its scope.
   Run all relevant tests, linters, static checks, and validation commands. Update
   documentation and project-history artifacts when the plan or repository requires it.
4. Leave the implementation uncommitted in `awaiting_review` state and provide the
   handoff below to a reviewer distinct from the implementing agent. Testing and
   validation are required implementation work; they are not a substitute for code
   review.

The `coding-agent` must not create a replacement implementation plan, run a
planning-and-approval phase, review its own implementation, commit, push, merge, alter
unrelated code, or claim final completion while review remains pending.

When orchestrated, coding-agent may only inspect/modify its assigned implementation
worktree, test, run static analysis, update docs, and emit protocol output. It must not
commit, amend, push, merge, rebase, create/remove worktrees, switch Git state, or leave
that directory.

## Role: fix-agent

Use `fix-agent` for in-scope corrections from independent review. It follows the
coding-agent implementation rules and creates an isolated worktree only when none is
assigned. When assigned an implementation worktree and branch, verify both and use
exactly them. It may modify files, test, update relevant docs, and report evidence, but
must not commit, amend, push, merge, rebase, create/remove worktrees, switch Git state,
or change working directory. Escalate scope-changing findings.

## Role: code-reviewer

Activate `code-reviewer` when the user requests code review or asks to validate an
implementation against its plan. Locate the complete plan, implementation worktree or
branch, current uncommitted diff, and coding-agent handoff when available. The reviewer
must be a different agent from the implementation agent; an implementation role cannot
review or integrate its own work.

1. Standalone: open/reuse the implementation worktree. Orchestrated: review only the
   exact assigned immutable candidate commit in its assigned detached review worktree;
   do not create another worktree, switch Git state/directory, or modify files. Inspect
   its status, diff, branch, and
   recorded base commit. Compare every plan task and acceptance criterion with the
   implementation.
2. Review for missing requirements, incorrect behavior, regressions, security,
   error handling, concurrency or persistence defects, edge cases, tests,
   documentation, and out-of-scope changes. Classify findings by severity.
3. Standalone reviewers correct valid, in-scope defects directly in that worktree.
   Orchestrated reviewers are read-only and return findings to the fix-agent. Escalate instead of
   changing requirements, approved architecture, scope materially, dependencies,
   acceptance criteria, or a substantial portion of the plan.
4. Run the complete relevant validation suite after corrections and reinspect the final
   diff. Do not commit with failing validations or unresolved findings.
5. Before integration, verify the primary `main` worktree is clean and determine
   whether `main` advanced since the recorded base commit. If it advanced, reconcile
   those changes in the isolated implementation branch, resolve conflicts there, and
   rerun affected validations. Do not edit implementation files in the primary worktree.
6. Standalone reviewers commit the reviewed implementation with a message consistent with the plan, then
   merge that branch locally into `main`. Verify the resulting `main` state, record
   review and merge commits, and update execution/history/decision/phase records that
   the repository requires. In orchestrated mode, only `project-orchestrator` may
   stage, commit/amend, merge, rebase, reset, checkout/switch, push, or manage branches
   and worktrees. Never push unless explicitly instructed.

The only primary-worktree mutation allowed to the reviewer is the final local merge
after its cleanliness, reconciliation, and validation gates pass. The worktree itself
is never merged; its branch is.

## Handoff Templates

### Implementation handoff

```md
## Implementation handoff: {task title}

Plan executed: {plan reference}
Repository: {absolute repository path}
Implementation agent: {agent or human identifier}
Review agent: {agent or human identifier, or "unassigned"}
Control authority: {human user | designated supervisor | direct user instruction}
Base commit: {SHA}
Worktree path: {absolute path | "not a Git repository"}
Branch name: {branch | "not applicable"}
Worktree exception: {none | "Target is not a Git repository; worktree isolation does not apply"}
Files changed:
- {path} - {reason}
Tests and validation commands executed:
- `{command}` - {result}
Results: {summary}
Deviations from the plan: {none | list}
Remaining issues: {none | list}
Working-tree status: {git status output or explanation}
Implementation completion time: {ISO 8601 timestamp}
Process state: awaiting_review
Suggested commit message: `{type}: {summary}`
```

### Review and integration record

```md
## Review and integration: {task title}

Plan checked: {reference}
Implementation worktree: {absolute path}
Branch / base commit: {branch} / {SHA}
Implementation agent / review agent: {identifiers}
Control authority: {human user | designated supervisor | direct user instruction}
Findings: {severity, file, disposition; or "none"}
Corrections made: {none | list}
Validation after review: `{command}` - {result}
Review completion time: {ISO 8601 timestamp}
Review commit: {SHA}
Merge commit: {SHA}
Main verification: `{command}` - {result}
Process state: completed
```

## Documentation and Output Location

When the target repository uses `project-documentation-archivist`, update only the
affected existing artifacts. Otherwise place minimal new traceability artifacts under
`.agent/` as defined by `_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md`.

### Output Exceptions

- `AGENTS.md`, `README.md`, and `RUNBOOK.md` - update in place only when the approved
  change directly affects them.

## Gotchas

- **Treating a detailed plan as merely a proposal:** route it to `coding-agent`; do
  not require a duplicate planning or approval phase.
- **Writing implementation code before TDD:** `developer` and `coding-agent` must use
  `superpowers:test-driven-development` when it is available. Its absence permits the
  RED-GREEN-REFACTOR fallback, not tests written after implementation.
- **Proposing a debugger fix without systematic investigation:** `debugger` must use
  `superpowers:systematic-debugging` when it is available. Its absence permits only
  the explicit evidence, reproduction, and root-cause fallback; it does not permit a
  guess-and-patch fix.
- **Reviewing or committing as the implementation role:** implementation roles finish
  uncommitted in `awaiting_review`; a reviewer distinct from the implementation agent
  owns corrections, commit, and local integration.
- **Using a branch without a worktree:** branches do not isolate uncommitted files.
  Create a unique linked worktree under `{repository-root}/.worktrees/` before
  modifying code in a Git repository; add and verify the root `.gitignore` rule first
  when it is absent.
- **Resolving an advanced-main conflict in the primary checkout:** reconcile on the
  implementation branch, validate there, then perform only the final merge on `main`.
- **Fixing scope-changing findings during review:** escalate them to the control
  authority; only defects and omissions within the approved plan are reviewer-owned.
- **Pushing as part of local integration:** a local merge does not authorize a push.

## References

- **REQUIRED for `developer` and `coding-agent`:** use
  `superpowers:test-driven-development` before implementation code when it is
  available; otherwise follow RED-GREEN-REFACTOR and disclose the unavailable skill.
- **REQUIRED for `debugger`:** use `superpowers:systematic-debugging` before
  proposing a fix when it is available; otherwise follow the evidence, reproduction,
  and root-cause fallback and disclose the unavailable skill.
- Use `superpowers:verification-before-completion` before any completion, commit, or
  integration claim when it is available.
- Use `superpowers:using-git-worktrees` when setting up the required isolated
  workspace, unless the environment already supplies an isolated worktree.
