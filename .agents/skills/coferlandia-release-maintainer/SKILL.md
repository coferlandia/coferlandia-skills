---
name: coferlandia-release-maintainer
description: >
  Use only inside the coferlandia-skills repository when a change is approaching its final
  commit, final pull-request readiness, integration, release, version bump, plugin rebuild,
  or release-readiness validation. Coordinates per-skill versions and changelogs, the
  repository/plugin version, release notes, README summary, manifests, package verification,
  and CI through one deterministic final-delivery gate. Do not activate for the first
  intermediate implementation edit or for unrelated repositories.
license: Apache-2.0
compatibility: >
  Requires Python 3.11+, git for diff-aware checks, and write access for prepare/render/package
  operations. The skill never commits, pushes, merges, tags, or publishes a GitHub Release.
metadata:
  author: coferlandia
  version: "1.0.0"
  category: meta
  status: active
  tested: "2026-08-01 - activation contract and deterministic CLI tests cover rendering, preparation, drift detection, release-ready enforcement, and verified packaging."
---

## Context

This repository ships two independent version axes:

- each public skill's `metadata.version`, with its history in that skill's `CHANGELOG.md`;
- one repository/plugin release version, with history in `RELEASE-NOTES.md`.

This skill is the repository-local release coordinator. It does not replace the public generic
`skill-repository-versioning` skill; that skill must defer here when this local contract exists.

The governing rule is:

> A shipped change is not ready for final commit, PR readiness, or integration until skill,
> repository, plugin, documentation, and package surfaces describe the same release.

Read `_protocol/RELEASE_MAINTENANCE.md` as the canonical policy. Read
`references/release-model.md` when deciding ownership and version axes.

## Activation

Activate when this repository is approaching:

- the final implementation or release-preparation commit;
- final PR review/readiness or explicit integration;
- a skill or plugin version change;
- release-note or README release-summary maintenance;
- plugin package generation or verification;
- release-readiness validation.

Do not activate merely because implementation started, a RED test was added, or an intermediate
checkpoint commit is being created. Intermediate commits may remain unreleased; the final branch
state may not.

## Required disciplines

- Use `superpowers:writing-skills` before changing any skill instructions or activation cases.
- Use `superpowers:test-driven-development` for CLI/check/render/package behavior.
- Use `superpowers:verification-before-completion` before claiming the gate or package passed.
- Inspect the complete final diff. Do not classify semantic impact from filenames alone.

## Workflow

### 1. Inspect the complete delivery diff

Run:

```bash
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py inspect --base <integration-base>
```

Identify:

- public skills whose shipped behavior changed;
- repository-local-only changes;
- protocol, manifest, packaging, installation, and discovery changes;
- README/index/release-note changes;
- compatibility or migration impact.

Read `references/change-classification.md` before selecting version impact.

### 2. Make semantic release decisions

For every affected public skill, decide explicitly:

- editorial only, or behavioral;
- previous and next skill version;
- concise externally meaningful summary;
- compatibility/migration note when required.

For the repository/plugin, select one semantic impact from the complete delivery:

- patch: compatible correction;
- minor: additive compatible capability;
- major: incompatible/removal/migration requiring consumer adaptation.

A public skill behavior/version change is a shipped plugin change and requires a repository/plugin
release. Repository-local `.agents/**` changes alone do not.

### 3. Prepare synchronized artifacts

Create a transient release plan under `.agent/` when persistence is useful, then run:

```bash
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py prepare --input .agent/release-plan.json
```

The deterministic preparation may update:

- affected `SKILL.md` versions;
- affected per-skill `CHANGELOG.md` files;
- `.claude-plugin/plugin.json`;
- `RELEASE-NOTES.md`;
- the managed latest-release block in `README.md`.

Update `skills/INDEX.md` only when inventory, name, path, category, status, or discovery summary
changed. Do not use it as release history.

Review plugin URLs, marketplace descriptions, installation text, and package inputs whenever those
surfaces changed.

### 4. Validate the final-delivery gate

Run the repository tests plus:

```bash
python _protocol/scripts/validate_skill.py --all skills
python _protocol/scripts/bump_version.py --check
python _protocol/scripts/bump_version.py --audit
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py check --base <integration-base> --release-ready
```

The gate fails when, among other conditions:

- a changed public skill lacks a version bump, changelog entry, or release-note row;
- a changelog's latest version differs from `metadata.version`;
- the plugin version differs from the latest released section;
- README's managed summary is stale;
- material content remains only under `Unreleased`;
- version drift/audit fails.

Do not commit or integrate with an unresolved gate failure.

### 5. Build and verify the plugin

Run:

```bash
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py package \
  --output coferlandia-skills.plugin --verify
```

The package must include the public skills, protocol, plugin metadata, README, AGENTS, release notes,
skills guide, and license. It must exclude `.agents/**`, `.agent/**`, Git state, caches, and secrets.
Do not run `git pull` as part of packaging. Reopen and verify the archive before success.

### 6. Hand off to review/integration

Use `references/final-delivery-checklist.md`. Report:

- changed skills and version transitions;
- repository/plugin version transition;
- release-note and README state;
- validation commands and results;
- package path, digest, and verification result;
- unresolved findings, if any;
- exact suggested final commit message.

The skill never commits, pushes, merges, tags, or publishes. The active Git authority performs those
actions only after this gate passes.

## Existing generic skill boundary

When `skills/meta/skill-repository-versioning/` activates in this repository, it must detect and
defer to this local skill. Do not run two competing release protocols or let the weaker generic
policy override this repository's rules.

## Gotchas

- **Running on every checkpoint commit:** wrong. Run at final delivery, not every RED/GREEN step.
- **Treating a skill bump as unrelated to plugin release:** wrong for shipped public skill changes.
- **Putting complete history in README:** wrong. README shows only the generated latest summary.
- **Using RELEASE-NOTES as the only skill history:** wrong. Each public skill owns a changelog.
- **Inferring semantic impact mechanically:** wrong. The agent decides; the CLI verifies consistency.
- **Packaging after pulling main:** wrong. Package the reviewed branch state exactly as validated.
- **Including `.agents/` in the plugin:** wrong. The release-maintainer is repository-local.
- **Declaring package success without reopening it:** prohibited.
- **Leaving shipped work under `Unreleased`:** prohibited in release-ready state.

## Output Location

This skill updates standard repository artifacts in place. Transient semantic release plans may be
stored under `.agent/` and must not be included in the plugin package.

## Expected Output

```text
Coferlandia release-maintenance result

Base: <ref>
Changed public skills: <name old->new | none>
Repository/plugin version: <old->new | unchanged>
Skill changelogs: PASS | FAIL
Release notes: PASS | FAIL
README managed summary: PASS | FAIL
Index/discovery: PASS | FAIL | not needed
Version check/audit: PASS | FAIL
Full validation: PASS | FAIL
Package: <path | not built>
Package SHA-256: <digest | n/a>
Package verification: PASS | FAIL | not run
Ready for final commit/integration: yes | no
Suggested commit message: <exact text>
```

## References

- Read `references/release-model.md` for canonical ownership, version axes, and shipped/local boundaries.
- Read `references/change-classification.md` before deciding editorial/behavioral and semantic impact.
- Read `references/final-delivery-checklist.md` during final validation, package verification, and handoff.
