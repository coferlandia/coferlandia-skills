---
name: hotfix
description: "Generic explicit emergency-remediation Chat controller that turns an existing Issue or free-form bug report into a repository-approved hotfix flow with durable permanent-fix follow-up when mitigation is temporary."
version: "1.1.0"
stage: hotfix
status: active
---

# Hotfix — Emergency remediation controller

## Responsibility

Turn one explicitly requested urgent bug report into the smallest safe repository-approved production correction while preserving exact evidence and any permanent follow-up debt.

Supported entry forms include:

```text
hotfix #123
hotfix: <free-form bug report>
```

This is a high-level orchestration controller. It does **not** replace or duplicate the repository's development controller, qualification gates, integration policy, release publisher, deployment authority, or post-merge verification.

Conceptually:

```text
explicit hotfix request
-> create/reuse primary Issue
-> preserve original report
-> diagnose and bound blast radius
-> classify PERMANENT | TEMPORARY_MITIGATION
-> create mandatory permanent-fix Issue when temporary
-> establish durable HOTFIX contract
-> invoke repository-approved hotfix development flow
-> exact READY_FOR_CI candidate
-> repository-approved emergency qualification
-> emergency integration
-> release/publication when repository policy requires it
-> generic coferlandia-deploy when repository policy requires production stabilization
-> exact release deployed HEALTHY
-> HOTFIX_STABILIZED
-> repository-defined post-deploy reconciliation/verification
-> HOTFIX_COMPLETE
```

## Invocation boundary

Load this controller only from an explicit `hotfix` invocation. A bug report, failing test, production-looking error, urgent wording, or severity label does not by itself authorize the exceptional hotfix path.

The explicit invocation is authority to attempt the repository's declared hotfix path; it is not authority to bypass safeguards. If the repository has no approved hotfix policy or the candidate cannot satisfy it safely, fail closed with `HOTFIX_BLOCKED`.

## Repository authority

Reconstruct current state from repository instructions and authoritative GitHub evidence. Do not hardcode a branch name, production ref, workflow/check, merge method, release version, deployment mechanism, Project ID, runner, or reconciliation topology.

Resolve the repository-approved emergency source/target, development surface, qualification contract, integration mechanism, publication policy, production-stabilization requirement/deployment authority and any post-deploy reconciliation/verification. Repository-specific facts belong in repository policy/configuration rather than this prompt.

## Primary Issue

For `hotfix #<id>`, verify that the referenced work item actually represents the reported incident and reuse it.

For a free-form report:

1. preserve the user's original report verbatim or by durable attachment/reference;
2. search current open/recent work for an unequivocal matching incident before creating anything;
3. reuse an existing matching Issue only when identity is clear;
4. otherwise create one primary bug Issue containing, as evidence permits:
   - observed behavior;
   - expected behavior;
   - reproduction/evidence;
   - impact;
   - known constraints;
   - acceptance criterion for production stabilization.

Do not fabricate reproduction steps, impact, root cause or certainty. Mark unknown facts as unknown and continue only when the hotfix can still be bounded safely.

## Diagnosis and resolution strategy

After establishing the primary Issue and repository-approved emergency target, create/update the durable HOTFIX record with `State: HOTFIX_PLANNED` and `Resolution strategy: UNRESOLVED` while diagnosis is still in progress. `UNRESOLVED` is evidence of incomplete classification, not an executable hotfix strategy.

Study the smallest relevant surface and establish the best-supported root cause or causal hypothesis before choosing the emergency correction. Prefer a permanent correction when it is small, safe, reviewable and validatable within the repository's hotfix budget.

Before `HOTFIX_READY`, classify exactly one executable strategy:

```text
Resolution strategy: PERMANENT
```

or:

```text
Resolution strategy: TEMPORARY_MITIGATION
```

Choose `TEMPORARY_MITIGATION` only when production can be stabilized safely but the permanent correction would materially increase emergency risk, for example because it requires broad refactoring, architectural redesign, destructive/risky migration, cross-system coordination, unresolved research, or a validation surface too large for the approved hotfix lane.

Urgency alone is not justification for an unsafe workaround. If neither a bounded permanent fix nor a bounded temporary mitigation is defensible, update the durable contract to `HOTFIX_BLOCKED`, preserve `Resolution strategy: UNRESOLVED`, record the concrete blocker, and stop. Never invent a strategy merely to make the record structurally complete.

## Mandatory permanent follow-up for temporary mitigation

A temporary mitigation is not allowed to become `HOTFIX_READY` until a distinct permanent-fix Issue exists and is durably linked to the primary hotfix Issue.

The follow-up Issue must be ordinary non-emergency work unless repository policy explicitly says otherwise. It must preserve enough context for a future independent agent, including at least:

```text
Originating hotfix: <Issue/PR reference>
Temporary mitigation: <what was changed to stabilize production>
Known/probable root cause: <evidence-backed statement or UNKNOWN>
Why permanent fix was deferred: <reason>
Required final behavior: <acceptance outcome>
Temporary surfaces to remove/replace: <code/config/flag/fallback references>
Removal criteria: <conditions proving mitigation can be removed>
Regression/prevention coverage: <tests/contracts/monitoring/invariants to add or preserve>
Related release: PENDING | <release reference>
```

Do not create this second Issue for a genuinely `PERMANENT` hotfix merely to satisfy ceremony.

## Durable hotfix contract

Create/update an idempotent managed record per `_protocol/delivery/HOTFIX.md` using:

```html
<!-- coferlandia-hotfix:v1 -->
```

At planning time record the primary Issue, current strategy (`UNRESOLVED` while diagnosis is incomplete), follow-up debt, repository-approved target and temporary-removal information.

Before emergency qualification, update it to `HOTFIX_READY` only after the strategy is resolved to `PERMANENT` or `TEMPORARY_MITIGATION` and the repository-approved development controller has produced current durable `READY_FOR_CI` evidence for the exact hotfix PR head. Bind `Candidate SHA` to that exact head.

Any head change invalidates `HOTFIX_READY` until development validation/review and the hotfix record are refreshed.

## Development delegation

Do not reimplement TDD, implementation, cheap development validation or code review in this controller. Invoke the repository-approved development controller in its explicitly declared emergency delivery mode and pass the primary work contract plus hotfix metadata.

When the repository uses generic `chat-coder`, it remains the owner of Development and `READY_FOR_CI`; the hotfix controller supplies the explicit exceptional delivery context so repository policy can resolve the appropriate base/target. Never invent an exceptional branch simply because this prompt was invoked.

If development discovers that the chosen mitigation is unsafe, broader than represented, or no longer satisfies the selected strategy, return to Diagnosis, update the durable hotfix contract and ensure temporary follow-up invariants still hold before proceeding.

## Qualification and integration

Use only the repository-declared emergency qualification path for the exact current candidate. Do not silently substitute ordinary FULL release qualification, Local CI, GitHub-native CI, or any other strategy unless repository policy explicitly declares it as the hotfix contract.

Current queued/pending work is not GREEN. Old-SHA, superseded, cancelled or unrelated evidence never authorizes integration.

After qualification succeeds, integrate only through repository-approved safeguards. Do not force-push, bypass required controls or weaken tests/checks to make the emergency path pass.

## Release, deployment, reconciliation and verification

When repository policy requires a formal release for a hotfix, pass the exact integrated commit to `coferlandia-release-publisher`; do not duplicate its SemVer/tag/GitHub Release logic. The repository decides whether the emergency release must be PATCH-compatible or follows another declared version policy.

When repository policy requires production stabilization through deployment, do not stop at a merely deployable release. After the exact release is formally published and verified, delegate immediately to generic `coferlandia-deploy` with the immutable release identity and the independently known exact expected SHA. The deployment skill resolves only the repository-declared authority; this controller must not implement host commands, provider state transitions, SSH fallbacks or deployment mechanics.

Production is `HOTFIX_STABILIZED` only when durable deployment evidence proves that the exact release resolved to the expected SHA and the declared deployment authority returned `HEALTHY`. A release/SHA mismatch, conflicting active deployment or unavailable authority remains fail-closed and resumable rather than permission to invent an emergency deployment path.

Treat stabilization and engineering closeout as distinct milestones. Perform repository-declared post-deploy reconciliation and verification after stabilization when policy classifies them as closeout guarantees. Examples may include reconciling the production line back into a development line or running asynchronous broad validation, but this prompt must not assume concrete branch names or workflows. Repository-declared post-deploy work **must not block production stabilization**.

When a release or deployment identity becomes known, update the primary Issue and, for temporary mitigation, the permanent-fix Issue with the durable release/PR/deployment references required by repository policy.

## Completion semantics

`HOTFIX_STABILIZED` means the production-restoration boundary is proven: the exact formal release is bound to the expected integrated SHA and the repository-declared deployment authority reports `HEALTHY`. It does not imply that broader reconciliation or verification has completed.

For `PERMANENT`, `HOTFIX_COMPLETE` means the emergency correction is integrated, production stabilization is complete when required, and all repository-required publication/post-deploy reconciliation/verification closeout has succeeded.

For `TEMPORARY_MITIGATION`, `HOTFIX_COMPLETE` means production stabilization is complete **while permanent resolution remains open**. Do not describe the structural bug as permanently fixed.

Terminal report example:

```text
HOTFIX workflow = COMPLETE
Primary issue = <identity>
Resolution strategy = TEMPORARY_MITIGATION
Production mitigation = COMPLETE
Production stabilization = HOTFIX_STABILIZED | repository-declared NONE
Candidate/integrated SHA = <sha>
Release = <release or NONE per repository policy>
Deployment evidence = <provider event/reference or NONE per repository policy>
Permanent resolution = PENDING <follow-up Issue>
Post-deploy verification = PASS | repository-defined pending state
```

Blocked example:

```text
HOTFIX workflow = HOTFIX_BLOCKED
Primary issue = <identity>
Resolution strategy = UNRESOLVED | <resolved strategy if blocking occurred later>
Reason = <concrete safety/policy/evidence blocker>
Permanent resolution = <existing follow-up or NONE>
```

A temporary mitigation must never report permanent resolution as complete merely because production symptoms stopped.
