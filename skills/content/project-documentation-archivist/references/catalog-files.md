# Catalog Files

Each catalog file has one role. Keep boundaries rigid.

## README.md

Treat `README.md` as the present state of the project.

Always include:

- project purpose
- current status
- current architecture
- main components
- installation
- configuration
- execution
- relevant environment variables
- common commands
- main flows
- relevant folder map
- links to extended documentation
- confirmed limitations
- links to `HISTORY.md`, `TODO.md`, `DECISIONS.md`, and `RUNBOOK.md`

Never turn `README.md` into a diary. Never present speculation as current fact.

## HISTORY.md

Treat `HISTORY.md` as verified historical memory.

Always include dated entries with source evidence for:

- implemented changes
- commits
- issues
- PRs
- incidents
- migrations
- refactors
- deploys
- dependency changes
- architecture changes
- infrastructure changes
- bug fixes

Every entry must answer: "Where did this come from?"

## TODO.md

Treat `TODO.md` as actionable future work.

Every task must include:

- stable ID
- status
- priority
- origin
- detection date
- context
- acceptance criteria when known
- dependencies when known

Use it for pending work, roadmap items, known bugs, future improvements, validation
tasks, documentation work, risks needing action, and valuable ideas.

## DECISIONS.md

Treat `DECISIONS.md` as project rationale.

Every decision entry must include:

- decision ID
- state
- date
- area
- context
- chosen option
- alternatives considered
- reasons
- consequences
- trade-offs
- sources
- related issue, commit, or PR references

Do not log plain events here. Only log why choices were made.

## RUNBOOK.md

Treat `RUNBOOK.md` as practical operations memory.

Always include:

- local startup
- deploy steps
- health checks
- relevant logs
- troubleshooting
- maintenance tasks
- backups
- restoration
- emergency procedures
- operational risks
- links to deeper operational docs

Never store secret values. Reference secret locations safely.

## docs/catalog/SOURCE_INDEX.md

Treat `SOURCE_INDEX.md` as the document inventory.

Maintain one row per detected source with these fields:

- status
- original document
- archived path
- document type
- detection date
- hash
- fed files
- generated conflicts
- generated questions
- notes

Allowed states:

- `pending`
- `processed`
- `skipped`
- `conflict`
- `unknown`
- `archived`

## docs/catalog/CONFLICTS.md

Treat `CONFLICTS.md` as the contradiction register.

Mandatory top-level structure:

```md
# Conflicts

## Open

## Resolved

## Archived
```

Record contradictions. Do not resolve them arbitrarily during the processing phase.

## docs/catalog/OPEN_QUESTIONS.md

Treat `OPEN_QUESTIONS.md` as the uncertainty register.

Mandatory top-level structure:

```md
# Open Questions

## Open

## Resolved

## Archived
```

Open questions do not block processing.

## docs/catalog/PROCESSING_RUNS.md

Treat `PROCESSING_RUNS.md` as the session log.

Record one entry per run with:

- date and time
- mode
- state
- branch
- base commit
- processed documents
- updated files
- open conflicts
- open questions
- validations run
- factual summary
- suggested commit

Keep it append-only except for fixing formatting mistakes in the newest entry.
