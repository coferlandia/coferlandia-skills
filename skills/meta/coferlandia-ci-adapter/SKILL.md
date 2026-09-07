---
name: coferlandia-ci-adapter
description: >
  Use when the user or controlling authority asks to adapt a repository to Coferlandia's generic
  Chat/Local CI controllers by studying its real CI/testing/workflow contract and creating or updating
  the minimal .coferlandia/ci/profile.json consumed by both strategies. Explicit repository-adaptation
  work only; it does not execute CI, copy generic prompts/skills, or invent project commands.
license: Apache-2.0
compatibility: >
  Requires read access to the target repository and its GitHub workflows/documentation, Python 3.11+
  for deterministic profile tooling, and write access only after the profile proposal is approved.
metadata:
  author: coferlandia
  version: "1.0.0"
  category: meta
  status: active
  tested: "2026-09-07 - deterministic profile validation/fingerprinting/rendering, unsafe-field rejection, activation boundaries, and repository conformance fixtures covered by unittest."
---

## Context

This meta-skill adapts one repository to the shared Coferlandia Qualification contract. It does not run CI itself.

```text
repository truth (docs/scripts/workflows/services)
        -> approved minimal CI profile
             -> Chat ci.md
             -> local-ci skill
```

The repository remains authoritative. The profile is a small, static interface definition at `.coferlandia/ci/profile.json`; it must not become a second CI engine, store current results, or contain secrets.

## Activation

Activate when the controlling authority explicitly asks to create/update a Coferlandia CI profile, adapt a repository for the generic CI prompt/skill, or names `coferlandia-ci-adapter` for a target repository.

Do not activate merely to run tests, diagnose one CI failure, merge a PR, or mine unrelated project skills.

## Workflow

### 1. Study without modification

Read `references/discovery.md`. Inspect current `AGENTS.md`, development/testing docs, canonical validation scripts, package/build metadata, required services, GitHub workflows/checks/gates, merge-group behavior, and exceptional lanes. Prefer executable current behavior over historical prose.

Record evidence for:

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

Do not modify the target repository during discovery.

### 2. Produce a proposal and approval gate

Propose the exact profile with source evidence and unresolved ambiguities. Do not guess a workflow/check or copy every incidental test command when one canonical repository command already owns full qualification.

Stop for explicit approval before writing `.coferlandia/ci/profile.json`, unless the user supplied an already-approved exact profile contract.

### 3. Validate deterministically

Place the approved semantic profile in a transient JSON input and run:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py profile validate --profile <input> --json
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py profile fingerprint --profile <input> --json
```

The CLI rejects unknown top-level fields, secret-bearing keys, empty local qualification, ambiguous gates and invalid merge-group settings.

### 4. Render the canonical repository profile

Preview:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py profile render \
  --input <approved-profile.json> --target-root <repo-root> --dry-run --json
```

After approval, repeat without `--dry-run`. The only canonical generated profile path is:

```text
.coferlandia/ci/profile.json
```

Do not generate repository-local copies of `prompts/ci.md`, `prompts/chat-coder.md`, `prompts/merge.md`, or the `local-ci` skill.

### 5. Verify profile drift and both consumers

Run `profile check` against the stored fingerprint. Then pressure-test both execution surfaces conceptually/with fixtures:

- Chat/GitHub-native CI can identify exact gates without local commands.
- Local CI can identify exact local qualification without hardcoded project knowledge.
- Both bind output to the same profile fingerprint and shared READY_FOR_MERGE envelope.
- Exceptional lanes remain externally authorized and repository-owned.

### 6. Maintenance

Re-run this skill when repository CI facts materially change: canonical command, required service, workflow/gate identity, allowed terminal conclusions, merge-group authority, base sensitivity, or exceptional-lane contract. A changed profile fingerprint invalidates older READY_FOR_MERGE evidence.

## Gotchas

- **Copying generic controllers into the project:** prohibited. Adapt through the profile.
- **Treating docs as newer than executable truth:** reconcile them; do not encode stale commands.
- **Storing tokens/secrets/current CI results:** prohibited by contract and deterministic validation.
- **Inventing a fallback:** the profile exposes both strategies; execution choice stays with the controlling authority.
- **Encoding merge behavior as CI:** keep Integration policy in repository authority; profile contains only qualification/effective-candidate facts needed to validate evidence.
- **Auto-authorizing HOTFIX:** prohibited. Record only the repository documentation and external authorization owner.

## Expected Output

```text
CI adapter result
Target repository: <owner/repo>
Profile: .coferlandia/ci/profile.json
Profile fingerprint: <sha256>
Canonical local qualification: <references>
GitHub qualification gates: <references>
Merge-group authority: <summary>
Exceptional lanes: <references | none>
Unresolved ambiguity: <none | items>
Generic prompt/skill copies generated: no
Validation: <commands/results>
```

## Output Location

Discovery/proposal notes are conversational or follow the target repository's approved `.agent/` planning convention. The only standard target-repository configuration written by this skill is `.coferlandia/ci/profile.json`.

### Output Exceptions

- `.coferlandia/ci/profile.json` — approved static CI interface definition.

## Scripts Available

- **`scripts/coferlandia-ci-adapter-cli.py`** — validates, fingerprints, checks and atomically renders repository CI profiles. Run `capabilities --json` for the public command catalog.

## References

- Read `references/discovery.md` before repository study.
- Read `references/profile-contract.md` while proposing/reviewing profile fields.
- Read `references/authority-and-staleness.md` when sources conflict or CI identity changed.
- Read `references/testing.md` before completion/pressure validation.
