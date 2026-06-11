# AGENTS.md — Coferlandia Skills Repository

> **Si eres un agente de IA, empieza aquí.**

Este archivo es tu punto de entrada a `coferlandia-skills`. Léelo completo antes de hacer cualquier cosa.

---

## Qué es este repositorio

Un repositorio de **Agent Skills** en formato [agentskills.io](https://agentskills.io), construido para ser usado y mantenido por agentes de IA. Cada skill es un conjunto de instrucciones especializadas que puedes cargar para ejecutar tareas específicas de Coferlandia con mayor precisión.

**Filosofía:** Este repo es *para agentes* y *por agentes*. Tienes toda la información necesaria para crear nuevas skills, mejorar las existentes y mantener el índice — sin necesidad de instrucciones adicionales del humano.

---

## Mapa del repositorio

```
coferlandia-skills/
├── AGENTS.md              ← Estás aquí
├── README.md              ← Overview para humanos
├── Genesis_Plan.md        ← Visión y arquitectura completa del repo
│
├── _protocol/             ← Lee esto antes de crear o modificar skills
│   ├── HOW_TO_CREATE_SKILLS.md   ← Protocolo completo de creación
│   ├── SKILL_TEMPLATE.md         ← Template listo para copiar
│   ├── QUALITY_STANDARDS.md      ← Checklist de calidad
│   ├── NAMING_CONVENTIONS.md     ← Reglas de naming
│   └── SKILL_LIFECYCLE.md        ← Estados de una skill
│
└── skills/                ← Todas las skills
    ├── INDEX.md           ← Catálogo completo (actualizar siempre)
    ├── meta/              ← Skills sobre skills
    ├── engineering/
    ├── data/
    ├── content/
    ├── design/
    └── ops/
```

---

## Cómo usar una skill existente

1. Lee `skills/INDEX.md` para descubrir skills disponibles
2. Navega a la carpeta de la skill relevante
3. Lee su `SKILL.md` completo
4. Sigue las instrucciones

---

## Cómo crear una skill nueva

1. Lee `_protocol/HOW_TO_CREATE_SKILLS.md` — contiene el protocolo completo
2. Usa `_protocol/SKILL_TEMPLATE.md` como punto de partida
3. Verifica tu skill contra `_protocol/QUALITY_STANDARDS.md` y corre `_protocol/scripts/validate_skill.py`
4. Actualiza `skills/INDEX.md`
5. Alternativamente: activa la skill `skills/meta/skill-factory/` que automatiza este proceso

Para entender *cómo* está diseñado este repo (y por qué evita duplicar reglas), estudia
`skills/meta/build-agentic-repo/` — es la skill ejemplar y el repo practica lo que ella enseña.

---

## Fuente de verdad por regla

Cada regla vive en **un solo archivo dueño**. Este entry point y cualquier otro documento
*enlazan* a ese dueño en lugar de copiar la regla (así una copia no puede contradecir a otra):

| Regla | Dueño |
|-------|-------|
| Naming, categorías y desempate | [`_protocol/NAMING_CONVENTIONS.md`](./_protocol/NAMING_CONVENTIONS.md) |
| Checklist de calidad y seguridad | [`_protocol/QUALITY_STANDARDS.md`](./_protocol/QUALITY_STANDARDS.md) |
| Formato de SKILL.md y disclosure progresivo | [`vault/Skill_Format.md`](./vault/Skill_Format.md) |
| Inventario de skills y formato de su fila | [`skills/INDEX.md`](./skills/INDEX.md) |
| Estados del ciclo de vida | [`_protocol/SKILL_LIFECYCLE.md`](./_protocol/SKILL_LIFECYCLE.md) |
| Invariantes mecánicos (ejecutable) | [`_protocol/scripts/validate_skill.py`](./_protocol/scripts/validate_skill.py) |

---

## Índice rápido de skills

Ver `skills/INDEX.md` para el catálogo completo y actualizado (fuente de verdad única).
