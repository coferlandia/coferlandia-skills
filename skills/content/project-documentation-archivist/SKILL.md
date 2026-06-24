---
name: project-documentation-archivist
description: >
  Catalog, normalize, update, and archive project documentation into README, HISTORY,
  TODO, DECISIONS, RUNBOOK, and traceable Obsidian-style project catalog files. Use
  when a user asks to organize project docs, process documentation inboxes, update
  project memory, archive notes, resolve documentation conflicts, keep project
  documentation synchronized with source notes and Git history, or maintain
  documentation catalogs for Git and non-Git technical projects.
license: Apache-2.0
compatibility: >
  Requires read/write access to the target project, shell access for file moves, and
  Python 3.11+ to run scripts/validate_catalog.py.
metadata:
  author: dc-sistemas
  version: "1.0.0"
  category: content
  status: active
  tested: "2026-06-24 - validated with _protocol/scripts/validate_skill.py and repo skill tests."
---

## Context

Use this skill to turn scattered project documentation into a stable catalog that
separates present state, verified history, future work, decisions, operations,
conflicts, open questions, source traceability, and processing sessions.

This skill works in autonomous mode by default. Do not ask questions while
processing documentation. Register uncertainty in `docs/catalog/CONFLICTS.md`,
`docs/catalog/OPEN_QUESTIONS.md`, and `docs/catalog/PROCESSING_RUNS.md`, then
continue.

## Prerequisites

- Work inside the user project root.
- Detect whether the project uses Git before moving archived files.
- Create missing catalog files from `assets/` before processing sources.
- Read reference files only when the phase requires extra detail.

## Modes

- **Non-interactive mode:** Process, distribute, archive, validate, and finish with a
  summary plus suggested commit message.
- **Interactive mode:** Execute the same processing flow without questions during the
  run. Present changes only after processing finishes.
- **Resolution mode:** Read active conflicts and open questions, apply supplied
  resolutions, update catalog files, move items to `Resolved`, and register the run.

## Workflow

1. Execute Phase 0 preparation. Read `references/workflow.md` before changing files.
2. Create missing target files from `assets/`:
   `README.md`, `HISTORY.md`, `TODO.md`, `DECISIONS.md`, `RUNBOOK.md`,
   `docs/catalog/SOURCE_INDEX.md`, `docs/catalog/CONFLICTS.md`,
   `docs/catalog/OPEN_QUESTIONS.md`, and `docs/catalog/PROCESSING_RUNS.md`.
3. Discover source documents in `docs/inbox/`, `docs/`, `notes/`,
   `documentation/`, `design/`, `specs/`, `planning/`, `issues/`, and the project
   root. Exclude `.git/`, `node_modules/`, `vendor/`, `bin/`, `obj/`, `dist/`,
   `build/`, `.venv/`, `__pycache__/`, binary files, heavy backups, raw logs, and
   generated artifacts unless the user explicitly asks for them.
4. Build or update `docs/catalog/SOURCE_INDEX.md`. Record one row per detected
   document with status, source path, archive path, document type, detection date,
   hash, fed files, conflicts, questions, and notes.
5. Classify each processable source as one of:
   `current-state-doc`, `historical-note`, `implementation-plan`, `bug-analysis`,
   `roadmap-note`, `decision-record`, `architecture-note`, `setup-guide`,
   `runbook-note`, `client-communication`, `mixed`, or `unknown`.
6. Read each source completely. For long files, process by sections and maintain one
   consolidated synthesis. Extract current facts, historical events, future tasks,
   decisions, operations data, risks, conflicts, open questions, references, and
   target catalog files.
7. Distribute extracted facts in this order:
   `HISTORY.md`, `DECISIONS.md`, `TODO.md`, `RUNBOOK.md`, `README.md`,
   `docs/catalog/CONFLICTS.md`, `docs/catalog/OPEN_QUESTIONS.md`,
   `docs/catalog/SOURCE_INDEX.md`, `docs/catalog/PROCESSING_RUNS.md`.
8. Keep present, past, future, decisions, and operations separated. Read
   `references/catalog-files.md` when writing or merging any catalog file.
9. Mark each processed source with merged YAML frontmatter. Read
   `references/frontmatter.md` before editing a source that already contains
   frontmatter.
10. Archive each processed source under `docs/archive/YYYY/YYYY-MM-DD-name.ext`. Use
    `git mv` when the project uses Git and the move is possible. Otherwise move the
    file normally and register the fallback.
11. Validate the catalog. Execute the validator from the skill directory and point it
    at the target project root, for example:
    `python skills/content/project-documentation-archivist/scripts/validate_catalog.py --project-root .`
    when the current working directory is the target project root. Read
    `references/validation.md` if validation fails.
12. Finish with a factual summary: processed documents, archived documents, updated
    files, open conflicts, open questions, validations executed, and the suggested
    commit message.

## Resolution Mode

1. Read `docs/catalog/CONFLICTS.md` and `docs/catalog/OPEN_QUESTIONS.md`.
2. Locate active items.
3. Apply the supplied resolution only to items covered by the user input.
4. Update `README.md`, `HISTORY.md`, `TODO.md`, `DECISIONS.md`, or `RUNBOOK.md` when
   the resolution changes project memory.
5. Change item state to `resolved`, append date and evidence, move the item to
   `Resolved`, and register the run in `docs/catalog/PROCESSING_RUNS.md`.

## Gotchas

- **Do not promote uncertain notes into `README.md`:** Keep doubtful or conflicting
  material in `CONFLICTS.md` or `OPEN_QUESTIONS.md`. `README.md` must describe only
  confirmed present state.
- **Do not merge history into decisions:** `HISTORY.md` records what happened.
  `DECISIONS.md` records why a choice was made, its alternatives, and consequences.
- **Do not destroy source context when adding frontmatter:** Merge existing
  frontmatter fields, preserve the original body, and record the archive path plus
  content hash.
- **Do not duplicate entries on repeated runs:** Reuse `source_sha256`, stable IDs,
  archived paths, and managed blocks to update existing entries instead of appending
  clones.
- **Do not ask questions mid-run:** Register uncertainty and continue. Ask only during
  the separate resolution phase if the session is interactive.

## Output Expected

Use this completion format after processing:

```text
Mode: non-interactive | interactive | resolution
Processed documents: <count>
Archived documents: <count>
Updated files:
- README.md
- HISTORY.md
- TODO.md
- DECISIONS.md
- RUNBOOK.md
- docs/catalog/SOURCE_INDEX.md
- docs/catalog/CONFLICTS.md
- docs/catalog/OPEN_QUESTIONS.md
- docs/catalog/PROCESSING_RUNS.md
Open conflicts: <count>
Open questions: <count>
Validations:
- python scripts/validate_catalog.py --project-root .
Suggested commit:
docs: update project documentation catalog
```

Use this completion format after resolution mode:

```text
Mode: resolution
Resolved conflicts: <count>
Resolved questions: <count>
Updated files:
- <file list>
Remaining open conflicts: <count>
Remaining open questions: <count>
Suggested commit:
docs: resolve documentation catalog conflicts
```

## Scripts Available

- **`scripts/validate_catalog.py`** - Validate required catalog files, archive
  frontmatter with `catalog_status: processed`, internal links, and obvious
  processing inconsistencies. Execute after every processing or resolution run.

Usage:

```bash
python skills/content/project-documentation-archivist/scripts/validate_catalog.py --help
```

## References

- Read `references/workflow.md` when starting a processing run or when deciding the
  next phase.
- Read `references/catalog-files.md` when updating `README.md`, `HISTORY.md`,
  `TODO.md`, `DECISIONS.md`, `RUNBOOK.md`, or catalog files.
- Read `references/frontmatter.md` when inserting or merging source frontmatter.
- Read `references/conflict-resolution.md` when recording contradictions, open
  questions, or applying a later resolution.
- Read `references/git-behavior.md` when the project has Git or when move operations
  need fallbacks.
- Read `references/validation.md` when running validation or diagnosing failures.
