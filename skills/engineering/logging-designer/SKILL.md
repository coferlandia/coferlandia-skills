---
name: logging-designer
description: >
  Rol diseñador del logging agent-friendly: estudia un sistema y define su modelo de observación
  —qué procesos, estados, decisiones, variables, dependencias y condiciones excepcionales deben
  registrarse para que una ejecución pueda reconstruirse y comprenderse. Produce un documento de
  modelo de observación y el header explicativo del log, sin tocar todavía el código. Keywords:
  diseño de logging, modelo de observación, qué loguear, estados, decisiones, variables, reglas
  de negocio, header de log, observabilidad semántica.
when_to_use: >
  Actívala antes de instrumentar: cuando haya que decidir QUÉ registrar de un sistema para que un
  agente lo entienda, cuando el usuario pida "diseñar el logging", "definir qué loguear", o
  cuando un análisis revele que faltan datos y haya que rediseñar el modelo de observación.
  Aplica aunque no exista logging previo (diseño desde cero) o aunque ya exista (rediseño). Es el
  paso 1 y 7 del ciclo de agent-friendly-logging. No la uses para escribir el código de logging
  —eso es logging-instrumenter— ni para leer logs ya generados —eso es logging-analyst.
license: MIT
compatibility: >
  Requiere acceso de lectura al repositorio y documentación del sistema a observar. No modifica
  código. Trabaja sobre el formato definido en agent-friendly-logging.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); modelo de observación verificado contra el header del spec compartido."
---

## Contexto

Esta skill es el rol **diseñador** de la suite `agent-friendly-logging`. Antes de crear o
modificar logging, hay que entender el sistema lo suficiente para decidir qué información permite
**reconstruir y comprender** una ejecución. El diseñador no escribe código de logging: produce un
**modelo de observación** que el instrumentador implementa.

Lee primero `../agent-friendly-logging/references/log-format-spec.md` — define el header y los
eventos que tu diseño debe poblar. No redefinas el formato aquí.

## Pasos

### 1. Estudiar el sistema de origen

Antes de diseñar nada, reúne (de código, docs y dueños del sistema):

- **Propósito y objetivo funcional** — qué hace y qué cuenta como éxito.
- **Arquitectura básica** — componentes y cómo se comunican.
- **Entradas y salidas** — qué recibe y qué produce.
- **Procesos principales** — el flujo de una ejecución típica.
- **Reglas de negocio** — las que gobiernan las decisiones.
- **Estados y transiciones** — el ciclo de vida de una corrida.
- **Variables relevantes** — y su significado, unidad y rango/valores posibles.
- **Dependencias externas** — servicios que llama y qué puede fallar.
- **Condiciones normales y excepcionales** — qué es esperado y qué no.

Si encuentras **contradicciones o documentación desactualizada, repórtalo — no la corrijas
automáticamente.** Diseñar no es arreglar el sistema.

### 2. Derivar el modelo de observación

Para cada elemento estudiado, decide qué hace falta registrar para que la corrida se reconstruya:

- ¿Qué **decisiones** toma el sistema y qué **condición** (`reason`) las dispara? → eventos `decision`.
- ¿Qué **estados** atraviesa y por qué transiciona? → eventos `state_change`.
- ¿Qué **variables** explican esas decisiones? → defínelas en el header (`meaning/unit/range/values`).
- ¿Qué **llamadas externas, reintentos y recuperaciones** importan? → `external_call`/`retry`/`recovery`.
- ¿Qué cuenta como **anomalía** (fuera de rango esperado)? → `anomaly` con `expected`/`actual`.
- ¿Cuál es el **resultado esperado** de la corrida y su **causa de finalización**? → `run_end`.

### 3. Definir el header explicativo

Completa el registro `header` del spec con los datos del paso 1: `system`, `purpose`,
`objective`, `scope` (incluye qué queda **fuera**), `correlation`, `states`, y el diccionario
`variables`. Este header se escribe una vez por corrida/rotación y hace el archivo autocontenido.

### 4. Fijar la profundidad inicial

Elige el `depth` de arranque (normalmente `explanatory`) y deja anotado qué eventos viven en cada
nivel, para que el instrumentador sepa qué condicionar y el analista qué pedir subir.

### 5. Entregar al instrumentador

Produce el documento de modelo de observación (template abajo). Es la entrada de
`logging-instrumenter`. No escribas el código tú.

## Gotchas

- **Diseñar por lo que es fácil de loguear, no por lo que hace falta entender.** El modelo parte
  de las preguntas que un agente debe poder responder, no de los `print` que ya existen.
- **Variables sin significado.** Listar `stock_level` sin unidad ni rango deja al agente
  adivinando. Toda variable del modelo lleva `meaning` y, según el caso, `unit`/`range`/`values`.
- **Decisiones sin causa.** Si una regla de negocio determina una decisión, el diseño debe exigir
  registrar el `reason`. Una `decision` sin `reason` es media decisión.
- **Corregir la documentación desactualizada al pasar.** Repórtalo, no lo arregles: estás
  diseñando observación, no modificando el sistema.
- **Diseñar el universo entero.** No registres cada variable existente "por si acaso"; empieza
  por lo que reconstruye la corrida y deja que el ciclo (analista→crítico→curador) agregue lo que
  falte cuando una pregunta real lo justifique.

## Output esperado

```markdown
# Modelo de observación — {system}

## Sistema
- Propósito: {...}
- Objetivo funcional (qué es éxito): {...}
- Scope observado: {...}  | Fuera de scope: {...}

## Correlación
- primary: {run_id|...}   secondary: [{order_id}, ...]
- (opcional) parent_run_id / op_id si hay sub-operaciones o traza distribuida — ver spec §3.5

## Estados y transiciones
{received → validating → reserving → confirmed|rejected}

## Variables a registrar
| nombre | significado | unidad | rango/valores |
|--------|-------------|--------|----------------|
| stock_level | unidades disponibles del SKU | unidades | 0..N |

## Decisiones y sus condiciones
| decisión | condición (reason) | evento |
|----------|--------------------|--------|
| reserve  | stock_level >= order_qty | decision |

## Dependencias externas a registrar
- inventory-db (get_stock): registrar status + latency_ms

## Anomalías a vigilar
- latencia de inventory-db > 1000ms → warning/anomaly

## Profundidad inicial
- depth=explanatory; {qué eventos suben a diagnostic/deep}

## Contradicciones/documentación desactualizada detectadas (reportar, no corregir)
- {...}
```

## Referencias

- Leer `../agent-friendly-logging/references/log-format-spec.md` al empezar: tu modelo debe poblar
  exactamente ese header y esos `event_type`.
