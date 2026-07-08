# Coferlandia Skills Release Notes

## v1.5.0 (2026-07-08)

### Skills

- **coferlandia-project-manager** (`meta`) - v1.0.0. Added a new project-local
  skill for operating a repo-scoped project manager home, with repo-local
  defaults for runtime artifacts, Obsidian vault output, onboarding, and
  readiness checks.

### Repository

- `coferlandia-skills` - bumped the repo-wide release version to include the new
  skill and its packaging surface.

## v1.4.0 (2026-07-07)

### Protocol

- `HOW_TO_CREATE_SKILLS.md` â€” added an explicit reference to
  `superpowers:writing-skills` in the prerequisites for skill authoring, so
  approved skill drafts follow the dedicated writing workflow when that skill is
  available.

## v1.3.0 (2026-07-07)

### Skills

- **coferlandia-project-skill-miner** (`meta`) — v1.0.0. Mines a project's
  documentation for current operational recipes, classifies candidate project-local
  skills by confidence and staleness, requires explicit approval before generation,
  and writes approved downstream skills only under the target repository's
  `.agents/skills/<skill-name>/` path. Integrates with
  `superpowers:writing-skills` when available before authoring each approved
  generated skill.

### Repository

- `skills/INDEX.md` — added the new `coferlandia-project-skill-miner` entry and
  updated the inventory date.
- Added a fixture-backed activation test set for the new skill, including current,
  dangerous, ambiguous, and stale documented procedures to verify proposal-vs-approval
  behavior.

## v1.2.0 (2026-07-06)

### Convention

- **Artifact output convention** — all skills now declare an `## Output Location`
  section. Generated artifacts default to `.coferlandia/` at the target project's
  root; standard repo artifacts (README.md, AGENTS.md, LICENSE, RUNBOOK.md) stay at
  the project root unless the skill explicitly overrides them. The single source of
  truth lives in `_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md`.

### Skills

- **project-documentation-archivist** (`content`) — v2.1.0. Catalog files now go to
  `.coferlandia/catalog/` and archived sources to `.coferlandia/archive/YYYY/` instead
  of `docs/catalog/` and `docs/archive/`. Standard repo artifacts (README.md, AGENTS.md,
  RUNBOOK.md) remain at the project root. HISTORY.md, TODO.md, and DECISIONS.md go to
  `.coferlandia/`.
- **coferlandia-software-dev** (`engineering`) — v2.3.0. Documentation artifacts default
  to `.coferlandia/` when no archivist structure exists in the target repo.
- **skill-repository-versioning** (`meta`) — v1.1.0. Explicit output location added
  (in-place repo management, no `.coferlandia/` needed).
- **using-coferlandia-skills** (`meta`) — v1.1.0. Explicit output location added (no
  file artifacts generated).
- **sagan-scientific-debunker** (`content`) — v1.2.0. Explicit output location added
  (conversation-only, no files).

### Protocol

- `ARTIFACT_OUTPUT_CONVENTIONS.md` — new single source of truth for output paths.
- `HOW_TO_CREATE_SKILLS.md` — references the new convention in prerequisites and Step 4.
- `SKILL_TEMPLATE.md` — includes `## Output Location` / `### Output Exceptions` sections.
- `AGENTS.md` — source-of-truth table updated.

## v1.1.0 (2026-07-01)

### Skills

- **skill-repository-versioning** (`meta`, `draft`) — pre-commit checklist for a skill
  repository: sync the skill index, decide whether a change needs only a per-skill
  version bump or a repo-wide release bump, and keep every version artifact (index,
  manifests, release notes) in sync. Written generically enough to apply to any
  repository following this same two-axis versioning convention, not just this one.

## v1.0.0 (2026-07-01)

Baseline tracked release. The plugin's version now lives in
`.claude-plugin/plugin.json` and is checked with
`_protocol/scripts/bump_version.py --check` / `--audit` (see
`_protocol/NAMING_CONVENTIONS.md` for how this differs from each skill's own
`metadata.version`). This entry documents the state that baseline reflects.

### Skills

- **coferlandia-software-dev** — control process for development tasks (developer /
  debugger roles, prior study, plan approval, code review, commit prep). Now
  integrates required `superpowers:test-driven-development`,
  `superpowers:systematic-debugging`, and `superpowers:verification-before-completion`
  when those skills are available in the environment.
- **project-documentation-archivist** — catalogs and archives project documentation.
  Dropped GitHub sync mode and merged the separate conflicts register into
  `docs/catalog/OPEN_QUESTIONS.md`.
- **sagan-scientific-debunker** — evaluates claims against scientific evidence with a
  traceable evidence map and confidence scale.
- **using-coferlandia-skills** (`draft`) — gates skill invocation: check
  `skills/INDEX.md` before responding to a task instead of skipping it. Adapted from
  `superpowers:using-superpowers`; not yet activated with a natural prompt.

### Repository

- Removed the agent-friendly-logging suite (9 skills), `build-agentic-repo`,
  `coferlandia-skill-testing`, `skill-auditor`, `skill-factory`, `sr-de-la-nata`, and
  `vault/` — reducing the repo to the 4 skills above.
- Relicensed the repo under Apache License 2.0 (added `LICENSE`; unified all skill
  frontmatter to `license: Apache-2.0`).
- Translated `README.md`, `AGENTS.md`, `skills/INDEX.md`, and all of `_protocol/` to
  English; fixed dangling references left by the deletions above (stale skill
  pointers, the `vault/Genesis_Plan.md` category-proposal instruction, and validator
  paths pointing at the deleted `coferlandia-skill-testing` runner).
- Fixed manifest drift in `.claude-plugin/plugin.json` and `marketplace.json`: the
  `skills` array was missing `./skills/content` entirely, the license field still said
  MIT, and both descriptions referenced a "14 skills" count that no longer matched
  reality. `scripts/update-plugin.ps1` now also packages `AGENTS.md` and `LICENSE`.
