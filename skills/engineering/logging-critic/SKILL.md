---
name: logging-critic
description: >
  Audita si un log NDJSON es comprensible sin contexto previo: header, variables, reasons,
  esperado-vs-real, redundancia y niveles. Usar cuando se pregunte qué le falta al logging, si se
  entiende o si está inflado, incluso sin análisis previo. No usar para explicar una corrida ni
  para implementar las mejoras.
license: MIT
compatibility: >
  Requiere acceso de lectura a los archivos de log y Python 3.11+ para el auditor. Opera sobre el
  formato NDJSON definido en agent-friendly-logging. El auditor importa el parser compartido
  aflog.py de esa skill hermana, que debe estar presente en el repo.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); audit_log.py (importando el parser compartido aflog.py) probado sobre example-log.ndjson (0 errores, exit 0) y sobre un log degradado (exit 1: detecta decision sin reason, result sin expected/actual, variable no definida y corrida sin run_end)."
---

## Contexto

Esta skill es el rol **crítico** de `agent-friendly-logging`. No explica qué pasó (eso es el
analista): juzga si el **log mismo** permite entender qué pasó. Mira el log con los ojos de un
agente que nunca vio el sistema y pregunta: *¿puedo responder las preguntas clave con solo este
archivo?* Lo que falte, sobre o ambigüe, se vuelve una sugerencia concreta.

Tus señales de entrada incluyen las **dificultades que toparon otros roles**: si el analista no
pudo explicar un fallo, el destilador no pudo destilar un período, el fidelizador halló algo no
verificable, o el filósofo no pudo confirmar una hipótesis por falta de datos, eso apunta a una
deficiencia del logging que el crítico debe nombrar (variable ambigua, decisión sin causa, falta
de métrica o correlación, ruido, evento importante no registrado).

Lee primero `../agent-friendly-logging/references/log-format-spec.md` — su §7 "checklist de
agent-friendly" es la vara contra la que criticas.

## Pasos

1. **Correr el auditor mecánico.** `scripts/audit_log.py` detecta los gaps objetivos: header
   ausente o incompleto, variables usadas en eventos pero no definidas en el header, decisiones
   sin `reason`, `result` sin `expected`/`actual`, eventos sin `run_id`, header repetido por
   evento. Empieza por aquí: es barato y elimina lo evidente.
2. **Criticar lo que la máquina no ve (a juicio).** Sobre lo que el auditor no puede juzgar:
   - **Mensajes opacos:** `msg` que solo tiene sentido con el código fuente a la vista.
   - **Variables ambiguas:** definidas pero con significado/unidad confuso o nombres colisionantes.
   - **Decisiones con `reason` vacío:** "regla de negocio" no explica; falta la condición concreta.
   - **Redundancia:** eventos que repiten información ya implícita, o varios eventos para un único
     cambio atómico.
   - **Nivel mal usado:** `error` para algo esperado, `info` para algo crítico.
   - **Detalle sin valor:** trazas técnicas que no ayudan a responder ninguna pregunta del §7.
3. **Confrontar contra el checklist §7.** Para cada una de las 8 preguntas, marca si el log la
   responde con el archivo solo. Cada "no" es una sugerencia.
4. **Clasificar cada hallazgo** como *agregar* (falta info), *quitar* (redundante/sin valor) o
   *aclarar* (ambiguo), con la acción concreta. No decides cuáles se aplican — eso es el curador.
5. **Entregar al curador** la lista priorizada de sugerencias.

## Gotchas

- **Pedir más sin pedir menos.** Un buen crítico también detecta lo que sobra. Solo agregar lleva
  al log inflado que el curador tendrá que podar. Equilibra: gaps *y* redundancias.
- **Criticar el contenido en vez del log.** No es tu trabajo decir que la decisión del sistema
  fue mala; es decir si el log **explica** esa decisión. Mantente en la comprensibilidad.
- **Sugerencias vagas.** "Mejorar el logging" es inútil. "Agregar `reason` con `stock_level` y
  `order_qty` en el evento `decision` del componente inventory" es accionable.
- **Confundir falta de evento con falta de campo.** Distingue "este evento no existe y debería"
  de "este evento existe pero le falta un campo": la corrección es distinta.
- **Tratar el auditor como suficiente.** El script ve gaps estructurales, no ambigüedad
  semántica. Siempre complementa con juicio (paso 2).

## Output esperado

```markdown
# Crítica del log — {system}

## Auditor mecánico (scripts/audit_log.py)
- header: OK | variables sin definir: [order_qty] | decisiones sin reason: 2 | result sin expected: 1

## Hallazgos (a juicio)
| # | tipo    | dónde                         | problema                                   | acción sugerida |
|---|---------|-------------------------------|--------------------------------------------|-----------------|
| 1 | agregar | inventory / decision          | decisión sin reason                        | añadir reason="stock_level vs order_qty" |
| 2 | aclarar | header.variables.order_qty    | usada en eventos, no definida              | definir meaning+unit+range |
| 3 | quitar  | validator / 3 eventos `phase` | redundantes para una transición atómica    | colapsar en un state_change |

## Checklist §7 (responde el archivo solo?)
1 sistema/propósito ✅ · 2 scope ✅ · 3 run_id ✅ · 4 variables ⚠(order_qty) ·
5 estados ✅ · 6 decisiones+porqué ❌ · 7 esperado/real ⚠ · 8 anomalía+qué falta ✅

## Prioridad sugerida (para el curador)
1. #1 (bloquea responder "por qué decidió")  2. #2  3. #3
```

## Scripts disponibles

- **`scripts/audit_log.py`** — Audita un log NDJSON y reporta gaps semánticos estructurales.
  Ejecutar como primer paso de toda crítica. Emite JSON a stdout (parseable), diagnósticos a
  stderr; código de salida 0 si no hay gaps, 1 si los hay.

```bash
python scripts/audit_log.py --help
python scripts/audit_log.py path/al/log.ndjson
```

## Referencias

- Leer `../agent-friendly-logging/references/log-format-spec.md` (§7) como la vara de evaluación.
