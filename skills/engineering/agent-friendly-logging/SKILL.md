---
name: agent-friendly-logging
description: >
  Orquesta observabilidad semántica para agentes: header autoexplicativo, eventos NDJSON,
  correlación, vista humana, destilación, fidelidad y mejora continua mediante ocho roles. Usar
  cuando haya que diseñar, instrumentar, leer, resumir, verificar, criticar o evolucionar logs
  para que una IA reconstruya qué ocurrió y por qué, aunque el pedido diga solo "mejorar nuestros
  logs" o "entender esta corrida". No usar para configurar un agregador concreto como Datadog o
  ELK.
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repositorio del sistema a instrumentar y git. Los
  scripts de análisis usan Python 3.11+. El formato NDJSON es agnóstico del lenguaje del sistema.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0). Capa de log: aflog.py provee el parseo a render_log.py/reconstruct_run.py/audit_log.py; render_log.py rinde example-log.ndjson (digest/timeline); correlación anidada y dashboard.html (node --check) verificados. Capa de destilación: summary-format-spec.md definido; check_summary.py aprueba un resumen correcto (exit 0) y rechaza uno degradado (exit 1: cobertura, conteos, referencia)."
---

## Qué construye esta suite

Un **log agent-friendly** sigue siendo un log técnico convencional —fecha y hora, nivel
(debug/info/warn/error/critical), componente de origen, mensaje, id de correlación, excepciones,
política de rotación—, pero **añade el contexto que un agente necesita para comprender qué
observa sin conocer el sistema de antemano**. El objetivo no es producir *más* logs, sino logs
con **mayor capacidad explicativa**: que un agente pueda responder de qué sistema se trata, para
qué sirve, qué ejecución observa, qué variables importan y qué significan, qué estados atravesó,
qué decidió, por qué, qué resultado esperaba y cuál obtuvo, y dónde hubo una anomalía.

La suite **no reemplaza** las herramientas de logging/monitoreo existentes; las **complementa**
con contexto semántico y funcional, y aporta un ciclo agéntico para que el sistema explique su
propia ejecución y los agentes le enseñen progresivamente qué registrar.

## Los formatos — fuente de verdad única

Dos formatos canónicos, cada uno en **un solo lugar**:

> **`references/log-format-spec.md`** — el log crudo (una ejecución): header autoexplicativo +
> eventos NDJSON, niveles de profundidad, hecho/interpretación/hipótesis, vista humana, base de
> conocimiento. Léelo antes de diseñar, instrumentar, analizar o criticar. Ejemplo en
> `references/example-log.ndjson`.
>
> **`references/summary-format-spec.md`** — la destilación temporal (un período): resumen Markdown
> con bloque meta, jerarquía logs→hora→día→semana→mes, trazabilidad `[ref: …]` y veredicto de
> fidelidad. Léelo antes de destilar, fidelizar o analizar tendencias.

Las skills de roles enlazan a estos archivos; no redefinas los formatos en otro lado.

## Los ocho roles

Estos roles son **capacidades**, no necesariamente agentes separados: en sistemas pequeños los
ejecuta un mismo agente en secuencia; en sistemas complejos se distribuyen. El destilador y el
fidelizador corren bien con **modelos baratos** (método estricto); el filósofo conviene en
**modelos de alta capacidad**. Cada uno tiene su skill:

| Rol | Skill | Qué hace |
|-----|-------|----------|
| **Diseñador** | `logging-designer` | Estudia el sistema y define el **modelo de observación**: qué procesos, estados, decisiones y variables registrar. |
| **Instrumentador** | `logging-instrumenter` | Implementa o adapta el logging según el diseño, **sin cambiar el comportamiento funcional** del sistema. |
| **Analista** | `logging-analyst` | Lee logs crudos, reconstruye ejecuciones concretas, detecta anomalías y compara corridas (comprensión **operativa**). |
| **Destilador** | `logging-distiller` | Compacta un período (hora/día/semana/mes) en un resumen **factual, completo y trazable**; no interpreta. |
| **Fidelizador** | `logging-fidelity-checker` | Verifica que un resumen represente fielmente sus fuentes (fidelidad, cobertura, trazabilidad) y emite un veredicto. |
| **Filósofo** | `logging-philosopher` | Piensa en profundidad sobre resúmenes validados: causas, tendencias, riesgos, oportunidades (análisis **estratégico**). |
| **Crítico** | `logging-critic` | Evalúa si las dificultades de los demás roles vienen de **deficiencias del logging**: variables ambiguas, decisiones sin causa, falta de métricas/correlación, ruido. |
| **Curador** | `logging-curator` | Decide qué propuestas (del crítico y del filósofo) incorporar; evita tanto la falta de información como el crecimiento descontrolado. |

## Los dos ciclos

La suite combina dos lazos: el **ciclo de conocimiento** convierte logs en entendimiento; el
**ciclo de mejora** convierte ese entendimiento en mejor instrumentación.

```
Sistema → Logs → Analista → Destilador → Fidelizador → Filósofo → Crítico → Curador → Diseñador → Instrumentador → Sistema
                 └────────────── ciclo de conocimiento ─────────────┘   └──────────── ciclo de mejora ────────────┘
```

**Ciclo de conocimiento** (logs → entendimiento):
1. (el sistema corre) → genera logs por rolling
2. logging-analyst          → reconstruye ejecuciones concretas (y puede asistir al destilador)
3. logging-distiller        → compacta el período en un resumen factual y trazable
4. logging-fidelity-checker → verifica fidelidad; si falla, vuelve al destilador hasta aprobar
5. logging-philosopher      → piensa sobre los resúmenes aprobados: patrones, riesgos, hipótesis

**Ciclo de mejora** (entendimiento → mejor logging):
6. logging-critic   → ¿las dificultades vienen de deficiencias del logging?
7. logging-curator  → decide qué propuestas (crítico + filósofo) incorporar, sin inflar el log
8. logging-designer / logging-instrumenter → evolucionan el modelo y la instrumentación → nuevo ciclo

Regla esencial: **responsabilidades separadas.** El destilador conserva y compacta hechos; el
fidelizador verifica que no se hayan deformado; el filósofo interpreta; el crítico evalúa la
calidad de la observación; el curador decide qué cambios entran; diseñador e instrumentador
evolucionan el logging. Solo los resúmenes **aprobados** se usan como fuente de períodos mayores o
del análisis del filósofo.

## Cómo usar la suite

1. Identifica en qué punto de los dos ciclos está el usuario (diseñar, instrumentar, analizar un
   log, destilar un período, verificar un resumen, pensar tendencias, criticar o curar) y carga la
   skill del rol correspondiente.
2. Lee primero el spec del formato que corresponda: `references/log-format-spec.md` para logs
   crudos; `references/summary-format-spec.md` para destilar, fidelizar o analizar períodos.
3. Si el pedido es "mejorá nuestro logging" sin más, corre el ciclo: diseñador → instrumentador,
   luego invita a generar corridas y volver con analista/crítico/curador. Si el pedido es "entendé
   qué pasó esta semana/mes", corre el ciclo de conocimiento: destilador → fidelizador → filósofo.
4. Mantén la **profundidad progresiva**: empieza en `explanatory`; sube a `diagnostic`/`deep`
   solo cuando una anomalía concreta no se explica con lo disponible, y de forma temporal.

## Profundidad progresiva (resumen)

`operational` (inicio/fin/resultado/errores) → `explanatory` (decisiones, razones, cambios de
estado; **default**) → `diagnostic` (snapshots de variables, detalle de llamadas externas y
reintentos) → `deep` (trazas finas de un componente, acotadas en el tiempo). Detalle completo en
el spec.

## Vista humana del log (Markdown + dashboard)

El NDJSON es para máquinas; para que un humano lo lea hay una **proyección humana canónica**
(spec §6): un layout único en Markdown (ficha de header con leyenda de variables, vista *digest*
por corrida, vista *timeline* evento-a-evento, marcadores `✅`/`❌`/`⚠`/`🔴`). Es una vista
**derivada**, nunca una segunda fuente de verdad — se genera desde el log, no se edita a mano. Dos
renderers producen ese mismo layout:

- **`scripts/render_log.py`** — NDJSON → Markdown (`--view digest|timeline|both`). Para informes,
  comentarios de PR o el cuerpo de un análisis.
- **`assets/dashboard.html`** (opcional, recomendado) — dashboard de un solo archivo, sin build ni
  dependencias, que hace *tail* del NDJSON por URL (vista en vivo) o por drag-and-drop (snapshot) y
  muestra la proyección canónica. El instrumentador puede entregarlo junto al sistema; su ausencia
  no degrada el log (sigue legible con `render_log.py`).

## Gotchas

- **Confundir "más logs" con "mejor logging".** El objetivo es capacidad explicativa, no volumen.
  Un evento `decision` con su `reason` vale más que diez líneas de ruido. Agregar datos solo
  cuando ayudan a responder una pregunta real de análisis.
- **Repetir el header en cada evento.** El header explicativo se escribe **una sola vez** por
  corrida o por rotación de archivo, no por línea. Repetirlo infla el log y no añade información.
- **Saltarse al instrumentador sin diseño.** Instrumentar sin haber estudiado el sistema produce
  logs que registran lo fácil de loguear, no lo que hace falta para comprender la ejecución.
- **Mezclar hechos con interpretaciones.** El sistema solo emite hechos; el destilador también
  solo hechos; analista, fidelizador, filósofo y crítico escriben en artefactos separados y
  etiquetan cada afirmación (fact/interpretation/hypothesis). Nunca metas conclusiones de agente en
  el log del sistema ni opiniones en un resumen destilado.
- **Saltarse la fidelización.** Un resumen no verificado no debe usarse como fuente de un período
  mayor ni del análisis del filósofo: los errores se componen nivel a nivel. Solo fuentes crudas o
  resúmenes con verdict aprobado.
- **Tratar los roles como agentes obligatoriamente separados.** En un sistema chico, un mismo
  agente hace los ocho roles en secuencia. La separación es de *capacidades*, no de procesos.
- **Subir a `deep` permanentemente.** El nivel profundo es temporal y localizado; dejarlo activo
  convierte el log en ruido caro.

## Output esperado

Según el rol activado, el entregable lo define la skill correspondiente (modelo de observación,
diff de instrumentación, informe de análisis, crítica, o decisión de curaduría). Como
orquestador, esta skill produce el **enrutamiento**: identifica el rol, enuncia en qué punto del
ciclo está el trabajo, y deja al usuario con la skill de rol cargada y el spec leído.

## Referencias

- Leer `references/log-format-spec.md` antes de cualquier trabajo sobre logs crudos (diseñar,
  instrumentar, analizar, criticar): define el formato del log que comparten esos roles.
- Leer `references/summary-format-spec.md` antes de destilar, fidelizar o analizar períodos:
  define el resumen de período (meta + secciones), la jerarquía, la trazabilidad `[ref: …]` y el
  veredicto de fidelidad que comparten destilador, fidelizador y filósofo.
- Leer `references/example-log.ndjson` cuando necesites un ejemplo concreto de header + eventos
  (dos corridas, una normal y una con anomalía) para mostrar o para probar los scripts.
- Ejecutar `scripts/render_log.py <log.ndjson>` para producir la vista humana en Markdown; ver
  `scripts/render_log.py --help` para las vistas disponibles.
- `scripts/aflog.py` es el **parser canónico compartido** (única implementación Python del
  parseo/agrupación): lo importan `render_log.py`, y los scripts de las skills `logging-analyst` y
  `logging-critic`. El `dashboard.html` replica esa lógica en JS. Si cambia el formato, ajusta el
  parseo en `aflog.py` (Python) y en el JS del dashboard — no en cada script.
- Entregar `assets/dashboard.html` cuando el sistema quiera una vista del log en vivo para humanos
  (apuntarlo a la URL del NDJSON con `?src=`); es opcional y recomendado, no obligatorio.
- El verificador mecánico de fidelidad vive en `logging-fidelity-checker/scripts/check_summary.py`
  (también importa `aflog.py`): valida cobertura, referencias y recomputa conteos de un resumen.
