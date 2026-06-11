---
tags:
  - coferlandia
  - skills
  - genesis
  - agent-skills
created: 2026-06-11
status: active
---

# Genesis Plan — Coferlandia Skills Repository

> **Filosofía central:** Este repositorio es construido por agentes de IA, para agentes de IA.

---

## Visión

`coferlandia-skills` captura el conocimiento operacional de Coferlandia como [[Agent Skills]] portables y reutilizables en formato [agentskills.io](https://agentskills.io).

La premisa es radical: **cualquier agente de IA que llegue al repo puede crear una nueva skill correctamente sin instrucciones adicionales del humano.** Todo lo que necesita está escrito en el repo.

→ Ver [[Philosophy]] para el desarrollo completo de la filosofía.

---

## Estructura del Repositorio

```
coferlandia-skills/
│
├── AGENTS.md               ← Entry point para agentes
├── README.md               ← Overview humano
├── Genesis_Plan.md         ← El plan original (este documento)
│
├── _protocol/              ← Protocolo para agentes
│   ├── HOW_TO_CREATE_SKILLS.md
│   ├── SKILL_TEMPLATE.md
│   ├── QUALITY_STANDARDS.md
│   ├── NAMING_CONVENTIONS.md
│   └── SKILL_LIFECYCLE.md
│
└── skills/                 ← Todas las skills
    ├── INDEX.md
    ├── meta/
    │   ├── skill-factory/  ← La skill más importante
    │   └── skill-auditor/
    ├── engineering/
    ├── data/
    ├── content/
    ├── design/
    └── ops/
```

→ Ver [[Architecture]] para el diagrama completo y rationale.

---

## Principios Clave

| Principio | Descripción |
|-----------|-------------|
| **Para agentes** | Skills escritas como instrucciones ejecutables, no documentación |
| **Por agentes** | Cualquier agente puede crear nuevas skills siguiendo el protocolo |
| **Auto-documentado** | El repo se explica a sí mismo — `AGENTS.md` es el entry point |
| **Progressive disclosure** | Metadata liviana → instrucciones completas → recursos |
| **Privacidad primero** | Repo público. Cero secretos, cero PII, nunca |
| **Versionable** | Git es la fuente de verdad |
| **Cross-agent** | Compatible con Claude Code, GitHub Copilot, Cursor, Gemini CLI y más |

→ Ver [[Privacy_And_Security]] para el protocolo completo de privacidad.

---

## La Skill Más Importante: skill-factory

La joya del repo es `skills/meta/skill-factory/` — una skill que permite a cualquier agente crear otras skills en el repo sin instrucciones del humano. Es la encarnación de "por agentes".

→ Ver [[Skill_Catalog]] para todas las skills disponibles.

---

## Formato de Skill (agentskills.io)

Cada skill = carpeta + `SKILL.md`:

```
skill-name/
├── SKILL.md      ← Requerido
├── scripts/      ← Opcional
├── references/   ← Opcional
└── assets/       ← Opcional
```

`SKILL.md` tiene frontmatter YAML + instrucciones Markdown:

```yaml
---
name: nombre-skill
description: >
  Qué hace Y cuándo activarla. Con keywords explícitos.
metadata:
  category: engineering
  status: active
---
```

→ Ver [[Skill_Format]] para la especificación completa.

---

## Roadmap de Skills

### Fase 1 — Meta-infraestructura ✅
- [x] `meta/skill-factory` — Crear nuevas skills
- [ ] `meta/skill-auditor` — Revisar y mejorar skills (draft)

### Fase 2 — Engineering Core
- [ ] `engineering/code-review`
- [ ] `engineering/deploy-checklist`
- [ ] `engineering/debug`
- [ ] `engineering/architecture-decision`

### Fase 3 — Data & Content
- [ ] `data/sql-query`
- [ ] `data/report-generation`
- [ ] `content/release-notes`
- [ ] `content/technical-doc`

### Fase 4 — Ops
- [ ] `ops/incident-response`
- [ ] `ops/standup`
- [ ] `ops/sprint-review`

→ Ver [[Roadmap]] para el roadmap expandido con criterios de éxito.

---

## Seguridad y Privacidad

⚠️ El repositorio es **público**. Reglas absolutas:

- **Cero secretos** — API keys, tokens, passwords: nunca en ninguna skill
- **Cero PII** — Nombres reales, emails, teléfonos: fuera
- **Cero datos internos sensibles** — URLs de producción, nombres de hosts, IPs: usar placeholders
- **Regla de oro:** Si no lo publicarías en Twitter, no va en la skill

→ Ver [[Privacy_And_Security]] para el protocolo completo.

---

## Meta

| Campo | Valor |
|-------|-------|
| Autor | Claude (Anthropic) via Cowork |
| Fecha | 2026-06-11 |
| Versión | 1.0 — Genesis |
| Estándar | [agentskills.io](https://agentskills.io) |

---

## Links

- [[Architecture]] — Diseño técnico del repo
- [[Philosophy]] — Filosofía "para y por agentes"
- [[Skill_Catalog]] — Catálogo de skills disponibles
- [[Skill_Format]] — Especificación del formato SKILL.md
- [[Privacy_And_Security]] — Protocolo de privacidad y seguridad
- [[Roadmap]] — Plan de desarrollo de skills
