# Coferlandia Skills Release Notes

## Unreleased (2026-07-29)

### Epic-based development workflow

- **coferlandia-project-manager** — adds Epic Planner as the initiative-level WHAT/WHY capability and records a normalized Execution Strategy. The PM now resolves only ambiguous workflow dimensions and supports both direct capable-agent execution and Analyst-decomposed execution, with GitHub preferred and `.agent/work-items/` as the local planning fallback.
- **software-development** — adds the first-class, analysis-only `analyst` role. Analyst owns broad system context and compiles it into Atomic + Self-contained + Low-context task contracts with explicit reuse, compatibility, dependency, consumer, and regression decisions. `coding-agent` now accepts any precise Executable Work Contract and does not require GitHub access in orchestrated mode.
- **project-orchestrator** — v2.0 replaces phase-per-worktree/amend/per-phase-merge execution with a v2 manifest, `direct-plan` and `task-execution` modes, one Epic branch/worktree, GitHub-to-filesystem materialization with freshness checks, additive task/review-fix commits, detached immutable reviews, a mandatory holistic Epic review, bidirectional Issue/commit/PR traceability, one final PR, explicit `integrate`, and post-delivery task archival.
- **CI** — exercises Project Manager workflow contracts and the Project Orchestrator v2 lifecycle on Linux and Windows in addition to existing repository validation.

No repo-wide plugin version bump is included in this implementation branch; the existing v2.0.0 plugin protocol version remains authoritative until a separate release action changes it.

## v2.0.0 (2026-07-27)

### Breaking project protocol change

- **project-documentation-archivist** — v3.0.0. GitHub Issues and GitHub Projects become the operational source of truth. `TODO.md`, `HISTORY.md`, and legacy `OPEN_QUESTIONS.md` are migration inputs only; Archivist now owns durable knowledge (`README.md`, `AGENTS.md`, `DECISIONS.md`, `RUNBOOK.md`) plus traceability metadata and ships a guarded, idempotent per-project migration workflow.
- **coferlandia-project-manager** — v0.6.0. PM becomes a GitHub-backed architecture and portfolio manager. It keeps design-oriented Superpowers, reads operational state from GitHub, and treats Obsidian as a generated projection rather than a task database.
- **software-development** — v4.4. Debugging and implementation traceability use GitHub Issues/PRs/commits in GitHub-native Coferlandia repositories instead of depending on local TODO/HISTORY files.
- **project-skill-miner** — v1.1.0. Current GitHub development evidence joins durable documentation as an authoritative mining source; legacy TODO/HISTORY files are migration evidence only.

### Migration

- Existing projects migrate repository-by-repository with Archivist preflight, inventory, reviewed decisions, idempotent GitHub Issue creation/mapping, knowledge distillation, cutover validation, and only then removal of legacy tracking files.
- This is a breaking protocol migration; mixed portfolios remain observable through an explicit legacy-migration compatibility mode until each project cuts over.

### Repository

- Bumped the repo-wide plugin version to 2.0.0 because the shared project-management/documentation protocol changes incompatibly.
- Updated `skills/INDEX.md` descriptions for the GitHub-native ownership model.

## v1.9.0 (2026-07-15)

### Skills

- **project-orchestrator** (`ops`) — v1.1. Adds real Codex/OpenCode execution,
  JSONL/session handling, provider fallbacks, schema-complete result validation,
  persisted recovery, candidate/review/fix/merge lifecycle controls, reports,
  doctor diagnostics, and fake-provider integration coverage.

### Repository

- `coferlandia-skills` — bumped the repo-wide release version for the new
  orchestration skill and its onboarding/configuration surface.

## v1.8.0 (2026-07-14)

### Skills

- **coferlandia-project-manager** (`ops`) — v0.5.1. Preserves explicit
  `projects.json` slugs across portfolio, health, archivist, and board outputs;
  reports `projects_count`; and rejects runtime commands when the managed-project
  manifest is absent instead of treating it as an empty portfolio.

### Repository

- `coferlandia-skills` — ships the `skills/ops` category in the plugin manifest,
  including `coferlandia-project-manager` at its canonical location.

## v1.7.0 (2026-07-13)

### Skills

- **coferlandia-skill-toolsmith** (`meta`) — v1.0.0. Explicit-invocation-only
  meta skill that analyzes a target skill, classifies its deterministic
  vs. semantic behavior, and consolidates the deterministic parts behind one
  unified Python CLI (`scripts/<skill-name>-cli.py`) following a stable output
  envelope, documented exit codes, and mandatory `--help` / `version` /
  `self-check` / `capabilities` commands. It then rewires the target `SKILL.md`
  to call that single public interface, preserving all semantic rules and
  decision criteria. Activation is gated to explicit requests only and enforced
  with an anti-rationalization table and red-flags list; it never self-activates
  on similarity, token inefficiency, or refactor opportunities. Ships with
  fixture-backed activation tests (`tests/test_activation.py`) and a walk-through
  target (`tests/fixtures/sample-target-skill/`).

### Repository

- `coferlandia-skills` — bumped the repo-wide release version to include the new
  meta skill and its test/fixture surface.

## v1.6.0 (2026-07-12)

### Skills

- **coferlandia-software-dev** (`engineering`) — v3.3.0. Adds distinct
  `coding-agent` and `code-reviewer` roles, repository-local isolated-worktree
  controls, reviewer reconciliation and local-integration gates, traceability
  handoffs, and fixture-backed REQUIRED TDD/systematic-debugging disciplines with
  explicit fallbacks.

### Repository

- `coferlandia-skills` — bumped the repo-wide release version for the updated
  development-control surface.

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

- `HOW_TO_CREATE_SKILLS.md` — added an explicit reference to
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
