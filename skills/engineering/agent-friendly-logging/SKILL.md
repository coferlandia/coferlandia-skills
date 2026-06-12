---
name: agent-friendly-logging
description: >
  Orquesta una suite para convertir el logging tradicional de un sistema en observabilidad
  comprensible por agentes de IA: logs que, además de los campos técnicos habituales (timestamp,
  nivel, componente, mensaje, correlación, excepciones, rotación), llevan el contexto semántico
  para que un agente que nunca vio el sistema reconstruya qué hizo, qué decidió y por qué. Define
  el formato canónico (header autoexplicativo + eventos NDJSON), los niveles de profundidad y el
  ciclo de mejora continua, y una vista humana canónica del log (render Markdown + dashboard en
  vivo). Enruta a los roles diseñador, instrumentador, analista, crítico y curador. Keywords:
  logging, logs, observabilidad, trazabilidad, NDJSON, structured logging, correlation id,
  diagnóstico, log agent-friendly, instrumentar, render markdown, dashboard de logs en vivo.
when_to_use: >
  Actívala cuando el usuario quiera diseñar, implementar, leer, analizar, criticar o mejorar
  logging pensado para que lo interpreten agentes; cuando hable de "logs que un agente pueda
  entender", "observabilidad semántica", "que el sistema explique su propia ejecución", o de
  transformar logging existente en algo más explicativo. Úsala como punto de entrada que decide
  qué rol aplicar; para una tarea puntual, salta directo al rol (logging-designer / -instrumenter
  / -analyst / -critic / -curator). Aplica aunque no digan "agent-friendly": basta "logs más
  útiles para depurar con IA", "que se entienda qué pasó en esta corrida" o "mejorar nuestro
  logging". No la uses para configurar un agregador concreto (Datadog, ELK) — eso es otra tarea.
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repositorio del sistema a instrumentar y git. Los
  scripts de análisis usan Python 3.11+. El formato NDJSON es agnóstico del lenguaje del sistema.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); parser compartido aflog.py provee load/group/outcome/state_path/markers a render_log.py, reconstruct_run.py y audit_log.py (las 3 dan la misma reconstrucción que antes del refactor); render_log.py renderiza example-log.ndjson en Markdown (digest/timeline, marcadores ✅/❌/⚠); correlación anidada parent/child verificada en aflog, render_log y dashboard; dashboard.html con sintaxis JS validada (node --check) y agrupación coincidente con aflog.py."
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

## El formato — fuente de verdad única

El formato canónico (header autoexplicativo + eventos NDJSON, niveles de profundidad, distinción
hecho/interpretación/hipótesis, base de conocimiento) vive en **un solo lugar**:

> **Lee `references/log-format-spec.md`** antes de diseñar, instrumentar, analizar o criticar un
> log. Todas las skills de roles enlazan a ese archivo; no lo redefinas en otro lado.
> Ejemplo trabajado en `references/example-log.ndjson`.

## Los cinco roles

Estos roles son **capacidades**, no necesariamente agentes separados: en sistemas pequeños los
ejecuta un mismo agente en secuencia; en sistemas complejos se distribuyen. Cada uno tiene su
skill:

| Rol | Skill | Qué hace |
|-----|-------|----------|
| **Diseñador** | `logging-designer` | Estudia el sistema y define el **modelo de observación**: qué procesos, estados, decisiones y variables registrar. |
| **Instrumentador** | `logging-instrumenter` | Implementa o adapta el logging según el diseño, **sin cambiar el comportamiento funcional** del sistema. |
| **Analista** | `logging-analyst` | Lee los logs, reconstruye ejecuciones, detecta anomalías y compara corridas; formula explicaciones e hipótesis. |
| **Crítico** | `logging-critic` | Evalúa si el log es **realmente comprensible**: datos faltantes, variables ambiguas, eventos redundantes, decisiones sin explicación. |
| **Curador** | `logging-curator` | Decide qué sugerencias incorporar; evita tanto la falta de información como el crecimiento descontrolado del log. |

## El ciclo de mejora continua

El núcleo de la suite es un lazo agéntico de aprendizaje. El logging evoluciona a partir de
necesidades **reales** de análisis, no agregando datos indiscriminadamente:

```
1. logging-designer   → estudia el sistema y diseña el modelo de observación
2. logging-instrumenter→ implementa/adapta la instrumentación
3. (el sistema corre)  → genera ejecuciones reales
4. logging-analyst     → reconstruye corridas y detecta qué NO puede responder
5. logging-critic      → propone mejoras concretas (gaps, ambigüedades, redundancias)
6. logging-curator     → decide qué incorporar (sin inflar el log)
7. logging-designer    → refina el modelo  ──┐
                                             └─► vuelve a 2, próximas corridas son más útiles
```

## Cómo usar la suite

1. Identifica en qué punto del ciclo está el usuario (diseñar desde cero, instrumentar, analizar
   un log existente, criticar, o curar sugerencias) y carga la skill del rol correspondiente.
2. En todos los casos, lee primero `references/log-format-spec.md` para hablar el mismo formato.
3. Si el pedido es "mejorá nuestro logging" sin más, corre el ciclo: diseñador → instrumentador,
   luego invita a generar corridas y volver con analista/crítico/curador.
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
- **Mezclar hechos con interpretaciones.** El sistema solo emite hechos; analista y crítico
  escriben en artefactos separados y etiquetan cada afirmación como fact/interpretation/hypothesis.
  Nunca escribas conclusiones de agente dentro del log del sistema.
- **Tratar los roles como agentes obligatoriamente separados.** En un sistema chico, un mismo
  agente hace los cinco roles en secuencia. La separación es de *capacidades*, no de procesos.
- **Subir a `deep` permanentemente.** El nivel profundo es temporal y localizado; dejarlo activo
  convierte el log en ruido caro.

## Output esperado

Según el rol activado, el entregable lo define la skill correspondiente (modelo de observación,
diff de instrumentación, informe de análisis, crítica, o decisión de curaduría). Como
orquestador, esta skill produce el **enrutamiento**: identifica el rol, enuncia en qué punto del
ciclo está el trabajo, y deja al usuario con la skill de rol cargada y el spec leído.

## Referencias

- Leer `references/log-format-spec.md` **siempre** antes de cualquier trabajo de logging: define
  el formato canónico que comparten los cinco roles.
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
