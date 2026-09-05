# Coferlandia Skills Release Notes

## Unreleased

## v2.5.0 (2026-09-05)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-release-publisher | new | 1.0 | Adds a generic Commit-to-Release standard with SemVer planning, exact annotated-tag identity, GitHub Release publication, idempotent recovery, and machine-readable verification/resolution independent of deployment. |

### Repository and protocol

- Adds a reusable product-release boundary after development/integration: an exact existing commit becomes a formal release without requiring a synthetic declaration commit.
- Separates semantic release decisions from deterministic Git/GitHub mechanics, including historical targets, release-line ancestry, prereleases, explicit policy checks, and fail-closed inconsistency handling.
- Preserves repository-local precedence only when a stronger local contract explicitly owns final Commit-to-published-Release; preparation-only release/versioning gates may compose before the generic publisher.
- Adds Linux/Windows CI coverage for activation, SemVer/policy contracts, real temporary Git histories, GitHub adapter behavior, release planning, and consistency states.

### Plugin and packaging

- Bumps the installable plugin from v2.4.0 to v2.5.0 for the additive `coferlandia-release-publisher` public skill.
- Refreshes plugin discovery metadata and the human skill guide to include deterministic release publication and machine-readable release resolution.
- Keeps transient release plans/provenance under `.agent/` and therefore excluded from plugin packaging; optional provenance becomes a GitHub Release asset rather than a required file in the target commit.

### Migration or compatibility

- Existing consumers may update normally; this is an additive compatible release.
- The generic publisher does not auto-migrate repositories whose published GitHub Release history uses another version scheme; those repositories require an explicit stronger local publication contract or policy decision.
- Deployment, production rollback, host selection, Docker/service operations, and deployed-version state remain outside the release publisher contract.

## v2.4.0 (2026-09-03)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| project-orchestrator | 2.3 | 2.4 | Adds fail-closed exact-candidate GitHub CI gates, durable integration-check states, remote base validation, merge-group awareness, double revalidation, and head-conditional squash merge protection. |

### Repository and protocol

- Adds deterministic exact-candidate integration-gate policy and regression coverage for project-orchestrator.

### Plugin and packaging

- Bumps the installable plugin for the additive project-orchestrator integration-safety behavior.

### Migration or compatibility

- Existing repositories remain compatible when integration.github is absent or required_gates is empty. Repositories that need controller-enforced CI may configure workflow or check-run gates explicitly.

## v2.3.0 (2026-08-03)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| coferlandia-config-toolsmith | new | 1.0.0 | Adds an explicit agentic-plus-deterministic process that discovers a project's existing configuration, builds a static contract and standardized native-or-fallback CLI, records ambiguous candidates, generates agent documentation, and preserves the project's native stores as the only runtime source of truth. |
| coferlandia-config-devops | new | 1.0.0 | Adds Config Operator Execute Mode and control-tower Guide Mode for converting natural-language configuration intent into exact prepare/apply/activate/rollback operations through the Toolsmith-generated interface. |

### Repository and protocol

- Added configuration operations as a first-class skill family while preserving the boundary between repository preparation and day-to-day operation.
- Added permanent Linux and Windows CI coverage for both new skill suites, contract validation, candidate lifecycle behavior, generated Python facades, Guide Mode, and activation boundaries.
- Updated the canonical skill index and human guide with the ownership, composition, and explicit-invocation rules for the new skills.
- Kept deterministic retrieval non-authoritative: agents must consult the complete generated handbook before concluding that a requested configuration outcome is unsupported.

### Plugin and packaging

- Bumped the installable plugin from v2.2.0 to v2.3.0 for the two additive public skills.
- Refreshed plugin and marketplace descriptions and keywords to include agent-operable configuration and DevOps workflows.
- Updated the README managed release block and verified that packaging excludes repository-local and transient artifacts.

### Migration or compatibility

- Existing consumers may update normally; this is an additive compatible release.
- `coferlandia-config-toolsmith` never migrates or replaces a project's configuration architecture implicitly. Generated contracts contain capabilities and bindings, not current or effective values.
- Projects must run Config Toolsmith explicitly before Config DevOps can operate them; Config DevOps consumes the generated contract and CLI and does not invent missing adapters or fields.

## v2.2.0 (2026-08-01)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
| project-evangelist | new | 1.0 | Adds progressive, evidence-based developer documentation with verified technology and architecture summaries, reading paths, repository maps, and contributor guidance. |
| the-architect | new | 1.0.0 | Adds cross-project architecture memory, Architecture Gates, evidence-based assessments, reusable-component governance, and a deterministic Markdown/Obsidian CLI. |
| coferlandia-project-manager | 0.6.0 | 0.8.0 | Adds Epic Planner execution strategies and Architecture Gate selection before material development work. |
| software-development | 4.4 | 4.6 | Adds the broad-context Analyst role, executable low-context task contracts, and Architecture Gate enforcement before decomposition or implementation. |
| project-orchestrator | 1.1 | 2.3 | Adds Epic/task execution, one-time contract materialization, immutable review lifecycles, final integration traceability, and durable concurrent work-item claims. |
| project-documentation-archivist | 3.0.0 | 3.1.0 | Clarifies in-project durable-knowledge ownership while the Architect owns cross-project architecture and component evidence. |
| skill-repository-versioning | 1.1.0 | 1.2.0 | Defers to stronger repository-local release-maintenance workflows instead of running a competing generic protocol. |

### Repository and protocol

- Added the repository-local `coferlandia-release-maintainer` final-delivery gate under `.agents/skills/` without shipping it as a public plugin skill.
- Added one canonical release-maintenance policy and per-skill `CHANGELOG.md` ownership for every public skill.
- Updated skill authoring templates, quality standards, and validation so new and modified public skills keep `metadata.version`, changelog history, release notes, and repository release metadata coherent.
- Added deterministic release inspection, preparation, validation, README rendering, and package verification through one Python CLI.
- Preserved `skills/INDEX.md` as the inventory source of truth rather than duplicating release history there.

### Plugin and packaging

- Bumped the installable plugin from v2.1.0 to v2.2.0 for the accumulated shipped skill and protocol changes.
- Corrected plugin repository/homepage metadata to `coferlandia/coferlandia-skills` and refreshed marketplace descriptions.
- Replaced pull-before-package behavior with deterministic packaging of the already-reviewed branch state.
- The package now includes `RELEASE-NOTES.md` and `SKILLS-GUIDE.md`, excludes repository-local `.agents/**` and `.agent/**`, reopens the archive for verification, and reports a SHA-256 digest.
- CI now enforces changelog/version consistency, the release-ready gate, README projection freshness, and verified plugin packaging on Linux and Windows.

### Migration or compatibility

- Existing consumers should reinstall or update the plugin to receive the accumulated v2.2.0 skill set.
- Repository contributors must run the local release-maintenance gate before final commit, pull-request readiness, or integration when a shipped surface changed; intermediate implementation commits remain allowed.
- The public `skill-repository-versioning` skill remains reusable in other repositories and delegates when a repository provides a stronger local release workflow.

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

## v1.1.0 (2026-07-05)

### Skills

- **coferlandia-software-dev** (`engineering`) — v2.2.0. Adds optional supervisory-agent role to Step 2, with explicit mode selection at task start, mandatory execution context package, structured checkpoint contract, role & authority boundary, and audit trail. No changes to Steps 1, 3, 4, or 5.
- **coferlandia-software-dev** (`engineering`) — v2.1.0. Adds commit proposal + explicit approval as Step 5.5, test-results-report requirement before proposing a commit, push never automatic, and optional integration with `project-documentation-archivist` for documentation updates (HISTORY.md, TODO.md, DECISIONS.md, RUNBOOK.md, AGENTS.md).
- **coferlandia-software-dev** (`engineering`) — v2.0.0. Complete redesign into a multi-role engineering workflow with Developer, Debugger, Code Reviewer, and Commit Prep modes. Adds strict mode detection, control-authority abstraction, code review protocol, and commit preparation gates. Replaces v1.x workflow entirely.
- **coferlandia-software-dev** (`engineering`) — v1.0.0. Initial development process skill: mandatory study → plan → implement → review → test/docs/commit workflow.
- **using-coferlandia-skills** (`meta`) — v1.0.0. First meta-skill: checks `skills/INDEX.md` and invokes matching skills before responding to any task.
- **skill-repository-versioning** (`meta`) — v1.0.0. Pre-commit checklist: update index, classify change, bump per-skill and repo-wide versions correctly.
- **project-documentation-archivist** (`content`) — v2.0.0. Evidence-first project knowledge base with managed blocks, deterministic source indexing, open questions, module manifests, and incremental processing.
- **sagan-scientific-debunker** (`content`) — v1.1.0. Adds systematic structured claim analysis and stronger source hierarchy.

### Protocol

- `HOW_TO_CREATE_SKILLS.md` — added a decision tree for per-skill vs. repo-wide version bumps; linked `superpowers:writing-skills` in Step 3; added "adding a skill" checklist.
- `VERSIONING.md` — added per-skill vs. repo-wide versioning examples, dirty-worktree note, release commit checklist.
- `CHANGELOG.md` — added historical entry guidance, documented the initial repo-wide release history as v1.0.0, added same-change-line multiple skill version bump guidance.
- `SKILL_TEMPLATE.md` — added `{category}` and `{status}` placeholders to metadata; added error-handling and gotchas guidance; clarified external tools in references section.

### Repository

- GitHub Actions CI validates all skills and checks version drift on push/PR (including Windows and Linux runners).
- The repository tracks its version through `.version-bump.json`.
- Added `RELEASE-NOTES.md` to keep detailed release history out of `README.md`.

## v1.0.0 (2026-07-04)

- Established the reusable Coferlandia skill repository protocol.
- Added Apache-2.0 licensing and repository-level author/license/version policy.
- Added `_protocol/` templates and `validate_skill.py` tooling.
- Added first four canonical skills under `skills/`.
