# NAMING_CONVENTIONS.md

> Reglas de naming para skills en coferlandia-skills.
> **Fuente de verdad única del naming.** Cualquier otro archivo que necesite estas reglas las
> enlaza a este documento; no las reproduce (evita que las copias se contradigan).

---

## Reglas del campo `name`

El campo `name` en el frontmatter de `SKILL.md` debe:

- Usar solo: letras minúsculas (`a-z`), números (`0-9`), y guiones (`-`)
- NO usar: mayúsculas, espacios, underscores, puntos, ni ningún otro carácter especial
- NO empezar ni terminar con guión
- NO tener guiones consecutivos (`--`)
- Tener máximo 64 caracteres
- **Coincidir exactamente con el nombre de la carpeta que la contiene**

```yaml
# Válidos
name: code-review
name: sql-query
name: skill-factory
name: deploy-checklist

# Inválidos
name: Code-Review       # mayúsculas
name: sql_query         # underscore
name: -deploy           # empieza con guión
name: deploy-           # termina con guión
name: deploy--checklist # guiones dobles
```

---

## Categorías disponibles

| Categoría | Directorio | Qué va aquí |
|-----------|------------|-------------|
| `meta` | `skills/meta/` | Skills sobre skills: crear, auditar, mejorar skills |
| `engineering` | `skills/engineering/` | Código, infraestructura, arquitectura, debugging |
| `data` | `skills/data/` | Análisis de datos, pipelines, queries, reportes |
| `content` | `skills/content/` | Escritura, documentación, comunicación, release notes |
| `design` | `skills/design/` | UX, producto, diseño visual, copy |
| `ops` | `skills/ops/` | Operaciones, automatizaciones, incidentes, standups |

Si tu skill no encaja en ninguna categoría, propón una nueva en `vault/Genesis_Plan.md`.

### Regla de desempate de categoría

Si una skill encaja en dos categorías, decide de forma determinista (para que dos agentes
elijan igual):

1. **Por el artefacto que produce:** código/infra → `engineering`; texto/comunicación →
   `content`; análisis o datos tabulares → `data`; UX/visual → `design`; proceso o
   automatización operacional → `ops`; skills sobre el propio repo o sobre otras skills → `meta`.
2. **Ante empate persistente:** elige la categoría que aparezca primero en la tabla de arriba.

---

## Convención de ruta completa

```
skills/{categoría}/{nombre-skill}/SKILL.md
```

Ejemplos:
```
skills/meta/skill-factory/SKILL.md
skills/engineering/code-review/SKILL.md
skills/data/sql-query/SKILL.md
skills/content/release-notes/SKILL.md
```

---

## Convención de commits

```
skill({categoría}/{nombre}): descripción corta en imperativo
```

Ejemplos:
```
skill(meta/skill-factory): agregar skill de creación automática de skills
skill(engineering/code-review): agregar checklist de seguridad
skill(data/sql-query): corregir gotcha de soft deletes
```

---

## Convención de versiones (metadata)

```yaml
metadata:
  version: "1.0"    # primera versión
  version: "1.1"    # bugfix o mejora menor
  version: "2.0"    # cambio significativo en instrucciones
```

---

## Nombres que evitar

- Evitar nombres muy genéricos: `helper`, `utils`, `misc`
- Evitar nombres que dupliquen la categoría: `engineering-code-review` (la categoría ya implica `engineering`)
- Evitar abreviaciones poco claras: `cr` en lugar de `code-review`
