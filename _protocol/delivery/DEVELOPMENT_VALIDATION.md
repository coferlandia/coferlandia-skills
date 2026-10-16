# Remote Development Validation v1

Remote Development validation is an execution backend for the Development stage. It exists so a development controller can produce fresh, repository-owned validation evidence when the active client cannot execute the repository's required Development checks locally.

It is **not Qualification**.

## Canonical repository contract

The standard repository-owned contract path is:

```text
.coferlandia/development/validation.json
```

Its schema is `_protocol/delivery/development-validation.schema.json`.

A conforming contract identifies:

- repository and supporting documentation;
- working directory;
- ordered cheap deterministic Development commands;
- required services and environment variable names;
- GitHub Actions workflow plus one supported submission mode;
- exact `pull-request-head` candidate binding;
- repository-owned runner labels and shell;
- optional ordered repository-owned setup actions for job-local project toolchains;
- one Development gate whose allowed GREEN conclusion is `success`;
- a deterministic SHA-256 fingerprint over the semantic contract.

Schema v1 supports two submission shapes:

```text
existing-pr-events
workflow-dispatch-exact-head
```

`existing-pr-events` remains valid for compatible repositories and may declare exact-head dispatch as a fallback. `workflow-dispatch-exact-head` may also be the primary mode; when primary it requires a trusted `control_ref` and does not imply an automatic Draft-PR run.

No private values, credentials, current run IDs or current conclusions belong in the contract.

## Development scope and cost boundary

The Development contract must preserve the Development/Qualification boundary in both semantics and cost. Do not select a repository's canonical FULL/Qualification suite merely because it is the easiest existing command to invoke remotely.

Prefer repository-owned affected/scoped routing when it exists. Development should run the smallest deterministic set of checks that covers the changed surface and must fail closed when that scope cannot be resolved; unresolved scope is not permission to silently fall back to FULL.

A script shared with Qualification is acceptable only when repository policy independently declares it as a Development check and its normal execution cost is genuinely compatible with iterative Development feedback. Remote execution being available does not make an otherwise expensive Qualification suite a suitable Development gate.

## Execution precedence

A Development controller resolves validation in this order:

1. Execute the repository-owned Development checks directly when the active environment can do so correctly.
2. When direct execution is unavailable, use a current repository-owned remote Development contract according to its declared primary submission mode.
3. When that contract is absent and the explicitly available repository adapter is authorized to materialize it, delegate only the minimal Development adaptation and then use the resulting remote surface.
4. Block when no authorized execution backend can produce fresh evidence for the exact candidate.

This precedence is about **where Development checks execute**. It does not select or fall back between Qualification strategies.

## Repository-owned toolchain setup

A remote Development contract may declare `github.setup` when its repository commands require project-specific runtimes or tools that should be provisioned deterministically for the job rather than assumed to exist in a generic runner image.

Setup is optional and additive within schema version 1. Existing contracts without it remain valid.

A conforming setup entry:

- has one unique human-readable name;
- references one static external GitHub Action as `owner/repo@ref`;
- may provide only flat string, integer or boolean action inputs;
- contains no dynamic action reference, local action, nested/multiline input or private-value transport.

Setup actions execute in declared order after the workflow verifies the exact PR head and records the Development fingerprint, and before repository Development commands. Setup actions and inputs are semantic contract data, so changing them changes the fingerprint and invalidates older evidence.

The adapter/controller must discover toolchain versions from repository-owned manifests, workflows or current development documentation. It must not invent project runtimes from the runner image.

## Remote workflow requirements

A GitHub-native remote Development workflow must:

- validate only the open Draft pull request used by the Development stage;
- submit according to the contract's declared mode rather than assuming PR events;
- for `existing-pr-events`, explicitly check out `github.event.pull_request.head.sha` and run only for the repository-declared Draft event surface;
- for `workflow-dispatch-exact-head`, dispatch from the contract's trusted `control_ref`, never from the candidate branch; before candidate checkout, use read-only GitHub metadata access to require an open Draft PR and prove the current PR head equals the requested candidate SHA;
- verify the checked-out `HEAD` equals that expected SHA;
- record the Development contract fingerprint and exact candidate SHA before project setup/execution;
- execute only repository-declared setup actions, when present, in their declared order;
- execute only repository-declared Development commands in their declared order;
- use the repository-declared runner labels, working directory and shell;
- grant candidate-controlled code no GitHub write authority; exact-head dispatch may add only the read permission required to re-read PR metadata;
- avoid injecting private values;
- never write the durable `READY_FOR_CI` or any `READY_FOR_MERGE` marker itself.

Repositories using self-hosted runners are responsible for runner isolation and ambient environment visible to candidate/setup code. Generic runner images should provide the execution substrate; project-specific runtime versions belong to the repository-owned setup contract when deterministic provisioning is needed.

## Evidence accepted by READY_FOR_CI

Remote evidence is valid Development evidence only when all of the following are true:

- current PR head equals the candidate SHA checked by the run;
- the stored Development contract validates and its fingerprint matches the run evidence;
- the observed gate is the gate declared by that contract;
- the gate reached an explicitly allowed terminal conclusion;
- every declared setup action and command required by the contract actually participated in that run;
- the run is not cancelled, stale, superseded, from another PR/head, or from an older Development fingerprint.

A later candidate SHA or Development fingerprint invalidates the evidence.

## Submission modes

### Controller-owned label trigger

`existing-pr-events` may declare `trigger` with `kind: pull-request-label`, a nonempty static `label`, boolean `rerun_on_synchronize`, and explicit unique `base_branches`. The trigger cannot coexist with a dispatch fallback. Plain PR events and primary/fallback dispatch remain backward compatible.

Only open Draft PRs on a declared base execute. Matching `labeled`, `reopened`, and `converted_to_draft` events submit; `synchronize` submits only when enabled and the label remains present. Unrelated labels never execute or participate in the eligible jobs' PR-scoped concurrency, including pending replacement. Checkout uses the exact PR event head, never the synthetic merge SHA.

The generated run title is `Development Validation / PR #<number> candidate:<sha> fingerprint:<sha256>`. The consumer validates the current contract/fingerprint, then requires the exact title, workflow, branch/head, latest successful attempt and declared successful gate. Missing or stale evidence fails closed. The existing READY run/attempt reference is unchanged.

Development owns adding/removing the label and READY_FOR_CI. Only previously resolved GITHUB_NATIVE Qualification may mark Ready. Terminal Development-only and LOCAL paths retain their Draft semantics. Reentry observes compatible existing work before submitting. Same-candidate transient failures/cancellations allow one bounded rerun per recovery pass after current Draft/head/base/fingerprint revalidation; repeated failures require environment recovery, not empty commits or label toggles.

### Primary exact-head dispatch

A repository may declare exact-head dispatch as the primary schema-v1 submission mode:

```json
{
  "mode": "workflow-dispatch-exact-head",
  "workflow": ".github/workflows/coferlandia-development-validation.yml",
  "control_ref": "dev"
}
```

The controller dispatches the declared workflow at exactly `control_ref`, not at the candidate branch/ref. The fixed inputs are `pr_number` and `candidate_sha`. The workflow fails before candidate checkout unless all of the following are true:

- the supplied PR number resolves to an open pull request in the same repository;
- the pull request is still Draft;
- the current PR head equals the requested full SHA;
- the dispatch itself is executing from the declared trusted control ref.

Primary dispatch means intermediate Draft pushes do not automatically run the complete remote Development contract. The controller requests it only for an explicitly chosen candidate when remote execution is needed. Reentry must first look for a compatible queued/running/completed run so it does not blindly create duplicates.

### Existing PR events with optional exact-head fallback

A compatible repository may retain:

```json
{
  "mode": "existing-pr-events",
  "workflow": ".github/workflows/coferlandia-development-validation.yml",
  "fallback": {
    "mode": "workflow-dispatch-exact-head",
    "control_ref": "dev"
  }
}
```

In this shape the normal PR-event path remains preferred. The fallback exists only when that event surface cannot produce fresh evidence for the current Draft candidate. It has the same trusted-control-ref, PR-state, exact-head and reentry requirements as primary dispatch.

Neither primary nor fallback dispatch selects Qualification, emits a READY marker, merges, publishes or deploys. Both execute only the same fingerprinted Development setup/actions/commands and declared gate.

## Qualification boundary

Remote Development validation establishes source-candidate Development readiness only. It cannot:

- satisfy `.coferlandia/ci/profile.json` gates;
- prove an effective/synthetic merge candidate;
- select `LOCAL` or `GITHUB_NATIVE` Qualification;
- emit `READY_FOR_MERGE`;
- merge, publish, deploy or close work.

A repository may technically reuse scripts between Development and Qualification, but evidence remains stage-specific unless repository policy independently declares the corresponding gate in each contract.

## Adapter bootstrap

When Chat Coder has explicit authority to implement a work item, it may delegate creation of the missing remote Development surface to an installed `coferlandia-ci-adapter` if:

- local required checks cannot execute correctly;
- the repository does not already own an equivalent current Development surface;
- repository facts needed to render the contract are deterministic;
- the adaptation changes only the bounded Development contract/workflow;
- the adapter's own approval boundary is satisfied by that explicit delegation.

Ambiguous commands, runner labels, toolchain versions, runner safety assumptions or required private-value execution remain blockers rather than guessed defaults.