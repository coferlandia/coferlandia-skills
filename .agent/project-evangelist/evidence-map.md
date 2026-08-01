# Project Evangelist Evidence Map

## Preflight

- **Repository:** `coferlandia/coferlandia-skills`
- **Default branch:** `main`
- **Studied revision:** `cd2d115559bd6e5b6c2aabff39bc676c7687c68e`
- **Study mode:** authenticated GitHub repository inspection through the GitHub connector.
- **Local worktree:** none available in this execution environment. Dirty-state inspection is therefore not applicable; no existing working tree was modified.
- **Proposal branch:** `docs/project-evangelist-proposal-2026-08-01`
- **Documentation changes during preflight:** none under `docs/**`.

## Existing Documentation Entrypoints

| Path | Role | Evidence state | Notes |
|---|---|---|---|
| `README.md` | Human-facing project overview, value proposition, skill families, install instructions, and compact repository map | confirmed | Strong high-level entrypoint; intentionally compact and Archivist-owned. |
| `SKILLS-GUIDE.md` | Human-oriented skill selection, ownership boundaries, and common compositions | confirmed | Good catalog narrative without duplicating full skill contracts. |
| `AGENTS.md` | Agent maintenance entrypoint, source-of-truth map, skill creation and release pointers | confirmed | Canonical agent orientation; Archivist-owned. |
| `skills/INDEX.md` | Canonical inventory of skills, categories, status, and location | confirmed | Current index contains 10 active distributed skills across meta, engineering, content, and ops. |
| `RELEASE-NOTES.md` | Repository/plugin release history and current unreleased changes | confirmed | Contains current `Unreleased` material and historical releases. |
| `_protocol/*.md` | Repository-wide authoring, naming, quality, lifecycle, output, and versioning rules | confirmed | Protocol rules are deliberately separated by ownership. |
| `skills/*/*/SKILL.md` | Complete operational contract for each skill | confirmed | Most skills also contain some combination of `references/`, `scripts/`, `assets/`, and `tests/`. |
| `docs/index.md` | Proposed developer documentation entrypoint | absent | No developer-oriented progressive documentation entrypoint currently exists. |

## Archivist Boundary Detection

- `README.md`: present.
- `AGENTS.md`: present.
- `DECISIONS.md`: absent at the studied revision.
- `RUNBOOK.md`: absent at the studied revision.
- `.agent/catalog/**`: no repository-owned catalog was found during code search.
- `docs/**`: no current developer-documentation tree was found.

Evangelist changes must therefore stay under `.agent/project-evangelist/**` until approval and under `docs/**` after approval. `README.md` and `AGENTS.md` remain link targets rather than rewrite targets.

## Product Model

| Finding | State | Evidence |
|---|---|---|
| The repository distributes operational contracts that specialize AI agents for real software-project work. | confirmed | `README.md`, `AGENTS.md`, `SKILLS-GUIDE.md`. |
| The public library covers skill-system maintenance, project knowledge and architecture, software delivery, and evidence/critical reasoning. | confirmed | `README.md`, `SKILLS-GUIDE.md`, `skills/INDEX.md`. |
| The repository targets both human maintainers and agent runtimes. | confirmed | Human-facing `README.md`/`SKILLS-GUIDE.md`; agent-facing `AGENTS.md`; plugin/global installation surfaces. |
| The library is active and versioned as an installable plugin. | confirmed | `.claude-plugin/plugin.json` version `2.1.0`, current release notes, recent merged commits. |
| Data and design categories currently contain no distributed skills. | confirmed | `skills/INDEX.md`. |

## Technology Model

| Responsibility | Verified technology or format | State | Evidence |
|---|---|---|---|
| Skill contracts | Markdown with YAML frontmatter following the Agent Skills specification | confirmed | `AGENTS.md`, `_protocol/HOW_TO_CREATE_SKILLS.md`, representative `SKILL.md` files. |
| Deterministic tooling | Python 3.11+ scripts and CLIs, primarily standard-library based | confirmed | `_protocol/scripts/validate_skill.py`, `_protocol/scripts/install_global_skills.py`, skill-local CLIs. |
| Automated tests | Python `unittest`, fixture-backed contract and activation tests | confirmed | `.github/workflows/ci.yml`, `skills/**/tests/test_*.py`. |
| Repository metadata | JSON plugin, marketplace, and version-bump manifests | confirmed | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.version-bump.json`. |
| Packaging compatibility | PowerShell packaging script | confirmed | `scripts/update-plugin.ps1`. |
| CI | GitHub Actions on Ubuntu and Windows with Python 3.11 and 3.13 | confirmed | `.github/workflows/ci.yml`. |
| Distribution | Claude/Copilot marketplace metadata plus flattened global-skill installation | confirmed | `README.md`, `.claude-plugin/**`, `_protocol/scripts/install_global_skills.py`. |
| Documentation publishing platform | none configured | confirmed | No MkDocs, Docusaurus, VitePress, Sphinx, or Pages configuration found. |

## Architecture Model

### 1. Human and agent entrypoints

- `README.md` explains value, scope, families, installation, and the documentation map.
- `SKILLS-GUIDE.md` helps humans choose and compose skills.
- `AGENTS.md` routes agents to the catalog and repository protocol.
- `skills/INDEX.md` is the only inventory/status catalog.

### 2. Distributed skill modules

Each skill lives under `skills/<category>/<skill-name>/` and is centered on `SKILL.md`. Optional adjacent surfaces provide:

- `references/` for deeper conditional guidance;
- `scripts/` for deterministic mechanics;
- `assets/` for templates and static resources;
- `tests/` for activation, contract, CLI, and regression evidence.

### 3. Shared repository protocol

`_protocol/` owns repository-wide creation, naming, quality, lifecycle, artifact-location, validation, installation, and versioning conventions. Skill documents link to these owners instead of reproducing them.

### 4. Distribution and release surfaces

`.claude-plugin/`, `.version-bump.json`, `RELEASE-NOTES.md`, `scripts/update-plugin.ps1`, and install instructions expose the repository as a consumable plugin/library.

### 5. Validation and delivery

GitHub Actions executes selected integration suites, validates every skill, checks repository-version drift, and audits version declarations on pull requests and pushes to `main`.

## Main Flows

### Discover and use a skill

```text
Project task
→ agent entrypoint or nearest skill catalog
→ `using-project-skills`
→ `skills/INDEX.md`
→ selected skill's `SKILL.md`
→ optional references/scripts/assets
→ expected output and validation
```

### Create or evolve a distributed skill

```text
Repository agent entrypoint
→ `_protocol/HOW_TO_CREATE_SKILLS.md`
→ naming/template/quality/output conventions
→ skill module implementation
→ activation/contract/CLI tests as applicable
→ `validate_skill.py`
→ `skills/INDEX.md`
→ version/release maintenance
```

### Validate repository changes

```text
Changed skill or protocol surface
→ focused skill tests
→ selected cross-skill tests
→ validate all skills
→ repository version drift check
→ version declaration audit
→ CI matrix on Windows and Ubuntu
```

### Package and install

```text
Repository/plugin metadata
→ package construction
→ marketplace or file installation
or
→ global installer flattens category/skill directories into runtime skill directories
```

The current packaging/release flow is under active redesign in GitHub Issue #21 and must not be documented as stable future architecture until that work is merged.

## Development Commands Traced to Authoritative Sources

| Command | Source | Verification status |
|---|---|---|
| `python _protocol/scripts/validate_skill.py --all skills` | `.github/workflows/ci.yml`, validator help | authoritative; not executed in this remote-only study |
| `python _protocol/scripts/bump_version.py --check` | `.github/workflows/ci.yml`, `AGENTS.md` | authoritative; not executed in this remote-only study |
| `python _protocol/scripts/bump_version.py --audit` | `.github/workflows/ci.yml`, `AGENTS.md` | authoritative; not executed in this remote-only study |
| `python -m unittest discover -s skills/engineering/the-architect/tests -p "test_*.py"` | `.github/workflows/ci.yml` | authoritative; not executed in this remote-only study |
| `python -m unittest discover -s skills/ops/project-orchestrator/tests -p "test_*.py"` | `.github/workflows/ci.yml` | authoritative; not executed in this remote-only study |
| `python _protocol/scripts/install_global_skills.py` | `README.md`, installer implementation | authoritative; not executed in this remote-only study |
| `.\scripts\update-plugin.ps1` | packaging script header and README-adjacent release surface | confirmed current command; unstable because Issue #21 plans replacement/delegation |

## Contradictions and Volatile Areas

### Repository ownership URLs

- The authenticated current repository is `coferlandia/coferlandia-skills`.
- `README.md` installation examples and `.claude-plugin/plugin.json` still reference `diegocofre/coferlandia-skills`.
- GitHub Issue #21 explicitly identifies stale organization/repository URLs as a migration target.

Classification: **contradictory but already tracked**. Developer docs should use repository-relative links and avoid duplicating owner-specific installation text until the canonical surfaces are corrected.

### Release state

- `.claude-plugin/plugin.json` reports version `2.1.0`.
- `RELEASE-NOTES.md` contains a dated `Unreleased` section that says the plugin surface was bumped to `2.1.0`.
- GitHub Issue #21 defines a new release-maintenance gate, per-skill changelogs, README managed release summary, and cross-platform packaging.

Classification: **confirmed current state, intentionally volatile**. Defer a stable release-maintenance guide until Issue #21 is merged.

### Documentation ownership

- `README.md` and `AGENTS.md` already provide strong canonical summaries.
- A new `docs/**` tree must orient developers without becoming a duplicate inventory, protocol, release history, or durable-memory system.

Classification: **confirmed design constraint**.

## GitHub Evidence

- Latest studied commit: `cd2d115559bd6e5b6c2aabff39bc676c7687c68e` — adds `project-evangelist`.
- Previous commit: `2573aaa1ea94d890c45a1a71cfe64e1857325d05` — adds skill philosophy and selection documentation.
- Open Issue #21 — repository release-maintenance gate and package/documentation synchronization.
- No open pull requests were found at study time.

## Exclusions

The study intentionally ignored:

- generated packages and caches;
- test fixtures as evidence of repository runtime behavior, except where they prove testing conventions;
- obsolete plans as present-state architecture;
- Issue #21 requested future behavior as though it were already implemented;
- external Agent Skills specification details not restated by this repository.
