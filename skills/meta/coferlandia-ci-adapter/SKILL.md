---
name: coferlandia-ci-adapter
description: >
  Use when the user or controlling authority asks to adapt a repository to Coferlandia's generic
  Chat/Local CI controllers or complete GitHub-native release delivery. Study the repository's real
  CI/testing/release workflow contracts, maintain the minimal .coferlandia/ci/profile.json, and when
  explicitly requested materialize the separate repository-declared GitHub-native publication surface.
  It does not execute CI/releases, copy generic prompts/skills, or invent project commands.
license: Apache-2.0
compatibility: >
  Requires read access to the target repository and its GitHub workflows/documentation, Python 3.11+
  for deterministic adapter tooling, and write access only after the proposed adaptation is approved.
metadata:
  author: coferlandia
  version: "1.1.1"
  category: meta
  status: active
  tested: "2026-09-12 - CI profile compatibility plus opt-in GitHub-native release publication policy/workflow validation, configurable publication runners, and deterministic rendering covered by unittest."
---

## Context

This meta-skill adapts one repository to shared Coferlandia delivery contracts. It does not run CI itself and does not publish a release.

Qualification remains a distinct contract:

```text
repository truth (docs/scripts/workflows/services)
        -> approved minimal CI profile
             -> Chat ci.md
             -> local-ci skill
```

When the controlling request explicitly includes complete GitHub-native release delivery, the adapter may additionally materialize a separate publication surface:

```text
repository release policy
        -> publication.github transport
        -> repository GitHub Actions workflow
        -> coferlandia-release-publisher
        -> chat-release observes/verifies publication
```

The repository remains authoritative. `.coferlandia/ci/profile.json` is only the Qualification interface; publication configuration belongs to `.coferlandia/release/policy.json` and MUST NOT be inserted into the CI profile.

## Activation

Activate when the controlling authority explicitly asks to create/update a Coferlandia CI profile, adapt a repository for the generic CI prompt/skill, adapt the repository for complete Coferlandia GitHub-native delivery, or names `coferlandia-ci-adapter` for a target repository.

Do not activate merely to run tests, diagnose one CI failure, merge a PR, publish one release from an already-adapted repository, or mine unrelated project skills.

## Workflow

### 1. Study without modification

Read `references/discovery.md`. Inspect current `AGENTS.md`, development/testing/release docs, canonical validation scripts, package/build metadata, required services, GitHub workflows/checks/gates, merge-group behavior, release policy and exceptional lanes. Prefer executable current behavior over historical prose.

Record evidence for Qualification:

```text
canonical documentation
local working directory and qualification command(s)
required local services/environment
GitHub submission mode/workflow
required authoritative gates + allowed conclusions
merge_group semantics
base/profile sensitivity
exceptional lanes and their external authorization owner
```

When GitHub-native release publication is in scope, additionally record:

```text
release policy location and current publication fields
publisher skill/path available in the target repository
repository-approved publication workflow path
publication-capable GitHub Actions runner label(s)
release PR/work surface usable for durable control comments
permissions/environment constraints for creating tags and GitHub Releases
whether publication is intentionally disabled
```

Do not assume `ubuntu-latest` is available. Determine the publication runner from current repository workflow/runner evidence. Do not infer publication runner labels from `.coferlandia/ci/profile.json`; Qualification and Publication remain separate contracts even when they happen to use the same runner pool.

Do not modify the target repository during discovery.

### 2. Produce a proposal and approval gate

Propose the exact CI profile with source evidence and unresolved ambiguities. Do not guess a workflow/check or copy every incidental test command when one canonical repository command already owns full qualification.

When publication adaptation is in scope, separately propose the exact `publication.github` policy block, publication runner contract, and generated workflow. Keep repository-owned publication siblings such as version-control decisions intact; the adapter owns only the GitHub-native transport block it materializes.

Stop for explicit approval before writing repository configuration unless the controlling request already authorizes the exact adaptation scope.

### 3. Validate CI deterministically

Place the approved semantic profile in a transient JSON input and run:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py profile validate --profile <input> --json
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py profile fingerprint --profile <input> --json
```

The CLI rejects unknown top-level fields, secret-bearing keys, empty local qualification, ambiguous gates and invalid merge-group settings.

### 4. Render the canonical repository CI profile

Preview:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py profile render \
  --input <approved-profile.json> --target-root <repo-root> --dry-run --json
```

After approval, repeat without `--dry-run`. The canonical generated CI profile path is:

```text
.coferlandia/ci/profile.json
```

Do not generate repository-local copies of generic prompts or skills.

### 5. Adapt GitHub-native release publication when explicitly in scope

Read `references/publication-contract.md`. Publication adaptation is opt-in and separate from the CI profile.

Validate an existing release policy without writing:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py publication validate \
  --policy <release-policy.json> --json
```

Preview deterministic materialization:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py publication render \
  --policy <release-policy.json> \
  --target-root <repo-root> \
  --publisher-path <repo-relative-coferlandia-release-publisher-entrypoint> \
  --workflow-path .github/workflows/coferlandia-release-publish.yml \
  --runs-on <runner-label> [<runner-label> ...] \
  --dry-run --json
```

Omit `--runs-on` only when repository study confirms the compatible default `ubuntu-latest` is intentionally valid. If the current policy already declares `publication.github.runs_on`, rendering without the flag preserves that value.

After approval, repeat without `--dry-run`. This writes only:

```text
.coferlandia/release/policy.json
.github/workflows/<approved-publication-workflow>.yml
```

The adapter preserves existing repository publication fields and materializes the Chat-compatible transport:

```json
{
  "publication": {
    "github": {
      "mode": "issue-comment",
      "workflow": ".github/workflows/<approved-publication-workflow>.yml",
      "runs_on": ["<repository-approved-runner-label>"]
    }
  }
}
```

`runs_on` may be a single non-empty runner string or a non-empty duplicate-free list of labels. The generated workflow uses the same value deterministically. When `runs_on` is absent, the adapter remains backward compatible and defaults to `ubuntu-latest`.

The generated workflow listens for the canonical `<!-- coferlandia-release-publication-request:v1 -->` marker on a newly created release-PR comment. The request carries only `schema`, `target_sha`, `version`, `impact`, `title`, and `notes`. The workflow independently requires `admin|maintain` authority, requires the PR to be merged, parses the request as data, checks out the exact SHA, grants only the minimal read permissions plus `contents: write`, and delegates Commit -> Release mechanics to `coferlandia-release-publisher`. It never deploys.

`workflow-dispatch` remains a valid policy transport for clients that actually expose an Actions dispatch primitive, but this adapter's standard generated Chat surface is `issue-comment` because it is executable through the generic Chat GitHub connector.

### 6. Verify drift and consumers

Run `profile check` against the stored CI fingerprint. Pressure-test the relevant execution surfaces:

- Chat/GitHub-native CI can identify exact gates without local commands.
- Local CI can identify exact local qualification without hardcoded project knowledge.
- Both bind output to the same profile fingerprint and shared READY_FOR_MERGE envelope.
- Exceptional lanes remain externally authorized and repository-owned.
- When publication adaptation is enabled, `chat-release` can resolve one repository-declared publication surface independently from CI qualification.
- For `issue-comment`, Chat can create the canonical request on the release PR and bind the resulting run to that exact request.
- Missing/disabled publication remains fail-closed; no LOCAL fallback is introduced.
- The publication workflow uses the repository-approved runner contract, exact integrated SHA supplied by `chat-release`, and invokes the generic publisher rather than reproducing tag/release shell logic.

### 7. Maintenance

Re-run this skill when repository CI facts materially change: canonical command, required service, workflow/gate identity, allowed terminal conclusions, merge-group authority, base sensitivity, or exceptional-lane contract. A changed profile fingerprint invalidates older READY_FOR_MERGE evidence.

When GitHub-native publication has been adapted, also re-run it when release-policy ownership, publisher path, publication workflow path, publication runner labels, release work-surface contract, required permissions, or supported publication transport changes. Publication changes do not alter the CI profile fingerprint unless Qualification facts also changed.

## Gotchas

- **Copying generic controllers into the project:** prohibited. Adapt through repository interfaces.
- **Treating docs as newer than executable truth:** reconcile them; do not encode stale commands.
- **Storing tokens/secrets/current CI results:** prohibited by contract and deterministic validation.
- **Inventing a fallback:** execution strategy stays with the controlling authority; GITHUB_NATIVE publication never silently falls back to LOCAL.
- **Encoding merge or publication behavior as CI:** keep Integration and Publication policy in repository authority; `.coferlandia/ci/profile.json` contains only Qualification/effective-candidate facts needed to validate evidence.
- **Assuming `ubuntu-latest`:** prohibited when repository evidence requires another publication runner. Declare `publication.github.runs_on` explicitly instead.
- **Inferring publication runners from the CI profile:** prohibited. Publication runner selection is repository-owned release transport configuration.
- **Duplicating release mechanics in a workflow:** prohibited. The workflow transports exact identity to `coferlandia-release-publisher`; it does not reimplement annotated tags or GitHub Releases.
- **Trusting arbitrary comment authors:** prohibited. The generated issue-comment workflow independently checks repository permission and merged-PR state before any publication mutation.
- **Auto-authorizing HOTFIX or release publication:** prohibited. Adaptation creates capability, not authority to use it.

## Expected Output

```text
Coferlandia repository adapter result
Target repository: <owner/repo>
CI profile: .coferlandia/ci/profile.json
Profile fingerprint: <sha256>
Canonical local qualification: <references>
GitHub qualification gates: <references>
Merge-group authority: <summary>
Exceptional lanes: <references | none>
GitHub-native publication: <not requested | disabled | issue-comment workflow path>
Publication runner: <default ubuntu-latest | repository labels | not applicable>
Release policy: <path | not touched>
Publisher entrypoint: <path | not applicable>
Unresolved ambiguity: <none | items>
Generic prompt/skill copies generated: no
Validation: <commands/results>
```

## Output Location

Discovery/proposal notes are conversational or follow the target repository's approved `.agent/` planning convention. Standard target-repository configuration written by this skill is limited to the CI profile and, when explicitly requested, release publication transport files.

### Output Exceptions

- `.coferlandia/ci/profile.json` — approved static CI interface definition.
- `.coferlandia/release/policy.json` — existing/approved release policy with `publication.github` transport materialized when requested.
- `.github/workflows/<approved-publication-workflow>.yml` — generated GitHub-native publication transport when requested.

## Scripts Available

- **`scripts/coferlandia-ci-adapter-cli.py`** — validates, fingerprints, checks and atomically renders repository CI profiles; validates and atomically renders optional GitHub-native release publication transport. Run `capabilities --json` for the public command catalog.

## References

- Read `references/discovery.md` before repository study.
- Read `references/profile-contract.md` while proposing/reviewing CI profile fields.
- Read `references/publication-contract.md` when complete GitHub-native release delivery is in scope.
- Read `references/authority-and-staleness.md` when sources conflict or CI/release identity changed.
- Read `references/testing.md` before completion/pressure validation.
