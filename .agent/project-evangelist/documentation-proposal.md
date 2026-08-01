# Developer Documentation Proposal

## Project Understanding

- **Purpose:** distribute evidence-based operational contracts that turn general-purpose AI agents into bounded, specialized collaborators for real software-project work.
- **Primary users:** software engineers, technical leads, repository maintainers, and agent operators who need repeatable planning, architecture, implementation, review, documentation, orchestration, and evidence workflows.
- **Implemented capabilities:** skill discovery and activation; skill authoring and mechanization; project knowledge preservation; architecture governance; project planning; development-role execution; Git/worktree orchestration; scientific claim evaluation; plugin/global installation; mechanical validation and regression testing.
- **Current scope and maturity:** active public Agent Skills repository with 10 active distributed skills, repository/plugin version `2.1.0`, current CI on Ubuntu and Windows with Python 3.11 and 3.13, and an evolving GitHub-native delivery protocol.
- **Confirmed limitations:** it is a portable skill library rather than a hosted development platform; `data` and `design` categories are currently empty; release/package maintenance is being redesigned in Issue #21; no documentation publishing platform is configured.

## Developer Audiences

| Reader goal | Required understanding | Current coverage |
|---|---|---|
| New to the project | Purpose, what a skill is in this repository, skill families, runtime shape, where truth lives | Partially covered across `README.md`, `SKILLS-GUIDE.md`, and `AGENTS.md`, but no unified developer path |
| Run locally | Python baseline, validation commands, focused/full tests, installer/package boundaries | Fragmented across `README.md`, `AGENTS.md`, CI, script help, and skill-local docs |
| Implement or evolve a skill | Module structure, protocol owners, tests, index/version implications, common impact areas | Strong canonical rules exist, but the navigation path is implicit |
| Investigate a bug | How semantic instructions, deterministic tooling, tests, manifests, and CI relate | No project-level architecture or repository map |
| Contribute safely | Ownership boundaries, change workflow, validation, release handoff, non-duplication rules | Covered in sources, but not assembled into a progressive contributor experience |
| Evaluate the library | Product scope, implemented families, architecture, maturity, limitations | Strong overview exists; deeper technical orientation requires manual exploration |

## Reading Paths

```text
New to the project
→ docs/index.md
→ SKILLS-GUIDE.md
→ docs/architecture.md
→ docs/repository-map.md
```

```text
Evaluating or installing the library
→ docs/index.md
→ README.md
→ SKILLS-GUIDE.md
→ skills/INDEX.md
```

```text
Implementing or changing a skill
→ docs/index.md
→ docs/repository-map.md
→ docs/guides/change-a-skill.md
→ relevant SKILL.md and tests
→ docs/development.md
```

```text
Investigating a regression
→ docs/architecture.md
→ docs/repository-map.md
→ relevant skill module and tests
→ docs/development.md
→ GitHub Issue/PR evidence when required
```

```text
Maintaining repository protocol or tooling
→ docs/architecture.md
→ docs/repository-map.md
→ _protocol/ owning document
→ docs/development.md
```

```text
Preparing a release after Issue #21
→ docs/development.md
→ future docs/guides/release-and-package.md
→ canonical release-maintenance protocol
```

## Existing Documentation Assessment

| Path | Current role | Quality/currentness | Decision |
|---|---|---|---|
| `README.md` | Human-facing value, philosophy, families, install, compact map | High-value and current at the conceptual level; owner URLs are currently contradictory | preserve and link; Archivist/release-maintainer handoff for owner-specific corrections |
| `SKILLS-GUIDE.md` | Human selection, boundaries, composition | Strong and recently updated | preserve and link |
| `AGENTS.md` | Agent entrypoint and source-of-truth map | Strong canonical maintenance entrypoint | preserve and link |
| `skills/INDEX.md` | Single inventory/status catalog | Strong and current | preserve and link; never mirror |
| `RELEASE-NOTES.md` | Repository release history | Canonical but currently contains volatile `Unreleased` state | preserve and link only where needed |
| `_protocol/HOW_TO_CREATE_SKILLS.md` | Skill creation procedure | Strong canonical procedure | preserve and link from change-path guide |
| `_protocol/QUALITY_STANDARDS.md` | Quality and security checklist | Strong canonical checklist | preserve and link |
| `_protocol/NAMING_CONVENTIONS.md` | Naming/category/version distinctions | Canonical owner | preserve and link |
| `_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md` | Artifact path ownership | Canonical owner | preserve and link |
| `skills/*/*/SKILL.md` | Per-skill operational contract | Canonical per skill | preserve; developer docs explain how modules fit together, not their full behavior |
| `.github/workflows/ci.yml` | Executable CI contract | Current implementation evidence | reference from development docs |
| `docs/**` | Progressive developer documentation | absent | create after approval |

## Proposed Documentation Structure

```text
docs/
├── index.md
├── architecture.md
├── repository-map.md
├── development.md
└── guides/
    └── change-a-skill.md
```

After GitHub Issue #21 is merged and the release contract stabilizes, consider adding:

```text
docs/guides/release-and-package.md
```

Do not create that release guide in the first approved pass unless Issue #21 has already landed and the final implementation can be verified.

## Document Decisions

### Create

- `docs/index.md` — developer entrypoint with project purpose, confirmed scope, Technology at a Glance, Architecture at a Glance, limitations, and goal-oriented reading paths.
- `docs/architecture.md` — explain the repository's architecture as five collaborating layers: entrypoints/catalog, distributed skill modules, shared protocol, deterministic tooling/tests, and distribution/release surfaces.
- `docs/repository-map.md` — semantic map of top-level areas and skill-module anatomy, including where to look for instructions, deeper references, CLIs, templates, activation cases, and regression tests.
- `docs/development.md` — verified prerequisites and commands; focused vs. full validation; CI matrix; safe debugging approach; command provenance; current constraints around packaging and releases.
- `docs/guides/change-a-skill.md` — repository-specific common change path that links to the canonical protocol and explains impact discovery across `SKILL.md`, `references/`, scripts, assets, tests, index, version metadata, release surfaces, and cross-skill contracts.

### Update

- None before approval.
- In the approved authoring pass, only the new `docs/**` files are in scope by default.

### Preserve

- `README.md` — remains the universal public entrypoint and value proposition.
- `SKILLS-GUIDE.md` — remains the human-oriented skill selection and composition guide.
- `AGENTS.md` — remains the agent maintenance entrypoint.
- `skills/INDEX.md` — remains the only skill inventory/status catalog.
- `RELEASE-NOTES.md` — remains repository release history.
- `_protocol/**` — remains the canonical repository-wide rule set.
- Every existing skill module — no skill behavior changes are part of this documentation pass.

### Link Instead of Duplicate

- `README.md` from `docs/index.md` — universal overview and installation remain README-owned.
- `SKILLS-GUIDE.md` from `docs/index.md` — selection and composition remain guide-owned.
- `AGENTS.md` from `docs/index.md`, `docs/development.md`, and `docs/guides/change-a-skill.md` — safe agent orientation remains canonical there.
- `skills/INDEX.md` from `docs/index.md` and `docs/repository-map.md` — inventory/status/category data must not be mirrored.
- `_protocol/HOW_TO_CREATE_SKILLS.md`, `QUALITY_STANDARDS.md`, `NAMING_CONVENTIONS.md`, and `ARTIFACT_OUTPUT_CONVENTIONS.md` from `docs/guides/change-a-skill.md` — the guide provides navigation and impact context, not copied rules.
- `RELEASE-NOTES.md` and the future canonical release-maintenance protocol from release-related documentation — history and release policy keep their own owners.
- Skill-local `references/**` from architecture/repository-map examples — deep domain behavior stays local to the owning skill.

### Potentially Obsolete

- None identified.
- No existing document should be deleted, moved, or superseded in this pass.

## Planned Page Content

### `docs/index.md`

1. What Coferlandia Skills does.
2. Current scope and confirmed limitations.
3. Technology at a Glance.
4. Architecture at a Glance.
5. Main capabilities by responsibility, linking to `SKILLS-GUIDE.md` and `skills/INDEX.md`.
6. Start Here paths for evaluation, contribution, skill change, debugging, and protocol/tooling work.
7. Project map links.
8. Canonical source boundaries.

### `docs/architecture.md`

1. Design principle: semantic judgment in skills, mechanical control in deterministic tooling.
2. Entry and discovery layer.
3. Skill module layer.
4. Shared protocol layer.
5. Tooling, tests, and CI layer.
6. Distribution and installation layer.
7. Ownership and dependency direction.
8. Main flows: discovery, skill evolution, validation, installation.
9. Boundaries: GitHub work state, durable repository docs, cross-project architecture memory, and release volatility.

### `docs/repository-map.md`

1. Top-level semantic map.
2. Anatomy of a skill directory.
3. How categories are used.
4. Where repository-wide rules live.
5. Where deterministic tooling lives.
6. Where test evidence lives.
7. Where plugin/distribution metadata lives.
8. Sensitive/high-impact zones: protocol, shared development/orchestrator contracts, manifests, CI, release surfaces.

### `docs/development.md`

1. Prerequisites: Git, Python 3.11+, repository access; `jsonschema` only where required by the current CI suites.
2. Working directory and branch/worktree expectations, linked to agent/development contracts where applicable.
3. Focused test strategy.
4. Full repository validation commands traced to CI.
5. Skill validator behavior and outputs.
6. Version drift/audit commands.
7. Global installer dry-run and execution.
8. Packaging caveat: current PowerShell implementation is confirmed but under active replacement in Issue #21.
9. Failure diagnosis path: focused test → full skill validation → version checks → CI parity.

### `docs/guides/change-a-skill.md`

1. Identify the owning skill and affected responsibility.
2. Read current `SKILL.md`, conditional references, scripts, assets, and tests.
3. Classify semantic vs. deterministic change.
4. Identify cross-skill contracts and consumers.
5. Update the smallest owning surfaces.
6. Add or update activation/contract/CLI/regression evidence.
7. Run focused and repository-wide validation.
8. Reconcile index/version/release surfaces through the current canonical process.
9. Stop before release-specific instructions that are not yet stabilized.

## Evidence

| Finding | State | Evidence |
|---|---|---|
| The project is an Agent Skills repository with local conventions beyond the external specification. | confirmed | `AGENTS.md`, `_protocol/HOW_TO_CREATE_SKILLS.md` |
| `README.md`, `SKILLS-GUIDE.md`, `AGENTS.md`, and `skills/INDEX.md` already have distinct ownership roles. | confirmed | Those files and their explicit source-of-truth statements |
| The repository combines Markdown contracts with Python deterministic tooling and tests. | confirmed | `skills/**`, `_protocol/scripts/**`, skill-local scripts/tests |
| CI runs on Ubuntu/Windows and Python 3.11/3.13. | confirmed | `.github/workflows/ci.yml` |
| The repository is distributed as plugin metadata and flattened global skills. | confirmed | `.claude-plugin/**`, `README.md`, `_protocol/scripts/install_global_skills.py` |
| No progressive developer entrypoint exists under `docs/**`. | confirmed | `docs/index.md` absent; code search found no repository developer-doc tree |
| The release/package system is not stable enough for a durable guide yet. | confirmed | Current script/manifests/release notes plus open Issue #21 |
| All proposed commands can be executed successfully in a local checkout. | unconfirmed | Commands are authoritative from CI/scripts, but this study had no local checkout execution capability |

## Contradictions and Unknowns

### Current repository owner versus documented owner

- Current repository: `coferlandia/coferlandia-skills`.
- Some installation examples and plugin metadata: `diegocofre/coferlandia-skills`.
- Impact: owner-specific installation instructions are not safe to duplicate in new docs.
- Resolution: link to canonical surfaces for now; Issue #21 should reconcile them.

### Release version and `Unreleased` presentation

- Plugin manifest is `2.1.0`.
- `RELEASE-NOTES.md` still groups the newest work under `Unreleased` while describing the plugin bump.
- Impact: avoid a stable release guide in the first pass.
- Resolution: defer until Issue #21 completes its release model migration.

### Command execution evidence

- CI and script sources provide authoritative commands.
- The current execution environment could not create a local checkout, so commands were not rerun.
- Impact: authoring may describe them as repository-defined commands, but final validation should execute them from a checkout before claiming the docs fully verified.

## Archivist Handoffs

```text
Archivist handoff
- Target: README.md
- Current statement: installation commands reference diegocofre/coferlandia-skills
- Conflicting evidence: current repository is coferlandia/coferlandia-skills; Issue #21 tracks stale owner URLs
- Required durable correction: reconcile installation/repository owner references through the approved release-maintenance migration
- Developer-doc impact: new docs will link to README but will not duplicate owner-specific commands until corrected
```

```text
Archivist handoff
- Target: README.md
- Current statement: compact repository structure lists only skills/, _protocol/, and AGENTS.md
- Conflicting evidence: current developer-relevant architecture also includes .claude-plugin/, .github/workflows/, scripts/, tests inside skill modules, SKILLS-GUIDE.md, and RELEASE-NOTES.md
- Required durable correction: after docs/** is approved, add only a concise link to the developer documentation entrypoint or refresh the compact map without duplicating the new repository map
- Developer-doc impact: discoverability of docs/index.md would otherwise depend only on direct repository navigation
```

No `DECISIONS.md` or `RUNBOOK.md` correction is required by the proposed first pass.

## Scope and Non-Goals

- **Included:** developer orientation, verified technology summary, repository architecture, semantic codebase map, development/validation commands, and one common change path for skills.
- **Excluded:** changes to skill behavior; new CLIs; changes to protocol rules; release-maintenance implementation; plugin/package changes; Issue/Project state duplication; release history duplication; architecture decision records; operational runbooks; hosted documentation infrastructure.
- **Language:** English, matching the repository's public entrypoints and protocol documentation.
- **Publishing/platform changes:** none for project-evangelist V1.

## Approval

- **Control authority:** Diego Cofré or delegated agentic supervisor.
- **Status:** proposed
- **Date:** 2026-08-01
- **Approved scope or requested changes:** pending.

## Approval Options

The recommended approval is:

```text
Approve the first-pass docs/** structure and content described above.
Keep README.md and AGENTS.md unchanged during Evangelist authoring.
Defer docs/guides/release-and-package.md until Issue #21 is merged.
After authoring, run link/Markdown checks and all repository-defined validation commands from a local checkout.
```
