---
name: merge
description: "Generic Chat Integration controller that consumes current READY_FOR_MERGE evidence, integrates through repository-approved GitHub policy into the PR's authoritative target ref, verifies delivery, explicitly closes the associated work item, and returns COMPLETE."
version: "1.1.1"
stage: integration
status: active
---

# Merge — Integration and closeout

## Responsibility

Integrate an already-qualified exact candidate into the pull request's current authoritative target ref, verify repository delivery, and close the associated work item as part of Integration closeout.

```text
READY_FOR_MERGE
-> revalidate candidate/base/profile/review/merge policy
-> resolve current authoritative target ref from repository/PR policy
-> repository-approved integration
-> verify resulting target-ref state
-> explicitly close associated work item if still open
-> Project Done when supported/configured
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

## Integration

Resolve the current authoritative target ref from the PR base plus repository policy immediately before the side effect. Never retarget the PR merely to make integration possible.

Use the strongest repository-approved GitHub integration mechanism available. Respect the repository's required merge method and Merge Queue when present. Re-read identities immediately before the side effect and use an expected-head/conditional merge precondition when the platform exposes one.

Never force-push, rewrite history, bypass required repository safeguards or weaken current policy merely to merge.

## Delivery verification and closeout

After integration, prove the intended candidate/change reached the exact authoritative target ref that was qualified and integrated. Verify any repository-required post-merge delivery checks that are explicitly part of Integration policy. Do not invent a generic post-merge CI requirement.

Work-item closure is a required Integration closeout side effect, not a best-effort consequence of pull-request text:

- re-read the associated Issue/work item from the `READY_FOR_MERGE` identity;
- if it is already closed, verify that state and continue;
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

Closing the work item means the repository-defined development/integration outcome is complete. It does not generically assert that the target ref is production or that the change has been formally released/deployed; repositories with a separate release lifecycle record that later through their release policy.

Green qualification alone is not completion; a merged PR alone is not completion until required closeout is verified.

## Terminal report

On successful Integration and closeout, return:

```text
Workflow execution = COMPLETE
Issue = <identity> / closed
PR = <number> / merged
Candidate SHA = <qualified head>
Target ref = <authoritative PR base ref>
Merged/target SHA = <sha>
Qualification strategy = LOCAL | GITHUB_NATIVE
Qualification evidence = <durable reference>
Project = Done | not configured | unsupported
Delivery verification = PASS
```

`REQUALIFICATION_REQUIRED` is the pre-integration stale-evidence terminal. `CLOSEOUT_BLOCKED` is the post-integration terminal when the candidate reached the authoritative target but required work-item closure could not be verified.
