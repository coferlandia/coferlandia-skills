---
name: skill-auditor
description: >
  Revisa y mejora skills existentes en coferlandia-skills. Usa cuando: una skill no
  se activa correctamente, las instrucciones producen resultados inconsistentes, hay que
  mejorar la description para mejor triggering, agregar gotchas tras encontrar errores en
  producción, o hacer un audit de calidad del repositorio completo. Activa también cuando
  el usuario pide "mejorar X skill", "la skill Y no funciona bien", o "revisar las skills".
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repo y git. La validación usa Python 3.11+.
metadata:
  author: coferlandia
  version: "1.0"
  category: meta
  status: draft
---

## Contexto

Esta skill audita y mejora skills existentes en `coferlandia-skills`.

El objetivo es mantener el repositorio en un estado de alta calidad: skills con buenos
descriptions que se activan correctamente, instrucciones procedurales claras, y gotchas
actualizados con errores reales encontrados en uso.

**⚠️ Seguridad obligatoria:** Al revisar skills, verificar que no contengan secretos,
PII ni datos confidenciales. Si se encuentran, eliminarlos inmediatamente y hacer commit
separado con mensaje: `security: eliminar {tipo de dato} de skill/{nombre}`.

## Pasos

### Audit de una skill específica

1. Leer `_protocol/QUALITY_STANDARDS.md` completo
2. Leer la skill objetivo (`skills/{categoria}/{nombre}/SKILL.md`)
3. Evaluar cada punto del checklist de QUALITY_STANDARDS.md
4. Documentar los puntos que fallan
5. Hacer las correcciones necesarias
6. Actualizar `version` en metadata (minor bump: `1.0` → `1.1`)
7. Commit: `skill(categoria/nombre): mejorar {qué se mejoró}`

### Audit de description (triggering)

Si la skill no se activa correctamente:

1. Evaluar la `description` actual: ¿tiene keywords del dominio? ¿indica cuándo activarla?
2. Proponer nueva description que:
   - Usa lenguaje imperativo ("Usa cuando...", "Activa cuando el usuario pide...")
   - Incluye keywords específicos del dominio
   - Menciona casos no-obvios de activación
   - No excede 1024 caracteres
3. Actualizar la description en el frontmatter
4. Commit: `skill(categoria/nombre): mejorar description para mejor triggering`

### Audit completo del repositorio

1. Correr el validador mecánico sobre todo el repo y partir de su salida JSON:
   ```bash
   python _protocol/scripts/validate_skill.py --all skills
   ```
   Cubre: `name`==carpeta, campos de frontmatter, límite de tamaño, scan de secretos/PII, y
   warnings de `active` sin `tested`.
2. Para lo que el validador NO chequea (juicio), revisar cada skill `active`:
   - La `description` tiene keywords de activación y no menciona el nombre de la skill
   - Existe sección Gotchas con errores reales
   - Las instrucciones son procedurales, no declarativas
3. Reportar los hallazgos en un resumen estructurado
4. Priorizar correcciones por impacto

## Gotchas

- **Los gotchas son la parte más valiosa de una skill.** Priorizarlos cuando haya que cortar contenido para llegar al límite de tamaño (~500 líneas / <5000 tokens).
- **Nunca cortar el contexto específico de Coferlandia.** Si algo parece redundante pero captura una convención interna, mantenerlo.
- **La description NO debe mencionar el nombre de la skill.** El agente ya sabe el nombre — la description debe describir la tarea del usuario, no el nombre de la herramienta.
- **Al agregar un gotcha, usar el error real.** "La tabla X usa soft deletes" es útil. "Maneja los edge cases correctamente" no lo es.

## Output esperado

Resumen de audit:

```
## Audit: {nombre-skill}

### Puntos OK
- [x] name coincide con carpeta
- [x] description tiene keywords

### Puntos a mejorar
- [ ] Gotchas: solo tiene 1, agregar más
- [ ] SKILL.md tiene 620 líneas (límite 500)

### Correcciones aplicadas
- Agregado gotcha sobre {qué}
- Movido sección X a references/

### Security scan
- Sin secretos detectados
- Sin PII detectada
```
