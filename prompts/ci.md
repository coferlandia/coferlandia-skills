---
name: ci
description: "Generic Chat GitHub-native Qualification controller resolved directly, by explicit composition, or by the declared standalone Chat Coder default pipeline."
version: "1.4.0"
stage: qualification
status: active
---

# CI — GitHub-native Qualification

## Responsibility

Qualify one exact development candidate through the repository's GitHub-native CI contract.

```text
READY_FOR_CI
-> validate repository CI profile
-> resolve exact current candidate/base
-> re-check environment/configuration declaration
-> request or observe profile-defined GitHub qualification
-> diagnose bounded failures
-> prove current required gates GREEN
-> READY_FOR_MERGE (strategy = GITHUB_NATIVE)
```

This controller **must not merge** and must not silently switch to Local CI.

## Invocation boundary

This is a Chat prompt controller, not an Agent Skill. Load it only when the current resolved sequence selects `ci`, whether that selection came from:

- a direct `ci`, `gh ci`, or `github ci` invocation;
- an explicit left-to-right composition containing that alias; or
- the registry-declared standalone `chat coder` / `chat-coder` default sequence.

The existence of `READY_FOR_CI`, discovery of Agent Skills, or completion of a bounded Development stage does **not** by itself invoke this controller. Standalone `chat dev` / `chat-dev` stops at `READY_FOR_CI`. The Chat Coder default invokes this stage because the registry resolved it before Development began, not because a handoff state was discovered afterward. Agent Skill/local Qualification belongs to `local-ci`; do not load this prompt as an inferred alternative or fallback.

Once this prompt is resolved, the Qualification strategy is `GITHUB_NATIVE`; do not ask a second strategy-selection question.

## Entry contract

Require all of:

1. a current durable `READY_FOR_CI` handoff matching `_protocol/delivery/READY_FOR_CI.md`;
2. current PR head equals its Candidate SHA;
3. `.coferlandia/ci/profile.json` exists and validates against the central profile contract;
4. the profile contains a GitHub qualification definition and current profile fingerprint;
5. the handoff contains `Base SHA synchronized`, and for a base-sensitive profile the current authoritative base SHA still equals that synchronized SHA and remains reconciled into the candidate.

If any precondition is stale or missing, fail closed. Do not infer readiness from chat history, old comments, old checks, cancelled runs or a different SHA. A base-sensitive current-base mismatch is `DEVELOPMENT_CURRENTIZATION_REQUIRED`; it must be resolved in Development before any operation that can submit or trigger expensive Qualification.

## Repository and profile authority

The target repository owns its actual workflows, checks, scripts, services and policy. The profile only points to those facts. Re-read referenced repository documentation and authoritative GitHub state before acting. Never invent a workflow/check name or terminal conclusion.

## Current-base qualification barrier

Before any operation that can submit, trigger, or intentionally observe a new expensive Qualification run, re-read the authoritative development base and the `Base SHA synchronized` recorded in `READY_FOR_CI`.

When the profile declares `identity.base_sensitive = true`, require the current authoritative base SHA to equal the synchronized base SHA and require repository/Git evidence that the current candidate is reconciled with that base. If the base moved, do **not** currentize the branch inside Qualification and do not start expensive CI. Return:

```text
DEVELOPMENT_CURRENTIZATION_REQUIRED
Candidate SHA: <current PR head>
Synchronized base SHA: <READY_FOR_CI base>
Current authoritative base SHA: <current base>
```

If this `ci` stage was reached from an already-resolved sequence that includes the upstream Development controller, hand control back to that Development flow to currentize, rerun cheap Development validation/review, refresh `READY_FOR_CI`, then re-enter the same selected Qualification strategy. A direct standalone `ci` invocation reports the state and stops rather than implicitly inventing Development authority.

A profile with `identity.base_sensitive = false` follows its declared identity policy; do not impose current-base equality that the repository explicitly disabled.

## Environment / configuration qualification barrier

Before accepting the development handoff for GitHub-native qualification, re-evaluate the exact candidate against the authoritative base for environment/configuration impact. Inspect changed environment variables, secrets/deployment credentials, application settings/configuration fields, compose/container inputs, deployment/runtime-required values and repository-owned environment examples/templates.

The `READY_FOR_CI` handoff must declare exactly one of:

```text
Environment change: YES
Environment change: NO
```

Fail closed when the declaration is missing, ambiguous or contradicted by the candidate. In particular, if the candidate appears to add, remove, rename, change defaults/requirements, or change semantics of environment/configuration inputs while the handoff says `Environment change: NO`, Qualification must stop until the development handoff is corrected on the exact current candidate.

When `Environment change: YES`, require candidate-bound evidence covering every affected input, production requirement, non-secret expected value/default description, secret classification and deployment/operator action. Re-check that repository-owned environment templates and deployment/runbook documentation are synchronized when applicable and that any repository-owned deterministic environment/configuration contract checker is fresh and passing. Never expose or request secret values as qualification evidence.

This barrier validates that environment impact was recognized and mechanically checked where the repository provides such checks; it does not invent repository-specific environment policy.

## Qualification

1. Resolve current PR, exact head, authoritative base, synchronized base and profile fingerprint, and pass the current-base qualification barrier.
2. Determine the profile-declared GitHub submission mode. Trigger only the declared workflow/operation when explicit dispatch is required; otherwise observe the repository's existing PR-event qualification. Never introduce `workflow_dispatch` merely because this controller is GitHub-native when the profile declares existing PR-event submission.
3. Read current workflow/check evidence for the exact authoritative candidate. Queued, waiting, requested, pending or in-progress is not GREEN.
4. Evaluate every profile-required gate against its explicit allowed terminal conclusions. Missing, stale, superseded, cancelled or old-SHA evidence never satisfies the gate.
5. If Merge Queue/`merge_group` is declared authoritative when present, bind qualification to that exact effective candidate rather than reusing older PR-head evidence.

### Non-terminal GitHub Actions state

Queued, waiting, requested, pending, or in-progress evidence is a non-terminal Qualification state, not success and not automatically a blocker. During the active execution, continue observing the authoritative exact-SHA gate when the available GitHub surface permits it. Do not ask the user to issue a separate `ci` command merely because a required run is still progressing.

If the required external GitHub Actions work remains non-terminal beyond what the active execution can observe, return a resumable state with no success claim:

```text
Qualification workflow = WAITING_CI
Issue = <identity>
PR = <number>
Candidate SHA = <sha>
Qualification strategy = GITHUB_NATIVE
Run/check = <authoritative identifier>
Current status = queued | waiting | requested | pending | in_progress
Next stage after GREEN = Merge | terminal READY_FOR_MERGE
```

On reentry, reconstruct the exact PR/head/profile/run state from GitHub rather than trusting the old waiting report. A stale or superseded run never becomes evidence for the current candidate.

## Failure loop

For a current RED gate, inspect the exact failing run/job/check. Classify repository/product defect versus transient/provider failure. When Chat capabilities and the approved work contract allow a bounded correction, use systematic debugging, add/regress the failing behavior where appropriate, perform fresh focused validation/review, push a new candidate through the repository-approved development flow, refresh `READY_FOR_CI`, and restart GitHub-native qualification for that new SHA.

A new candidate invalidates old qualification evidence. Do not switch to Local CI because GitHub-native qualification failed or is unavailable.

## Durable READY_FOR_MERGE

Only after every current required GitHub-native gate is authoritative and allowed-GREEN for the exact effective candidate, create/update one idempotent managed PR comment per `_protocol/delivery/READY_FOR_MERGE.md` using:

```html
<!-- coferlandia-ready-for-merge:v1 -->
```

Minimum payload:

```text
State: READY_FOR_MERGE
Issue: <identity>
PR: <number>
Candidate SHA: <current PR head>
Qualified base SHA: <authoritative base/effective base>
Effective candidate: <PR head or merge_group SHA>
Qualification strategy: GITHUB_NATIVE
CI profile fingerprint: <sha256>
Qualification evidence: <workflow/check/run identifiers and conclusions>
Review Critical: 0
Review Important: 0
Next stage: Merge
```

Re-read PR/base/profile immediately before writing the handoff. If any identity changed, qualification is stale.

## Terminal report

When Qualification is the terminal resolved stage, return `READY_FOR_MERGE` with exact candidate/base/profile/evidence, `WAITING_CI` for a still-authoritative non-terminal external run, or a precise failure/blocker state.

When the resolved sequence contains `merge` next, including the standalone Chat Coder default, treat `READY_FOR_MERGE` as an internal durable handoff and yield immediately to `merge` without asking the user for confirmation. Never invoke `merge` merely because `READY_FOR_MERGE` exists; it must already be the next resolved stage.
