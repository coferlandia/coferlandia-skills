# HOTFIX v1

Default durable marker:

```html
<!-- coferlandia-hotfix:v1 -->
```

The contract is an idempotent managed lifecycle record for an explicitly requested emergency remediation. It may be maintained on the primary Issue while planning and on the hotfix PR once a candidate exists. Repository policy decides the concrete storage location, but current state must be reconstructable from GitHub/repository evidence rather than chat history.

Required fields:

```text
State: HOTFIX_PLANNED | HOTFIX_READY | HOTFIX_STABILIZED | HOTFIX_COMPLETE | HOTFIX_BLOCKED
Primary issue: <identity>
Resolution strategy: UNRESOLVED | PERMANENT | TEMPORARY_MITIGATION
Permanent fix issue: NONE | <identity>
Target ref: <repository-approved emergency integration target>
Candidate SHA: PENDING | <exact hotfix PR head>
READY_FOR_CI evidence: PENDING | <durable reference>
Reason temporary: NONE | <why the permanent correction is outside the safe hotfix budget>
Temporary surfaces: NONE | <durable code/config/flag/fallback references to remove>
Removal criteria: NONE | <conditions proving the temporary mitigation can be removed>
Qualification evidence: PENDING | <repository-approved hotfix qualification evidence>
Release: PENDING | <formal release identity/reference when repository policy requires one>
```

When repository policy requires production deployment, the managed record also carries durable stabilization evidence once known:

```text
Deployment evidence: PENDING | <authority/target/application/release/expected-SHA/resolved-SHA/event/HEALTHY reference>
```

`Deployment evidence` is conditional rather than a new pre-qualification field so existing `HOTFIX_READY` records remain valid before publication/deployment.

## Strategy invariants

`UNRESOLVED` is allowed only while the hotfix is still being diagnosed or when it is `HOTFIX_BLOCKED` before a safe resolution strategy can be justified. A record with `Resolution strategy: UNRESOLVED` must never advance to `HOTFIX_READY`, `HOTFIX_STABILIZED` or `HOTFIX_COMPLETE`.

`PERMANENT` means the bounded emergency change is itself the intended long-term correction. It requires:

```text
Permanent fix issue: NONE
Reason temporary: NONE
Temporary surfaces: NONE
Removal criteria: NONE
```

`TEMPORARY_MITIGATION` means the emergency change intentionally stabilizes production without representing the complete structural correction. Before state may advance to `HOTFIX_READY`, all of the following are mandatory:

- `Permanent fix issue` references a distinct open follow-up work item;
- `Reason temporary` explains why the permanent correction was deferred from the emergency change;
- `Temporary surfaces` identifies the temporary code, configuration, feature flag, fallback, operational workaround, or other debt that must later be removed or replaced;
- `Removal criteria` defines what the permanent correction must prove before the temporary mitigation can be removed.

The permanent-fix work item must preserve enough context for an independent future agent to continue without reconstructing the incident from chat history. At minimum it records the originating hotfix, known or probable root cause, temporary mitigation, reason for deferral, required final behavior, temporary surfaces to remove, removal criteria, regression/prevention coverage expected, and related PR/release references when known.

## Exact-candidate authority

`HOTFIX_READY` requires a resolved `PERMANENT` or `TEMPORARY_MITIGATION` strategy, a current exact `Candidate SHA`, and durable `READY_FOR_CI evidence` for that same candidate. Any later PR-head change makes the hotfix record stale until development/review evidence and the managed record are refreshed.

The hotfix record does not replace the repository's normal development evidence or its hotfix qualification gate. It binds emergency intent, strategy, follow-up debt, target and exact candidate so repository-specific CI can authorize the exceptional lane without an unrelated manual label.

## Production stabilization and completion

When repository policy declares production deployment as part of emergency stabilization, `HOTFIX_STABILIZED` is the first durable state that proves production restoration. It requires all of the following:

- formal immutable `Release` identity is known;
- the release resolves to the exact integrated commit expected by the hotfix;
- the repository-declared deployment authority reports terminal `HEALTHY`;
- `Deployment evidence` durably references that authority result and exact identity.

Deployment-provider transient states such as PREPARING, DEPLOYING or CHECKING remain provider-owned and are not HOTFIX protocol states.

`HOTFIX_STABILIZED` is intentionally distinct from engineering closeout. Repository-declared post-deploy reconciliation, broad validation or administrative verification may remain pending without invalidating already-proven production stabilization. They may still be required before `HOTFIX_COMPLETE`.

When repository policy does not require deployment, it may define its existing publication/integration evidence as the stabilization boundary without inventing deployment evidence.

`HOTFIX_COMPLETE` means repository-required emergency integration, formal release/publication when required, required production stabilization when declared, and all repository-owned post-deploy reconciliation/verification closeout have completed. For `TEMPORARY_MITIGATION`, the permanent-fix Issue intentionally remains open; completion means production is mitigated, not that the structural cause is resolved.

`HOTFIX_BLOCKED` is fail-closed. Use it when no repository-approved emergency path exists, the blast radius cannot be bounded safely, required evidence cannot be produced, deployment identity/authority cannot be proven when required, or neither a safe permanent correction nor a safe temporary mitigation can be justified. When blocking occurs before strategy selection, preserve `Resolution strategy: UNRESOLVED` instead of inventing a permanent or temporary classification.
