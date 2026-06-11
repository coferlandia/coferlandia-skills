# SKILL_LIFECYCLE.md

> Estados de una skill y cómo transicionar entre ellos.

---

## Estados

```
draft ──→ active ──→ deprecated
  ↑           │
  └───────────┘ (iteración)
```

| Estado | Descripción | Cuándo usar |
|--------|-------------|------------|
| `draft` | En desarrollo. Puede tener instrucciones incompletas | Al crear una skill nueva |
| `active` | Probada, completa, lista para producción | Tras pasar el checklist de QUALITY_STANDARDS.md |
| `deprecated` | Reemplazada o desactualizada | Cuando una skill es superada por otra mejor |

El estado va en el frontmatter de `SKILL.md`:
```yaml
metadata:
  status: active
```

---

## Ciclo de vida típico

### 1. Creación (`draft`)

- Un agente o humano identifica la necesidad de una skill
- Se sigue el protocolo en `HOW_TO_CREATE_SKILLS.md`
- La skill se crea con `status: draft`
- Se hace commit con mensaje: `skill(category/name): crear skill en draft`

### 2. Activación (`active`)

- Se prueba la skill con al menos un caso real
- Se verifica el checklist completo en `QUALITY_STANDARDS.md`
- Se actualiza `status: active` en el frontmatter
- Se actualiza `skills/INDEX.md`
- Commit: `skill(category/name): activar skill tras verificación`

### 3. Iteración

- Al encontrar un error → agregar Gotcha y hacer commit
- Al mejorar instrucciones → actualizar `version` en metadata
- Al agregar scripts → documentar en `SKILL.md`
- Commit: `skill(category/name): corregir {qué}`

### 4. Deprecación (`deprecated`)

- La skill ya no es relevante, o fue superada por otra
- Actualizar `status: deprecated`
- Agregar al inicio del cuerpo de `SKILL.md`:
  ```
  > ⚠️ **DEPRECATED** — Usar `skills/{categoria}/{nueva-skill}/` en su lugar.
  ```
- Commit: `skill(category/name): deprecar, reemplazada por {nueva-skill}`
- Mantener el archivo (no eliminar) para referencia histórica

---

## Responsabilidad del agente durante iteración

Cuando un agente usa una skill y encuentra un error o comportamiento inesperado:

1. **Corregir** el problema en el momento
2. **Documentar** el error como Gotcha en `SKILL.md`
3. **Actualizar** la versión minor (e.g., `1.0` → `1.1`)
4. **Commitear** con el formato: `skill(category/name): agregar gotcha sobre {qué}`

Esto es parte del ciclo "por agentes" — cada agente que usa una skill contribuye a mejorarla.
