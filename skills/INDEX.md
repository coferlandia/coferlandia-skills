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
| [software-development](./engineering/software-development/) | Routes developer, debugger, coding-agent, and code-reviewer work through isolated worktrees, validation, review, and supervisor-controlled Git integration | active |

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
| [coferlandia-project-manager](./ops/coferlandia-project-manager/) | Design project initiatives and manage a GitHub Issues/Projects-backed multi-project portfolio with Obsidian projections | active |
| [project-orchestrator](./ops/project-orchestrator/) | Explicitly execute approved development specifications through deterministic phase, commit, review, and merge orchestration | active |

---

*Last updated: 2026-07-27*
