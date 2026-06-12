# SKILL_TEMPLATE.md

> Copia este template para crear una nueva skill.  
> Reemplaza todo lo que está entre `{llaves}` con valores reales.  
> Elimina las líneas de comentario (`<!-- -->`) antes de guardar.

---

## Template de SKILL.md

```markdown
---
name: {nombre-skill}
<!-- Reglas de naming: ver _protocol/NAMING_CONVENTIONS.md (fuente de verdad). Coincide con la carpeta. -->
description: >
  {QUÉ hace la skill y CUÁNDO usarla, con keywords específicos del dominio.}
  {Máximo 1024 caracteres. Mencionar casos no-obvios sin inventar campos adicionales.}
license: MIT
compatibility: >
  <!-- ENTORNO REQUERIDO, no marcas de agentes. Ej: "Requiere git y Python 3.11+". -->
  Requiere {dependencias/accesos reales}
metadata:
  author: coferlandia
  version: "1.0"
  category: {meta|engineering|data|content|design|ops}
  status: active
  tested: "{fecha} — {cómo se probó}"   # obligatorio si status: active
---

## Contexto

<!-- Qué sabe el agente gracias a esta skill. Solo lo que no sabría sin ella. -->
{Descripción del conocimiento específico de Coferlandia que aporta esta skill:
convenciones del equipo, APIs internas, schemas, patrones establecidos, etc.}

## Prerequisitos

<!-- Eliminar esta sección si no aplica -->
- {Herramienta o acceso requerido}
- {Versión mínima si es relevante}

## Pasos

<!-- Instrucciones procedurales. Cada paso es una acción concreta del agente. -->

1. {Primer paso concreto}
2. {Segundo paso concreto}
3. {Tercer paso concreto}

<!-- Si hay un workflow con validación intermedia, usar este patrón: -->
<!--
1. Ejecutar: `scripts/analyze.py {input}`
2. Revisar output y crear plan en `plan.json`
3. Validar: `scripts/validate.py plan.json`
4. Si falla validación: corregir `plan.json` y volver a paso 3
5. Ejecutar: `scripts/execute.py plan.json`
-->

## Gotchas

<!-- Esta sección es obligatoria. Mínimo 1 entrada. -->
<!-- Incluir errores reales que un agente cometería sin esta información. -->

- **{Error común 1}:** {Qué pasa y cómo evitarlo}
- **{Error común 2}:** {Qué pasa y cómo evitarlo}

## Output esperado

<!-- Template concreto del output. Más útil que una descripción en prosa. -->

{Si aplica, pegar aquí un template o ejemplo de output:}

```
{ejemplo de formato de output}
```

## Scripts disponibles

<!-- Eliminar esta sección si la skill no tiene scripts -->

- **`scripts/{nombre}.py`** — {Qué hace. Ejecutar cuando: condición específica}

Uso:
\```bash
python scripts/{nombre}.py --help
\```

## Referencias

<!-- Eliminar esta sección si no hay references/ -->
<!-- Siempre indicar CUÁNDO cargar cada referencia, no solo que existe -->

- Leer `references/{archivo}.md` cuando: {condición específica que dispara la carga}
```

---

## Checklist antes de guardar

La lista autoritativa está en [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md); no se reproduce
aquí para no duplicarla. Atajo: corre el validador, que cubre todo lo mecánico —

```bash
python skills/meta/coferlandia-skill-testing/scripts/test_skills.py .   # código 0 = OK
```

Lo que el validador no puede chequear y debes revisar a mano: que las instrucciones sean
procedurales, que los Gotchas sean errores reales, y que actualizaste `skills/INDEX.md`.
