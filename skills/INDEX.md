# Skills Index â€” coferlandia-skills

> **Fuente de verdad Ãºnica del inventario de skills.** Este es el Ãºnico archivo que lista quÃ©
> skills existen y su estado. El protocolo de contribuciÃ³n manda actualizar SOLO este archivo;
> no hay catÃ¡logos espejo que sincronizar a mano (las vistas del `vault/` son derivadas).
>
> **Formato de fila (definido aquÃ­, no se repite en otro lado):**
> `| [nombre-skill](./{categoria}/{nombre-skill}/) | DescripciÃ³n breve en una lÃ­nea | {status} |`
> donde `status` âˆˆ `draft | active | deprecated`. La ruta del link es relativa a este archivo
> (que vive dentro de `skills/`), por eso empieza con `./{categoria}/`.

---

## Meta

Skills sobre skills y sobre el repositorio â€” para crear, auditar y estructurar.

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| [build-agentic-repo](./meta/build-agentic-repo/) | DiseÃ±ar/auditar repos agÃ©nticos autoritativos: una fuente de verdad, sin duplicaciÃ³n ni contradicciones | active |
| [coferlandia-skill-testing](./meta/coferlandia-skill-testing/) | Auditar y probar skills contra agentskills.io y los invariantes locales del repositorio | active |
| [skill-factory](./meta/skill-factory/) | Crear nuevas skills en este repositorio siguiendo el protocolo completo | active |
| [skill-auditor](./meta/skill-auditor/) | Auditar y modificar skills existentes sin romperlas â€” gate de proporcionalidad, modo auditorÃ­a y modo cirugÃ­a | active |

---

## Engineering

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| [coferlandia-software-dev](./engineering/coferlandia-software-dev/) | Proceso de control para tareas de desarrollo con autoridad activa y roles developer/debugger: estudio previo, plan aprobado, implementacion, review y commit | active |

### Suite â€” Logging orientado a agentes

Convierte el logging tradicional en observabilidad comprensible por agentes. `agent-friendly-logging` es el punto de entrada (formato canÃ³nico + ciclo de mejora); las otras ocho son los roles del ciclo.

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| [agent-friendly-logging](./engineering/agent-friendly-logging/) | Orquesta la suite: formato canÃ³nico (header explicativo + eventos NDJSON), niveles de profundidad y ciclo de mejora; enruta a los ocho roles | active |
| [logging-designer](./engineering/logging-designer/) | Estudia el sistema y define el modelo de observaciÃ³n: quÃ© estados, decisiones y variables registrar | active |
| [logging-instrumenter](./engineering/logging-instrumenter/) | Implementa/adapta el logging segÃºn el diseÃ±o, en NDJSON, sin alterar el comportamiento funcional | active |
| [logging-analyst](./engineering/logging-analyst/) | Lee logs, reconstruye ejecuciones, detecta anomalÃ­as y compara corridas; separa hechos de hipÃ³tesis | active |
| [logging-distiller](./engineering/logging-distiller/) | Compacta un perÃ­odo (hora/dÃ­a/semana/mes) en un resumen factual, completo y trazable; destilaciÃ³n jerÃ¡rquica | active |
| [logging-fidelity-checker](./engineering/logging-fidelity-checker/) | Verifica que un resumen represente fielmente sus fuentes (cobertura, conteos, trazabilidad) y emite un veredicto | active |
| [logging-philosopher](./engineering/logging-philosopher/) | Pensamiento profundo sobre resÃºmenes validados: causas, tendencias, riesgos, oportunidades; separa hechos/inferencias/hipÃ³tesis | active |
| [logging-critic](./engineering/logging-critic/) | EvalÃºa si el log es realmente comprensible: gaps, variables ambiguas, redundancias; audita NDJSON | active |
| [logging-curator](./engineering/logging-curator/) | Decide quÃ© sugerencias incorporar sin inflar el log y mantiene la base de conocimiento acumulado | active |

## Data

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| *(prÃ³ximamente)* | | |

## Content

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| [project-documentation-archivist](./content/project-documentation-archivist/) | Catalogar, normalizar y archivar memoria documental del proyecto con trazabilidad, conflictos y sesiones | active |
| [sagan-scientific-debunker](./content/sagan-scientific-debunker/) | Evaluar afirmaciones y noticias con rigor cientifico, mapa de evidencia y conclusiones trazables a papers y fuentes primarias | active |

## Design

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| *(prÃ³ximamente)* | | |

## Ops

| Skill | DescripciÃ³n | Status |
|-------|-------------|--------|
| [sr-de-la-nata](./ops/sr-de-la-nata/) | DirecciÃ³n privada de proyectos: abre expediente, investiga, evalÃºa con honestidad brutal, planifica y empuja la ejecuciÃ³n con bitÃ¡coras y registros vivos | active |

---

*Ãšltima actualizaciÃ³n: 2026-06-25*
