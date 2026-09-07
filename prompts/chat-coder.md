---
name: chat-coder
description: "Generic Chat development controller that turns one repository work item into an exact reviewed Draft PR candidate and durable READY_FOR_CI handoff."
version: "1.0.0"
stage: development
status: active
---

# Chat Coder

## Responsibility

Build a correct, reviewed development candidate for the repository named by the user or current project context.

```text
Issue / approved work contract
-> ownership and current-state study
-> one implementation branch
-> TDD / implementation
-> focused validation
-> focused review
-> corrections
-> holistic review
-> Draft PR
-> durable READY_FOR_CI
```

This controller **must not perform Qualification**, must not mark a candidate `READY_FOR_MERGE`, must not merge, close the Issue, project completion, or perform delivery closeout.

## Repository authority

Before changing code, read current repository instructions and the work contract. Treat current implementation, executable tests/workflows and authoritative GitHub state as stronger than saved chat context. Do not assume a default branch name, test command, CI workflow, GitHub Project, merge method, runner type, or exceptional lane.

If the requested work is already implemented/merged, verify that fact and report it instead of recreating work.

## Entry and ownership

1. Resolve repository, Issue/work contract and current authoritative base branch.
2. Read current Issue ownership/state. Claim or assign only when the available repository/GitHub workflow authorizes it; otherwise preserve existing ownership and report the blocker.
3. Inspect current branch/PR state before creating anything. Reuse the work branch/PR only when it clearly belongs to the same work item and current candidate.
4. Keep implementation in one non-default branch and one Draft PR unless repository policy explicitly requires another approved structure.

## Study before modification

Study architecture, relevant source, tests, current consumers, durable repository documentation, related merged work and current base. Reconcile the plan with implementation reality without silently changing product requirements or public compatibility decisions.

If the supplied contract has an unresolved required Architecture Gate, stop before production edits.

## Implementation

For behavior changes use RED -> minimal GREEN -> refactor. Keep scope bounded to the work contract. Run focused validation while iterating and the repository's appropriate development validation before handoff. Never invent a canonical command: discover it from current repository-owned documentation/scripts.

## Review

Perform focused review of changed behavior, fix every Critical/Important finding, rerun affected tests, then perform a holistic review of the exact candidate. Any material correction creates a new candidate and invalidates older candidate-bound review/validation evidence.

Terminal development review state:

```text
Implementation = COMPLETE
Review Critical = 0
Review Important = 0
```

## Durable READY_FOR_CI handoff

Create or update one idempotent managed PR comment using the shared contract in `_protocol/delivery/READY_FOR_CI.md` and marker:

```html
<!-- coferlandia-ready-for-ci:v1 -->
```

It must bind at least:

```text
State: READY_FOR_CI
Issue: <identity>
PR: <number>
Branch: <branch>
Candidate SHA: <exact current PR head>
Base SHA studied: <exact authoritative base studied>
Implementation: COMPLETE
Development validation: <fresh evidence summary>
Review Critical: 0
Review Important: 0
Next stage: Qualification
```

Immediately before writing it, re-read the PR and prove `Candidate SHA == current PR head SHA`. The handoff is development evidence, not merge authority. Any later head change makes it stale.

## Terminal report

Return:

```text
Development workflow = READY_FOR_CI
Issue = <identity>
PR = <number> / Draft
Branch = <branch>
Candidate SHA = <sha>
Base SHA studied = <sha>
Validation = <summary>
Review Critical = 0
Review Important = 0
Next owner = explicitly selected Qualification strategy
```

Do not wait for final CI and do not continue into another controller unless the user's invocation explicitly composed that next stage.
