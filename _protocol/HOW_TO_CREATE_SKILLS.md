# HOW_TO_CREATE_SKILLS.md

> **Full protocol for creating a skill in coferlandia-skills.**
> Any AI agent can follow this protocol autonomously.

---

## Prerequisites

Before creating a skill, read:
- [The canonical agentskills.io specification](https://agentskills.io/specification)
- [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md) â€” naming and category rules
- [`SKILL_TEMPLATE.md`](./SKILL_TEMPLATE.md) â€” template to use
- [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md) â€” quality checklist
- [`ARTIFACT_OUTPUT_CONVENTIONS.md`](./ARTIFACT_OUTPUT_CONVENTIONS.md) â€” where skills save generated files
- If available in the environment, invoke `superpowers:writing-skills` before
  authoring each approved skill; use it to shape the draft, then tighten the
  result against this protocol and the quality checklist.

---

## Step 1: Define the skill's scope

A good skill encapsulates **one coherent unit of work**. Ask yourself:

- What specific task does it solve?
- What Coferlandia-specific knowledge does an agent need to do it well?
- Is it too narrow? (would force loading several skills for one task)
- Is it too broad? (hard to trigger precisely)

**Signs of good scope:**
- A task an agent would do in 2-5 distinct steps
- Coferlandia-specific knowledge (schemas, internal APIs, team conventions)
- An output format that needs to stay consistent

**Signs of bad scope:**
- "Everything related to X" â†’ too broad
- A single bash command â†’ too narrow, inline it instead

---

## Step 2: Choose a name and category

1. Check [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md).
2. Pick the right category: `meta`, `engineering`, `data`, `content`, `design`, `ops`.
3. Define the name as `lowercase-with-hyphens` (64 characters max).
4. Confirm no skill with that name already exists in `skills/INDEX.md`.

**Path format:** `skills/{category}/{skill-name}/`

---

## Step 3: Create the folder structure

```bash
mkdir -p skills/{category}/{skill-name}
# If the skill has scripts:
mkdir -p skills/{category}/{skill-name}/scripts
# If it has long external references:
mkdir -p skills/{category}/{skill-name}/references
# If it has templates or static resources:
mkdir -p skills/{category}/{skill-name}/assets
```

---

## Step 4: Write SKILL.md

Copy the template from [`SKILL_TEMPLATE.md`](./SKILL_TEMPLATE.md) and fill in every
section.

### Frontmatter (required)

```yaml
---
name: {skill-name}          # MUST match the folder name (see NAMING_CONVENTIONS.md)
description: >              # WHAT it does + WHEN to use it. The canonical triggering field.
  [What the skill does and when to activate it, with domain-specific keywords.]
license: Apache-2.0
compatibility: >            # REQUIRED ENVIRONMENT (binaries, runtime, access), not agent brands.
  Requires {real dependencies/access}
metadata:
  author: community
  version: "1.0"
  category: {category}
  status: active
  tested: "{date} - {how it was tested}"   # required for status: active
---
```

> **Triggering:** agentskills.io defines `description` as the field that explains what
> the skill does and when to use it. It loads during discovery, so keep it specific and
> concise. Operational detail belongs in the body of `SKILL.md`, not in invented
> frontmatter fields.

### Instruction body

Recommended structure:

```markdown
## Context

[What the agent knows about Coferlandia thanks to this skill, that it wouldn't know without it]

## Steps

1. Concrete step
2. Concrete step
3. Concrete step

## Gotchas

- [Common error 1 and how to avoid it]
- [Common error 2 and how to avoid it]

## Expected Output

[Template or description of the output format]

## Scripts Available (if applicable)

- **`scripts/name.py`** - What it does and when to run it
```

### Content rules

**Include:**
- Coferlandia-specific conventions
- Gotchas and fixes for typical mistakes
- Concrete output templates
- Multi-step checklists
- When to load `references/` files (with an explicit condition)

**Don't include:**
- General knowledge any LLM already has
- Explanations of basic concepts
- Every edge case (delegate to the agent's judgment when reasonable)

**Limit:** target <5000 tokens; hard cap ~500 lines in SKILL.md. Extensive material â†’
`references/`.

- **Output Location** â€” declare where the skill's artifacts go, following
  [`ARTIFACT_OUTPUT_CONVENTIONS.md`](./ARTIFACT_OUTPUT_CONVENTIONS.md). Default is
  `.agent/`. If any artifact targets a standard repo file (README.md, AGENTS.md,
  LICENSE, RUNBOOK.md), list it under an `### Output Exceptions` subsection.

---

## Step 5: Write scripts (if applicable)

If the skill needs scripts, put them in `scripts/`. Minimum requirements:

1. **No interactive prompts** â€” the agent runs in a non-interactive shell.
2. **Must have documented `--help`.**
3. **Descriptive error messages** â€” the agent uses the error to fix its next attempt.
4. **Structured output** â€” prefer JSON/CSV over free text.
5. **Idempotent** â€” the agent can retry them with no side effects.
6. **Declare dependencies inline** â€” use PEP 723 for Python (`# /// script`), etc.

---

## Step 6: Verify quality

The authoritative list lives in [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md) â€”
check it in full (not reproduced here to avoid duplication). First run the mechanical
validator:

```bash
python _protocol/scripts/validate_skill.py .
# must exit with code 0 (no errors)
```

---

## Step 7: Update the index

**Required.** Add the skill to `skills/INDEX.md`. The **row format is defined in the
header of `INDEX.md`** (single source of truth) â€” use it from there, don't copy it
here. In short:
`| [skill-name](./{category}/{skill-name}/) | Brief description | {status} |`.

---

## Step 8: Commit

Commit format:

```
skill({category}/{skill-name}): add skill for {what it does}
```

Example:
```
skill(engineering/code-review): add review skill with Coferlandia standards
```

---

## Notes for the agent

- If you find an error in an existing skill while working, fix it and add a Gotcha.
- If the scope of what you need to create doesn't fit any category, propose a new one
  directly in `_protocol/NAMING_CONVENTIONS.md` (add it to the category table).
