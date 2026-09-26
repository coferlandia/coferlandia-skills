---
name: chat-coder
description: "Generic Chat Development controller used by the standalone GitHub-native Chat Coder pipeline or by explicit Development-only/composed delivery flows."
version: "1.7.0"
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
-> authoritative-base currentization
-> post-currentization Development validation and final review
-> durable READY_FOR_CI
```

This controller **must not perform Qualification**, must not mark a candidate `READY_FOR_MERGE`, must not merge, close the Issue, project completion, or perform delivery closeout.

## Invocation and default orchestration

This file owns the Development stage only. `prompts/registry.json` owns how the user-facing alias is resolved around it:

- standalone `chat coder` / `chat-coder` resolves to this Development stage, then `ci` with `GITHUB_NATIVE` Qualification, then `merge`;
- standalone `chat dev` / `chat-dev` resolves only this Development stage and terminates at durable `READY_FOR_CI`;
- any explicit `+` composition executes exactly as written and suppresses the standalone default sequence;
- delegation from an explicitly invoked higher-level controller, such as `hotfix`, is stage-scoped and never activates the standalone default merely because it uses this Development controller.

The registry-declared standalone default is orchestration, not an expansion of this stage's authority. Qualification remains owned by `ci` or `local-ci`, and Integration remains owned by `merge`.

When this stage is the first step of the standalone Chat Coder default, `READY_FOR_CI` is an internal durable handoff. After writing and revalidating that handoff, yield immediately to the resolved `ci` stage without asking the user for another command or presenting Development readiness as top-level completion. When this stage is terminal because the user invoked `chat dev` or an explicit composition ending here, return the Development terminal report normally.

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

For behavior changes use RED -> minimal GREEN -> refactor. Keep scope bounded to the work contract. Run focused validation while iterating. Never invent a canonical command: discover validation from current repository-owned documentation, scripts, package metadata, Development validation contract, CI profile, or executable workflows.

For every behavior or contract change, inspect the existing tests that cover the affected surface before adding or modifying tests. Treat the affected test suite as part of the implementation contract:

- preserve tests for behavior that remains valid;
- update tests whose approved expected behavior intentionally changed;
- remove tests only when the behavior or contract they verify was intentionally removed or superseded;
- consolidate or remove materially duplicate or overlapping tests when they provide no meaningful additional coverage or diagnostic value, while preserving distinct boundary cases, regressions, failure modes and contracts;
- prefer updating, extending, parameterizing or consolidating existing tests when that provides the required coverage without reducing clarity or diagnostic value;
- remove test-only fixtures, helpers, mocks, snapshots or data that became unreachable or unused because of the change;
- do not leave obsolete tests skipped, disabled, commented out, or asserting superseded behavior.

Test-count growth is not a goal. Add new tests only for meaningful missing coverage, and leave the smallest clear suite that adequately describes and protects the intended current behavior. Never remove, weaken, bypass or broaden a test merely to make validation pass.

### Candidate batching and dependent-branch propagation

Treat one logical correction batch as one candidate publication. When one exact RED Development result exposes several related stale fixtures, assertions, mappings or bounded implementation defects, investigate the complete failing evidence first and batch the related corrections before publishing the next candidate whenever that can be done safely. Do not create a new remote candidate merely because the next individual edit is known.

When repository policy explicitly uses dependent or stacked implementation branches, distinguish three different operations:

- **stack propagation** moves an exact parent implementation candidate into a dependent child implementation branch;
- **authoritative-base currentization** reconciles an implementation branch with the repository's current development base before handoff;
- **final integration** moves a qualified implementation candidate into its canonical integration target.

Stack propagation changes the child candidate and invalidates child-bound validation/review evidence. It does **not** by itself currentize the child against the authoritative development base, consume the parent branch's integration lifecycle, or prove the parent is integrated into its canonical target. Follow the repository's explicit stack policy when it exists; never invent auxiliary merge semantics from branch names alone.


## Development readiness validation

Focused tests are iteration evidence; they are not sufficient by themselves for `READY_FOR_CI` when the repository defines broader cheap deterministic checks for the changed surface.

Immediately before the terminal development review and handoff, discover and run every applicable cheap deterministic development check owned by the repository on the exact candidate that will be handed off. Before those checks, identify repository-owned derived artifacts that repository-owned instructions, tooling, or policy explicitly declare to be versioned contracts and whose authoritative inputs changed; synchronize those artifacts with the repository-owned generation or synchronization mechanism rather than editing generated output by hand. At minimum:

- for changed behavior, verify that the affected pre-existing tests were reviewed and that the resulting suite contains no known assertions for superseded behavior, materially duplicate coverage without independent value, or test-only artifacts made obsolete by the change;
- synchronize every applicable repository-owned derived artifact explicitly declared as a versioned contract and affected by changed inputs, such as generated API/schema clients, schemas, snapshots, inventories/manifests, and equivalent code-generation outputs; when the repository defines a deterministic freshness, idempotence, or diff check for that versioned contract, rerun it and require no unexpected diff after the expected outputs are part of the candidate;
- do not create, add to Git, or require snapshot freshness for a reproducible diagnostic/report output merely because the repository can generate it; a test inventory, generated test manifest, or equivalent report is a synchronization prerequisite only when repository-owned policy explicitly declares that output to be a versioned contract;
- for backend behavior or contract changes, run the narrow regression target plus the repository's standard backend development validation when one is defined;
- for frontend behavior or contract changes, run the repository's canonical complete frontend unit-test suite, plus repository-defined lint and typecheck checks when they are part of the cheap development contract;
- run any other cheap deterministic contract check that repository instructions, scripts, or repository-owned Development/CI contracts explicitly require before Qualification.

### Execution backends for Development validation

Development requirements do not weaken merely because the active Chat client cannot execute them locally. Resolve where the required checks can run using `_protocol/delivery/DEVELOPMENT_VALIDATION.md` when that shared protocol is available:

1. Prefer direct execution in the active development environment when it can correctly run every applicable required check.
2. If direct execution is unavailable, look for a current repository-owned remote Development contract, canonically `.coferlandia/development/validation.json`, and validate its fingerprint and declared GitHub workflow/gate.
3. When that contract is absent and an installed `coferlandia-ci-adapter` supports remote Development adaptation, Chat Coder may explicitly delegate only the minimum bootstrap needed to execute its required Development checks. Derive commands, services, runner labels, shell and paths from repository truth; never invent them.
4. If the remote surface uses existing Draft-PR events, create or reuse the one allowed Draft PR before remote validation even though terminal review and `READY_FOR_CI` are still pending.
5. Prefer the contract's normal PR-event submission. When the contract explicitly declares an exact-head dispatch fallback, use it only when the normal event surface cannot produce fresh evidence for the current Draft candidate. Dispatch only the repository-declared trusted control ref and pass the PR number plus exact current head SHA; never dispatch the candidate branch as control-plane authority.
6. Observe only the declared Development gate for the exact current PR head SHA and current Development contract fingerprint. Pending, skipped, cancelled, stale, superseded, old-SHA or old-fingerprint evidence is not GREEN.
7. Queued, waiting, requested, pending or in-progress Development evidence is non-terminal. During the active execution, continue observing the authoritative exact-SHA gate when the available GitHub surface permits it. If the external run remains non-terminal beyond what the active execution can observe, report `Development workflow = WAITING_CI` with the exact PR, candidate SHA and run/check identity. On reentry, reconstruct current PR/head/fingerprint/run state from GitHub and consume the existing result; do not blindly submit a duplicate run.
8. If the Development gate is RED, classify it explicitly as a **Development** failure, inspect its exact failing job/log, make only bounded in-scope corrections, produce one new batched candidate, and repeat Development validation. Never report a remote Development gate failure as Qualification failure; Qualification has not started before a current durable `READY_FOR_CI`.
9. Block only when no authorized Development execution backend can produce fresh evidence for the exact candidate, or when the repository facts needed to adapt a missing remote surface are ambiguous.

Remote Development validation is still **Development**. It must not invoke or reuse Qualification merely as a workaround, select a Qualification strategy, satisfy `.coferlandia/ci/profile.json`, emit `READY_FOR_MERGE`, merge, publish or deploy. A remote workflow itself never writes the durable `READY_FOR_CI`; Chat Coder evaluates the evidence and owns that handoff after review.

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

Never expose secret values. Synchronize `.env.example` or the repository's equivalent environment template when applicable, and update repository-owned deployment/runbook documentation when the operational contract changed. Discover and execute any repository-owned deterministic environment/configuration contract checker. If required environment documentation, synchronization, deployment instructions, or deterministic validation is missing, stale, contradictory or no authorized Development execution backend can execute it, treat that as a development blocker.

Do not emit `READY_FOR_CI` while an applicable required development check is failing, skipped, unknown, stale, or was run against an older candidate SHA. A required versioned derived artifact that is missing, stale, manually approximated instead of produced by the repository-owned mechanism, or would still change under an applicable deterministic generation/freshness check is also a development blocker. Reproducible diagnostic/report outputs that are not repository-declared versioned contracts are not required candidate files and do not block readiness solely because a committed snapshot is absent or stale. When local execution is unavailable, require fresh repository-owned remote Development evidence rather than reporting readiness without execution.

These checks establish source-candidate development readiness only. They do not replace Qualification against the repository's effective or synthetic merge candidate.

If Chat Coder is resumed after a Qualification failure, first identify the exact failing command/assertion and the validation/effective-candidate SHA that produced it. Correct the implementation when it violates the work contract; update or remove a test or contract only when it is demonstrably stale or superseded relative to the approved behavior. Never weaken, delete, bypass, or broaden an assertion merely to make CI green.

## Review

Perform focused review of changed behavior, fix every Critical/Important finding, rerun affected tests, then perform a holistic review of the exact candidate. Any material correction creates a new candidate and invalidates older candidate-bound review/validation evidence.

Terminal development review state:

```text
Implementation = COMPLETE
Review Critical = 0
Review Important = 0
```

## Authoritative-base currentization before handoff

Development must hand Qualification a candidate that is already reconciled with the repository's current authoritative development base. Do this **before** durable `READY_FOR_CI`, not inside Qualification. If a repository uses stacked implementation branches, complete any repository-approved parent-to-child stack propagation separately; stack propagation is not authoritative-base currentization.

1. Re-read the authoritative development base ref and exact SHA after the candidate has passed its ordinary Development checks/review.
2. Determine whether the current candidate already contains/reconciles that exact base according to repository-approved Git policy. Never invent merge/rebase/update-branch policy.
3. If currentization changes the PR head, treat all older candidate-bound Development validation and review evidence as stale. Resolve conflicts within the approved work contract, then rerun every applicable cheap deterministic Development check affected by the currentization and perform the terminal exact-candidate review again.
4. Re-read the authoritative base immediately before handoff. For repositories whose Qualification identity is base-sensitive, the candidate must still be synchronized with that exact base SHA. Record it as `Base SHA synchronized`.
5. Only after currentization, post-currentization validation, and final review are current may the exact PR head be frozen as the Development candidate and receive `READY_FOR_CI`.

If the candidate cannot be safely currentized with the available repository-approved Git surface, stop with `DEVELOPMENT_CURRENTIZATION_BLOCKED`. Do not spend Qualification capacity on a knowingly stale candidate.

Base movement after the handoff does not authorize Qualification against stale identity. A selected Qualification surface must re-check current-base identity before starting expensive qualification and return to Development currentization when the repository profile is base-sensitive.

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
Base SHA synchronized: <exact authoritative base reconciled into the candidate immediately before handoff>
Implementation: COMPLETE
Development validation: <fresh evidence for every applicable required development check, including remote run/gate + Development fingerprint when used>
Environment change: YES | NO
Environment evidence: <NONE or concise candidate-bound evidence including affected inputs and deployment actions>
Review Critical: 0
Review Important: 0
Next stage: Qualification
```

Immediately before writing it, re-read the PR and prove `Candidate SHA == current PR head SHA`. Re-read the PR target and ensure it still matches the repository-authorized target for the active delivery context. The handoff is development evidence, not merge authority. Any later head change makes it stale; a target/context mismatch blocks the handoff until reconciled.

## Terminal report

When Development is the terminal resolved stage, return:

```text
Development workflow = READY_FOR_CI
Issue = <identity>
Assignee = <authenticated GitHub user>
Delivery context = STANDARD | <explicit repository-approved context>
PR = <number> / Draft
Branch = <branch>
Candidate SHA = <sha>
Base SHA studied = <sha>
Base SHA synchronized = <sha>
Validation = <fresh evidence for every applicable required development check after currentization>
Environment change = YES | NO
Environment action = <NONE or concise deployment/operator action>
Environment variables = <NONE or concise affected-variable list without secret values>
Review Critical = 0
Review Important = 0
Next owner = <next resolved controller/surface or NONE>
```

When `Environment change = YES`, the terminal report must make the operational consequence visible without requiring the user to inspect the PR comment. Do not use ambiguous wording such as "may require" when the candidate-bound analysis can classify the change.

When a resolved downstream stage follows, the same candidate-bound report is internal handoff evidence rather than top-level completion. Do not wait for final CI inside Development and do not perform another controller's responsibility; continue only by yielding to the next stage already resolved by the registry, an explicit composition, or a previously explicit higher-level controller.
