---
tags: [formato, especificacion, agentskills]
created: 2026-06-11
---

# Skill Format — Especificación

> Referencia técnica del formato SKILL.md. Fuente: [agentskills.io/specification](https://agentskills.io/specification)

---

## Estructura de carpeta

```
skill-name/
├── SKILL.md          ← Requerido
├── scripts/          ← Opcional: scripts ejecutables
├── references/       ← Opcional: documentación extensa
└── assets/           ← Opcional: templates, recursos
```

---

## Frontmatter SKILL.md

| Campo | Requerido | Restricciones |
|-------|-----------|---------------|
| `name` | ✅ | Lowercase, hyphens, 1-64 chars, coincide con carpeta |
| `description` | ✅ | 1-1024 chars. QUÉ hace (conciso) — se carga siempre en discovery |
| `when_to_use` | No (recomendado) | Reglas de activación detalladas. Descarga la `description` |
| `license` | No | Nombre de licencia o referencia a archivo |
| `compatibility` | No | 1-500 chars. **Entorno requerido** (binarios/runtime/accesos), no marcas de agentes |
| `metadata` | No | Key-value libre (category, version, status, `tested`) |
| `allowed-tools` | No | Restringe qué tools puede usar la skill (seguridad) |

> `metadata.tested` registra la evidencia de prueba (`"<fecha> — <cómo>"`); obligatorio para
> `status: active`. Hace verificable un criterio que de otro modo nadie puede comprobar.

### Reglas del `name`

- Solo: `a-z`, `0-9`, `-`
- Sin mayúsculas, sin espacios, sin underscores
- Sin `-` al inicio o final
- Sin `--` (guiones dobles)
- Máximo 64 caracteres
- **Debe coincidir exactamente con el nombre de la carpeta**

### Buena `description`

```yaml
# Bien: específica, con keywords, indica cuándo activar
description: >
  Analiza archivos CSV y datos tabulares — calcula estadísticas, agrega
  columnas derivadas, genera gráficos y limpia datos sucios. Usar cuando
  el usuario tiene un CSV, TSV o Excel y quiere explorar, transformar o
  visualizar los datos, incluso si no menciona explícitamente "CSV" o "análisis".

# Mal: genérica, sin keywords, no indica cuándo
description: Ayuda con archivos de datos.
```

### `description` vs `when_to_use` — presupuesto de discovery

Toda `description` se carga durante discovery, en **todas** las skills a la vez (~100 tokens ×
N). Por eso es un costo fijo que escala con el tamaño del repo: mantén `description` tensa con el
"qué hace". Las reglas de activación largas (casos no-obvios, sinónimos, "aplica aunque digan X")
van en `when_to_use`, que solo se evalúa al decidir si activar — no infla el costo de discovery.

---

## Progressive Disclosure en la práctica

```
tokens usados por skill durante discovery: ~100
  └─ name + description

tokens usados al activar: <5000 (recomendado)
  └─ cuerpo completo de SKILL.md

tokens adicionales al ejecutar: on demand
  └─ scripts/, references/, assets/
     cargados solo cuando la instrucción lo dice explícitamente
```

**Implicación:** objetivo <5000 tokens; tope duro ~500 líneas en SKILL.md. Material extenso →
`references/`.

Cuando referencies un archivo de `references/`, especifica cuándo cargarlo:
```markdown
Leer `references/api-errors.md` si la API retorna código no-200.
```
No:
```markdown
Ver `references/` para más detalles.
```

---

## Patrones de instrucciones

### Checklist para multi-paso
```markdown
- [ ] Paso 1: ejecutar análisis
- [ ] Paso 2: crear plan
- [ ] Paso 3: validar plan
- [ ] Paso 4: ejecutar
```

### Gotchas
```markdown
## Gotchas
- La tabla `users` usa soft deletes. Toda query debe incluir `WHERE deleted_at IS NULL`.
- El campo `user_id` en la DB se llama `uid` en el auth service y `accountId` en billing.
```

### Template de output
````markdown
## Output esperado
```markdown
# [Título]
## Resumen ejecutivo
[Un párrafo]
## Hallazgos
- Hallazgo 1
```
````

### Plan-validate-execute
```markdown
1. Generar plan: `scripts/plan.py input.json` → `plan.json`
2. Validar: `scripts/validate.py plan.json`
3. Si falla: corregir `plan.json` y volver a 2
4. Ejecutar: `scripts/execute.py plan.json`
```

---

## Links

- [[Genesis_Plan]]
- [[Architecture]]
- [Especificación oficial](https://agentskills.io/specification)
- [Best practices](https://agentskills.io/skill-creation/best-practices)
