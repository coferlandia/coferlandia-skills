# Summary Format Spec — Destilación de logs agent-friendly

> **Fuente de verdad única del formato de resúmenes.** Las skills `logging-distiller`,
> `logging-fidelity-checker` y `logging-philosopher` enlazan a este archivo en vez de redefinir el
> formato. Es la contraparte temporal de `log-format-spec.md`: aquel define el log crudo (una
> ejecución); éste define cómo se compacta un **período** (horas, días, semanas, meses) de forma
> factual, completa, compacta y **trazable**.

El log crudo NDJSON no escala: nadie analiza un mes leyendo millones de líneas. La **destilación**
produce resúmenes de período que preservan todos los hechos significativos y, sobre todo, **las
referencias para volver a la evidencia**. Sin trazabilidad, la destilación jerárquica acumula
error nivel a nivel y el resumen mensual se vuelve ficción.

---

## 1. Anatomía de un resumen de período

Un resumen es un **archivo Markdown** con dos partes:

1. Un **bloque meta legible por máquina** (JSON en un fence ` ```json-meta `), al inicio.
2. El **cuerpo en prosa Markdown** para humanos y para el Filósofo.

El bloque meta permite la verificación mecánica (cobertura, conteos, referencias) sin parsear la
prosa. El cuerpo preserva el panorama completo de forma legible. Ambos describen lo mismo; ante
discrepancia, manda lo que respaldan las **fuentes**, no el resumen.

### 1.1 Bloque meta (obligatorio, primero en el archivo)

````markdown
# Resumen {level} — {system} — {label}

```json-meta
{
  "type": "period-summary",
  "schema_version": "1.0",
  "system": "order-reservation-worker",
  "level": "hourly",
  "period": {"start": "2026-06-11T14:00:00Z", "end": "2026-06-11T15:00:00Z", "label": "2026-06-11 14:00–15:00 UTC"},
  "sources": [
    {"kind": "log", "ref": "logs/2026-06-11-14.ndjson", "period": {"start": "2026-06-11T14:00:00Z", "end": "2026-06-11T15:00:00Z"}}
  ],
  "coverage": {"complete": true, "gaps": []},
  "counts": {"runs": 120, "by_event_type": {"decision": 240, "run_end": 120}, "by_level": {"info": 1180, "warn": 14, "error": 3}, "errors": 3, "anomalies": 5},
  "metrics": {"latency_ms_inventory_db": {"p50": 120, "p95": 800, "max": 1820}},
  "produced_by": "logging-distiller",
  "distilled_at": "2026-06-11T15:02:00Z"
}
```
````

Campos del meta:

| Campo | Obligatorio | Significado |
|-------|-------------|-------------|
| `type` | sí | Siempre `"period-summary"` |
| `schema_version` | sí | Versión de este spec |
| `system` | sí | Sistema resumido (coincide con `header.system` del log) |
| `level` | sí | `hourly` / `daily` / `weekly` / `monthly` / `custom` |
| `period` | sí | `start`/`end` (ISO-8601 UTC) y `label` legible del intervalo cubierto |
| `sources` | sí | Lista del material usado: `kind` (`log` o `summary`), `ref` (ruta), `period`, y para `summary` su `verdict` |
| `coverage` | sí | `complete` (bool) y `gaps` = lista de `{start,end,reason}` sin datos |
| `counts` | sí | Conteos factuales: `runs`, `by_event_type`, `by_level`, `errors`, `anomalies`, … |
| `metrics` | reco. | Rangos/percentiles de variables relevantes (`p50`/`p95`/`max`/`min`) |
| `produced_by` | sí | `logging-distiller` (o el agente/modelo que destiló) |
| `distilled_at` | sí | Cuándo se produjo |

**Regla de oro:** `coverage.complete` solo puede ser `true` si `gaps` está vacío **y** la unión de
los `period` de las `sources` cubre todo `period` sin huecos. Nunca presentar un período como
completo si falta material — eso es lo que verifica el Fidelizador.

### 1.2 Cuerpo en prosa (secciones canónicas, en este orden)

1. **Período y cobertura** — intervalo cubierto; si `coverage.complete=false`, listar los `gaps`
   (cuándo y por qué no hay datos). Esto va primero: el lector debe saber qué NO se cubrió.
2. **Panorama general** — 2–4 frases factuales del comportamiento del período. Sin opinión.
3. **Cronología** — hitos ordenados temporalmente (no cada evento; los significativos).
4. **Eventos agrupados con conteos** — tabla `clase de evento | cantidad | notas | ref`. Agrupar
   repetidos **conservando la cantidad**.
5. **Estados y transiciones** — estados atravesados, frecuencias, transiciones notables.
6. **Decisiones** — distribución de decisiones y las condiciones típicas (`reason`), con `ref`.
7. **Errores, advertencias y excepciones** — cada clase con su conteo y `ref`. **Los eventos
   excepcionales NO se ocultan dentro de una agrupación**: se listan aparte aunque sean únicos.
8. **Métricas, valores y variaciones** — rangos, percentiles, desvíos respecto de lo habitual.
9. **Resultados** — exitosos / fallidos / incompletos, con conteos.
10. **Interrupciones / períodos sin información** — además de los `gaps`, caídas o silencios.
11. **Fuentes y trazabilidad** — las `sources` usadas y cómo se referencia la evidencia (§3).

El Destilador llena estas secciones **solo con hechos**. No diagnostica, no opina, no recomienda,
no formula hipótesis (eso es del Filósofo, §4).

---

## 2. Destilación jerárquica

El Destilador puede partir de logs crudos o de resúmenes menores **ya aprobados** por el
Fidelizador:

```
logs NDJSON      → resumen  hourly
resúmenes hourly → resumen  daily
resúmenes daily  → resumen  weekly
resúmenes weekly → resumen  monthly
```

Reglas de la jerarquía:

- Un resumen **solo** debe usar como `sources` logs crudos o resúmenes con `verdict: aprobado`
  (o `aprobado_con_observaciones`). Usar un resumen no verificado propaga errores hacia arriba.
- Al destilar desde resúmenes, dejar constancia en `sources` (con su `ref` y `verdict`) y **sumar
  sus conteos** — los `counts` de un resumen superior deben ser consistentes con la suma de los
  `counts` de sus fuentes.
- Si una sub-fuente tiene `coverage.complete=false`, el período superior **hereda el hueco**:
  no puede declararse completo.

---

## 3. Trazabilidad: la sintaxis `[ref: …]`

Todo hecho significativo conserva una referencia a su evidencia, con marcador inline canónico
`[ref: <token>]`. Tres formas de token:

| Token | Apunta a | Resoluble si… |
|-------|----------|---------------|
| `run-9b41dd#4` | evento concreto (`run_id`#`seq`) en un log fuente | alguna `source` de `kind:log` contiene ese run/seq |
| `2026-06-11-14.ndjson` | un segmento/archivo de log fuente | la ruta existe entre las `sources` |
| `hourly/2026-06-11-13#errores` | una sección de un resumen inferior | esa `source` `summary` existe y tiene esa sección |

El Fidelizador (y `check_summary.py`) verifican que estas referencias **resuelvan**. Un hecho sin
`[ref: …]` no es trazable: el Fidelizador lo marca como observación.

---

## 4. Procedencia a lo largo de la cadena

La disciplina de `log-format-spec.md` §5 (hecho / interpretación / hipótesis) se vuelve un
invariante de toda la cadena de destilación:

- **Destilador** → emite **solo hechos** (`fact`), con `[ref: …]`.
- **Fidelizador** → emite un **veredicto de fidelidad** (§5), no interpreta el sistema.
- **Filósofo** → separa explícitamente **hechos / inferencias / hipótesis / recomendaciones**, y
  cuando la evidencia es insuficiente dice **qué falta** y **qué observación** confirmaría o
  descartaría la hipótesis. No inventa explicaciones.

---

## 5. Veredicto de fidelidad (salida del Fidelizador)

El Fidelizador compara un resumen con sus fuentes y emite un archivo con bloque meta + prosa:

```json-meta
{
  "type": "fidelity-verdict",
  "schema_version": "1.0",
  "summary_ref": "summaries/hourly/2026-06-11-14.md",
  "verdict": "aprobado",
  "scope": {"method": "mixto", "coverage": "conteos 100% + muestreo 10% de eventos", "notes": ""},
  "findings": [],
  "checked_at": "2026-06-11T15:05:00Z"
}
```

`verdict` ∈ (mapea los cuatro resultados de la propuesta):

| `verdict` | Significado |
|-----------|-------------|
| `aprobado` | Representa fielmente sus fuentes |
| `aprobado_con_observaciones` | Fiel, con observaciones menores que no invalidan |
| `requiere_correccion` | Hay desviaciones; vuelve al Destilador con `findings` concretos |
| `no_verificable` | Faltan fuentes para verificar |

`scope.method` ∈ `completo` / `muestreo` / `mixto` — **siempre** declarar el alcance de la
verificación. `findings[].type` ∈ `omision` · `alteracion` · `conteo` · `cronologia` ·
`generalizacion` · `excepcion_oculta` · `inventado` · `opinion_como_hecho` · `cobertura` ·
`referencia`. Cada finding lleva `detail` y `where` (sección o `ref`).

**Solo los resúmenes con `aprobado` (o `aprobado_con_observaciones`) deben usarse como fuente** de
períodos mayores o de análisis del Filósofo.

---

## 6. Qué verifica `check_summary.py` (mecánico) vs el juicio del Fidelizador

`scripts/check_summary.py` (de `logging-fidelity-checker`) cubre lo objetivo, y el agente cubre lo
semántico:

| Mecánico (script) | A juicio (agente) |
|-------------------|-------------------|
| Bloque meta presente y con campos obligatorios | Omisiones de hechos relevantes |
| `coverage.complete` consistente con `gaps` y con el span de `sources` | Alteraciones de significado |
| Las `sources.ref` existen | Generalizaciones excesivas |
| `counts` recomputados desde NDJSON / suma de sub-resúmenes coinciden | Eventos excepcionales ocultos en agrupaciones |
| Tokens `[ref: …]` resuelven (cuando son verificables) | Opiniones presentadas como hechos |

El Fidelizador corre el script **primero** (barato, elimina lo evidente) y luego aplica juicio.
