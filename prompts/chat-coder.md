---
name: chat-coder
description: "Generic Chat development controller that turns one repository work item into an exact reviewed Draft PR candidate and durable READY_FOR_CI handoff."
version: "1.3.0"
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

## Delivery context

The default delivery context is ordinary repository development. Chat Coder must never infer an exceptional lane from bug severity, urgency, labels, incident wording, branch names, or a production-looking failure.

An explicit controlling invocation may delegate a repository-defined delivery context, such as an emergency remediation context, only when all of the following are true:

- the upstream controller was explicitly invoked and owns authority to request that context;
- durable repository/GitHub evidence identifies the work item and requested context;
- current repository policy explicitly supports that context and resolves its authoritative development base/target/branch rules;
- the delegated context does not weaken Development requirements, ownership, TDD, tests, environment/configuration analysis, review, or `READY_FOR_CI` identity.

When those conditions hold, resolve the authoritative base/target from repository policy for the delegated context instead of substituting the repository's ordinary development base. The exceptional context may select a different approved delivery route; it is **not** permission to invent one, bypass safeguards, reduce required development validation, merge, publish, or close work.

If the delegated context is missing durable authority, unsupported by current repository policy, ambiguous, or contradicted by current PR/branch state, stop with a development-context blocker. Do not silently fall back to ordinary development because doing so could send an emergency candidate to the wrong integration target.

## Entry and ownership

1. Resolve repository, Issue/work contract, authenticated GitHub user, any explicitly delegated delivery context, and the current authoritative base/target under repository policy.
2. Read current Issue ownership/state.
3. If the Issue has no assignees, the first state-changing action for the work item MUST assign it to the authenticated GitHub user. Re-read the Issue and verify that assignment succeeded before continuing.
4. If the authenticated GitHub user is already an assignee, continue without changing ownership.
5. If the Issue has one or more assignees and the authenticated GitHub user is not among them, preserve the existing ownership and stop, reporting an ownership blocker.
6. Inspect current branch/PR state before creating anything. Reuse the work branch/PR only when it clearly belongs to the same work item, delivery context, target and current candidate.
7. Keep implementation in one non-default branch and one Draft PR unless repository policy explicitly requires another approved structure.

## Study before modification

Study architecture, relevant source, tests, current consumers, durable repository documentation, related merged work and current base. Reconcile the plan with implementation reality without silently changing product requirements or public compatibility decisions.

If the supplied contract has an unresolved required Architecture Gate, stop before production edits.

## Implementation

For behavior changes use RED -> minimal GREEN -> refactor. Keep scope bounded to the work contract. Run focused validation while iterating. Never invent a canonical command: discover validation from current repository-owned documentation, scripts, CI profile, package metadata, or executable workflows.

For every behavior or contract change, inspect the existing tests that cover the affected surface before adding or modifying tests. Treat the affected test suite as part of the implementation contract:

- preserve tests for behavior that remains valid;
- update tests whose approved expected behavior intentionally changed;
- remove tests only when the behavior or contract they verify was intentionally removed or superseded;
- consolidate or remove materially duplicate or overlapping tests when they provide no meaningful additional coverage or diagnostic value, while preserving distinct boundary cases, regressions, failure modes and contracts;
- prefer updating, extending, parameterizing or consolidating existing tests when that provides the required coverage without reducing clarity or diagnostic value;
- remove test-only fixtures, helpers, mocks, snapshots or data that became unreachable or unused because of the change;
- do not leave obsolete tests skipped, disabled, commented out, or asserting superseded behavior.

Test-count growth is not a goal. Add new tests only for meaningful missing coverage, and leave the smallest clear suite that adequately describes and protects the intended current behavior. Never remove, weaken, bypass or broaden a test merely to make validation pass.

## Development readiness validation

Focused tests are iteration evidence; they are not sufficient by themselves for `READY_FOR_CI` when the repository defines broader cheap deterministic checks for the changed surface.

Immediately before the terminal development review and handoff, discover and run every applicable cheap deterministic development check owned by the repository on the exact candidate that will be handed off. Before those checks, identify repository-owned derived artifacts that repository-owned instructions, tooling, or policy explicitly declare to be versioned contracts and whose authoritative inputs changed; synchronize those artifacts with the repository-owned generation or synchronization mechanism rather than editing generated output by hand. At minimum:

- for changed behavior, verify that the affected pre-existing tests were reviewed and that the resulting suite contains no known assertions for superseded behavior, materially duplicate coverage without independent value, or test-only artifacts made obsolete by the change;
- synchronize every applicable repository-owned derived artifact explicitly declared as a versioned contract and affected by changed inputs, such as generated API/schema clients, schemas, snapshots, inventories/manifests, and equivalent code-generation outputs; when the repository defines a deterministic freshness, idempotence, or diff check for that versioned contract, rerun it and require no unexpected diff after the expected outputs are part of the candidate;
- do not create, add to Git, or require snapshot freshness for a reproducible diagnostic/report output merely because the repository can generate it; a test inventory, generated test manifest, or equivalent report is a synchronization prerequisite only when repository-owned policy explicitly declares that output to be a versioned contract;
- for backend behavior or contract changes, run the narrow regression target plus the repository's standard backend development validation when one is defined;
- for frontend behavior or contract changes, run the repository's canonical complete frontend unit-test suite, plus repository-defined lint and typecheck checks when they are part of the cheap development contract;
- run any other cheap deterministic contract check that repository instructions, scripts, or the repository CI profile explicitly require before Qualification.

### Environment / configuration impact

Before `READY_FOR_CI`, inspect the exact candidate for additions, removals, renames, changed defaults, changed requirements, or changed semantics affecting environment variables, secrets or deployment-owned credentials, application settings/configuration fields, compose/container inputs, deployment/runtime-required values, or repository-owned environment examples/templates.

Compare the resulting runtime/configuration contract against repository-owned examples, documentation, deployment configuration, validation mechanisms and the authoritative base. Always classify the candidate explicitly as:

```text
Environment change: YES | NO
```

`YES` means the candidate changes the environment/configuration contract an operator, deployment or runtime must understand, even when application code provides a development default. When `Environment change: YES`, record every affected variable or configuration input with at least:

```text
- <name>
  Change: added | removed | renamed | semantics/default changed
  Production required: YES | NO | CONDITIONAL
  Expected value/default: <non-secret description>
  Secret: YES | NO
  Deployment action: <required action or NONE>
```

Never expose secret values. Synchronize `.env.example` or the repository's equivalent environment template when applicable, and update repository-owned deployment/runbook documentation when the operational contract changed. Discover and execute any repository-owned deterministic environment/configuration contract checker. If required environment documentation, synchronization, deployment instructions, or deterministic validation is missing, stale, contradictory or cannot be executed, treat that as a development blocker.

Do not emit `READY_FOR_CI` while an applicable required development check is failing, skipped, unknown, stale, or was run against an older candidate SHA. A required versioned derived artifact that is missing, stale, manually approximated instead of produced by the repository-owned mechanism, or would still change under an applicable deterministic generation/freshness check is also a development blocker. Reproducible diagnostic/report outputs that are not repository-declared versioned contracts are not required candidate files and do not block readiness solely because a committed snapshot is absent or stale. If a required check or required artifact synchronization cannot be executed in the current environment, report a development blocker instead of representing the candidate as ready.

These checks establish source-candidate development readiness only. They do not replace Qualification against the repository's effective candidate or synthetic merge candidate.

If Chat Coder is resumed after a Qualification failure, first identify the exact failing command/assertion and the validation/effective-candidate SHA that produced it. Correct the implementation when it violates the work contract; update or remove a test or contract only when it is demonstrably stale or superseded relative to the approved behavior. Never weaken, delete, bypass, or broaden an assertion merely to make CI green.

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
Environment change: YES | NO
Environment evidence: <NONE or concise candidate-bound evidence including affected inputs and deployment actions>
Review Critical: 0
Review Important: 0
Next stage: Qualification
```

Immediately before writing it, re-read the PR and prove `Candidate SHA == current PR head SHA`. Re-read the PR target and ensure it still matches the repository-authorized target for the active delivery context. The handoff is development evidence, not merge authority. Any later head change makes it stale; a target/context mismatch blocks the handoff until reconciled.

## Terminal report

Return:

```text
Development workflow = READY_FOR_CI
Issue = <identity>
Assignee = <authenticated GitHub user>
Delivery context = STANDARD | <explicit repository-approved context>
PR = <number> / Draft
Branch = <branch>
Candidate SHA = <sha>
Base SHA studied = <sha>
Validation = <fresh evidence for every applicable required development check>
Environment change = YES | NO
Environment action = <NONE or concise deployment/operator action>
Environment variables = <NONE or concise affected-variable list without secret values>
Review Critical = 0
Review Important = 0
Next owner = explicitly selected Qualification strategy
```

When `Environment change = YES`, the terminal report must make the operational consequence visible without requiring the user to inspect the PR comment. Do not use ambiguous wording such as "may require" when the candidate-bound analysis can classify the change.

Do not wait for final CI and do not continue into another controller unless the user's invocation explicitly composed that next stage or a previously explicit higher-level controller owns the continuation and delegated this Development stage under its durable contract.
