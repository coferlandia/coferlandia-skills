# Log Format Spec — Logging orientado a agentes

> **Fuente de verdad única del formato.** Las skills `logging-designer`, `logging-instrumenter`,
> `logging-analyst`, `logging-critic` y `logging-curator` enlazan a este archivo en vez de
> redefinir el formato. Si el formato cambia, cambia **aquí** y solo aquí.

Este documento define la estructura concreta de un log *agent-friendly*: un log técnico
convencional (timestamp, nivel, componente, mensaje, correlación, excepciones, rotación) que
**además** incluye el contexto semántico para que un agente que nunca vio el sistema pueda leer
el archivo y reconstruir qué pasó y por qué.

---

## 1. Formato canónico: NDJSON (JSON Lines)

Un segmento de log es un archivo **NDJSON**: una línea = un registro JSON. Esto es agnóstico del
lenguaje (cualquier runtime puede emitir JSON) y es directamente parseable por los scripts de la
suite. Una renderización legible para humanos se define en §6, pero la **fuente de verdad es el
NDJSON**.

Cada registro tiene un campo `rec` que lo clasifica:

| `rec` | Cuántos por archivo | Qué es |
|-------|---------------------|--------|
| `header` | Exactamente 1, **primera línea** | Contexto autoexplicativo del segmento |
| `event` | N | Un evento de la ejecución |

El sistema instrumentado **solo emite estos dos**. Los agentes (analista, crítico) **nunca
escriben en el log del sistema**: producen artefactos separados (§5).

---

## 2. Registro `header` — la apertura explicativa

Se emite **una sola vez** cuando arranca una corrida o cuando rota el archivo (nueva apertura).
**No se repite por evento.** Gracias a él, cada segmento es razonablemente autocontenido.

Responde, para un agente sin contexto previo: *¿qué sistema es? ¿para qué sirve? ¿qué parte
observo? ¿qué variables hay y qué significan? ¿cómo se relacionan los eventos de una corrida?*

```json
{
  "rec": "header",
  "ts": "2026-06-11T14:03:21.512Z",
  "schema_version": "1.0",
  "system": "order-reservation-worker",
  "purpose": "Reserva inventario para órdenes de compra entrantes",
  "objective": "Confirmar o rechazar cada orden dejando el inventario consistente",
  "scope": "Worker de reserva (NO incluye cobro ni envío)",
  "run_id": "run-8f2a1c",
  "correlation": { "primary": "run_id", "secondary": ["order_id"] },
  "depth": "explanatory",
  "levels": ["debug", "info", "warn", "error", "critical"],
  "states": ["received", "validating", "reserving", "confirmed", "rejected"],
  "variables": {
    "stock_level": { "meaning": "Unidades disponibles del SKU", "unit": "unidades", "range": "0..N" },
    "order_qty":   { "meaning": "Unidades solicitadas en la orden", "unit": "unidades", "range": "1..N" },
    "decision":    { "meaning": "Resultado de evaluar la orden", "values": ["reserve", "backorder", "reject"] }
  },
  "rotation": "size=50MB OR time=1h",
  "notes": "Una corrida = un order_id. Eventos ordenables por seq."
}
```

### Campos del header

| Campo | Obligatorio | Significado |
|-------|-------------|-------------|
| `rec` | sí | Siempre `"header"` |
| `ts` | sí | Apertura del segmento (ISO-8601, UTC) |
| `schema_version` | sí | Versión de este spec que respeta el archivo |
| `system` | sí | Identificador del sistema/proceso que genera el log |
| `purpose` | sí | Para qué existe el sistema (1 frase) |
| `objective` | sí | Objetivo funcional de la ejecución (qué cuenta como éxito) |
| `scope` | sí | Qué parte del sistema se observa, y qué queda **fuera** |
| `run_id` | sí* | Id de correlación de la corrida (\*omitible si el archivo agrupa muchas corridas; entonces cada evento lleva su `run_id`) |
| `correlation` | sí | `primary` = campo que une los eventos de una corrida; `secondary` = otros ids útiles; opcional `parent_run_id` para sub-corridas (§3.5) |
| `depth` | sí | Nivel de detalle activo: `operational` / `explanatory` / `diagnostic` / `deep` (§4) |
| `levels` | sí | Niveles posibles en orden de severidad |
| `states` | reco. | Estados por los que puede pasar el sistema (vocabulario cerrado) |
| `variables` | sí | Diccionario `nombre → {meaning, unit?, range?, values?}`. **Define cada variable que aparece en los eventos.** |
| `rotation` | sí | Política de rotación por tamaño y/o tiempo |
| `notes` | opc. | Aclaraciones de relación entre eventos |

**Regla de oro del header:** toda variable o estado que aparezca en un `event` debe estar
definido aquí. Si un agente ve `decision: "backorder"` en un evento, debe poder volver al header
y leer qué significa `decision` y qué valores admite.

---

## 3. Registro `event` — la ejecución

### 3.1 Campos técnicos (log convencional) — siempre presentes

| Campo | Significado |
|-------|-------------|
| `rec` | Siempre `"event"` |
| `ts` | Timestamp ISO-8601 UTC con milisegundos |
| `level` | `debug` / `info` / `warn` / `error` / `critical` |
| `component` | Módulo/origen que emite el evento |
| `run_id` | Id de correlación (une los eventos de una corrida) |
| `seq` | Entero monótono dentro de la corrida (ordena eventos aunque coincidan timestamps) |
| `msg` | Mensaje del evento, redactado para que un agente lo entienda sin el código fuente |

### 3.2 Campos semánticos (agent-friendly) — presentes cuando aplican

El campo `event_type` usa un **vocabulario cerrado** que permite a un agente reconstruir la
corrida sin adivinar:

| `event_type` | Cuándo | Campos semánticos esperados |
|--------------|--------|------------------------------|
| `run_start` | Inicio de la corrida | `objective`, `inputs` (datos de entrada relevantes), `state` inicial |
| `input` | Llega un dato de entrada relevante | `data` |
| `phase` | Entra a una etapa del proceso | `state` |
| `decision` | El sistema elige entre opciones | `decision`, `reason` (la condición que la provocó), `alternatives?` |
| `state_change` | Cambia de estado | `from_state`, `to_state`, `reason` |
| `external_call` | Llama a un servicio externo | `external` = `{service, op, status, latency_ms}` |
| `retry` | Reintento de una operación | `attempt`, `max_attempts`, `reason` |
| `recovery` | Mecanismo de recuperación actuó | `reason`, `outcome` |
| `warning` | Anomalía no fatal | `reason`, `data?` |
| `anomaly` | Algo fuera de rango esperado | `expected`, `actual`, `data?` |
| `result` | Resultado de una operación/corrida | `expected`, `actual` |
| `run_end` | Fin de la corrida | `state` final, `cause` (motivo de finalización), `result` |

Campo de excepción (en cualquier evento de error):
```json
"exception": { "type": "TimeoutError", "message": "...", "stack": "..." }
```

### 3.3 Principio rector de los eventos

**Registrar no solo QUÉ ocurrió, sino POR QUÉ — cuando esa causa es conocida por el sistema.**
Un `decision` o `state_change` sin `reason` obliga al agente a inventar la causa. Si el sistema
sabe por qué decidió, el `reason` va en el evento. Si no la sabe, se omite (no se inventa).

### 3.4 Ejemplos de eventos

```json
{"rec":"event","ts":"2026-06-11T14:03:21.610Z","level":"info","component":"intake","run_id":"run-8f2a1c","seq":1,"event_type":"run_start","msg":"Inicia reserva para orden","objective":"Reservar 3 u. del SKU-77","inputs":{"order_id":"ord-551","sku":"SKU-77","order_qty":3},"state":"received"}
{"rec":"event","ts":"2026-06-11T14:03:21.640Z","level":"info","component":"validator","run_id":"run-8f2a1c","seq":2,"event_type":"state_change","msg":"Orden validada","from_state":"received","to_state":"validating","reason":"payload completo y SKU existe"}
{"rec":"event","ts":"2026-06-11T14:03:21.700Z","level":"info","component":"inventory","run_id":"run-8f2a1c","seq":3,"event_type":"decision","msg":"Stock suficiente, se reserva","decision":"reserve","reason":"stock_level(5) >= order_qty(3)","data":{"stock_level":5,"order_qty":3}}
{"rec":"event","ts":"2026-06-11T14:03:21.760Z","level":"info","component":"inventory","run_id":"run-8f2a1c","seq":4,"event_type":"run_end","msg":"Orden confirmada","state":"confirmed","cause":"reserva exitosa","result":{"expected":"confirmed","actual":"confirmed"}}
```

### 3.5 Correlación anidada y distribuida (opcional)

Para sistemas simples basta `run_id` + ids secundarios. Cuando una corrida dispara
**sub-operaciones** o cruza **varios servicios**, hay dos campos opcionales:

- **`parent_run_id`** — vincula una sub-corrida con la corrida padre que la originó (va en los
  eventos de la sub-corrida o en `header.correlation.parent_run_id`). Permite reconstruir el árbol
  padre → hijos.
- **`op_id`** — identifica una sub-operación distinguible dentro de una misma corrida, cuando un
  `run_id` agrupa varias operaciones que conviene separar sin abrir corridas nuevas.

**Traza distribuida:** dos convenciones válidas — (a) todos los servicios comparten el mismo
`run_id` (que actúa como *trace id*) y se distinguen por `component`, abriendo cada uno su `header`
con su `scope`; o (b) cada servicio usa su `run_id` local y enlaza al padre con `parent_run_id`.

Son **opcionales**: ausentes, todo se comporta como una corrida plana. Presentes, los renderers
(`render_log.py`, dashboard) muestran la relación padre → sub-corridas y `reconstruct_run.py`
expone `parent_run_id` y `children`.

```json
{"rec":"event","ts":"...","level":"info","component":"sub","run_id":"child-1","parent_run_id":"parent-1","seq":1,"event_type":"run_start","msg":"Inicia sub-operación","state":"a"}
```

---

## 4. Profundidad progresiva (`depth`)

El header declara el nivel activo. Más detalle = más costo; se sube **a propósito**, no por
defecto.

| Nivel | `depth` | Qué registra |
|-------|---------|--------------|
| Operativo | `operational` | `run_start`, `run_end`, `result`, errores. Confirma inicio/progreso/fin y fallos. |
| Explicativo | `explanatory` | + `decision`, `reason`, `state_change`, `phase`. **Default recomendado.** |
| Diagnóstico | `diagnostic` | + snapshots de `inputs`/variables, detalle de `external_call`, `retry`/`recovery`. |
| Profundo | `deep` | + trazas finas de **un** componente específico, **acotadas en tiempo** y revertidas después. |

El analista puede **recomendar** subir el nivel temporalmente cuando una anomalía no se explica
con la información disponible. Subir a `deep` siempre es temporal y localizado.

---

## 5. Procedencia: hechos vs interpretaciones vs hipótesis

Distinguir el origen de cada afirmación es obligatorio. Tres tipos:

| `kind` | Qué es | Quién lo produce |
|--------|--------|------------------|
| `fact` | Registrado directamente en el log (citable por `ts`+`seq`) | El sistema |
| `interpretation` | Lectura que un agente hace de los hechos | Analista / crítico |
| `hypothesis` | Explicación aún no confirmada | Analista |

**El sistema solo emite `fact`.** Los agentes nunca escriben en el log del sistema; escriben en
artefactos separados (informe de análisis, base de conocimiento §5.1), y **cada afirmación** allí
lleva su `kind`. Una hipótesis nunca se presenta como hecho.

### 5.1 Base de conocimiento acumulado

Vive fuera del log del sistema (p. ej. `logging-knowledge/<system>.md` o `.ndjson`). Acumula,
con `kind` y fecha, lo aprendido entre corridas:

- comportamientos normales y rangos habituales (p. ej. `stock_level` típico 2..50);
- patrones recurrentes;
- anomalías conocidas y problemas ya investigados;
- hipótesis confirmadas o descartadas (con su evidencia);
- variables que demostraron ser útiles, e información redundante candidata a eliminar.

Entrada NDJSON sugerida:
```json
{"kind":"interpretation","date":"2026-06-11","system":"order-reservation-worker","topic":"rango_normal","statement":"stock_level normal observado entre 2 y 50","evidence":["run-8f2a1c#3","run-77b2#3"]}
```

---

## 6. Proyección humana canónica (derivada)

El NDJSON es para máquinas; los humanos necesitan leerlo a ojo. La **proyección humana** es una
vista legible **derivada** del NDJSON — nunca una segunda fuente de verdad. Nadie la edita a mano:
se **genera** desde el log. Si difiere del NDJSON, el NDJSON manda y la vista se regenera.

El **formato canónico de la vista es Markdown** (tablas, se renderiza en chat, GitHub, docs,
reportes y dashboards). Esta sección define el **layout** —qué secciones, qué columnas, qué
marcadores—; cualquier renderer (CLI Markdown, dashboard HTML, etc.) debe producir este mismo
layout. El layout vive **solo aquí**.

### 6.1 Marcadores deterministas

Derivados del log, sin criterio humano:

| Marcador | Condición |
|----------|-----------|
| `✅` | Corrida con `expected == actual` (o sin mismatch) |
| `❌` | Corrida con `expected != actual` (mismatch de resultado) |
| `⚠` | Evento con `level=warn` o `event_type` ∈ {`warning`,`anomaly`} |
| `🔴` | Evento con `level` ∈ {`error`,`critical`} |

### 6.2 Vista *digest* (una ficha por corrida) — default

Para lectura rápida. Una ficha por `run_id`, en este orden:

1. **Encabezado:** `### {system} · {run_id} · depth={depth}  {✅\|❌} {etiqueta de desenlace}`
2. **Línea de contexto:** `**Objetivo:** {objective} · **Scope:** {scope}`
3. **Tabla de variables** (de `header.variables`): columnas `variable | significado | unidad | valores`
4. **Estados:** `**Estados:** s0 → s1 → s2` (del `state_path`)
5. **Tabla de decisiones:** columnas `seq | decisión | porqué (reason)`. Si falta `reason`, **celda vacía** (el gap se muestra, no se rellena).
6. **Líneas de alerta:** una por evento `⚠`/`🔴`, con `seq`, descripción y datos clave.
7. **Desenlace:** `**Desenlace:** esperado \`{expected}\` / real \`{actual}\` — causa: {cause}`

```markdown
### order-reservation-worker · run-9b41dd · depth=explanatory  ❌ no confirmada
**Objetivo:** Reservar 8 u. del SKU-77 · **Scope:** Worker de reserva (no cobro/envío)

| variable | significado | unidad | valores |
|----------|-------------|--------|---------|
| stock_level | Unidades disponibles del SKU | unidades | 0..N |
| order_qty | Unidades solicitadas en la orden | unidades | 1..N |
| decision | Resultado de evaluar la orden | — | reserve · backorder · reject |

**Estados:** received → validating → backordered

| seq | decisión | porqué (reason) |
|-----|----------|-----------------|
| 4 | backorder | stock_level(2) < order_qty(8) |

⚠ seq 3 · external_call inventory-db/get_stock · latency=1820ms

**Desenlace:** esperado `confirmed` / real `backordered` — causa: stock insuficiente al momento de reservar
```

### 6.3 Vista *timeline* (tabla evento-a-evento)

Para el detalle. Una fila por evento, ordenadas por `seq`/`ts`. Columnas fijas:

`marcador | seq | hora | nivel | componente | event_type | mensaje | datos clave`

donde **datos clave** depende del `event_type` (proyección compacta de los campos semánticos):

| event_type | datos clave |
|------------|-------------|
| `decision` | `decision` + `reason` |
| `state_change` | `from_state → to_state` (+ `reason`) |
| `external_call` | `service/op status latency_ms` |
| `retry`/`recovery` | `attempt/max_attempts` + `reason` |
| `anomaly` | `expected` vs `actual` |
| `result`/`run_end` | `expected` vs `actual` + `cause` |

La **hora** es la porción de tiempo de `ts` (`HH:MM:SS.mmm`); la fecha completa ya está en la
ficha de header, no se repite por fila.

```markdown
| | seq | hora | nivel | componente | tipo | mensaje | datos |
|-|-----|------|-------|------------|------|---------|-------|
| | 1 | 14:09:02.050 | info | intake | run_start | Inicia reserva para orden | obj: Reservar 8 u. |
| | 2 | 14:09:02.090 | info | validator | state_change | Orden validada | received → validating |
| ⚠ | 3 | 14:09:02.300 | warn | inventory | external_call | Consulta de stock lenta | inventory-db/get_stock ok 1820ms |
| | 4 | 14:09:02.320 | info | inventory | decision | Stock insuficiente, backorder | backorder ← stock_level(2) < order_qty(8) |
| ❌ | 5 | 14:09:02.340 | info | inventory | run_end | Orden en backorder | esperado confirmed / real backordered |
```

### 6.4 Renderers

- **CLI Markdown — `scripts/render_log.py`** (de la skill `agent-friendly-logging`): NDJSON →
  Markdown. Vistas `digest` (default), `timeline`, `both`. Sin dependencias. Úsalo para producir
  informes, comentarios de PR, o el cuerpo de un análisis.
- **Dashboard en vivo — `assets/dashboard.html`** (§6.5): mismo layout, en una página.

### 6.5 Dashboard en vivo (opcional, recomendado)

Patrón recomendado —no obligatorio— para que un sistema agent-log-friendly muestre su log a un
humano **en vivo**: un dashboard de **un solo archivo HTML, sin build ni dependencias**, que
renderiza la proyección canónica (§6.2/§6.3) y se actualiza solo.

Dos fuentes de datos, ambas agnósticas del stack del sistema:

- **URL (vista en vivo):** el sistema expone el archivo NDJSON (o un endpoint de *tail*) en una
  URL; el dashboard hace *polling* cada N segundos y re-renderiza. Es la "vista del log en vivo".
- **Drag-and-drop (snapshot):** se arrastra un `.ndjson` al dashboard para inspección offline,
  sin infraestructura.

Requisitos para que el dashboard siga siendo una proyección y no una segunda verdad:

- **Solo lee** el NDJSON; nunca lo modifica ni persiste una versión propia.
- Aplica los marcadores de §6.1 y las vistas de §6.2/§6.3 sin agregar interpretación.
- Si un campo falta (p. ej. `reason`), lo muestra vacío — el gap es información.

El instrumentador puede entregar `assets/dashboard.html` junto al sistema y apuntarlo a la URL
del log. Por ser opcional, su ausencia no degrada el log: el NDJSON sigue siendo legible con
`render_log.py`.

---

## 7. Checklist de "¿es agent-friendly?"

Un agente sin contexto debería poder responder, leyendo **solo el archivo**:

1. ¿De qué sistema se trata y para qué sirve? → `header.system/purpose/objective`
2. ¿Qué parte se observa? → `header.scope`
3. ¿Qué ejecución es? → `header.run_id` / `event.run_id`
4. ¿Qué variables importan y qué significan? → `header.variables`
5. ¿Qué estados atravesó? → eventos `state_change` + `header.states`
6. ¿Qué decisiones tomó y por qué? → eventos `decision` con `reason`
7. ¿Cuál era el resultado esperado vs el real? → `expected`/`actual`
8. ¿Dónde hubo anomalía y qué falta para entenderla? → `anomaly` + recomendación de `depth`

Si alguna no se puede responder con el archivo solo, el log todavía no es agent-friendly.
