# QUALITY_STANDARDS.md

> Quality checklist for coferlandia-skills.
> **Single source of truth for the quality checklist.** Other files link here instead
> of reproducing the list. **Every agent must verify these criteria before committing.**
> Mechanical checks are automated by `_protocol/scripts/validate_skill.py` and the
> repository-local release-maintainer CLI.

The base format belongs to
[agentskills.io/specification](https://agentskills.io/specification). The rules in
this file are local extensions.

---

## ⚠️ Security and Privacy — CRITICAL

These rules are **non-negotiable**. This repository is public.

- [ ] **Zero secrets** — the skill does NOT contain API keys, tokens, passwords, or credentials
- [ ] **Zero personal data** — the skill does NOT contain real names, emails, phone numbers, ID documents, or PII
- [ ] **Zero sensitive business data** — the skill does NOT expose internal IPs, private production URLs, real database names, or private information
- [ ] **Generic references** — use placeholders (`{DATABASE_URL}`, `{API_ENDPOINT}`), never real values
- [ ] **No assumed private context** — instructions work without hardcoded private information

> **Golden rule:** if you wouldn't post that data publicly, it doesn't go in the skill.

If a skill needs private configuration, instruct it to read environment variables or a
local config file — never the public repository.

---

## Format and Structure

- [ ] `name` follows [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md) and matches the folder
- [ ] `description` is between 1 and 1024 characters
- [ ] `category` is one of: `meta`, `engineering`, `data`, `content`, `design`, `ops`
- [ ] `status` is one of: `draft`, `active`, `deprecated`
- [ ] `SKILL.md` stays below the hard cap of ~500 lines
- [ ] The public skill lives at `skills/{category}/{name}/SKILL.md`
- [ ] The public skill has `CHANGELOG.md`
- [ ] The latest changelog version equals `SKILL.md` `metadata.version`

---

## Description (Triggering)

- [ ] `description` includes explicit domain keywords
- [ ] `description` states when to use the skill
- [ ] `description` mentions non-obvious applicable cases
- [ ] `description` is specific and actionable
- [ ] Triggering lives in `description`, not invented frontmatter fields

---

## Instructions

- [ ] Instructions are procedural, not merely declarative
- [ ] Each step is a concrete action the agent can execute
- [ ] The skill teaches a reusable method
- [ ] A `## Gotchas` section exists with at least one real entry
- [ ] Gotchas are specific errors, not generic advice
- [ ] Expected outputs use a concrete template when applicable
- [ ] References specify **when** to load them

---

## Content — What Should NOT Be in a Skill

- [ ] No general knowledge any LLM already has
- [ ] No explanations of basic domain concepts
- [ ] Does not enumerate every possible edge case
- [ ] No contradictory instructions

---

## Scripts (if applicable)

- [ ] No interactive runtime prompts
- [ ] Documented `--help`
- [ ] Descriptive errors
- [ ] Structured stdout; diagnostics to stderr
- [ ] Idempotent retries
- [ ] Dependencies declared inline where appropriate
- [ ] Destructive operations support dry-run/confirmation
- [ ] No hardcoded secrets, tokens, private data, or implicit Git publication

---

## Index, Changelog, and Release Documentation

- [ ] `skills/INDEX.md` was updated when inventory/discovery changed
- [ ] `CHANGELOG.md` describes externally meaningful skill behavior, newest first
- [ ] A changed public skill version appears in the current repository release table
- [ ] `RELEASE-NOTES.md` latest released version matches the plugin manifest
- [ ] README's managed latest-release block matches `RELEASE-NOTES.md`
- [ ] `Unreleased` is empty in a release-ready branch
- [ ] The final plugin archive includes public release documentation and excludes `.agents/**` and `.agent/**`
- [ ] The commit follows repository conventions

See [`RELEASE_MAINTENANCE.md`](./RELEASE_MAINTENANCE.md) for canonical ownership and
the final-delivery gate.

---

## Minimum Test (Verifiable)

A skill can't be marked `active` without recorded evidence:

- [ ] Ran `_protocol/scripts/validate_skill.py {folder}` and it exited with code 0
- [ ] Activated it with a natural prompt and observed the expected contract
- [ ] Recorded the date and evidence in `metadata.tested`
- [ ] `tests/cases.json` exists with at least one positive and one negative prompt

For a repository release, also run:

```bash
python _protocol/scripts/validate_skill.py --all skills
python _protocol/scripts/bump_version.py --check
python _protocol/scripts/bump_version.py --audit
python .agents/skills/coferlandia-release-maintainer/scripts/coferlandia-release-maintainer-cli.py check --base <ref> --release-ready
```

---

## Status Levels

| Status | Meaning |
|--------|---------|
| `draft` | In development, not for production use |
| `active` | Tested and ready to use |
| `deprecated` | Replaced by another skill; do not use |
