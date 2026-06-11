# Genesis Plan — Coferlandia Skills Repository

> **Filosofía central:** Este repositorio es construido por agentes de IA, para agentes de IA.  
> Los humanos definen la visión. Los agentes ejecutan, crean y mejoran.

---

## 1. Visión

`coferlandia-skills` es un repositorio de **Agent Skills** (formato [agentskills.io](https://agentskills.io)) que captura el conocimiento operacional de Coferlandia en forma de instrucciones portables y reutilizables que cualquier agente de IA compatible puede leer, activar y ejecutar.

La premisa es radical: **cualquier agente de IA que llegue a este repo debe poder crear una nueva skill correctamente sin recibir más instrucciones que las que están escritas aquí.**

---

## 2. Filosofía: Para y Por Agentes

| Principio | Significado |
|-----------|-------------|
| **Para agentes** | Las skills están escritas como instrucciones que un agente ejecuta, no documentación que un humano lee |
| **Por agentes** | Cualquier agente IA puede crear nuevas skills siguiendo el protocolo del repo |
| **Auto-documentado** | El repo se explica a sí mismo — `AGENTS.md` es el punto de entrada para cualquier agente |
| **Progressive disclosure** | Metadata liviana primero, instrucciones completas solo cuando se activa la skill |
| **Versionable** | Todo en Git. Skills evolucionan con el proyecto |
| **Cross-agent** | Compatible con Claude Code, GitHub Copilot, Cursor, Gemini CLI, VS Code, y cualquier agente agentskills.io |

---

## 3. Estructura del Repositorio

```
coferlandia-skills/
│
├── AGENTS.md                        ← LEER PRIMERO (entry point para agentes)
├── README.md                        ← Overview para humanos
├── Genesis_Plan.md                  ← Este documento
│
├── _protocol/                       ← Instrucciones para crear/mantener skills
│   ├── HOW_TO_CREATE_SKILLS.md      ← Protocolo completo de creación
│   ├── SKILL_TEMPLATE.md            ← Template listo para copiar
│   ├── QUALITY_STANDARDS.md         ← Criterios de calidad y checklist
│   ├── NAMING_CONVENTIONS.md        ← Reglas de naming y categorías
│   └── SKILL_LIFECYCLE.md           ← Estados: draft → review → active → deprecated
│
├── skills/                          ← Todas las skills viven aquí
│   ├── INDEX.md                     ← Catálogo de skills (actualizar al agregar)
│   │
│   ├── meta/                        ← Skills que crean y gestionan otras skills
│   │   ├── skill-factory/           ← Crear nuevas skills en este repo
│   │   │   └── SKILL.md
│   │   └── skill-auditor/           ← Revisar y mejorar skills existentes
│   │       └── SKILL.md
│   │
│   ├── engineering/                 ← Code, infra, arquitectura
│   ├── data/                        ← Análisis, pipelines, reportes
│   ├── content/                     ← Escritura, comunicación, documentación
│   ├── design/                      ← UX, producto, visual
│   └── ops/                         ← Procesos operacionales, automatizaciones
│
└── vault/                           ← Obsidian vault
    ├── Genesis_Plan.md              ← Este plan con wikilinks
    ├── Architecture.md
    ├── Skill_Catalog.md
    └── Philosophy.md
```

---

## 4. Formato de Skill (Estándar agentskills.io)

Cada skill es una **carpeta** que contiene al mínimo un archivo `SKILL.md`:

```
skill-name/
├── SKILL.md          ← Requerido: metadata YAML + instrucciones Markdown
├── scripts/          ← Opcional: scripts ejecutables
├── references/       ← Opcional: documentación de referencia
└── assets/           ← Opcional: templates, recursos estáticos
```

### Estructura de `SKILL.md`

```markdown
---
name: skill-name                    # Requerido. Lowercase, hyphens, 1-64 chars
description: >                      # Requerido. Qué hace y CUÁNDO usarla. 1-1024 chars
  Descripción detallada con keywords
  que ayudan al agente a activarla en el momento correcto.
license: MIT                        # Opcional
compatibility: Claude Code, VS Code # Opcional
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
---

# Instrucciones

[Aquí van las instrucciones que el agente seguirá cuando active esta skill]
```

### Reglas críticas del nombre

- Solo minúsculas, números y guiones (`-`)
- Sin guiones al inicio o final
- Sin guiones dobles (`--`)
- Debe coincidir exactamente con el nombre de la carpeta
- Máximo 64 caracteres

---

## 5. Cómo Trabajan los Agentes con Este Repo

### Flujo de descubrimiento (Progressive Disclosure)

```
1. DISCOVERY   → Agente lee AGENTS.md y el frontmatter de cada skill
                 (solo name + description, ~100 tokens por skill)
                 
2. ACTIVATION  → Cuando una tarea coincide con una skill, agente carga
                 el cuerpo completo de SKILL.md (<5000 tokens recomendado)
                 
3. EXECUTION   → Agente sigue las instrucciones, carga scripts/references
                 solo cuando los necesita
```

### Flujo de creación de skills (skill-factory)

```
1. Agente activa la skill "skill-factory" (en skills/meta/skill-factory/)
2. Sigue el protocolo en _protocol/HOW_TO_CREATE_SKILLS.md
3. Usa el template en _protocol/SKILL_TEMPLATE.md
4. Verifica calidad con _protocol/QUALITY_STANDARDS.md
5. Actualiza skills/INDEX.md
6. Crea PR o commit directo según contexto
```

---

## 6. Categorías de Skills

| Categoría | Descripción | Ejemplos |
|-----------|-------------|---------|
| `meta` | Skills sobre skills | skill-factory, skill-auditor |
| `engineering` | Código, infra, arquitectura | code-review, deploy-checklist, debug |
| `data` | Datos, análisis, reportes | sql-query, csv-analysis, data-pipeline |
| `content` | Escritura y comunicación | blog-post, email-draft, release-notes |
| `design` | UX, producto | ux-copy, design-critique, user-research |
| `ops` | Operaciones, automatización | incident-response, standup, sprint-review |

---

## 7. Estándares de Calidad

El checklist autoritativo y completo vive en [`_protocol/QUALITY_STANDARDS.md`](./_protocol/QUALITY_STANDARDS.md)
(fuente de verdad única — no se reproduce aquí para no duplicarlo). Lo mecánico está
automatizado en `_protocol/scripts/validate_skill.py`. En una frase: una skill es apta para
producción cuando pasa el validador (código 0), sus instrucciones son procedurales con Gotchas
reales, y tiene evidencia de prueba registrada en `metadata.tested`.

---

## 8. Principios de Diseño de Skills

### Lo que va en una skill

- Conocimiento específico de Coferlandia que el agente no tendría sin la skill
- Convenciones de proyecto, patrones internos, APIs propias
- Gotchas y correcciones a errores típicos
- Templates de output para resultados consistentes
- Checklists para workflows multi-paso

### Lo que NO va en una skill

- Conocimiento general que cualquier LLM ya tiene
- Explicaciones de conceptos básicos ("un PDF es...")
- Código que el agente puede escribir por sí mismo sin errores

### Calibración de prescriptividad

- **Alta prescriptividad** → operaciones frágiles, secuencias exactas, scripts específicos
- **Baja prescriptividad** → tareas creativas, análisis donde múltiples enfoques son válidos

---

## 9. Roadmap de Skills Iniciales

### Fase 1 — Meta-infraestructura (Fundación)
- [ ] `meta/skill-factory` — Crear nuevas skills
- [ ] `meta/skill-auditor` — Revisar y mejorar skills

### Fase 2 — Engineering Core
- [ ] `engineering/code-review` — Review con estándares de Coferlandia
- [ ] `engineering/deploy-checklist` — Pre-deploy verification
- [ ] `engineering/debug` — Debugging estructurado
- [ ] `engineering/architecture-decision` — ADRs

### Fase 3 — Data & Content
- [ ] `data/sql-query` — Queries sobre schemas de Coferlandia
- [ ] `data/report-generation` — Reportes en formato Coferlandia
- [ ] `content/release-notes` — Release notes desde commits
- [ ] `content/technical-doc` — Documentación técnica

### Fase 4 — Ops
- [ ] `ops/incident-response` — Protocolo de incidentes
- [ ] `ops/standup` — Standup desde actividad reciente
- [ ] `ops/sprint-review` — Review de sprint

---

## 10. Agentes Compatibles

Este repositorio es compatible con cualquier agente que soporte el estándar agentskills.io, incluyendo:

- Claude Code / Claude (Anthropic)
- GitHub Copilot / VS Code
- Cursor
- Gemini CLI
- OpenAI Codex
- Roo Code, OpenCode, Amp, Goose, y más

El directorio de skills puede configurarse en cada agente. Convenciones comunes:
- VS Code / Copilot: `.agents/skills/`
- Claude Code: configurable vía settings
- La carpeta `skills/` de este repo es la fuente de verdad

---

## 11. Protocolo de Contribución

Todo agente que cree o modifique una skill debe:

1. Leer `_protocol/HOW_TO_CREATE_SKILLS.md` antes de crear
2. Usar `_protocol/SKILL_TEMPLATE.md` como base
3. Verificar contra `_protocol/QUALITY_STANDARDS.md`
4. Actualizar `skills/INDEX.md` con la nueva skill
5. Nombrar commits con el formato: `skill(category/name): descripción`

---

## Meta

| Campo | Valor |
|-------|-------|
| Autor del plan | Claude (Anthropic) via Cowork |
| Fecha | 2026-06-11 |
| Versión | 1.0 — Genesis |
| Estándar | [agentskills.io](https://agentskills.io) |
| Próxima revisión | Tras crear las primeras 5 skills |
