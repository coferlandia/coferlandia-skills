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

Use this skill to adapt repository-specific CI and release-delivery facts to Coferlandia's generic controllers without copying generic controller behavior into the repository.

Do not generate repository-local copies of generic Coferlandia prompts or skills. Adapt only the repository-owned CI profile, release policy, and publication workflow surfaces described here. This skill does not run CI itself; CI execution remains owned by the selected CI controller.

The boundaries are deliberate:

```text
repository study
  -> .coferlandia/ci/profile.json              # Qualification only
  -> repository release policy
       -> publication.github transport          # Publication transport only
       -> repository GitHub Actions workflow
            -> coferlandia-release-publisher    # Commit -> Release mechanics
```

Qualification and publication are separate contracts. Do not put release publication fields into `.coferlandia/ci/profile.json`.

## CI adaptation

Study the repository's actual documentation, workflows, scripts, tests, required services and authoritative GitHub gates before changing the CI profile. Preserve existing commands and semantics; do not invent or generalize project-specific facts.

The CI profile remains the minimal deterministic contract shared by Chat GitHub-native CI and Local CI. Validate/fingerprint/render it with the adapter CLI and change it only when Qualification facts change.

## GitHub-native publication adaptation

Publication adaptation is explicit and opt-in. When complete GitHub-native release delivery is requested, read `references/publication-contract.md` before materializing anything.

The adapter may maintain only the repository's `publication.github` transport block and the workflow named by that block. Repository-owned sibling publication fields must be preserved.

The standard Chat-compatible transport is `issue-comment`: a merged release PR receives one versioned publication request comment, and the generated workflow validates actor authority, binds the exact request SHA to that PR's exact integration commit, checks out that SHA, and delegates Commit -> Release mechanics to `coferlandia-release-publisher`.

Publication runner selection is repository-specific. Do not assume GitHub-hosted runners are available. During repository study, determine the publication-capable runner contract explicitly. If no repository-specific runner is needed, the adapter defaults to `ubuntu-latest`; otherwise materialize `publication.github.runs_on` and the matching generated `runs-on` expression. Never infer publication runner labels from unrelated Qualification profile fields.

Preview deterministic materialization:

```bash
python skills/meta/coferlandia-ci-adapter/scripts/coferlandia-ci-adapter-cli.py publication render \
  --policy <release-policy.json> \
  --target-root <repo-root> \
  --publisher-path <repo-relative-coferlandia-release-publisher-entrypoint> \
  --runs-on <runner-label> [<runner-label> ...] \
  --dry-run \
  --json
```

Omit `--runs-on` only when the repository may intentionally use the default `ubuntu-latest` runner. Existing `publication.github.runs_on` policy is preserved by rendering when the CLI flag is omitted.

## Review requirements

Before applying changes, verify:

- CI profile changes correspond to real Qualification changes only;
- publication transport stays out of `.coferlandia/ci/profile.json`;
- existing repository publication fields are preserved;
- `publication.github.workflow` is a safe repository-relative workflow path;
- `publication.github.runs_on`, when present, is a non-empty runner label or non-empty unique label list actually available to the repository;
- generated publication workflows do not deploy;
- exact release identity is supplied by the controller, not inferred by the workflow;
- actor authorization, merged-PR checks and exact `merge_commit_sha` binding remain intact;
- the publisher entrypoint is repository-relative and safe;
- repository review/CI covers the generated workflow before it is used for release publication.

## Deterministic tooling

Use the adapter CLI for profile validation/fingerprinting/rendering and publication policy/workflow validation/rendering. The tooling is deterministic, non-interactive and supports dry-run. The skill itself does not execute CI or publish releases.
