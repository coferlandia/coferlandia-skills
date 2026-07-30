# Skills Index — coferlandia-skills

> **Single source of truth for the skill inventory.** This is the only file that lists
> which skills exist and their status. Update only this file when adding, removing, or
> changing a skill — there are no mirror catalogs to sync by hand.
>
> **Row format (defined here, not repeated elsewhere):**
> `| [skill-name](./{category}/{skill-name}/) | One-line description | {status} |`
> where `status` is `draft | active | deprecated`. The link path is relative to this
> file (which lives inside `skills/`), so it starts with `./{category}/`.

---

## Meta

Skills about skills and about the repository itself: creating, auditing, structuring.

| Skill | Description | Status |
|-------|-------------|--------|
| [using-project-skills](./meta/using-project-skills/) | Check skills/INDEX.md and invoke a matching skill before responding to any task, instead of skipping the check | active |
| [skill-repository-versioning](./meta/skill-repository-versioning/) | Pre-commit checklist for a skill repository: sync the skill index, bump per-skill vs. repo-wide release versions correctly | active |
| [project-skill-miner](./meta/project-skill-miner/) | Extract current operational recipes from durable project knowledge plus GitHub development evidence and convert approved ones into project-local agent skills | active |
| [coferlandia-skill-toolsmith](./meta/coferlandia-skill-toolsmith/) | Explicit-invocation-only skill that analyzes a target skill, consolidates its deterministic behavior behind one unified Python CLI (scripts/<name>-cli.py), and rewires the skill to use it | active |

## Engineering

Code, infrastructure, architecture, debugging.

| Skill | Description | Status |
|-------|-------------|--------|
| [software-development](./engineering/software-development/) | Routes broad-context Analyst decomposition, developer/debugger work, executable coding-agent contracts, and independent review while keeping Git authority separate from semantic workers | active |

## Data

Data analysis, pipelines, queries, reports.

| Skill | Description | Status |
|-------|-------------|--------|
| *(none yet)* | | |

## Content

Writing, documentation, communication, release notes.

| Skill | Description | Status |
|-------|-------------|--------|
| [project-documentation-archivist](./content/project-documentation-archivist/) | Distill durable project knowledge and migrate legacy TODO/HISTORY work tracking into GitHub Issues with traceability | active |
| [sagan-scientific-debunker](./content/sagan-scientific-debunker/) | Evaluate claims and news with scientific rigor: evidence map, confidence scale, and conclusions traceable to sources | active |

## Design

UX, product, visual design, copy.

| Skill | Description | Status |
|-------|-------------|--------|
| *(none yet)* | | |

## Ops

Operations, automation, incidents, standups.

| Skill | Description | Status |
|-------|-------------|--------|
| [coferlandia-project-manager](./ops/coferlandia-project-manager/) | Design Epics, resolve execution strategy, and manage GitHub Issues/Projects-backed portfolio state with a local planning fallback when GitHub is unavailable | active |
| [project-orchestrator](./ops/project-orchestrator/) | Explicitly execute direct plans or Analyst task DAGs through one Epic worktree, additive immutable reviews, GitHub/filesystem materialization, final PR traceability, and explicit integration | active |

---

*Last updated: 2026-07-29*
