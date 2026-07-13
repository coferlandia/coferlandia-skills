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
| [using-coferlandia-skills](./meta/using-coferlandia-skills/) | Check skills/INDEX.md and invoke a matching skill before responding to any task, instead of skipping the check | active |
| [skill-repository-versioning](./meta/skill-repository-versioning/) | Pre-commit checklist for a skill repository: sync the skill index, bump per-skill vs. repo-wide release versions correctly | active |
| [coferlandia-project-skill-miner](./meta/coferlandia-project-skill-miner/) | Extract current operational recipes from project documentation and convert approved ones into project-local agent skills | active |

## Engineering

Code, infrastructure, architecture, debugging.

| Skill | Description | Status |
|-------|-------------|--------|
| [coferlandia-software-dev](./engineering/coferlandia-software-dev/) | Routes developer, debugger, coding-agent, and code-reviewer work through isolated worktrees, validation, review, and local integration | active |

## Data

Data analysis, pipelines, queries, reports.

| Skill | Description | Status |
|-------|-------------|--------|
| *(none yet)* | | |

## Content

Writing, documentation, communication, release notes.

| Skill | Description | Status |
|-------|-------------|--------|
| [project-documentation-archivist](./content/project-documentation-archivist/) | Catalog, normalize, and archive a project's documentation memory with traceability and open-item tracking | active |
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
| *(none yet)* | | |

---

*Last updated: 2026-07-12*

