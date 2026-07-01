# Coferlandia Skills Release Notes

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
