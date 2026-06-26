# Validation

Run validation at the end of every processing or resolution session.

## Command

Execute:

```bash
python skills/content/project-documentation-archivist/scripts/validate_catalog.py --project-root .
```

Run the command from the target project root. If the skill is installed in another
location, replace the script path with the installed absolute or relative path to
`validate_catalog.py`.

## What the Validator Checks

- required files exist
- `AGENTS.md` exists
- `docs/catalog/` exists
- `CONFLICTS.md` contains `Open`, `Resolved`, and `Archived`
- `OPEN_QUESTIONS.md` contains `Open`, `Resolved`, and `Archived`
- `PROCESSING_RUNS.md` exists and has a title
- archived processed sources contain frontmatter with `catalog_status: processed`
- basic Obsidian-style and Markdown links point to existing archive files
- sources marked `archived` are not still left in `docs/inbox/`

## Manual Checks

Also verify manually:

- `README.md` stays focused on present state
- `AGENTS.md` stays agent-oriented, concise at the top, and uses relative links
- existing semantic content in `AGENTS.md` was preserved or explicitly quarantined in a legacy section
- `HISTORY.md` entries have evidence
- `TODO.md` avoids duplicate tasks
- synchronized GitHub issue references in `TODO.md` use canonical `owner/repo#123` form
- synchronized closed issues moved into `HISTORY.md` still keep evidence and issue references
- `DECISIONS.md` explains reasons
- `RUNBOOK.md` does not expose secret values
- `SOURCE_INDEX.md` rows match the files actually processed

## Failure Handling

When validation fails:

1. Read the failing items.
2. Fix the catalog structure or links.
3. Re-run the validator.
4. Register the failed and successful attempts in `PROCESSING_RUNS.md`.
