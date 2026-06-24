# Frontmatter

Use frontmatter to mark processed sources without losing original content.

## Required Header

Every processed archived source must contain this header:

```yaml
---
catalog_status: processed
catalog_processed_at: YYYY-MM-DDTHH:mm:ss
catalog_processor: project-documentation-archivist
source_original_path: "<original-path>"
source_archived_path: "<archived-path>"
source_sha256: "<sha256>"
git_commit_at_processing: "<commit-or-none>"
document_type: "<document-type>"
project_area: "<backend|frontend|infra|product|docs|architecture|operations|mixed|unknown>"
feeds:
  - README.md
references_detected:
  issues: []
  commits: []
  prs: []
  external_refs: []
catalog_notes:
  - "How the source was used."
---
```

## Merge Rules

When the source already has frontmatter:

1. Parse the existing frontmatter.
2. Preserve all unrelated keys.
3. Replace or add the catalog keys above.
4. Keep the original body unchanged below the merged header.
5. Normalize list fields to arrays.
6. Do not duplicate keys with different names.

## Path Rules

- `source_original_path` stores the path before archiving.
- `source_archived_path` stores the final archive path.
- Use project-relative paths.

## Feed Rules

Record every catalog file touched by the source in `feeds`.

Examples:

- `README.md`
- `HISTORY.md`
- `TODO.md`
- `DECISIONS.md`
- `RUNBOOK.md`
- `docs/catalog/CONFLICTS.md`
- `docs/catalog/OPEN_QUESTIONS.md`

## Reference Rules

Record extracted references in `references_detected`:

- `issues`
- `commits`
- `prs`
- `external_refs`

Store empty arrays when nothing is detected. Do not omit the keys.

## Notes Rules

Use `catalog_notes` for short factual notes only:

- how the source was classified
- what catalog files were fed
- whether conflicts or questions were generated

Do not write long summaries into the frontmatter.
