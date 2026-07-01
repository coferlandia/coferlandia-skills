---
name: project-documentation-archivist
description: >
  Use when organizing project docs, processing a documentation inbox, updating
  project memory, creating or maintaining AGENTS.md for safe agent onboarding,
  archiving notes, resolving documentation conflicts or open questions, or
  keeping project documentation synchronized with source notes and Git history.
license: Apache-2.0
compatibility: >
  Requires read/write access to the target project, shell access for file moves,
  and Python 3.11+ to run scripts/validate_catalog.py.
metadata:
  author: dc-sistemas
  version: "2.0.0"
  category: content
  status: active
  tested: "2026-06-30 - removed GitHub sync mode and merged CONFLICTS.md into OPEN_QUESTIONS.md; pending re-validation with _protocol/scripts/validate_skill.py."
---

## Context

This skill turns scattered project documentation into a stable catalog with one file
per role: present state, agent orientation, verified history, future work, decisions,
operations, open items, source traceability, and processing sessions.

`AGENTS.md` is a first-class artifact. It is the minimum an agent should read before
touching the project — not a duplicate of `README.md`, `RUNBOOK.md`, `HISTORY.md`,
`DECISIONS.md`, or `TODO.md`, but a distillation of the instructions, constraints,
sensitive areas, and commands an agent needs before acting.

This skill runs autonomously by default. It does not ask questions while processing
documentation. Uncertainty goes into `docs/catalog/OPEN_QUESTIONS.md` and
`docs/catalog/PROCESSING_RUNS.md`, and processing continues.

## Catalog Files

| File | Role |
|---|---|
| `README.md` | present state |
| `AGENTS.md` | agent entry point |
| `HISTORY.md` | verified past events |
| `TODO.md` | actionable future work |
| `DECISIONS.md` | rationale and trade-offs |
| `RUNBOOK.md` | operations |
| `docs/catalog/SOURCE_INDEX.md` | source inventory |
| `docs/catalog/OPEN_QUESTIONS.md` | contradictions and open items |
| `docs/catalog/PROCESSING_RUNS.md` | session log |

See `references/catalog-files.md` for what belongs in each file.

## Prerequisites

- Work inside the user's project root.
- Detect whether the project uses Git before moving archived files.
- Create any missing catalog file from `assets/` before processing sources.
- Read reference files only when the current phase needs the extra detail.
- Preserve semantic content already in `AGENTS.md`. Reorganize and distill it, but
  never discard meaning silently.

## Modes

- **Non-interactive mode:** process, distribute, archive, validate, and finish with a
  summary plus a suggested commit message.
- **Interactive mode:** same flow, no questions during the run. Present changes only
  after processing finishes.
- **Resolution mode:** read open items in `docs/catalog/OPEN_QUESTIONS.md`, apply the
  supplied resolutions, update catalog files, move items to `Resolved`, and register
  the run.

## Workflow

1. Run Phase 0 preparation. Read `references/workflow.md` before changing files.
2. Create any missing catalog file from `assets/` (see Catalog Files above).
3. Discover source documents in `docs/inbox/`, `docs/`, `notes/`, `documentation/`,
   `design/`, `specs/`, `planning/`, `issues/`, and the project root. Skip `.git/`,
   `node_modules/`, `vendor/`, `bin/`, `obj/`, `dist/`, `build/`, `.venv/`,
   `__pycache__/`, binaries, backups, raw logs, and generated artifacts unless the
   user explicitly asks for them.
4. Build or update `docs/catalog/SOURCE_INDEX.md`: one row per detected document with
   status, source path, archive path, document type, detection date, hash, fed files,
   open items, and notes.
5. Classify each processable source as one of: `current-state-doc`, `historical-note`,
   `implementation-plan`, `bug-analysis`, `roadmap-note`, `decision-record`,
   `architecture-note`, `setup-guide`, `runbook-note`, `client-communication`, `mixed`,
   or `unknown`.
6. Read each source in full. For long files, process by section and keep one running
   synthesis. Extract current facts, historical events, future tasks, decisions,
   operational data, agent-critical instructions, non-obvious conventions, sensitive
   areas, validation commands, risks, contradictions, open questions, references, and
   the target catalog files.
7. Distribute extracted facts in this order: `HISTORY.md`, `DECISIONS.md`, `TODO.md`,
   `RUNBOOK.md`, `README.md`, `AGENTS.md`, `docs/catalog/OPEN_QUESTIONS.md`,
   `docs/catalog/SOURCE_INDEX.md`, `docs/catalog/PROCESSING_RUNS.md`.
8. Keep present, past, future, decisions, and operations in separate files. Read
   `references/catalog-files.md` before writing or merging any catalog file.
9. When `AGENTS.md` already exists, preserve every idea in it. Reorganize, summarize,
   deduplicate, move excess detail downward or into linked docs, and use a
   `Legacy / Existing Notes` section when content can't be integrated cleanly.
10. Mark each processed source with merged YAML frontmatter. Read
    `references/frontmatter.md` before editing a source that already has frontmatter.
11. Archive each processed source under `docs/archive/YYYY/YYYY-MM-DD-name.ext`. Use
    `git mv` when the project uses Git and the move is possible; otherwise move the
    file normally and note the fallback.
12. Validate the catalog:
    `python skills/content/project-documentation-archivist/scripts/validate_catalog.py --project-root .`
    Read `references/validation.md` if it fails.
13. Finish with a factual summary: processed documents, archived documents, updated
    files, open items, validations run, and the suggested commit message.

## Resolution Mode

1. Read `docs/catalog/OPEN_QUESTIONS.md`.
2. Locate active items.
3. Apply the supplied resolution only to items covered by the user's input.
4. Update `README.md`, `HISTORY.md`, `TODO.md`, `DECISIONS.md`, or `RUNBOOK.md` when
   the resolution changes project memory.
5. Mark the item resolved, append date and evidence, move it to `Resolved`, and
   register the run in `docs/catalog/PROCESSING_RUNS.md`.

## AGENTS.md Curation Rules

1. Read `AGENTS.md` fully when it already exists. Never overwrite it wholesale.
2. Preserve semantic content. Never delete an instruction just because it looks old,
   redundant, disordered, or unclear.
3. Distill the top of the file into a short `Critical Instructions for Agents`
   section with high-impact, actionable bullets.
4. Keep `AGENTS.md` brief at the top and navigable below. Push operational detail,
   history, and deep rationale into linked artifacts instead of bloating the file.
5. Maintain these sections, in order: `Critical Instructions for Agents`,
   `Project Essentials`, `Documentation Index`, `Maintenance Notes`.
6. Under `Project Essentials`, keep concise subsections for `Architecture`,
   `Main Conventions`, `Sensitive Areas`, and `Validation Commands`.
7. Under `Documentation Index`, use relative links only, pointing to whichever of
   `README.md`, `AGENTS.md`, `HISTORY.md`, `DECISIONS.md`, `TODO.md`, `RUNBOOK.md`, and
   `OPEN_QUESTIONS.md` exist.
8. If a command, convention, or sensitive-area claim isn't confirmed, mark it pending
   in `AGENTS.md` and log the doubt in `docs/catalog/OPEN_QUESTIONS.md`.
9. If `AGENTS.md` contradicts other evidence, log the contradiction in
   `docs/catalog/OPEN_QUESTIONS.md` and leave a brief pointer in `AGENTS.md` instead of
   silently picking a winner.
10. If existing notes don't fit the target structure without losing meaning, keep them
    in a `Legacy / Existing Notes` section.

## Gotchas

- **Don't promote uncertain notes into `README.md`:** doubtful or conflicting material
  stays in `OPEN_QUESTIONS.md`. `README.md` describes only confirmed present state.
- **Don't merge history into decisions:** `HISTORY.md` records what happened.
  `DECISIONS.md` records why a choice was made, its alternatives, and consequences.
- **Don't destroy source context when adding frontmatter:** merge existing frontmatter
  fields, preserve the original body, and record archive path plus content hash.
- **Don't duplicate entries on repeated runs:** reuse `source_sha256`, stable IDs,
  archived paths, and managed blocks to update existing entries instead of appending
  clones.
- **Don't ask questions mid-run:** log uncertainty and continue. Ask only during a
  separate resolution phase if the session is interactive.
- **Don't turn `AGENTS.md` into a README clone:** keep it focused on agent-critical
  instructions, non-obvious constraints, sensitive areas, validation commands, and
  links.
- **Don't silently erase existing AGENTS notes:** reorganize, summarize, and quarantine
  messy material if needed, but preserve semantic content.
- **Don't invent commands or conventions for `AGENTS.md`:** if build, test, lint, or
  run commands aren't confirmed, mark them pending and log an open question.

## Output Expected

After processing:

```text
Mode: non-interactive | interactive | resolution
Processed documents: <count>
Archived documents: <count>
Updated files:
- README.md
- AGENTS.md
- HISTORY.md
- TODO.md
- DECISIONS.md
- RUNBOOK.md
- docs/catalog/SOURCE_INDEX.md
- docs/catalog/OPEN_QUESTIONS.md
- docs/catalog/PROCESSING_RUNS.md
Open items: <count>
Validations:
- python scripts/validate_catalog.py --project-root .
Suggested commit:
docs: update project documentation catalog
```

After resolution mode:

```text
Mode: resolution
Resolved items: <count>
Updated files:
- <file list>
Remaining open items: <count>
Suggested commit:
docs: resolve documentation catalog open items
```

## Scripts Available

- **`scripts/validate_catalog.py`** - validates required catalog files, archive
  frontmatter with `catalog_status: processed`, internal links, and obvious processing
  inconsistencies. Run after every processing or resolution run.

Usage:

```bash
python skills/content/project-documentation-archivist/scripts/validate_catalog.py --help
```

## References

- Read `references/workflow.md` when starting a processing run or deciding the next
  phase.
- Read `references/catalog-files.md` when updating `README.md`, `HISTORY.md`,
  `TODO.md`, `DECISIONS.md`, `RUNBOOK.md`, `AGENTS.md`, or catalog files.
- Read `references/frontmatter.md` when inserting or merging source frontmatter.
- Read `references/open-questions.md` when logging a contradiction or open question,
  or applying a later resolution.
- Read `references/git-behavior.md` when the project has Git or when move operations
  need fallbacks.
- Read `references/validation.md` when running validation or diagnosing failures.
