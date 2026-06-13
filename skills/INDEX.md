# Skills Index — coferlandia-skills

> **Fuente de verdad única del inventario de skills.** Este es el único archivo que lista qué
> skills existen y su estado. El protocolo de contribución manda actualizar SOLO este archivo;
> no hay catálogos espejo que sincronizar a mano (las vistas del `vault/` son derivadas).
>
> **Formato de fila (definido aquí, no se repite en otro lado):**
> `| [nombre-skill](./{categoria}/{nombre-skill}/) | Descripción breve en una línea | {status} |`
> donde `status` ∈ `draft | active | deprecated`. La ruta del link es relativa a este archivo
> (que vive dentro de `skills/`), por eso empieza con `./{categoria}/`.

---

## Meta

Skills sobre skills y sobre el repositorio — para crear, auditar y estructurar.

| Skill | Descripción | Status |
|-------|-------------|--------|
| [build-agentic-repo](./meta/build-agentic-repo/) | Diseñar/auditar repos agénticos autoritativos: una fuente de verdad, sin duplicación ni contradicciones | active |
| [coferlandia-skill-testing](./meta/coferlandia-skill-testing/) | Auditar y probar skills contra agentskills.io y los invariantes locales del repositorio | active |
| [skill-factory](./meta/skill-factory/) | Crear nuevas skills en este repositorio siguiendo el protocolo completo | active |
| [skill-auditor](./meta/skill-auditor/) | Revisar y mejorar skills existentes — calidad, descriptions, gotchas | draft |

---

## Engineering

| Skill | Descripción | Status |
|-------|-------------|--------|
| [coferlandia-software-dev](./engineering/coferlandia-software-dev/) | Proceso de control para tareas de desarrollo: estudio previo, plan aprobado, implementación, code review obligatoria y preparación de commit | active |

### Suite — Logging orientado a agentes

Convierte el logging tradicional en observabilidad comprensible por agentes. `agent-friendly-logging` es el punto de entrada (formato canónico + ciclo de mejora); las otras ocho son los roles del ciclo.

| Skill | Descripción | Status |
|-------|-------------|--------|
| [agent-friendly-logging](./engineering/agent-friendly-logging/) | Orquesta la suite: formato canónico (header explicativo + eventos NDJSON), niveles de profundidad y ciclo de mejora; enruta a los ocho roles | active |
| [logging-designer](./engineering/logging-designer/) | Estudia el sistema y define el modelo de observación: qué estados, decisiones y variables registrar | active |
| [logging-instrumenter](./engineering/logging-instrumenter/) | Implementa/adapta el logging según el diseño, en NDJSON, sin alterar el comportamiento funcional | active |
| [logging-analyst](./engineering/logging-analyst/) | Lee logs, reconstruye ejecuciones, detecta anomalías y compara corridas; separa hechos de hipótesis | active |
| [logging-distiller](./engineering/logging-distiller/) | Compacta un período (hora/día/semana/mes) en un resumen factual, completo y trazable; destilación jerárquica | active |
| [logging-fidelity-checker](./engineering/logging-fidelity-checker/) | Verifica que un resumen represente fielmente sus fuentes (cobertura, conteos, trazabilidad) y emite un veredicto | active |
| [logging-philosopher](./engineering/logging-philosopher/) | Pensamiento profundo sobre resúmenes validados: causas, tendencias, riesgos, oportunidades; separa hechos/inferencias/hipótesis | active |
| [logging-critic](./engineering/logging-critic/) | Evalúa si el log es realmente comprensible: gaps, variables ambiguas, redundancias; audita NDJSON | active |
| [logging-curator](./engineering/logging-curator/) | Decide qué sugerencias incorporar sin inflar el log y mantiene la base de conocimiento acumulado | active |

## Data

| Skill | Descripción | Status |
|-------|-------------|--------|
| *(próximamente)* | | |

## Content

| Skill | Descripción | Status |
|-------|-------------|--------|
| *(próximamente)* | | |

## Design

| Skill | Descripción | Status |
|-------|-------------|--------|
| *(próximamente)* | | |

## Ops

| Skill | Descripción | Status |
|-------|-------------|--------|
| [sr-de-la-nata](./ops/sr-de-la-nata/) | Dirección privada de proyectos: abre expediente, investiga, evalúa con honestidad brutal, planifica y empuja la ejecución con bitácoras y registros vivos | active |

---

*Última actualización: 2026-06-13*
