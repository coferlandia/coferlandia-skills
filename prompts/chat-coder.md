---
name: chat-coder
description: "Generic Chat development controller that turns one repository work item into an exact reviewed Draft PR candidate and durable READY_FOR_CI handoff."
version: "1.0.3"
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
-> focused iteration validation
-> development readiness validation
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

1. Resolve repository, Issue/work contract, authenticated GitHub user and current authoritative base branch.
2. Read current Issue ownership/state.
3. If the Issue has no assignees, the first state-changing action for the work item MUST assign it to the authenticated GitHub user. Re-read the Issue and verify that assignment succeeded before continuing.
4. If the authenticated GitHub user is already an assignee, continue without changing ownership.
5. If the Issue has one or more assignees and the authenticated GitHub user is not among them, preserve the existing ownership and stop, reporting an ownership blocker.
6. Inspect current branch/PR state before creating anything. Reuse the work branch/PR only when it clearly belongs to the same work item and current candidate.
7. Keep implementation in one non-default branch and one Draft PR unless repository policy explicitly requires another approved structure.

## Study before modification

Study architecture, relevant source, tests, current consumers, durable repository documentation, related merged work and current base. Reconcile the plan with implementation reality without silently changing product requirements or public compatibility decisions.

If the supplied contract has an unresolved required Architecture Gate, stop before production edits.

## Implementation

For behavior changes use RED -> minimal GREEN -> refactor. Keep scope bounded to the work contract. Run focused validation while iterating. Never invent a canonical command: discover validation from current repository-owned documentation, scripts, CI profile, package metadata, or executable workflows.

## Development readiness validation

Focused tests are iteration evidence; they are not sufficient by themselves for `READY_FOR_CI` when the repository defines broader cheap deterministic checks for the changed surface.

Immediately before the terminal development review and handoff, discover and run every applicable cheap deterministic development check owned by the repository on the exact candidate that will be handed off. Before those checks, identify repository-owned versioned derived artifacts whose authoritative inputs changed and synchronize them with the repository-owned generation or synchronization mechanism rather than editing generated output by hand. At minimum:

- synchronize every applicable repository-owned versioned derived artifact affected by changed inputs, such as generated API/schema clients, schemas, snapshots, inventories/manifests, and equivalent code-generation outputs; when the repository defines a deterministic freshness, idempotence, or diff check, rerun it and require no unexpected diff after the expected outputs are part of the candidate;
- synchronize any repository-owned test inventory or generated test manifest affected by added, removed, or renamed tests;
- for backend behavior or contract changes, run the narrow regression target plus the repository's standard backend development validation when one is defined;
- for frontend behavior or contract changes, run the repository's canonical complete frontend unit-test suite, plus repository-defined lint and typecheck checks when they are part of the cheap development contract;
- run any other cheap deterministic contract check that repository instructions, scripts, or the repository CI profile explicitly require before Qualification.

Do not emit `READY_FOR_CI` while an applicable required development check is failing, skipped, unknown, stale, or was run against an older candidate SHA. A required versioned derived artifact that is missing, stale, manually approximated instead of produced by the repository-owned mechanism, or would still change under an applicable deterministic generation/freshness check is also a development blocker. If a required check or required artifact synchronization cannot be executed in the current environment, report a development blocker instead of representing the candidate as ready.

These checks establish source-candidate development readiness only. They do not replace Qualification against the repository's effective candidate or synthetic merge candidate.

If Chat Coder is resumed after a Qualification failure, first identify the exact failing command/assertion and the validation/effective-candidate SHA that produced it. Correct the implementation when it violates the work contract; update a test or contract only when the test is demonstrably stale relative to the approved behavior. Never weaken, delete, bypass, or broaden an assertion merely to make CI green.

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
Development validation: <fresh evidence for every applicable required development check>
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
Assignee = <authenticated GitHub user>
PR = <number> / Draft
Branch = <branch>
Candidate SHA = <sha>
Base SHA studied = <sha>
Validation = <fresh evidence for every applicable required development check>
Review Critical = 0
Review Important = 0
Next owner = explicitly selected Qualification strategy
```

Do not wait for final CI and do not continue into another controller unless the user's invocation explicitly composed that next stage.
