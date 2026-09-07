# AGENTS.md — Agent Skills Repository

> **If you're an AI agent, start here.**

This file is your entry point to `coferlandia-skills`. Read it in full before doing anything.

---

## What this repository is

An **Agent Skills** repository in [agentskills.io](https://agentskills.io) format, built to be used and maintained by AI agents. Each public skill is a specialized operational contract. The repository also owns a small `prompts/` family for reusable Chat delivery controllers. Repository-local skills under `.agents/skills/` govern this repository itself and are not shipped in the plugin.

## Canonical contract

The [agentskills.io specification](https://agentskills.io/specification) is the authority on public skill structure/frontmatter/progressive disclosure. `_protocol/PROMPT_SPEC.md` owns the separate Chat prompt format. This repo adds verifiable local conventions for categories, status, behavioral evidence, delivery handoffs, version history, packaging, and release readiness.

**Philosophy:** this repo is *for agents* and *by agents*. You have everything required to create, improve, validate, release, and maintain its contracts without relying on hidden conversational instructions.

---

## Repository map

```text
coferlandia-skills/
├── AGENTS.md              ← You are here
├── README.md              ← Human-facing overview and generated latest-release summary
├── RELEASE-NOTES.md       ← Repository/plugin release history
├── SKILLS-GUIDE.md        ← Human-oriented catalog
├── LICENSE                ← Apache License 2.0
├── prompts/               ← Repository-addressable Chat delivery controllers; not Agent Skills plugin payload in V1
├── .claude-plugin/        ← Agent Skills plugin and marketplace metadata
├── .agents/skills/        ← Repository-local maintenance skills; never shipped
├── _protocol/             ← Creation, quality, delivery, versioning, and release protocol
└── skills/                ← Public Agent Skills
    ├── INDEX.md           ← Canonical public skill inventory
    └── <category>/<skill>/
        ├── SKILL.md       ← Current contract and version
        └── CHANGELOG.md   ← Skill-specific version history
```

---

## Before doing anything else

1. Read `skills/meta/using-project-skills/` and invoke any matching public skill before responding or acting.
2. Also inspect `.agents/skills/` for a repository-local skill that more specifically owns the requested repository operation.
3. When the request explicitly invokes a Chat delivery controller, resolve it through `prompts/registry.json` and load only the requested prompt(s).
4. A repository-local skill overrides a weaker generic public workflow when it explicitly owns the same operation.

## Using an existing public skill

1. Read `skills/INDEX.md` to find available public skills.
2. Read the relevant skill's `SKILL.md` in full.
3. Load its references only under the conditions stated by that skill.
4. Follow the complete contract and preserve its authority boundaries.

## Using Chat delivery prompts

1. Read `prompts/BOOTSTRAP.md` and `prompts/registry.json`.
2. Resolve only aliases explicitly requested (`chat coder`, `ci`/`gh ci`, `merge`, or external `local ci`).
3. Execute compositions left-to-right without inserting missing stages or changing Qualification strategy.
4. Read `_protocol/delivery/` for shared READY_FOR_CI / READY_FOR_MERGE / requalification contracts.
5. `prompts/` is repository-addressable in V1; do not pretend it is installed as an Agent Skill through the `.plugin` package.

## Creating or changing a public skill

1. Read `_protocol/HOW_TO_CREATE_SKILLS.md`.
2. Use `_protocol/SKILL_TEMPLATE.md` for both `SKILL.md` and `CHANGELOG.md`.
3. Use `superpowers:writing-skills` when available.
4. Validate against `_protocol/QUALITY_STANDARDS.md` and run `_protocol/scripts/validate_skill.py`.
5. Update `skills/INDEX.md` only when inventory, location, category, status, or discovery summary changes.
6. Before final delivery, run the repository-local release-maintenance gate described below.

## Creating or changing a Chat prompt

1. Read `_protocol/PROMPT_SPEC.md` and `_protocol/PROMPT_QUALITY_STANDARDS.md`.
2. Keep repository-specific CI facts out of generic prompt bodies; use `.coferlandia/ci/profile.json` in consumer repositories.
3. Update `prompts/registry.json` only for prompt identity/alias/composition changes.
4. Run `python _protocol/scripts/validate_prompt.py validate --root .` and the prompt/delivery contract tests.
5. Treat prompt changes as repository public-surface changes and document them in release notes; do not silently package them as Agent Skills.

---

## Source of truth per rule

Every rule has one owner. Other documents link to it instead of copying competing versions.

| Rule | Owner |
|---|---|
| Naming, categories, commit convention, and skill version format | [`_protocol/NAMING_CONVENTIONS.md`](./_protocol/NAMING_CONVENTIONS.md) |
| Quality and safety checklist | [`_protocol/QUALITY_STANDARDS.md`](./_protocol/QUALITY_STANDARDS.md) |
| SKILL.md format and progressive disclosure | [agentskills.io/specification](https://agentskills.io/specification) |
| Skill inventory and row format | [`skills/INDEX.md`](./skills/INDEX.md) |
| Chat prompt identity/aliases/composition | [`prompts/registry.json`](./prompts/registry.json) |
| Chat prompt format/quality | [`_protocol/PROMPT_SPEC.md`](./_protocol/PROMPT_SPEC.md), [`_protocol/PROMPT_QUALITY_STANDARDS.md`](./_protocol/PROMPT_QUALITY_STANDARDS.md) |
| Delivery handoffs/requalification | [`_protocol/delivery/`](./_protocol/delivery/) |
| Lifecycle states | [`_protocol/SKILL_LIFECYCLE.md`](./_protocol/SKILL_LIFECYCLE.md) |
| When and how to invoke project skills | [`skills/meta/using-project-skills/`](./skills/meta/using-project-skills/) |
| Artifact output paths | [`_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md`](./_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md) |
| Per-skill changelog and repository release policy | [`_protocol/RELEASE_MAINTENANCE.md`](./_protocol/RELEASE_MAINTENANCE.md) |
| Semantic final-delivery classification and coordination | [`.agents/skills/coferlandia-release-maintainer/`](./.agents/skills/coferlandia-release-maintainer/) |
| Current repository/plugin release | [`.claude-plugin/plugin.json`](./.claude-plugin/plugin.json) |
| Repository/plugin release history | [`RELEASE-NOTES.md`](./RELEASE-NOTES.md) |
| Latest human-facing release summary | Generated block in [`README.md`](./README.md) |

---

## Mandatory final-delivery release gate

The gate applies before:

- the final implementation or release-preparation commit;
- marking a pull request ready for final review/integration;
- merging or squashing into `main`;
- generating or publishing an installable plugin package.

It does **not** require every intermediate RED/GREEN/refactor checkpoint commit to represent a complete release.

When a final diff touches any shipped Agent Skill surface (`skills/**`, `_protocol/**`, `.claude-plugin/**`, public installation/discovery documentation, packaging, or license):

1. Read and invoke `.agents/skills/coferlandia-release-maintainer/SKILL.md`.
2. Inspect the complete diff against the intended integration base.
3. Classify every affected public skill and the repository/plugin semantic impact.
4. Synchronize skill versions, per-skill changelogs, plugin version, release notes, and the README managed summary.
5. Run:

```bash
python _protocol/scripts/validate_skill.py --all skills
python _protocol/scripts/bump_version.py --check
python _protocol/scripts/bump_version.py --audit
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py check --base <integration-base> --release-ready
```

6. Build and verify the exact reviewed branch state:

```bash
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py package \
  --output coferlandia-skills.plugin --verify
```

7. Do not commit, mark ready, or integrate while any release gate, validation, review, or package verification finding remains unresolved.

The Agent Skills package must exclude `.agents/**`, `.agent/**`, Git state, caches, temporary plans, secrets, and the repository-addressable `prompts/` family in V1. Packaging must never run `git pull`; it packages the already-reviewed Agent Skills state.

---

## Skills at a glance

See `skills/INDEX.md` for the complete public Agent Skill catalog and `prompts/INDEX.md` for Chat delivery controllers. Repository-local skills are intentionally absent from the public index and plugin packages.

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE). This repository and its contracts are provided "as is," without warranty. Verify behavior and evidence before relying on any skill or prompt for consequential work.
