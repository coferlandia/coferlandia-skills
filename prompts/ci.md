---
name: ci
description: "Generic Chat GitHub-native Qualification controller, loaded only by explicit `ci`/`gh ci`/`github ci` prompt invocation, that consumes READY_FOR_CI plus a repository CI profile and emits exact-candidate READY_FOR_MERGE evidence."
version: "1.2.0"
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

This is a Chat prompt controller, not an Agent Skill. Load it only when the controlling request explicitly resolves `ci`, `gh ci`, or `github ci` through the prompt registry, including an explicit left-to-right composition that contains that alias.

The existence of `READY_FOR_CI`, discovery of Agent Skills, or completion of a bounded controller such as `chat-coder` does **not** invoke this controller. A standalone `chat-coder` request stops at `READY_FOR_CI`. Agent Skill/local Qualification belongs to `local-ci`; do not load this prompt as an inferred alternative or fallback.

Once this prompt is explicitly invoked, the Qualification strategy is `GITHUB_NATIVE`; do not ask a second strategy-selection question.

## Entry contract

Require all of:

1. a current durable `READY_FOR_CI` handoff matching `_protocol/delivery/READY_FOR_CI.md`;
2. current PR head equals its Candidate SHA;
3. `.coferlandia/ci/profile.json` exists and validates against the central profile contract;
4. the profile contains a GitHub qualification definition and current profile fingerprint.

If any precondition is stale or missing, fail closed. Do not infer readiness from chat history, old comments, old checks, cancelled runs or a different SHA.

## Repository and profile authority

The target repository owns its actual workflows, checks, scripts, services and policy. The profile only points to those facts. Re-read referenced repository documentation and authoritative GitHub state before acting. Never invent a workflow/check name or terminal conclusion.

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

1. Resolve current PR, exact head, authoritative base and profile fingerprint.
2. Determine the profile-declared GitHub submission mode. Trigger only the declared workflow/operation when explicit dispatch is required; otherwise observe the repository's existing PR-event qualification. Never introduce `workflow_dispatch` merely because this controller is GitHub-native when the profile declares existing PR-event submission.
3. Read current workflow/check evidence for the exact authoritative candidate. Queued, waiting, requested, pending or in-progress is not GREEN.
4. Evaluate every profile-required gate against its explicit allowed terminal conclusions. Missing, stale, superseded, cancelled or old-SHA evidence never satisfies the gate.
5. If Merge Queue/`merge_group` is declared authoritative when present, bind qualification to that exact effective candidate rather than reusing older PR-head evidence.

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

Return `READY_FOR_MERGE` with exact candidate/base/profile/evidence, or a resumable waiting/failure state. Do not invoke `merge.md` unless the user's original composition explicitly requested it.
