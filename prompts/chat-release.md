---
name: chat-release
description: "Generic Chat GITHUB_NATIVE release controller that initializes or reuses one release candidate, reviews and qualifies it, integrates it through repository policy, and publishes the resulting exact commit through coferlandia-release-publisher."
version: "1.1.0"
stage: release
status: active
---

# Chat Release — GitHub-native release controller

## Responsibility

Own one explicit GITHUB_NATIVE release lifecycle from repository-approved source/target state through one exact published release candidate.

```text
explicit chat-release request
-> resolve repository release policy/source/target
-> initialize or reuse release work surface
-> build/currentize release manifest
-> bind exact release candidate/base
-> aggregate release review
-> validate repository CI profile
-> qualify exact candidate through GitHub-native gates
-> READY_FOR_RELEASE (strategy = GITHUB_NATIVE)
-> revalidate release identity
-> repository-approved release integration
-> verify exact resulting target commit
-> repository-declared GitHub-native publication surface
-> coferlandia-release-publisher
-> verify published release
-> COMPLETE
```

This controller **must not deploy**. It does not invoke `ci.md`, does not fall back to `local-release`, and does not silently insert development, repair, deployment, or rollback stages.

## Invocation boundary

This is a Chat prompt controller, not an Agent Skill. Load it only when the controlling request explicitly resolves `chat release` or `chat-release` through `prompts/registry.json`, including an explicit left-to-right composition containing that alias.

Invoking `chat-release` selects release Qualification strategy `GITHUB_NATIVE`. Do not ask a second strategy-selection question and do not switch to LOCAL because GitHub-native qualification is blocked or RED.

A release is not inferred merely because development work is merged, a branch exists, CI is green, or a commit has not yet been tagged.

Unless the user explicitly requests a dry-run/planning-only release, an explicit `chat-release` invocation authorizes this controller's release-side effects: initialization/reuse of the repository-approved release work surface, repository-approved release integration, and publication through `coferlandia-release-publisher`. It never grants deployment authority.

## Repository authority

Repository policy owns the actual release topology. Never hardcode branch names, merge method, workflow/check names, version baseline, deployment target, or test commands.

Reconstruct authoritative state from current repository/GitHub evidence rather than chat history. Resolve at least:

- repository and repository-defined release source/target refs;
- authoritative target/base SHA;
- repository-approved release work-surface/integration mechanism, including whether GitHub PR integration is required;
- current `.coferlandia/ci/profile.json` and fingerprint;
- repository-defined release manifest storage/format and included-work discovery rules;
- required review policy;
- repository-declared reconciliation, ancestry, freeze or active-release preconditions;
- current release publication policy, including any `publication.github` transport, previous published release, and version lineage when relevant.

If source/target identity, qualification policy, integration policy, manifest contract, candidate-initialization rules, or publication transport are ambiguous, stop fail-closed rather than guessing.

## Release candidate initialization

Before Qualification, establish exactly one current release candidate through repository policy.

1. Re-read source ref and target ref and prove all repository-declared pre-release ancestry/reconciliation/freeze conditions are satisfied.
2. Resolve the exact current source SHA and target/base SHA.
3. If repository policy uses a GitHub pull request as the release work surface:
   - search for an existing open release PR matching the exact source/target and repository release identity;
   - reuse it only when it unambiguously represents the same active release candidate;
   - when no matching PR exists and policy permits controller creation, create the repository-approved release PR (Draft when policy requires a qualification phase before review-ready state);
   - if a conflicting/ambiguous active release PR exists, stop rather than creating a competing release.
4. If repository policy uses another work surface, initialize/reuse only that declared mechanism; do not invent a GitHub PR requirement.
5. Build or currentize the release manifest from authoritative repository/GitHub delta evidence. At minimum, include the work identities required by repository policy and enough release-impact evidence to support later review/version classification. When available/relevant this commonly includes integrated PRs/work items, migrations, environment/configuration changes, and other release-impacting contracts, but the generic controller must not invent project-specific fields.
6. Store/update the manifest only in the repository-defined durable location (managed comment, PR body section, file, or equivalent) and bind it to the exact source candidate and target/base identity.
7. Re-read the initialized work surface. The release candidate SHA is the exact current source/head candidate represented by that work surface, not a value remembered from earlier chat state.

If source changes while a release PR/manifest already exists, currentize the work surface/manifest, mark any previous review/qualification evidence stale, and treat the new exact source SHA as a new release candidate. Do not silently reuse evidence from the older candidate.

Initialization is release metadata/control-plane work; it does not authorize product-code corrections in the release controller.

## Aggregate release review

Before release Qualification, perform or consume the repository-approved aggregate review of the complete exact release delta represented by source candidate versus target/base and the current release manifest.

At minimum, reason across the combined release rather than merely trusting each previously merged work item in isolation. Review relevant cross-change interactions, integration/history correctness, public/API/data-contract compatibility, migrations, environment/configuration effects, release-manifest completeness, operational impact, and any repository-declared release risks.

Use the repository's review mechanism when one is declared; otherwise perform the review within this controller. The resulting exact-candidate release review must end with:

```text
Review Critical: 0
Review Important: 0
```

A release-owned metadata/manifest finding may be corrected within this controller, followed by a fresh aggregate review. A product/development finding returns `RELEASE_REPAIR_REQUIRED`; do not patch product code inside the release controller. If any correction changes the source candidate, base authority, or manifest identity, previous review and qualification evidence are stale.

## Entry contract after initialization/review

Require all of:

1. one current exact release candidate with authoritative source and target refs;
2. a current durable release manifest/reference bound to that candidate/base identity;
3. a valid `.coferlandia/ci/profile.json` with GitHub qualification facts;
4. current profile fingerprint;
5. current aggregate release review with Critical = 0 and Important = 0 for the exact candidate/base/manifest;
6. repository policy that permits release integration from the resolved source into the resolved target;
7. no repository-declared reconciliation, ancestry, freeze, active-release, or release-state blocker.

A repository may impose stronger release preconditions. Consume them without copying project-specific facts into this generic prompt.

## GitHub-native release Qualification

1. Re-read source ref, target ref, exact release candidate SHA, target/base SHA, release manifest, work surface, review state and CI profile fingerprint.
2. Determine the profile-declared GitHub submission mode. Trigger only the declared operation when explicit dispatch is required; otherwise observe existing repository events/checks.
3. Bind all qualification evidence to the exact candidate/effective candidate required by repository identity policy.
4. Evaluate every profile-required gate against its allowed terminal conclusions. Queued, waiting, requested, pending, in-progress, cancelled, stale, superseded, old-SHA or old-profile evidence is not GREEN.
5. Re-read candidate/base/profile/manifest/work-surface/review identity after GitHub gates settle. Any relevant identity drift invalidates qualification.

The repository decides, through its own workflows and routing policy, what constitutes release-grade validation. `chat-release` never substitutes a development-only result for the repository's release gate.

## Failure and repair loop

For RED qualification, inspect the exact current run/job/check and classify the failure.

- **Transient/provider failure:** retry only through repository-approved mechanisms and remain bound to the same candidate unless repository state changes.
- **Release-controller/metadata defect:** correct only release-owned metadata or evidence that is explicitly within this controller's responsibility, perform fresh aggregate review when affected, then requalify.
- **Product/development defect:** return `RELEASE_REPAIR_REQUIRED`. Do not edit product code inside this release controller and do not implicitly invoke `chat-coder`, debugger, Local CI, or another development stage. The repository's normal development flow creates a corrected candidate; re-enter `chat-release` afterward.

Any corrected/new source SHA makes previous release review, Qualification and `READY_FOR_RELEASE` evidence stale. On reentry, currentize the release PR/work surface and manifest, perform fresh aggregate review, and start Qualification again.

## Durable READY_FOR_RELEASE

Only after every current GITHUB_NATIVE release gate is authoritative and GREEN for the exact candidate and the aggregate release review remains current/clean, create or update the repository's managed release handoff using `_protocol/delivery/READY_FOR_RELEASE.md` and marker:

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

Immediately before integration, re-read source/head, target/base, manifest, work surface, profile fingerprint, review state, mergeability and all repository-declared release blockers.

If any release identity, review state, or required gate authority changed, invalidate `READY_FOR_RELEASE` and return `REQUALIFICATION_REQUIRED` rather than integrating stale evidence.

Use the strongest repository-approved integration mechanism. Respect the repository's required merge strategy and history policy. Never force-push, rewrite protected history, silently squash when repository release policy forbids it, or bypass current safeguards.

After integration, prove the intended release candidate reached the declared target ref and resolve the exact resulting target commit SHA. Do not infer the publish target from a pre-merge source SHA when integration produced a distinct commit.

## Release publication

Use the public `coferlandia-release-publisher` skill for **Commit -> Release**. Do not duplicate version/tag/GitHub Release mechanics in this prompt.

The publisher must receive the exact integrated target commit and current repository release policy. Semantic impact comes from the complete release delta and must not be inferred mechanically from filenames or commit prefixes.

For a first published release, unresolved product maturity/version baseline remains a control decision; do not invent `1.0.0` or another baseline.

### GitHub-native publication transport

After integration, re-read current release policy and resolve `publication.github` independently from `.coferlandia/ci/profile.json`. Qualification and publication are distinct contracts. Repository policy may contain additional publication fields owned by the repository or publisher; preserve them.

Supported generic publication modes are:

```json
{
  "publication": {
    "github": {
      "mode": "issue-comment",
      "workflow": ".github/workflows/<repository-declared-workflow>.yml"
    }
  }
}
```

and, only when the active GitHub-native client exposes an explicit workflow-dispatch operation:

```json
{
  "publication": {
    "github": {
      "mode": "workflow-dispatch",
      "workflow": ".github/workflows/<repository-declared-workflow>.yml"
    }
  }
}
```

The canonical publication identity is always explicit: `target_sha`, `version`, `impact`, `title`, and `notes`. No transport may infer those values.

#### `issue-comment` mode

This is the standard Chat-compatible transport. It requires a repository-approved release PR/work surface that accepts GitHub issue comments and a declared workflow listening for the canonical request marker:

```html
<!-- coferlandia-release-publication-request:v1 -->
```

Immediately before requesting publication:

1. Re-read the integrated target ref/SHA, release work surface, current policy, requested version/impact/title/notes, and prove no release identity drift occurred.
2. Verify the declared workflow exists on the repository's publication-capable default/target history and is the workflow named by policy.
3. Create one new top-level release-work-surface comment containing the marker followed by exactly one fenced `json` object with schema `1` and exactly these fields: `schema`, `target_sha`, `version`, `impact`, `title`, `notes`.
4. Do not place secrets, tokens, environment credentials, or deployment instructions in the request comment.
5. The repository workflow must independently authorize the commenting actor, require the release PR to be merged/integrated, require the request `target_sha` to equal that same release PR's exact integration commit (`merge_commit_sha` for a GitHub PR work surface), parse the request as data rather than shell, checkout the exact SHA, and invoke `coferlandia-release-publisher`.
6. Bind publication evidence to the workflow run causally triggered by that exact newly created comment/event. Older runs are not current evidence.
7. Observe the run to a successful terminal conclusion; queued/pending/cancelled/stale/RED runs are not success.
8. Independently re-read the resulting annotated tag and GitHub Release and prove both resolve coherently to the exact integrated target SHA and requested release identity.

If the declared workflow does not bind request `target_sha` to the exact release-work-surface integration commit, treat the publication surface as invalid and return `RELEASE_PUBLICATION_BLOCKED` rather than sending a request to a weaker transport.

If reentry sees an existing request comment, inspect its causally associated run and resulting publication state before creating another request. Rely on publisher idempotency/recovery semantics rather than duplicating or moving published identities.

#### `workflow-dispatch` mode

Use this mode only when the active GitHub-native surface actually exposes an explicit Actions dispatch capability. Verify the declared workflow contract, dispatch only that workflow with the canonical exact identity inputs, bind to the newly created run, require success, then independently verify tag/Release identity exactly as above. Never claim this mode is executable merely because GitHub Actions supports it if the current client cannot dispatch it.

The repository workflow is only a transport for `coferlandia-release-publisher`; it never becomes a second implementation of annotated tag/GitHub Release mechanics and it never deploys.

If `publication.github` is absent, declares `mode = none`, is invalid, references a missing workflow, cannot be triggered by the active GitHub-native surface, cannot authorize/bind the publication request unambiguously, or produces mismatched publication evidence, return `RELEASE_PUBLICATION_BLOCKED`. Do not fall back to LOCAL, do not bypass the repository contract with ad-hoc tag/release creation, and do not mutate publication identity directly from this prompt.

After publication, verify the annotated tag and GitHub Release resolve coherently to the exact intended commit. Publication success is not deployment success.

## Closeout and reentry

Apply only repository-declared release closeout behavior after publication verification, for example release-manifest traceability, issue annotations, branch reconciliation, or release-state cleanup. Generic `chat-release` does not invent those policies.

Reentry always reconstructs current state. If integration already completed but publication is partially complete, use `coferlandia-release-publisher` consistency/recovery semantics rather than recreating or moving published identities. If a prior GitHub-native publication workflow already ran, bind to and inspect that exact run/release state before considering any new trigger.

Terminal/resumable states include:

```text
RELEASE_INITIALIZATION_BLOCKED
RELEASE_REVIEW_BLOCKED
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
Review Critical = 0
Review Important = 0
Qualification evidence = <durable reference>
Included work = <release manifest/reference>
Publication evidence = <request comment + workflow/run identity>
Release = <version/tag/GitHub Release identity>
Deployment = NOT PERFORMED
```
