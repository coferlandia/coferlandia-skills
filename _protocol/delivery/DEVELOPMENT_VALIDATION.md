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
- GitHub Actions workflow submitted by existing Draft-PR events;
- exact `pull-request-head` candidate binding;
- repository-owned runner labels and shell;
- optional ordered repository-owned setup actions for job-local project toolchains;
- one Development gate whose allowed GREEN conclusion is `success`;
- a deterministic SHA-256 fingerprint over the semantic contract.

No private values, credentials, current run IDs or current conclusions belong in the contract.

## Execution precedence

A Development controller resolves validation in this order:

1. Execute the repository-owned Development checks directly when the active environment can do so correctly.
2. When direct execution is unavailable, use a current repository-owned remote Development contract.
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

- run only on the Draft pull request used by the Development stage;
- use repository-declared existing PR events rather than inventing a Qualification dispatch;
- explicitly check out `github.event.pull_request.head.sha`;
- verify the checked-out `HEAD` equals that expected SHA;
- record the Development contract fingerprint and exact candidate SHA before project setup/execution;
- execute only repository-declared setup actions, when present, in their declared order;
- execute only repository-declared Development commands in their declared order;
- use the repository-declared runner labels, working directory and shell;
- grant candidate-controlled code no GitHub write authority; the standard generated surface uses only `contents: read`;
- avoid injecting private values;
- never writes the durable `READY_FOR_CI` or any `READY_FOR_MERGE` marker itself.

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
