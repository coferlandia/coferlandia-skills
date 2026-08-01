# Skills Index — coferlandia-skills

> **Single source of truth for the skill inventory.** This is the only file that lists
> which skills exist and their status. Update only this file when adding, removing, or
> changing a skill — there are no mirror catalogs to sync by hand.
>
> **Row format (defined here, not repeated elsewhere):**
> `| [skill-name](RELATIVE_SKILL_PATH) | One-line description | {status} |`
> where `RELATIVE_SKILL_PATH` is `./{category}/{skill-name}/` and `status` is
> `draft | active | deprecated`. The path is relative to this file, which lives inside
> `skills/`.

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
| [software-development](./engineering/software-development/) | Routes broad-context Analyst decomposition with single-store outputs, developer/debugger work, executable coding-agent contracts, and independent review while keeping Git authority separate | active |
| [the-architect](./engineering/the-architect/) | Govern cross-project architecture memory, reusable components, evidence-based assessments, concise release deltas, and optional pre-execution Architecture Gates | active |

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
| [project-evangelist](./content/project-evangelist/) | Build progressive, evidence-based developer documentation with a verified technology overview, architecture, repository map, reading paths, and contributor orientation | active |
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
| [coferlandia-project-manager](./ops/coferlandia-project-manager/) | Design Epics, resolve execution strategy, and emit one complete GitHub or local planning representation for orchestrator initialization | active |
| [project-orchestrator](./ops/project-orchestrator/) | Execute direct plans or Analyst DAGs after one-time GitHub/filesystem initialization, using a frozen local snapshot, immutable reviews, final PR traceability, and explicit integration | active |

---

*Last updated: 2026-08-01*
