---
name: local-release
description: >
  Use when one repository release must be initialized or resumed, reviewed, qualified through the LOCAL
  execution surface, integrated, and formally published when repository policy requires it. Invoking this
  skill selects LOCAL release qualification and never falls back to chat-release.
license: Apache-2.0
compatibility: >
  Requires read/write access to the target repository, git, Python 3.11+ for profile validation,
  every local runtime/service declared by the repository CI profile, and access required by the
  repository-approved release work-surface, integration, and publication mechanisms.
metadata:
  author: coferlandia
  version: "1.0.0"
  category: engineering
  status: active
  tested: "2026-09-11 - LOCAL release candidate initialization, aggregate review, READY_FOR_RELEASE, no GitHub-native qualification fallback, exact-candidate identity, review/profile authority, repair boundary, and publisher composition covered by contract tests."
---

## Context

`local-release` is the Agent Skills/local surface for one complete repository-approved release lifecycle whose Qualification strategy is LOCAL:

```text
explicit local-release invocation
-> resolve repository release policy/source/target
-> initialize or reuse release work surface
-> build/currentize release manifest
-> bind exact release candidate/base
-> aggregate release review
-> LOCAL release qualification
-> READY_FOR_RELEASE
-> repository-approved release integration
-> coferlandia-release-publisher when formal publication is required
-> COMPLETE
```

Invoking this skill selects `LOCAL` for release Qualification. It **never falls back to `chat-release`** and **must not invoke GitHub-native Qualification** as a substitute when local qualification fails or cannot run. Repository policy may still use GitHub for durable Issues/PRs/release integration/publication; that does not convert the Qualification strategy to GITHUB_NATIVE.

The target repository owns its release topology, source/target refs, release manifest, local qualification commands, integration method, publication requirements, reconciliation and deployment policy. This skill must not hardcode project branch names, workflow names, test commands, version numbers, runners or production topology.

This skill **must not deploy**. Deployment remains a separate repository-owned authority.

## Activation boundary

Activate when the user explicitly selects local release / `local-release`, or when an already-selected Agent Skills/local workflow delegates a repository release to this skill.

Do not activate merely because development reached `READY_FOR_MERGE`, because a release PR exists, or because a GitHub-native `chat-release` attempt is unavailable. Do not use this skill as an automatic fallback from `chat-release`.

Unless the controlling request is explicitly dry-run/planning-only, `local-release` owns repository-approved release work-surface initialization/reuse, LOCAL Qualification, release integration, and formal publication through the shared publisher when policy requires it. It never gains deployment authority.

## Release candidate initialization

Before review/Qualification, establish exactly one current release candidate through repository policy.

1. Read current repository instructions and resolve authoritative release source/target refs, source SHA, target/base SHA, release integration mechanism, manifest contract, reconciliation/ancestry/freeze policy, and publication policy.
2. Prove repository-declared pre-release reconciliation/ancestry/freeze conditions are satisfied.
3. If repository policy uses a GitHub pull request as the release work surface:
   - search for an existing open release PR matching the authoritative source/target and active release identity;
   - reuse it only when it unambiguously represents the same release;
   - when none exists and policy permits controller creation, create the repository-approved release PR (Draft when the repository keeps release qualification/review pre-integration);
   - stop rather than creating a competing release if an ambiguous/conflicting active release exists.
4. If repository policy uses another work surface, initialize/reuse only that declared mechanism.
5. Build or currentize the repository-defined release manifest from authoritative source-vs-target delta evidence, including the work identities and release-impact information required by repository policy.
6. Persist the manifest only in the repository-defined durable location and bind it to exact source candidate and target/base identity.
7. Re-read the initialized work surface and candidate identity before review.

A source/base/manifest/work-surface identity change creates a new release candidate for review/Qualification purposes and invalidates older evidence. Release initialization/control-plane operations do not authorize product-code corrections.

## Aggregate release review

Before LOCAL qualification, perform or consume the repository-approved aggregate review of the complete release delta and current manifest. Review the combined candidate rather than trusting previously integrated work items independently.

Cover relevant cross-change interactions, integration/history correctness, public/API/data-contract compatibility, migrations, environment/configuration effects, manifest completeness, operational impact, and repository-declared release risks.

The exact-candidate release review must end with:

```text
Review Critical: 0
Review Important: 0
```

Release-owned metadata/manifest findings may be corrected within this skill followed by a fresh aggregate review. Product/development findings return `RELEASE_REPAIR_REQUIRED`; do not patch product code inside `local-release` unless repository policy explicitly defines that as the normal development path. A source/base/manifest change invalidates the prior review.

## Qualification preconditions

Before LOCAL qualification:

1. Prove the initialized release source ref, target ref, current candidate SHA and target/base SHA remain current.
2. Prove the durable release manifest belongs to that exact candidate/base identity.
3. Prove any repository-required reconciliation/ancestry/freeze/active-release precondition remains satisfied.
4. Require `.coferlandia/ci/profile.json`, validate it against the central profile contract, and compute the current profile fingerprint.
5. Resolve the profile/repository-declared LOCAL release qualification commands and required local services/environment.
6. Require the current aggregate release review to remain `Review Critical: 0` and `Review Important: 0` for the exact candidate/base/manifest.
7. Confirm there is no conflicting release authority or stale work-surface state.

Missing, ambiguous or stale release identity, profile authority, review state, or local qualification contract blocks qualification.

## LOCAL qualification

1. Keep the exact release candidate unchanged while qualification runs.
2. Execute only repository-declared local release/FULL qualification commands, in declared order and working directory.
3. Record exact candidate SHA, qualified target/base SHA, profile fingerprint, release manifest identity, review state and command/result evidence.
4. Current failures are RED. Missing tools/services are blocked, not GREEN.
5. A material product correction is not made directly inside the release candidate unless repository policy explicitly defines that as its normal development path.
6. When correction must return through ordinary development, report:

```text
RELEASE_REPAIR_REQUIRED
Reason: <defect or violated contract>
Candidate SHA: <stale release candidate>
Required repair path: <repository-defined development path>
```

7. A corrected source creates a new release candidate and invalidates old local release review/qualification evidence; restart from candidate initialization/currentization and aggregate review.
8. Re-read source/target/work-surface/profile/manifest/review identity after all local commands pass and require review state to remain Critical = 0 / Important = 0.

## READY_FOR_RELEASE

Only after the exact release candidate is fully GREEN under the repository's LOCAL release contract and current aggregate release review remains clean, create/update durable evidence matching `_protocol/delivery/READY_FOR_RELEASE.md`:

```text
State: READY_FOR_RELEASE
Source ref: <source>
Target ref: <target>
Release candidate SHA: <exact candidate>
Qualified base SHA: <exact target/base used>
Effective candidate: <repository-defined exact candidate>
Qualification strategy: LOCAL
CI profile fingerprint: <sha256>
Qualification evidence: <ordered local command/result evidence>
Included work: <durable release manifest/reference>
Review Critical: 0
Review Important: 0
Next stage: Release integration
```

Any later source SHA, target/base, effective candidate, work-surface, profile, manifest or required-review change makes the handoff stale.

## Release integration

After `READY_FOR_RELEASE`, integrate only through the repository-approved release mechanism and re-read identity immediately before the consequential operation. Preserve repository-required history/genealogy and safeguards. Never force-push or weaken policy to complete a release.

If candidate/base/work-surface/profile/manifest/review state changed before integration, stop and return `RELEASE_REQUALIFICATION_REQUIRED` rather than integrating stale evidence.

After integration, resolve the exact resulting target commit and verify repository-required release closeout/reconciliation that belongs to this release lifecycle.

## Formal publication

When repository policy requires a formal version/tag/GitHub Release, invoke `coferlandia-release-publisher` on the exact integrated commit. Do not duplicate SemVer classification, annotated-tag creation, GitHub Release publication, idempotent recovery or publication verification.

If publication requires an explicit semantic-version decision not already established by repository policy, preserve the publisher's authority boundary rather than inventing one.

## Failure boundaries

- Candidate initialization/work-surface conflict: `LOCAL_RELEASE_BLOCKED`.
- Missing/invalid CI profile or stale profile fingerprint: `LOCAL_RELEASE_BLOCKED` or `RELEASE_REQUALIFICATION_REQUIRED` depending on when drift occurred.
- Missing/unclean aggregate review state: `LOCAL_RELEASE_BLOCKED` before qualification or `RELEASE_REQUALIFICATION_REQUIRED` after evidence was emitted.
- Missing LOCAL runtime/service: `LOCAL_RELEASE_BLOCKED`; never fall back to `chat-release`.
- Product/test/review defect: `RELEASE_REPAIR_REQUIRED`; return through repository-defined development/correction flow.
- Candidate/base/work-surface/profile/manifest/review drift: `RELEASE_REQUALIFICATION_REQUIRED`.
- Integration policy unavailable or conflicting: `LOCAL_RELEASE_BLOCKED`.
- Formal publication failure: preserve the exact integrated commit and use publisher recovery/verification semantics; do not create a synthetic replacement commit.
- Deployment request: outside this skill; this skill must not deploy.

## Expected output

```text
Release workflow = COMPLETE | LOCAL_RELEASE_BLOCKED | RELEASE_REPAIR_REQUIRED | RELEASE_REQUALIFICATION_REQUIRED
Qualification strategy = LOCAL
Source ref = <ref>
Target ref = <ref>
Release candidate SHA = <sha>
Qualified base SHA = <sha>
CI profile fingerprint = <sha256>
Release manifest = <durable reference>
Review Critical = 0
Review Important = 0
Qualification evidence = <local commands/results>
Integrated target SHA = <sha or PENDING>
Formal release = <release identity or NONE/PENDING per repository policy>
Deployment = NOT OWNED
```

## Output location

Use the repository's durable release evidence surfaces. `READY_FOR_RELEASE` follows the shared protocol marker. Test/build artifacts remain owned by repository commands. This skill creates no shadow release configuration.
