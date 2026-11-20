---
name: coferlandia-deploy
description: >
  Use when a formal immutable release must be deployed to a repository-declared environment through
  its approved deployment authority, especially for HOTFIX production stabilization, exact release/SHA
  verification, idempotent re-entry, or machine-readable deployment evidence. Not for release publication,
  arbitrary host commands, mutable-branch deployment, or choosing infrastructure ad hoc.
license: Apache-2.0
compatibility: >
  Requires a repository deployment declaration, an immutable formal release, the exact expected
  40-character commit SHA, and access to the declared deployment authority. The initial supported
  authority is cofer-vm-admin through its non-interactive exact-release interface.
metadata:
  author: coferlandia
  version: "1.0"
  category: ops
  status: active
  tested: "2026-11-20 - contract and pressure cases cover exact identity, fail-closed authority, provider-state ownership, idempotent HEALTHY re-entry, and HOTFIX stabilization integration."
---

## Context

This skill owns exactly **published immutable release -> declared deployment authority -> terminal deployment evidence**.

It does not publish releases and it does not implement a deployment engine. The repository declares
where production lives and which authority owns mutation. The provider owns its internal execution
states and host mechanics.

The generic contract is:

```text
immutable release + expected SHA
        |
repository-declared deployment authority
        |
verify resolved SHA == expected SHA
        |
provider deployment / exact-identity re-entry
        |
HEALTHY | FAILED | BLOCKED
```

For `cofer-vm-admin`, the provider remains the sole owner of PREPARING, DEPLOYING, CHECKING and
HEALTHY. This skill **must not mirror** those states or reproduce the Host Agent/deployment adapter.

## Prerequisites

1. A formal immutable release identity already exists.
2. The caller supplies the exact expected SHA independently from the deployment provider.
3. Repository policy declares the target environment, deployment authority and application identity.
4. The declared authority is reachable through its approved non-interactive surface.

The preferred Coferlandia declaration is an optional sibling in
`.coferlandia/release/policy.json`:

```json
{
  "deployment": {
    "production": {
      "authority": "cofer-vm-admin",
      "target": "<target-id>",
      "application_id": "<application-id>"
    }
  }
}
```

This declaration selects an authority; it never contains an arbitrary command, executable, secret
or mutable Git ref.

## Workflow

1. Read repository policy and resolve the requested environment.
2. Fail `BLOCKED` when the deployment declaration is absent, ambiguous, unsupported or unavailable.
3. Verify that the caller supplied an immutable release identity and a full expected SHA. Never turn
   a branch such as `main` into deployment authority.
4. Invoke only the repository-declared provider with:
   - application identity;
   - immutable release tag;
   - expected SHA;
   - durable audit actor/causality when supported.
5. Require the provider's resolved SHA to equal the expected SHA before accepting mutation evidence.
   A mismatch is `BLOCKED`, never an emergency override.
6. Normalize the provider's terminal result:
   - `HEALTHY`: deployment or exact-identity no-op succeeded;
   - `FAILED`: the declared provider executed the requested deployment but ended unsuccessfully;
   - `BLOCKED`: mutation was not authorized/started because identity, policy, authority or conflict
     preconditions failed.
7. Persist or return the provider's deployment event/reference as deployment evidence.
8. On re-entry, if the exact same application/release/SHA is already HEALTHY, return HEALTHY as a
   no-op. Do not redeploy merely to recreate evidence.
9. If another identity is actively deploying, return `BLOCKED`; never hijack or bypass it.
10. If the declared provider is unavailable, return `BLOCKED`. Never fall back to SSH, a host
    script, Docker, a mutable branch, or any other arbitrary command path.

### cofer-vm-admin provider

When `authority: cofer-vm-admin`, use its supported non-interactive exact-release operation. The
semantic request is:

```text
application_id
immutable release
expected SHA
audit actor
```

The provider resolves the GitHub Release, verifies exact SHA identity, reuses existing HEALTHY or
same-identity active history when appropriate, and otherwise runs its existing deployment
orchestrator. Treat that provider result as authority; do not reimplement its state machine.

## HOTFIX use

When an explicitly invoked HOTFIX requires production stabilization, the emergency controller may
delegate here immediately after formal publication is verified.

A successful exact deployment gives the HOTFIX durable evidence for `HOTFIX_STABILIZED`. Repository
post-deploy reconciliation, broad validation or administrative closeout may still be required for
`HOTFIX_COMPLETE`, but repository-declared post-deploy work must not be pulled back onto the
production-stabilization critical path.

## Expected Output

```text
Deployment authority: <authority>
Deployment target: <target>
Application: <application-id>
Release: <immutable-release>
Expected SHA: <40-char-sha>
Resolved SHA: <40-char-sha>
Deployment event: <provider-event-reference>
Deployment evidence: <durable-reference>
Status: HEALTHY | FAILED | BLOCKED
Mode: DEPLOYED | NO_OP | NONE
```

Provider-specific transient states remain provider evidence and are not copied into this contract.

## Gotchas

- **Treating publication as deployment:** release publication establishes immutable identity; this
  skill starts only after that identity exists.
- **Emergency SHA mismatch override:** prohibited. A release resolving to a different SHA is
  `BLOCKED` before mutation.
- **Redeploying an already HEALTHY exact identity:** unnecessary risk. Exact re-entry is a no-op.
- **Fallback SSH or host command:** prohibited. Provider unavailability is a blocker, not permission
  to invent another deployment authority.
- **Waiting for post-deploy closeout before reporting stabilization:** wrong when repository policy
  classifies that work as post-deploy. HEALTHY exact deployment is the stabilization boundary.
- **Copying provider states into Skills:** PREPARING/DEPLOYING/CHECKING remain provider-owned; this
  contract normalizes only terminal evidence.

## Output Location

Transient local evidence generated by this skill goes under `.agent/deploy/`.
Durable deployment authority remains the provider's own history/event plus repository-required
HOTFIX/Issue evidence.
