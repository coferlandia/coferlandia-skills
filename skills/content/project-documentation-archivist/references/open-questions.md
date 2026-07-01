# Open Questions

Track every unresolved item — questions and conflicts alike — in one register:
`docs/catalog/OPEN_QUESTIONS.md`. Use the `Type` field to tell them apart.

## When to Open One

- **Type: conflict** - two or more sources make incompatible claims about current
  architecture, operational procedures, dependency versions, deployment state,
  ownership, roadmap status, or implementation state.
- **Type: question** - processing reveals a gap, missing evidence, or an unresolved
  decision.

## Format

```md
## QUESTION-YYYYMMDD-NNN - Short title

Status: open
Type: question | conflict
Detected: YYYY-MM-DD
Detected in session: [[docs/catalog/PROCESSING_RUNS.md#yyyy-mm-dd-hhmm-processing-run]]
Area: backend | frontend | infra | product | docs | architecture | operations | unknown
Priority: low | medium | high

Question or conflict:
...

Context:
...

Sources:
- [[docs/archive/YYYY/document-a.md]]
- [[docs/archive/YYYY/document-b.md]] (second source only applies to conflicts)

Impact:
...

Temporary decision (conflicts only):
...

Action needed:
...
```

For conflicts, apply a conservative temporary decision and keep the uncertain claim
out of `README.md`. Questions never block processing.

## Resolution Mode

Use resolution mode only after the user supplies answers or chooses a policy.

1. Read active items from `docs/catalog/OPEN_QUESTIONS.md`.
2. Match the user's input to exact IDs.
3. Update the relevant catalog files.
4. Append resolution details with date and source.
5. Set `Status: resolved`.
6. Move the item under `## Resolved`.
7. Register the action in `PROCESSING_RUNS.md`.

Never delete resolved items. Preserve traceability.
