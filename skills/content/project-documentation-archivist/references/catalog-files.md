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
- links to `AGENTS.md`, `HISTORY.md`, `TODO.md`, `DECISIONS.md`, and `RUNBOOK.md`

Never turn `README.md` into a diary. Never present speculation as current fact.

## AGENTS.md

Treat `AGENTS.md` as the minimum reliable entrypoint for agents before they change the
project.

Always include:

- short critical instructions for agents
- essential architecture summary
- non-obvious conventions
- sensitive areas
- confirmed validation commands
- a documentation index with relative links
- maintenance notes for preserving and updating the file

Never use `AGENTS.md` as a dump of full project history, long design discussions, or
deep operational detail that belongs in `README.md`, `RUNBOOK.md`, `HISTORY.md`, or
`DECISIONS.md`.

If `AGENTS.md` already exists:

- preserve semantic content
- reorganize without silent deletion
- summarize carefully
- move bulky detail downward or into linked docs
- keep a `Legacy / Existing Notes` section when material cannot be integrated cleanly

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

## .coferlandia/catalog/SOURCE_INDEX.md

Treat `SOURCE_INDEX.md` as the document inventory.

Maintain one row per detected source with these fields:

- status
- original document
- archived path
- document type
- detection date
- hash
- fed files
- generated open items
- notes

Allowed states:

- `pending`
- `processed`
- `skipped`
- `conflict`
- `unknown`
- `archived`

## .coferlandia/catalog/OPEN_QUESTIONS.md

Treat `OPEN_QUESTIONS.md` as the register for both contradictions and unresolved
questions, distinguished by the `Type` field on each entry.

Mandatory top-level structure:

```md
# Open Questions

## Open

## Resolved

## Archived
```

Record contradictions rather than resolving them arbitrarily during the processing
phase. Open questions never block processing.

## .coferlandia/catalog/PROCESSING_RUNS.md

Treat `PROCESSING_RUNS.md` as the session log.

Record one entry per run with:

- date and time
- mode
- state
- branch
- base commit
- processed documents
- updated files
- open items
- validations run
- factual summary
- suggested commit

Keep it append-only except for fixing formatting mistakes in the newest entry.
