---
name: merge
description: "Generic Chat Integration controller that consumes current READY_FOR_MERGE evidence, integrates through repository-approved GitHub policy into the PR's authoritative target ref, verifies delivery, and returns COMPLETE."
version: "1.1.0"
stage: integration
status: active
---

# Merge — Integration and closeout

## Responsibility

Integrate an already-qualified exact candidate into the pull request's current authoritative target ref and verify repository delivery.

```text
READY_FOR_MERGE
-> revalidate candidate/base/profile/review/merge policy
-> resolve current authoritative target ref from repository/PR policy
-> repository-approved integration
-> verify resulting target-ref state
-> close work item / Project Done when supported
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

## Delivery verification

After integration, prove the intended candidate/change reached the exact authoritative target ref that was qualified and integrated. Verify any repository-required post-merge delivery checks that are explicitly part of Integration policy. Do not invent a generic post-merge CI requirement.

Then, when tooling/policy supports it:

- close the Issue/work item if not already closed;
- move its GitHub Project item to Done;
- verify final PR merged state and resulting target-ref SHA.

Closing the work item means the repository-defined development/integration outcome is complete. It does not generically assert that the target ref is production or that the change has been formally released/deployed; repositories with a separate release lifecycle record that later through their release policy.

Green qualification alone is not completion; a merged PR alone is not completion until required closeout is verified.

## Terminal report

Return:

```text
Workflow execution = COMPLETE
Issue = <identity> / closed or verified repository state
PR = <number> / merged
Candidate SHA = <qualified head>
Target ref = <authoritative PR base ref>
Merged/target SHA = <sha>
Qualification strategy = LOCAL | GITHUB_NATIVE
Qualification evidence = <durable reference>
Project = Done | not configured | unsupported
Delivery verification = PASS
```
