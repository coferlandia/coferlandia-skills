# AGENTS.md — Coferlandia Skills Repository

> **If you're an AI agent, start here.**

This file is your entry point to `coferlandia-skills`. Read it in full before doing
anything.

---

## What this repository is

An **Agent Skills** repository in [agentskills.io](https://agentskills.io) format,
built to be used and maintained by AI agents. Each skill is a set of specialized
instructions you can load to execute specific Coferlandia tasks with more precision.

## Canonical contract

The [agentskills.io specification](https://agentskills.io/specification) is the
authority on structure, frontmatter, and progressive disclosure. When in doubt about
format, check that spec first. This repo doesn't duplicate the specification — it adds
only verifiable local conventions: categories, status, behavioral evidence, and the
index.

**Philosophy:** this repo is *for agents* and *by agents*. You have everything you
need to create new skills, improve existing ones, and maintain the index — without
needing extra instructions from a human.

---

## Repository map

```
coferlandia-skills/
├── AGENTS.md              ← You are here
├── README.md              ← Human-facing overview
├── LICENSE                ← Apache License 2.0
│
└── skills/                ← All skills
    ├── INDEX.md           ← Full catalog (always keep updated)
    ├── meta/               skills about skills
    ├── engineering/
    ├── data/
    ├── content/
    ├── design/
    └── ops/
```

See `skills/INDEX.md` for which of those categories currently have skills in them.

---

## Before doing anything else

Check `skills/meta/using-coferlandia-skills/` — it defines when and how to invoke a
skill (before responding, not after). Follow it for any task in a project where this
plugin is installed.

## Using an existing skill

1. Read `skills/INDEX.md` to find available skills.
2. Go to the relevant skill's folder.
3. Read its `SKILL.md` in full.
4. Follow the instructions.

---

## Creating a new skill

1. Read `_protocol/HOW_TO_CREATE_SKILLS.md` — the full protocol.
2. Use `_protocol/SKILL_TEMPLATE.md` as your starting point.
3. Check your skill against `_protocol/QUALITY_STANDARDS.md` and run
   `_protocol/scripts/validate_skill.py`.
4. Update `skills/INDEX.md`.

---

## Source of truth per rule

Every rule lives in **exactly one owning file**. This entry point, and any other
document, *link* to that owner instead of copying the rule, so no copy can contradict
another:

| Rule | Owner |
|------|-------|
| Naming, categories, and tie-breaking | [`_protocol/NAMING_CONVENTIONS.md`](./_protocol/NAMING_CONVENTIONS.md) |
| Quality and safety checklist | [`_protocol/QUALITY_STANDARDS.md`](./_protocol/QUALITY_STANDARDS.md) |
| SKILL.md format and progressive disclosure | [agentskills.io/specification](https://agentskills.io/specification) |
| Skill inventory and row format | [`skills/INDEX.md`](./skills/INDEX.md) |
| Lifecycle states | [`_protocol/SKILL_LIFECYCLE.md`](./_protocol/SKILL_LIFECYCLE.md) |
| When and how to invoke a skill | [`skills/meta/using-coferlandia-skills/`](./skills/meta/using-coferlandia-skills/) |

---

## Skills at a glance

See `skills/INDEX.md` for the full, current catalog (the single source of truth).

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE). This repository and the skills in it
are provided "as is," with no warranty. Verify a skill's behavior before relying on it
for consequential work.
