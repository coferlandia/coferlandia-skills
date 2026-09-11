---
name: chat-release
description: "Generic Chat GITHUB_NATIVE release controller that qualifies one exact release candidate, integrates it through repository policy, and publishes the resulting exact commit through coferlandia-release-publisher."
version: "1.0.0"
stage: release
status: active
---

# Chat Release — GitHub-native release controller

## Responsibility

Own one explicit GITHUB_NATIVE release lifecycle for one exact release candidate.

```text
release candidate
-> reconstruct source/target/release manifest
-> validate repository CI profile
-> qualify exact candidate through GitHub-native gates
-> READY_FOR_RELEASE (strategy = GITHUB_NATIVE)
-> revalidate release identity
-> repository-approved release integration
-> verify exact resulting target commit
-> coferlandia-release-publisher
-> verify published release
-> COMPLETE
```

This controller **must not deploy**. It does not invoke `ci.md`, does not fall back to `local-release`, and does not silently insert development, repair, deployment, or rollback stages.

## Invocation boundary

This is a Chat prompt controller, not an Agent Skill. Load it only when the controlling request explicitly resolves `chat release` or `chat-release` through `prompts/registry.json`, including an explicit left-to-right composition containing that alias.

Invoking `chat-release` selects release Qualification strategy `GITHUB_NATIVE`. Do not ask a second strategy-selection question and do not switch to LOCAL because GitHub-native qualification is blocked or RED.

A release is not inferred merely because development work is merged, a branch exists, CI is green, or a commit has not yet been tagged.

Unless the user explicitly requests a dry-run/planning-only release, an explicit `chat-release` invocation authorizes this controller's release-side effects: repository-approved release integration plus publication through `coferlandia-release-publisher`. It never grants deployment authority.

## Repository authority and release candidate

Repository policy owns the actual release topology. Never hardcode branch names, merge method, workflow/check names, version baseline, deployment target, or test commands.

Reconstruct authoritative state from current repository/GitHub evidence rather than chat history. Resolve at least:

- repository and current release work surface, normally an existing release PR when GitHub integration is used;
- source ref and target ref;
- exact source/head Release candidate SHA;
- authoritative target/base SHA;
- repository-approved release integration mechanism;
- current `.coferlandia/ci/profile.json` and fingerprint;
- current release manifest identifying the work included in the candidate;
- required review state;
- current release publication policy, previous published release, and version lineage when relevant.

The release manifest may be a repository-defined managed comment, file, PR body section, or other durable source. It must be current and attributable to the exact release candidate. Do not invent a generic manifest storage location.

If source/target identity, manifest, qualification policy, or integration policy is ambiguous, stop fail-closed rather than guessing.

## Entry contract

Require all of:

1. one current exact release candidate with authoritative source and target refs;
2. a current durable release manifest/reference for that candidate;
3. a valid `.coferlandia/ci/profile.json` with GitHub qualification facts;
4. current profile fingerprint;
5. current required review state with Critical = 0 and Important = 0;
6. repository policy that permits release integration from the resolved source into the resolved target;
7. no repository-declared reconciliation, ancestry, freeze, or release-state blocker.

A repository may impose stronger release preconditions. Consume them without copying project-specific facts into this generic prompt.

## GitHub-native release Qualification

1. Re-read source ref, target ref, exact Release candidate SHA, target/base SHA, release manifest, review state and CI profile fingerprint.
2. Determine the profile-declared GitHub submission mode. Trigger only the declared operation when explicit dispatch is required; otherwise observe existing repository events/checks.
3. Bind all qualification evidence to the exact candidate/effective candidate required by repository identity policy.
4. Evaluate every profile-required gate against its allowed terminal conclusions. Queued, waiting, requested, pending, in-progress, cancelled, stale, superseded, old-SHA or old-profile evidence is not GREEN.
5. Re-read candidate/base/profile/manifest after GitHub gates settle. Any relevant identity drift invalidates qualification.

The repository decides, through its own workflows and routing policy, what constitutes release-grade validation. `chat-release` never substitutes a development-only result for the repository's release gate.

## Failure and repair loop

For RED qualification, inspect the exact current run/job/check and classify the failure.

- **Transient/provider failure:** retry only through repository-approved mechanisms and remain bound to the same candidate unless repository state changes.
- **Release-controller/metadata defect:** correct only release-owned metadata or evidence that is explicitly within this controller's responsibility, then requalify.
- **Product/development defect:** return `RELEASE_REPAIR_REQUIRED`. Do not edit product code inside this release controller and do not implicitly invoke `chat-coder`, debugger, Local CI, or another development stage. The repository's normal development flow creates a corrected candidate; re-enter `chat-release` afterward.

Any corrected/new source SHA makes previous release Qualification and `READY_FOR_RELEASE` evidence stale.

## Durable READY_FOR_RELEASE

Only after every current GITHUB_NATIVE release gate is authoritative and GREEN for the exact candidate, create or update the repository's managed release handoff using `_protocol/delivery/READY_FOR_RELEASE.md` and marker:

```html
<!-- coferlandia-ready-for-release:v1 -->
```

Record:

```text
State: READY_FOR_RELEASE
Schema: 1
Source ref: <source ref>
Target ref: <target ref>
Release candidate SHA: <exact source/head SHA>
Qualified base SHA: <target/base SHA used by qualification>
Effective candidate: <candidate used by authoritative gates>
Qualification strategy: GITHUB_NATIVE
CI profile fingerprint: <sha256>
Qualification evidence: <workflow/check/run identifiers and conclusions>
Included work: <durable release manifest/reference>
Review Critical: 0
Review Important: 0
Next stage: Release integration
```

`READY_FOR_RELEASE` is exact-candidate integration evidence, not a tag, GitHub Release, or deployment authority.

## Release integration

Immediately before integration, re-read source/head, target/base, manifest, profile fingerprint, review state, mergeability and all repository-declared release blockers.

If any release identity or required gate authority changed, invalidate `READY_FOR_RELEASE` and return `REQUALIFICATION_REQUIRED` rather than integrating stale evidence.

Use the strongest repository-approved integration mechanism. Respect the repository's required merge strategy and history policy. Never force-push, rewrite protected history, silently squash when repository release policy forbids it, or bypass current safeguards.

After integration, prove the intended release candidate reached the declared target ref and resolve the exact resulting target commit SHA. Do not infer the publish target from a pre-merge source SHA when integration produced a distinct commit.

## Release publication

Use the public `coferlandia-release-publisher` skill for **Commit -> Release**. Do not duplicate version/tag/GitHub Release mechanics in this prompt.

The publisher must receive the exact integrated target commit and current repository release policy. Semantic impact comes from the complete release delta and must not be inferred mechanically from filenames or commit prefixes.

For a first published release, unresolved product maturity/version baseline remains a control decision; do not invent `1.0.0` or another baseline.

After publication, verify the annotated tag and GitHub Release resolve coherently to the exact intended commit. Publication success is not deployment success.

## Closeout and reentry

Apply only repository-declared release closeout behavior after publication verification, for example release-manifest traceability, issue annotations, branch reconciliation, or release-state cleanup. Generic `chat-release` does not invent those policies.

Reentry always reconstructs current state. If integration already completed but publication is partially complete, use `coferlandia-release-publisher` consistency/recovery semantics rather than recreating or moving published identities.

Terminal/resumable states include:

```text
RELEASE_QUALIFICATION_PENDING
RELEASE_REPAIR_REQUIRED
REQUALIFICATION_REQUIRED
READY_FOR_RELEASE
RELEASE_PUBLICATION_BLOCKED
COMPLETE
```

## Terminal report

On success return factual evidence:

```text
Release workflow = COMPLETE
Qualification strategy = GITHUB_NATIVE
Source ref = <ref>
Target ref = <ref>
Release candidate SHA = <sha>
Integrated target SHA = <sha>
CI profile fingerprint = <sha256>
Qualification evidence = <durable reference>
Included work = <release manifest/reference>
Release = <version/tag/GitHub Release identity>
Deployment = NOT PERFORMED
```
