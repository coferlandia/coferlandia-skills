# GitHub Sync

Use this reference only when the user explicitly requests GitHub issue synchronization
or when the current task must be linked to an issue before work starts.

## Goal

Treat GitHub issues as the active external registry for tracked work while preserving
`TODO.md` as the local mirrored backlog and `HISTORY.md` as the verified record of
closed issue history.

## Preconditions

1. Confirm connector access to GitHub.
2. Identify the target repository in `owner/repo` form.
3. Read the current `TODO.md` and `HISTORY.md` completely before reconciling anything.

If connector access is unavailable, stop the sync flow, register the limitation in
`docs/catalog/PROCESSING_RUNS.md`, and do not invent remote state.

## Canonical Link Fields

### TODO.md task fields

When a task is synchronized with GitHub, keep these fields present:

- `GitHub issue: owner/repo#123`
- `GitHub state: open | closed`
- `Last sync: YYYY-MM-DDTHH:MM:SSZ`

Tasks without `GitHub issue` are considered local-only until the backfill phase runs.

### HISTORY.md fields

Closed issue entries should include:

- `Fecha:` date of the historical entry
- `Fuentes:` evidence that the issue existed or changed state
- `Relaciones -> Issue:` canonical `owner/repo#123` reference when known

Do not copy the entire issue body into `HISTORY.md`. Record only the verified event,
its summary, and its evidence.

## Sync Order

Always run these stages in order:

1. **Backfill local TODO tasks**
2. **Import unmatched open GitHub issues into TODO.md**
3. **Move closed issues from TODO.md into HISTORY.md**
4. **Restore reopened issues to TODO.md**
5. **Register conflicts and validation**

## Backfill Rules

For each actionable task in `TODO.md` without a `GitHub issue`:

1. Search for an equivalent open issue by title and context.
2. Link the issue only when the match is clear.
3. If no clear match exists, create a new GitHub issue.
4. Write the canonical issue reference, state, and sync timestamp back into `TODO.md`.

Do not create issues for vague notes, parking-lot ideas, or entries that are not yet
actionable enough to be worked.

## Import Rules

For each open issue not represented in `TODO.md`:

1. Create a stable TODO entry.
2. Set `Origen:` to GitHub issue evidence.
3. Copy only the title and concise actionable context needed locally.
4. Record `GitHub issue`, `GitHub state`, and `Last sync`.

## Closed Issue Rules

For each linked issue that is now closed:

1. Remove or mark complete the corresponding TODO entry so it no longer stays in the
   active backlog.
2. Create or update a `HISTORY.md` entry describing the closure as a verified
   historical event.
3. Record issue reference and evidence in `Fuentes:` and `Relaciones:`.

If the issue is closed but local evidence shows the work was rejected, postponed, or
closed as duplicate, reflect that nuance in the history summary instead of pretending
it shipped.

## Reopened Issue Rules

If a closed issue reopens:

1. Recreate or reactivate the TODO entry.
2. Preserve the previous `HISTORY.md` entry because the prior closure is still a real
   event that happened.
3. Update `GitHub state: open` and `Last sync`.

## Conflict Rules

Register a conflict instead of auto-merging when:

- two or more GitHub issues plausibly match one local task
- one GitHub issue plausibly matches multiple local tasks
- titles look similar but acceptance criteria differ materially
- local status and remote state imply different work scopes

Record the alternatives and the evidence in `docs/catalog/CONFLICTS.md`.

## Preflight Before Work

Before starting work on a task that belongs in `TODO.md`:

1. Check whether it already has `GitHub issue`.
2. If not, search for an equivalent issue.
3. If none exists, create it.
4. Update `TODO.md` before the task moves into active execution.

This keeps the local backlog and GitHub aligned from the moment real work starts.
