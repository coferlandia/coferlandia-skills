---
name: using-coferlandia-skills
description: >
  Use at the start of any task in a project that has this plugin installed, before
  responding, exploring files, or asking clarifying questions — check skills/INDEX.md
  and invoke any Coferlandia skill that applies. Also triggers when about to skip a
  skill because "it's just a quick question," "I already know how to do this," or "I
  don't need the full process for something this small."
license: Apache-2.0
compatibility: >
  Requires this plugin's skills/INDEX.md to be readable from the working project.
metadata:
  author: coferlandia
  version: "1.0.0"
  category: meta
  status: draft
  tested: "not yet activated with a natural prompt; adapted from
    superpowers:using-superpowers (prime-radiant-inc/superpowers), pending a real
    activation run before promoting to active per QUALITY_STANDARDS.md"
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

## Context

Coferlandia skills only help if they actually get invoked. The common failure mode
isn't ignorance that a skill exists — it's skipping the check because the task feels
too small, too obvious, or too urgent to pause for it. This skill is the gate that
runs before that skip happens.

**If there's even a small chance a skill in `skills/INDEX.md` applies to what you're
about to do, invoke it. This isn't optional, and it isn't something to reason your
way out of.**

## The Rule

**Check `skills/INDEX.md` and invoke a matching skill before any response or
action** — including clarifying questions, exploring the repository, or reading
files. If it turns out not to fit once you're in it, you can drop it; that's not a
reason to skip the check up front.

Announce it: **"Using [skill] to [purpose],"** then follow it exactly. If it has a
checklist, track each item as a todo.

## Skill Priority

When more than one skill could apply, process skills go first — they set the
approach, then domain skills carry it out.

- Any task that adds, modifies, or fixes code → `coferlandia-software-dev` first (it
  sets the control gates and roles), then whatever domain skill the task needs.
- A documentation or project-memory task → `project-documentation-archivist`.
- A strong factual or scientific claim → `sagan-scientific-debunker`.

## Red Flags

These thoughts mean stop — you're rationalizing your way past a skill check:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check `skills/INDEX.md` first. |
| "I need more context before I check" | The skill check comes before gathering context, not after. |
| "This doesn't need the full process" | If a skill applies, use it — small tasks are exactly where skipping it goes unnoticed. |
| "I already know this skill" | Skills change. Re-read the current `SKILL.md` before relying on memory of it. |

## Precedence

User instructions (project instructions, direct requests) override skills, which in
turn override default behavior. Only skip a skill's process when the human partner has
explicitly said to.

## Gotchas

- **Treating this as a one-time check:** the gate applies at the start of every task
  in the session, not just the first one — a new task can trigger a different skill
  even mid-conversation.
- **Reading the skill's description instead of its body:** the description tells you
  *when* to invoke; the actual steps live in the skill body. Load and follow the full
  `SKILL.md`, don't infer behavior from the description alone.
