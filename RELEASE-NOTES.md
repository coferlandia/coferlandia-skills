# Coferlandia Skills Release Notes

## Unreleased (2026-07-31)

### The Architect

- **the-architect** — v1.0.0 adds cross-project architecture memory, evidence-based preflight and assessment, reusable-component lifecycle/application history, explicit extraction contracts, concise delta-first reports, and a portable Markdown/Obsidian architecture home managed through one deterministic Python CLI.
- **Architecture Gate integration** — `coferlandia-project-manager` v0.8.0 may select the gate for material architecture work; `software-development` v4.6 consumes/blocks it before Analyst or direct execution; `project-orchestrator` v2.3 enforces it before materialization/worktree creation; `project-documentation-archivist` v3.1.0 retains in-project documentation ownership while the Architect owns cross-project evidence.
- **Validation** — cross-skill ownership and gate behavior are regression-tested alongside the Architect CLI and the full Project Orchestrator suite on Linux and Windows.

### Durable orchestrator claims

- **project-orchestrator** — v2.3 adds repository-wide atomic Epic/task claims under the Git common directory, preventing different runs and worktrees from executing the same work item concurrently.
- **GitHub Project lifecycle** — configured Epic/task items move to `In Progress` before coding begins, remain there through review and merge approval, and move to `Done` only after verified delivery to `main`.
- **Recovery and administration** — claims survive provider waits, blocked states, retries, resumes, and process termination; cancellation and audited `claims release` operations provide explicit release paths without timeout-based claim stealing.
- **Validation** — concurrency, duplicate-run exclusion, path-independent local identities, early Project failure cleanup, cancellation release, and Project projection behavior are covered on Linux and Windows.

### Epic-based development workflow

- **coferlandia-project-manager** — v0.7 adds Epic Planner as the initiative-level WHAT/WHY capability, records a normalized Execution Strategy, and emits exactly one complete planning representation for one-time orchestrator initialization. The PM now resolves only ambiguous workflow dimensions and supports both direct capable-agent execution and Analyst-decomposed execution, with GitHub preferred and `.agent/work-items/` as the local planning fallback.
- **software-development** — v4.5 adds the first-class, analysis-only `analyst` role and formalizes single-store output plus the canonical marked GitHub analysis contract. Analyst owns broad system context and compiles it into Atomic + Self-contained + Low-context task contracts with explicit reuse, compatibility, dependency, consumer, and regression decisions. `coding-agent` now accepts any precise Executable Work Contract and does not require GitHub access in orchestrated mode.
- **project-orchestrator** — v2.1 keeps the Epic/task v2 lifecycle and replaces ongoing contract freshness refreshes with one-time bidirectional Initial Contract Materialization. GitHub-only plans become frozen local Epic/analysis/task snapshots; complete local GitHub-tracked plans are published with stable retry-safe markers before execution. Operational Issue/Project/commit/PR traceability remains active.
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
- `VERSIONING.md` — added per-skill and repo-wide versioning examples, dirty-worktree note, release commit checklist.
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
