---
name: local-release
description: >
  Use when one exact repository release candidate must be qualified and promoted through the LOCAL
  execution surface. Invoking this skill selects LOCAL release qualification, emits READY_FOR_RELEASE,
  performs only repository-approved release integration/publication, and never falls back to chat-release.
license: Apache-2.0
compatibility: >
  Requires read/write access to the target repository, git, Python 3.11+ for profile validation,
  every local runtime/service declared by the repository CI profile, and access required by the
  repository-approved integration and release-publishing mechanisms.
metadata:
  author: coferlandia
  version: "1.0.0"
  category: engineering
  status: active
  tested: "2026-09-11 - LOCAL release ownership, READY_FOR_RELEASE, no GitHub-native fallback, exact-candidate identity, review/profile authority, repair boundary, and publisher composition covered by contract tests."
---

## Context

`local-release` is the Agent Skills/local surface for qualifying and promoting one exact release candidate:

```text
exact release candidate
-> LOCAL release qualification
-> READY_FOR_RELEASE
-> repository-approved release integration
-> coferlandia-release-publisher when formal publication is required
-> COMPLETE
```

Invoking this skill selects `LOCAL`. It **never falls back to `chat-release`** and **must not invoke GitHub-native Qualification** as a substitute when local qualification fails or cannot run.

The target repository owns its release topology, source/target refs, release manifest, local qualification commands, integration method, publication requirements, reconciliation and deployment policy. This skill must not hardcode project branch names, workflow names, test commands, version numbers, runners or production topology.

This skill **must not deploy**. Deployment remains a separate repository-owned authority.

## Activation boundary

Activate when the user explicitly selects local release / `local-release`, or when an already-selected Agent Skills/local workflow delegates one exact release candidate to this skill.

Do not activate merely because development reached `READY_FOR_MERGE`, because a release PR exists, or because a GitHub-native `chat-release` attempt is unavailable. Do not use this skill as an automatic fallback from `chat-release`.

## Preconditions

Before qualification:

1. Read current repository instructions and authoritative release policy.
2. Resolve the exact release source ref, target ref and current release candidate SHA.
3. Resolve/rebuild the repository-defined release manifest and prove it belongs to that candidate/base identity.
4. Prove any repository-required reconciliation precondition is satisfied.
5. Require `.coferlandia/ci/profile.json`, validate it against the central profile contract, and compute the current profile fingerprint.
6. Resolve the profile/repository-declared LOCAL release qualification commands and required local services/environment.
7. Resolve the current required release review state and require `Review Critical: 0` and `Review Important: 0` before qualification authority can be emitted.
8. Confirm there is no conflicting release authority or stale candidate state.

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

7. A corrected source creates a new release candidate and invalidates old local release evidence; restart qualification from the beginning.
8. Re-read source/target/profile/manifest/review identity after all local commands pass and require review state to remain Critical = 0 / Important = 0.

## READY_FOR_RELEASE

Only after the exact release candidate is fully GREEN under the repository's LOCAL release contract and current required review state remains clean, create/update durable evidence matching `_protocol/delivery/READY_FOR_RELEASE.md`:

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

Any later source SHA, target/base, effective candidate, profile, manifest or required-review change makes the handoff stale.

## Release integration

After `READY_FOR_RELEASE`, integrate only through the repository-approved release mechanism and re-read identity immediately before the consequential operation. Preserve repository-required history/genealogy and safeguards. Never force-push or weaken policy to complete a release.

If the candidate/base/profile/manifest/review state changed before integration, stop and return `RELEASE_REQUALIFICATION_REQUIRED` rather than integrating stale evidence.

After integration, resolve the exact resulting target commit and verify repository-required release closeout/reconciliation that belongs to this release lifecycle.

## Formal publication

When repository policy requires a formal version/tag/GitHub Release, invoke `coferlandia-release-publisher` on the exact integrated commit. Do not duplicate SemVer classification, annotated-tag creation, GitHub Release publication, idempotent recovery or publication verification.

If publication requires an explicit semantic-version decision not already established by repository policy, preserve the publisher's authority boundary rather than inventing one.

## Failure boundaries

- Missing/invalid CI profile or stale profile fingerprint: `LOCAL_RELEASE_BLOCKED` or `RELEASE_REQUALIFICATION_REQUIRED` depending on when drift occurred.
- Missing/unclean required review state: `LOCAL_RELEASE_BLOCKED` before qualification or `RELEASE_REQUALIFICATION_REQUIRED` after evidence was emitted.
- Missing LOCAL runtime/service: `LOCAL_RELEASE_BLOCKED`; never fall back to `chat-release`.
- Product/test failure: `RELEASE_REPAIR_REQUIRED`; return through repository-defined development/correction flow.
- Candidate/base/profile/manifest/review drift: `RELEASE_REQUALIFICATION_REQUIRED`.
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
