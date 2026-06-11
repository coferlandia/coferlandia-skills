---
tags: [arquitectura, estructura, coferlandia]
created: 2026-06-11
---

# Architecture — coferlandia-skills

---

## Estructura de carpetas

```
coferlandia-skills/
│
├── AGENTS.md                   ← Entry point para agentes (leer primero)
├── README.md                   ← Overview para humanos
├── Genesis_Plan.md             ← Documento fundacional
│
├── _protocol/                  ← Protocolo del repo (solo instrucciones, no skills)
│   ├── HOW_TO_CREATE_SKILLS.md ← Protocolo completo de creación
│   ├── SKILL_TEMPLATE.md       ← Template a copiar
│   ├── QUALITY_STANDARDS.md    ← Checklist de calidad + seguridad
│   ├── NAMING_CONVENTIONS.md   ← Reglas de naming y categorías
│   └── SKILL_LIFECYCLE.md      ← draft → active → deprecated
│
├── skills/                     ← Todas las skills viven aquí
│   ├── INDEX.md                ← Catálogo completo (actualizar siempre)
│   ├── meta/                   ← Skills sobre skills
│   │   ├── skill-factory/      ← Crear nuevas skills
│   │   └── skill-auditor/      ← Revisar y mejorar skills
│   ├── engineering/
│   ├── data/
│   ├── content/
│   ├── design/
│   └── ops/
│
└── vault/                      ← Obsidian vault
    ├── Genesis_Plan.md
    ├── Architecture.md         ← Este archivo
    ├── Philosophy.md
    ├── Skill_Catalog.md
    ├── Skill_Format.md
    ├── Privacy_And_Security.md
    └── Roadmap.md
```

---

## Flujo de un agente llegando al repo

```
Agente llega al repo
        │
        ▼
Lee AGENTS.md
        │
        ├── ¿Necesita usar una skill? ──→ Lee skills/INDEX.md ──→ Activa skill
        │
        └── ¿Necesita crear una skill? ──→ Lee _protocol/ ──→ Crea skill
```

---

## Separación de responsabilidades

| Directorio | Propósito | ¿Agentes lo modifican? |
|-----------|-----------|----------------------|
| `_protocol/` | Instrucciones del repo | No (solo humanos o meta-skills) |
| `skills/` | Las skills en sí | Sí (skill-factory, skill-auditor) |
| `vault/` | Documentación Obsidian | No (refleja el estado del repo) |

---

## Compatibilidad con agentskills.io

El repo implementa el estándar abierto [agentskills.io](https://agentskills.io):

- Cada skill es una carpeta con `SKILL.md`
- Frontmatter YAML con `name` y `description` obligatorios
- Directorio de skills configurable en cada agente

**Convenciones de directorio por agente:**

| Agente | Directorio default | Config en coferlandia |
|--------|-------------------|----------------------|
| VS Code / GitHub Copilot | `.agents/skills/` | Symlink o config |
| Claude Code | Configurable | Apuntar a `skills/` |
| Cursor | `.cursorrules` + skills | Configurable |
| Gemini CLI | Configurable | Apuntar a `skills/` |

---

## Links

- [[Genesis_Plan]] — El plan fundacional
- [[Philosophy]] — Por qué esta arquitectura
- [[Skill_Format]] — Especificación técnica de SKILL.md
