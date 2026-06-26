# Workflow

Execute the documentation catalog process in fixed phases. Do not skip ordering.

## Phase 0 - Preparation

1. Identify the project root.
2. Detect whether `.git/` exists.
3. Detect the current branch when Git exists.
4. Detect the current commit when Git exists.
5. Detect whether the working tree already contains changes.
6. Locate existing canonical files:
   `README.md`, `AGENTS.md`, `HISTORY.md`, `TODO.md`, `DECISIONS.md`, `RUNBOOK.md`,
   `docs/catalog/SOURCE_INDEX.md`, `docs/catalog/CONFLICTS.md`,
   `docs/catalog/OPEN_QUESTIONS.md`, `docs/catalog/PROCESSING_RUNS.md`.
7. Create missing canonical files from the templates in `assets/`.
8. Create `docs/catalog/` and `docs/archive/` when missing.
9. Register pre-existing dirty state in `docs/catalog/PROCESSING_RUNS.md`.

## Phase 1 - Inventory

1. Scan the candidate directories:
   `docs/inbox/`, `docs/`, `notes/`, `documentation/`, `design/`, `specs/`,
   `planning/`, `issues/`, and the project root.
2. Exclude ignored directories and binary files.
3. Compute a content hash for each processable source.
4. Detect sources already marked with `catalog_status: processed`.
5. Detect hashes already present as processed in `docs/catalog/SOURCE_INDEX.md`.
6. Set status per source:
   `pending`, `processed`, `skipped`, `unknown`, `conflict`, or `archived`.
7. Update `docs/catalog/SOURCE_INDEX.md` immediately after classification changes.

## Phase 2 - Classification

Classify each processable source before integration:

- `current-state-doc`
- `historical-note`
- `implementation-plan`
- `bug-analysis`
- `roadmap-note`
- `decision-record`
- `architecture-note`
- `setup-guide`
- `runbook-note`
- `client-communication`
- `mixed`
- `unknown`

Use `mixed` only when one source materially feeds multiple catalog files. Use
`unknown` only when the source stays unclassifiable after full reading.

## Phase 3 - Detailed Reading

Read the full source. Extract:

- one concise summary
- confirmed present facts
- agent-critical instructions
- non-obvious conventions
- sensitive areas
- validation commands
- historical events
- future tasks
- decision records
- operational procedures
- risks
- contradictions
- open questions
- references to issues, commits, PRs, and external documents
- target files to feed

Process long files by sections and maintain one global synthesis. Do not stop after
the first useful paragraph.

## Phase 4 - Distribution

Route extracted information strictly by role:

- confirmed present state -> `README.md`
- minimum agent orientation -> `AGENTS.md`
- verified past events -> `HISTORY.md`
- actionable future work -> `TODO.md`
- rationale and choice records -> `DECISIONS.md`
- operational procedures -> `RUNBOOK.md`
- contradictions -> `docs/catalog/CONFLICTS.md`
- missing data -> `docs/catalog/OPEN_QUESTIONS.md`
- source traceability -> `docs/catalog/SOURCE_INDEX.md`
- run metadata -> `docs/catalog/PROCESSING_RUNS.md`

Allow one source to feed multiple files. Never collapse all information into the
README.

## Phase 5 - Catalog Update Order

Update files in this exact order:

1. `HISTORY.md`
2. `DECISIONS.md`
3. `TODO.md`
4. `RUNBOOK.md`
5. `README.md`
6. `AGENTS.md`
7. `docs/catalog/CONFLICTS.md`
8. `docs/catalog/OPEN_QUESTIONS.md`
9. `docs/catalog/SOURCE_INDEX.md`
10. `docs/catalog/PROCESSING_RUNS.md`

Preserve existing human content. Use managed blocks only when the skill must control
one section repeatedly:

```md
<!-- DOC-CATALOG:START section="section-name" -->
...
<!-- DOC-CATALOG:END -->
```

Do not overwrite human content outside managed blocks unless the change is required to
keep the file coherent. If that happens, explain it in `PROCESSING_RUNS.md`.

For `AGENTS.md`, apply stricter preservation:

- read the full existing file before editing
- preserve semantic content
- reorganize instead of replacing
- use a `Legacy / Existing Notes` section when uncertain
- record contradictions in `docs/catalog/CONFLICTS.md`
- record missing confirmations in `docs/catalog/OPEN_QUESTIONS.md`

## Phase 6 - Source Marking

Add or merge frontmatter on each processed source. Required keys:

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

Preserve the original body under the frontmatter. Preserve unrelated existing
frontmatter keys.

## Phase 7 - Archiving

Move each processed source to:

```text
docs/archive/YYYY/YYYY-MM-DD-original-name.ext
```

If the destination exists, generate a unique name:

```text
YYYY-MM-DD-original-name-2.ext
```

Use `git mv` when Git exists and the source is tracked. If that fails, use a normal
move and register the fallback in the processing run.

## Phase 8 - Validation

Validate:

- required catalog files exist
- `AGENTS.md` exists
- archived processed sources contain frontmatter
- source index is updated
- conflict and question files keep required sections
- processing runs are recorded
- `AGENTS.md` stays brief at the top and navigable below
- `AGENTS.md` does not silently delete preserved instructions
- no obvious duplicates were introduced into `HISTORY.md` or `TODO.md`
- `README.md` stays present-focused
- `DECISIONS.md` records reasons, not just events
- `RUNBOOK.md` does not contain secrets
- archived sources are no longer left in `docs/inbox/` after they are marked archived

Run:

```bash
python scripts/validate_catalog.py --project-root .
```

Register the validation result in `docs/catalog/PROCESSING_RUNS.md`.

## Optional GitHub Sync Extension

Run this extension only when the user explicitly requests issue synchronization.

1. Read `references/github-sync.md`.
2. Confirm connector access and target repository.
3. Backfill local TODO tasks without issue references.
4. Import unmatched open issues into `TODO.md`.
5. Move linked closed issues into `HISTORY.md`.
6. Restore reopened issues into `TODO.md`.
7. Record conflicts instead of forcing ambiguous links.
8. Re-run validation and register the sync run in `docs/catalog/PROCESSING_RUNS.md`.
