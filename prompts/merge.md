---
name: merge
description: "Generic Chat Integration controller that consumes current READY_FOR_MERGE evidence, integrates through repository-approved GitHub policy, verifies delivery, and returns COMPLETE."
version: "1.0.0"
stage: integration
status: active
---

# Merge — Integration and closeout

## Responsibility

Integrate an already-qualified exact candidate and verify repository delivery.

```text
READY_FOR_MERGE
-> revalidate candidate/base/profile/review/merge policy
-> repository-approved integration
-> verify resulting default branch state
-> close work item / Project Done when supported
-> COMPLETE
```

This controller **must not execute CI**. If qualification is missing or stale, return `REQUALIFICATION_REQUIRED` and stop. Never call `ci.md` or Local CI implicitly.

## Entry contract

Require a current durable `READY_FOR_MERGE` handoff matching `_protocol/delivery/READY_FOR_MERGE.md`. Re-read authoritative repository/GitHub state and prove:

- Issue/work item and PR identities still match;
- current PR head equals qualified Candidate SHA;
- authoritative base/effective candidate still satisfies the recorded identity rule;
- CI profile fingerprint still matches the profile used for qualification;
- required review state remains valid;
- the PR is open and mergeable under current repository policy;
- any repository-declared Merge Queue/merge-group authority is current.

If head/base/effective candidate/profile or required gate authority changed, return:

```text
REQUALIFICATION_REQUIRED
Reason: <exact stale identity/evidence>
Qualified strategy: LOCAL | GITHUB_NATIVE
```

Do not choose a strategy or rerun it.

## Integration

Use the strongest repository-approved GitHub integration mechanism available. Respect the repository's required merge method and Merge Queue when present. Re-read identities immediately before the side effect and use an expected-head/conditional merge precondition when the platform exposes one.

Never force-push, rewrite history, bypass required repository safeguards or weaken current policy merely to merge.

## Delivery verification

After integration, prove the intended candidate/change reached the authoritative default branch and verify any repository-required post-merge delivery checks that are explicitly part of Integration policy. Do not invent a generic post-merge CI requirement.

Then, when tooling/policy supports it:

- close the Issue/work item if not already closed;
- move its GitHub Project item to Done;
- verify final PR merged state and resulting default-branch SHA.

Green qualification alone is not completion; a merged PR alone is not completion until required closeout is verified.

## Terminal report

Return:

```text
Workflow execution = COMPLETE
Issue = <identity> / closed or verified repository state
PR = <number> / merged
Candidate SHA = <qualified head>
Merged/default-branch SHA = <sha>
Qualification strategy = LOCAL | GITHUB_NATIVE
Qualification evidence = <durable reference>
Project = Done | not configured | unsupported
Delivery verification = PASS
```
