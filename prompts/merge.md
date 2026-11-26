---
name: merge
description: "Generic Chat Integration controller that consumes current READY_FOR_MERGE evidence, integrates through repository-approved GitHub policy into the PR's authoritative target ref, verifies delivery, applies the explicit work-item closeout disposition, and returns COMPLETE."
version: "1.1.2"
stage: integration
status: active
---

# Merge — Integration and closeout

## Responsibility

Integrate an already-qualified exact candidate into the pull request's current authoritative target ref, verify repository delivery, and apply the controlling work item's explicit closeout disposition.

```text
READY_FOR_MERGE
-> revalidate candidate/base/profile/review/merge policy
-> resolve CLOSE (default) or authorized KEEP_OPEN
-> resolve current authoritative target ref from repository/PR policy
-> repository-approved integration
-> verify resulting target-ref state
-> CLOSE: explicitly close associated work item if still open
   KEEP_OPEN: verify associated work item remains open
-> Project projection consistent with the selected disposition when supported/configured
-> COMPLETE
```

This controller **must not execute CI**. If qualification is missing or stale, return `REQUALIFICATION_REQUIRED` and stop. Never call `ci.md` or Local CI implicitly.

The integration target is not generically hardcoded to the repository default branch. The current PR/repository policy owns the target ref. A simple repository may still use its default branch for every ordinary delivery; a repository with a separate integration branch may use that branch instead.

## Entry contract

Require a current durable `READY_FOR_MERGE` handoff matching `_protocol/delivery/READY_FOR_MERGE.md`. Re-read authoritative repository/GitHub state and prove:

- Issue/work item and PR identities still match;
- current PR head equals qualified Candidate SHA;
- current PR base ref is the authoritative integration target permitted by repository policy;
- authoritative base/effective candidate still satisfies the recorded identity rule;
- CI profile fingerprint still matches the profile used for qualification;
- required review state remains valid;
- the PR is open and mergeable under current repository policy;
- any repository-declared Merge Queue/merge-group authority is current.

If head/base ref/base SHA/effective candidate/profile or required gate authority changed, return:

```text
REQUALIFICATION_REQUIRED
Reason: <exact stale identity/evidence>
Qualified strategy: LOCAL | GITHUB_NATIVE
```

Do not choose a strategy or rerun it.

### Work-item closeout disposition

Resolve closeout from the durable `READY_FOR_MERGE` record:

- `CLOSE` is the ordinary completed-work-item disposition.
- For backward compatibility, absence means `CLOSE`.
- `KEEP_OPEN` is valid only when `Closeout authority` names durable current evidence that explicitly requires the same controlling work item to remain open across this partial delivery.

Do not infer `KEEP_OPEN` from issue labels, title words such as epic/umbrella/parent, milestones, branch names, PR naming, project hierarchy, or incomplete-looking acceptance criteria. The closeout decision is control authority, not classification.

Before integration, re-read the referenced `KEEP_OPEN` authority and the controlling work item. If the authority is missing, stale, ambiguous, applies to a different work item, or contradicts current repository/supervisor policy, do not merge and return:

```text
CLOSEOUT_POLICY_CONFLICT
Issue: <identity>
PR: <number> / not merged
Reason: <missing, stale, ambiguous, mismatched, or contradictory closeout authority>
```

For `KEEP_OPEN`, if the work item is already closed before integration, also return `CLOSEOUT_POLICY_CONFLICT`; do not use close-then-reopen or reopen-then-merge as a normal lifecycle repair. For `CLOSE`, an already closed work item is an idempotent valid closeout state.

## Integration

Resolve the current authoritative target ref from the PR base plus repository policy immediately before the side effect. Never retarget the PR merely to make integration possible.

Use the strongest repository-approved GitHub integration mechanism available. Respect the repository's required merge method and Merge Queue when present. Re-read identities immediately before the side effect and use an expected-head/conditional merge precondition when the platform exposes one.

Never force-push, rewrite history, bypass required repository safeguards or weaken current policy merely to merge.

## Delivery verification and closeout

After integration, prove the intended candidate/change reached the exact authoritative target ref that was qualified and integrated. Verify any repository-required post-merge delivery checks that are explicitly part of Integration policy. Do not invent a generic post-merge CI requirement.

### CLOSE

Work-item closure is a required Integration closeout side effect when the disposition is `CLOSE`, not a best-effort consequence of pull-request text:

- re-read the associated Issue/work item from the `READY_FOR_MERGE` identity;
- if it is already closed, verify that state and continue idempotently;
- if it is open, explicitly close it through the available Issue/work-item mutation surface after the integration is verified;
- do **not** rely on `Closes`, `Fixes`, `Resolves`, linked-PR metadata, or repository-default-branch behavior to perform that closure;
- a merge into a repository-approved non-default integration target is sufficient to trigger this explicit closeout when that target is the authoritative development/integration outcome;
- after the close operation, re-read the work item and verify it is closed before reporting `COMPLETE`.

GitHub Project projection remains separate from Issue closure. When a Project is configured and the active tooling/policy supports it, move the item to Done and verify the projection. Lack of optional Project mutation support does not reopen an otherwise completed Issue.

If the associated work item is still open and the active Integration surface cannot close it, or if the explicit close operation fails, return:

```text
CLOSEOUT_BLOCKED
Issue: <identity> / still open
PR: <number> / merged
Target ref: <authoritative PR base ref>
Reason: <missing capability or close failure>
```

Do not report `COMPLETE` while required work-item closure is unverified.

### KEEP_OPEN

For an authorized partial delivery, the controlling work item must remain open after the merge:

- re-read the work item after delivery verification;
- if it is already open, verify that state and continue idempotently;
- do not close it, and do not manufacture a transient close followed by reopen;
- Project Done must not be applied for this partial delivery;
- when Project state is configured and readable, verify the item is not Done; when the active surface cannot read or mutate that optional projection, report that limitation explicitly and never claim Project synchronization.

If the issue is unexpectedly closed after integration, or a configured/verifiable Project is already Done and cannot be corrected by the authorized surface, return `CLOSEOUT_BLOCKED` with the actual state. Do not silently reopen or rewrite Project state merely to make closeout appear successful.

Closing or preserving the work item describes only the repository-defined development/integration boundary. It does not generically assert that the target ref is production or that the change has been formally released/deployed; repositories with a separate release lifecycle record that later through their release policy.

Green qualification alone is not completion; a merged PR alone is not completion until the selected closeout disposition is verified.

## Terminal report

On successful Integration and closeout, return:

```text
Workflow execution = COMPLETE
Work-item closeout = CLOSE | KEEP_OPEN
Issue = <identity> / closed | open (KEEP_OPEN verified)
PR = <number> / merged
Candidate SHA = <qualified head>
Target ref = <authoritative PR base ref>
Merged/target SHA = <sha>
Qualification strategy = LOCAL | GITHUB_NATIVE
Qualification evidence = <durable reference>
Project = Done | not configured | not Done (KEEP_OPEN verified) | unsupported/unverified
Delivery verification = PASS
```

`REQUALIFICATION_REQUIRED` is the pre-integration stale-evidence terminal. `CLOSEOUT_POLICY_CONFLICT` is the pre-integration terminal for invalid or contradictory closeout authority. `CLOSEOUT_BLOCKED` is the post-integration terminal when the candidate reached the authoritative target but the selected work-item closeout disposition could not be verified.
