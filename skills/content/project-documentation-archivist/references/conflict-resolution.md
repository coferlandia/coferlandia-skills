# Conflict Resolution

Use separate registers for contradictions and open questions. Do not mix them.

## Conflict Mode

Open a conflict when two or more sources make incompatible claims about:

- current architecture
- operational procedures
- dependency versions
- deployment state
- ownership
- roadmap status
- implementation state

Record the conflict in `docs/catalog/CONFLICTS.md` using this format:

```md
## CONFLICT-YYYYMMDD-NNN - Short conflict title

Estado: open
Detectado: YYYY-MM-DD
Detectado en sesion: [[docs/catalog/PROCESSING_RUNS.md#yyyy-mm-dd-hhmm-processing-run]]
Area: backend | frontend | infra | product | docs | architecture | operations | unknown
Severidad documental: low | medium | high

Descripcion:
...

Fuente A:
- Documento: [[docs/archive/YYYY/document-a.md]]
- Afirmacion: ...

Fuente B:
- Documento: [[docs/archive/YYYY/document-b.md]]
- Afirmacion: ...

Impacto:
...

Decision temporal aplicada:
...

Accion requerida:
...
```

Apply a conservative temporary decision. Keep uncertain claims out of `README.md`.

## Open Question Mode

Open a question when processing reveals a gap, missing evidence, or unresolved decision.

Record the question in `docs/catalog/OPEN_QUESTIONS.md` using this format:

```md
## QUESTION-YYYYMMDD-NNN - Short question title

Estado: open
Detectado: YYYY-MM-DD
Detectado en sesion: [[docs/catalog/PROCESSING_RUNS.md#yyyy-mm-dd-hhmm-processing-run]]
Area: backend | frontend | infra | product | docs | architecture | operations | unknown
Prioridad: low | medium | high

Pregunta:
...

Contexto:
...

Fuente:
- [[docs/archive/YYYY/document-source.md]]

Impacto:
...

Accion requerida:
...
```

Questions do not block processing.

## Resolution Mode

Use resolution mode only after the user supplies answers or chooses a temporary policy.

Execute this sequence:

1. Read active items from `CONFLICTS.md` and `OPEN_QUESTIONS.md`.
2. Match the user input to exact IDs.
3. Update the relevant catalog files.
4. Append resolution details with date and source.
5. Change state to `resolved`.
6. Move the item under `## Resolved`.
7. Register the action in `PROCESSING_RUNS.md`.

Do not delete resolved items. Preserve traceability.
