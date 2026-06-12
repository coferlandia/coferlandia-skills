---
name: coferlandia-skill-testing
description: >
  Audita Agent Skills y repositorios de skills contra agentskills.io y las convenciones de
  Coferlandia. Usar al crear, modificar, revisar o publicar skills; detecta metadata no canónica,
  drift del índice, links rotos, scripts sin contrato, secretos y falta de casos conductuales.
license: MIT
compatibility: >
  Requiere Python 3.11+ y acceso de lectura al repositorio. No instala dependencias.
metadata:
  author: coferlandia
  version: "1.0"
  category: meta
  status: active
  tested: "2026-06-12 - 6 unit tests; auditoría 14/14; discovery por junction en Codex, Claude, Gemini y Copilot; invocación explícita confirmada en Codex"
---

## Contexto

La especificación canónica es [agentskills.io](https://agentskills.io/specification). Esta skill
no la reescribe: automatiza ese contrato y agrega los invariantes locales de Coferlandia.

El runner produce JSON estable para que un agente pueda corregir hallazgos por código. No ejecuta
scripts arbitrarios durante la auditoría; inspecciona su contrato y sintaxis de forma estática.

## Pasos

1. Ejecuta la suite sobre la raíz del repositorio:

   ```bash
   python skills/meta/coferlandia-skill-testing/scripts/test_skills.py . --pretty
   ```

2. Corrige primero los issues con `severity=error`.
3. Para cada skill `active`, mantiene `tests/cases.json` con prompts `positive` y `negative`.
4. Repite el runner hasta obtener código de salida 0.
5. Ejecuta los unit tests del runner antes de modificar sus criterios:

   ```bash
   python -m unittest skills/meta/coferlandia-skill-testing/tests/test_test_skills.py -v
   ```

6. Completa el smoke test en los clientes destino cuando cambie triggering o compatibilidad.

## Contrato conductual

`tests/cases.json` registra ejemplos mínimos de descubrimiento:

```json
{
  "positive": ["Prompt que debería activar la skill"],
  "negative": ["Prompt cercano que no debería activarla"]
}
```

Estos casos son evidencia versionada y reusable. La invocación real en Codex, Claude, Gemini o
Copilot sigue siendo un smoke test de integración y debe registrarse en `metadata.tested`.

## Códigos principales

| Prefijo | Significado |
|---|---|
| `frontmatter.*` | Contrato agentskills.io |
| `metadata.*` | Convenciones locales de categoría y estado |
| `behavior.*` | Evidencia de triggering |
| `index.*` | Sincronización con `skills/INDEX.md` |
| `links.*` | Referencias locales |
| `script.*` | Contrato y sintaxis de scripts |
| `security.*` | Credenciales o material sensible |

## Gotchas

- **No conviertas preferencias editoriales en errores.** Solo automatiza invariantes objetivos;
  el juicio sobre claridad o utilidad pertenece a la auditoría humana/agéntica.
- **No ejecutes scripts desconocidos para probar `--help`.** Una auditoría debe ser segura sobre
  repositorios no confiables; usa análisis estático y deja la ejecución para un sandbox explícito.
- **Un `cases.json` no demuestra por sí solo buen triggering.** Conserva los prompts como contrato,
  pero valida al menos una invocación real antes de marcar la skill como probada.
- **No dupliques agentskills.io.** Si cambia el estándar, actualiza el runner y enlaza la fuente;
  no copies la especificación completa a documentos locales.

## Output esperado

```json
{
  "ok": true,
  "scope": "repository",
  "skills": 14,
  "errors": 0,
  "warnings": 0,
  "issues": []
}
```

## Scripts

- `scripts/test_skills.py`: auditoría estructural, semántica y de repositorio.
- `tests/test_test_skills.py`: regresiones del contrato del runner.
