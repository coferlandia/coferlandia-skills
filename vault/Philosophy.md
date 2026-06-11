---
tags: [coferlandia, filosofia, agentes]
created: 2026-06-11
---

# Filosofía: Para y Por Agentes

> El repositorio como ecosistema autónomo de conocimiento.

---

## La Premisa

Los agentes de IA son cada vez más capaces — pero frecuentemente carecen del **contexto específico** para hacer trabajo real en un entorno particular. Un agente que no conoce tus convenciones internas, tus APIs propias, tus gotchas de proyecto, producirá resultados genéricos.

Las Agent Skills resuelven esto empaquetando conocimiento específico en instrucciones portables. `coferlandia-skills` lleva esta idea un paso más allá: **el propio repositorio enseña a los agentes a crear más conocimiento.**

---

## Para Agentes

Las skills no son documentación para humanos. Son **instrucciones ejecutables** para agentes:

- Lenguaje imperativo y procedural: "Ejecuta X. Si falla, haz Y."
- Sin explicaciones de conceptos básicos — el agente ya los sabe
- Con el contexto específico de Coferlandia que el agente *no* tendría sin la skill
- Con templates de output concretos — el agente pattern-matchea mejor contra ejemplos

## Por Agentes

El repo está diseñado para que los agentes contribuyan a él:

- `AGENTS.md` es el entry point que cualquier agente lee al llegar al repo
- `_protocol/` contiene instrucciones completas para crear, auditar y mantener skills
- `skills/meta/skill-factory/` es la skill que permite crear más skills
- Cada agente que usa una skill y encuentra un error puede agregar un Gotcha

El ciclo ideal: **agente usa skill → encuentra problema → agrega Gotcha → próximo agente se beneficia.**

---

## Progressive Disclosure

Inspirado en el estándar agentskills.io, el repo maximiza la información disponible minimizando el uso de context window:

```
Nivel 1 — Discovery    (~100 tokens/skill)
  └─ name + description de cada skill
  
Nivel 2 — Activation   (<5000 tokens)
  └─ Cuerpo completo de SKILL.md
  
Nivel 3 — Execution    (on demand)
  └─ scripts/, references/, assets/
     cargados solo cuando la instrucción lo indica
```

---

## Privacidad como Valor Fundacional

El repo es público. Esto no es una limitación técnica — es una elección filosófica: el conocimiento de proceso debe ser compartible. Lo que no es compartible (secretos, PII, datos confidenciales) **nunca debe llegar a una skill**.

→ [[Privacy_And_Security]]

---

## Links

- [[Genesis_Plan]] — El plan fundacional
- [[Architecture]] — Cómo se implementa esta filosofía
- [[Privacy_And_Security]] — La dimensión de seguridad de la filosofía
