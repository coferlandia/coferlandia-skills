# NAMING_CONVENTIONS.md

> Naming rules for skills in coferlandia-skills.
> **Single source of truth for naming.** Any other file that needs these rules links
> to this document instead of reproducing it (so copies can't contradict each other).

---

## `name` field rules

The `name` field in `SKILL.md` frontmatter must:

- Use only: lowercase letters (`a-z`), digits (`0-9`), and hyphens (`-`)
- NOT use: uppercase, spaces, underscores, periods, or any other special character
- NOT start or end with a hyphen
- NOT have consecutive hyphens (`--`)
- Be at most 64 characters
- **Match exactly the name of the folder containing it**

```yaml
# Valid
name: code-review
name: sql-query
name: release-notes
name: deploy-checklist

# Invalid
name: Code-Review       # uppercase
name: sql_query         # underscore
name: -deploy           # starts with a hyphen
name: deploy-           # ends with a hyphen
name: deploy--checklist # double hyphen
```

---

## Available categories

| Category | Directory | What goes here |
|-----------|------------|-------------|
| `meta` | `skills/meta/` | Skills about skills: creating, auditing, improving skills |
| `engineering` | `skills/engineering/` | Code, infrastructure, architecture, debugging |
| `data` | `skills/data/` | Data analysis, pipelines, queries, reports |
| `content` | `skills/content/` | Writing, documentation, communication, release notes |
| `design` | `skills/design/` | UX, product, visual design, copy |
| `ops` | `skills/ops/` | Operations, automation, incidents, standups |

If your skill doesn't fit any category, propose a new one directly in this file (add
it to the table above).

### Category tie-breaking rule

If a skill fits two categories, decide deterministically (so two agents pick the
same one):

1. **By the artifact it produces:** code/infra → `engineering`; text/communication →
   `content`; analysis or tabular data → `data`; UX/visual → `design`; operational
   process or automation → `ops`; skills about the repo itself or about other skills →
   `meta`.
2. **On a persistent tie:** pick whichever category appears first in the table above.

---

## Full path convention

```
skills/{category}/{skill-name}/SKILL.md
```

Examples:
```
skills/meta/using-project-skills/SKILL.md
skills/engineering/software-development/SKILL.md
skills/content/project-documentation-archivist/SKILL.md
```

---

## Commit convention

```
skill({category}/{name}): short description in imperative
```

Examples:
```
skill(meta/using-project-skills): add skill-usage gate
skill(engineering/code-review): add security checklist
skill(data/sql-query): fix soft-delete gotcha
```

---

## Version convention (metadata)

```yaml
metadata:
  version: "1.0"    # first version
  version: "1.1"    # bugfix or minor improvement
  version: "2.0"    # significant change to instructions
```

This is a **per-skill** version — it tracks changes to one skill's own instructions,
per `_protocol/SKILL_LIFECYCLE.md`. It's a different axis from the **plugin release
version** in `.claude-plugin/plugin.json`, which tracks the whole repo's releases and
is checked with `_protocol/scripts/bump_version.py --check` / `--audit`. Changelog
entries for plugin releases go in `RELEASE-NOTES.md`, not here.

---

## Names to avoid

- Overly generic names: `helper`, `utils`, `misc`
- Names that duplicate the category: `engineering-code-review` (the category already
  implies `engineering`)
- Unclear abbreviations: `cr` instead of `code-review`
