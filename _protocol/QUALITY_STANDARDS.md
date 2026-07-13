# QUALITY_STANDARDS.md

> Quality checklist for coferlandia-skills.
> **Single source of truth for the quality checklist.** Other files link here instead
> of reproducing the list. **Every agent must verify these criteria before committing.**
> The mechanical parts of this checklist are automated in `_protocol/scripts/validate_skill.py`.

The base format belongs to
[agentskills.io/specification](https://agentskills.io/specification). The rules in
this file are local extensions. The mechanical validator is
`_protocol/scripts/validate_skill.py`.

---

## ⚠️ Security and Privacy — CRITICAL

These rules are **non-negotiable**. This repository is public.

- [ ] **Zero secrets** — the skill does NOT contain API keys, tokens, passwords, or any credentials
- [ ] **Zero personal data** — the skill does NOT contain real names, emails, phone numbers, ID documents, or any personally identifiable information (PII)
- [ ] **Zero sensitive business data** — the skill does NOT expose internal IPs, private production URLs, real database names, or information that shouldn't be public
- [ ] **Generic references** — if the skill mentions internal systems, use descriptive placeholders (`{DATABASE_URL}`, `{API_ENDPOINT}`), never real values
- [ ] **No assumed private context** — the skill's instructions work without the agent having hardcoded private information

> **Golden rule:** if you wouldn't post that data on Twitter, it doesn't go in the skill.

### Handling references to internal systems

```yaml
# BAD — never do this
metadata:
  api_endpoint: https://internal.example.invalid/api/v2
  db_host: postgres-prod-01.internal.example.invalid

# GOOD — use placeholders
metadata:
  api_endpoint: "{API_ENDPOINT}"
  # Configure via environment variables or the project's CLAUDE.md
```

If the skill needs private configuration data, instruct it to read from environment
variables or a local config file — never from the repository.

---

## Format and Structure

- [ ] `name` follows the rules in [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md) and matches the folder name
- [ ] `description` is between 1 and 1024 characters
- [ ] `category` is one of: `meta`, `engineering`, `data`, `content`, `design`, `ops`
- [ ] `status` is one of: `draft`, `active`, `deprecated`
- [ ] `SKILL.md` stays within the size limit: **target <5000 tokens; hard cap ~500 lines** (extensive material → `references/`)
- [ ] The skill lives at `skills/{category}/{name}/SKILL.md`

---

## Description (Triggering)

- [ ] `description` includes explicit domain keywords (tools, formats, action verbs)
- [ ] `description` states when to use the skill ("Use when...", "Activate when the user asks...")
- [ ] `description` mentions non-obvious cases where it applies, even if the user doesn't use the exact terms
- [ ] `description` is NOT generic ("This skill helps with X") — it must be specific and actionable
- [ ] The frontmatter adds no fields outside agentskills.io; triggering lives in `description`

---

## Instructions

- [ ] Instructions are **procedural** (how to do it, step by step), not declarative (what to produce)
- [ ] Each step is a concrete action the agent can execute
- [ ] The skill teaches a **reusable method** for a class of problems, not a one-off solution
- [ ] A `## Gotchas` section exists with at least 1 real, concrete entry
- [ ] Gotchas are specific errors (not generic advice like "handle errors correctly")
- [ ] If an output format is expected, a **concrete template** exists (not just prose description)
- [ ] References to `references/` or `assets/` specify **when** to load them, not just that they exist

---

## Content — What Should NOT Be in a Skill

- [ ] No general knowledge any LLM already has
- [ ] No explanations of basic domain concepts (the agent already knows them)
- [ ] Doesn't cover every edge case — delegates to the agent's judgment when reasonable
- [ ] No instructions that contradict each other

---

## Scripts (if applicable)

- [ ] Scripts have NO interactive prompts (runtime questions to the user)
- [ ] Scripts have a `--help` flag with: description, available flags, usage examples
- [ ] Error messages are descriptive: what failed + what was expected + what to try
- [ ] Output is structured (JSON, CSV, TSV) — not hard-to-parse free text
- [ ] Data goes to stdout; diagnostics/logs go to stderr
- [ ] Scripts are idempotent (safe to retry)
- [ ] Dependencies are declared inline (PEP 723 for Python, etc.)
- [ ] Destructive scripts have a `--dry-run` or `--confirm` flag
- [ ] **Scripts do NOT hardcode secrets, tokens, or private data**

---

## Index and Documentation

- [ ] `skills/INDEX.md` was updated with this skill
- [ ] The INDEX.md entry includes: name, brief description, category, status
- [ ] The commit follows the format: `skill({category}/{name}): description`

---

## Minimum Test (Verifiable)

A skill can't be marked `active` without recorded test evidence. "It was tested" is
unverifiable without a trail, so record it in the frontmatter:

- [ ] Ran `_protocol/scripts/validate_skill.py {folder}` and it exited with code 0
- [ ] Activated it with a natural prompt (without naming the skill) and the output matched the expected format
- [ ] The result is recorded in `metadata.tested` with a date and how it was tested, e.g.:
  ```yaml
  metadata:
    status: active
    tested: "2026-06-11 - validated with validate_skill.py; activated with the prompt '...'"
  ```

If an `active` skill has no `metadata.tested`, the validator flags it with a warning.
- [ ] `tests/cases.json` exists with at least one positive and one negative prompt

---

## Status Levels

| Status | Meaning |
|--------|---------|
| `draft` | In development, not for production use |
| `active` | Tested and ready to use |
| `deprecated` | Replaced by another skill; do not use |
