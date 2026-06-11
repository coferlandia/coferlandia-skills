# HOW_TO_CREATE_SKILLS.md

> **Protocolo completo para crear una skill en coferlandia-skills.**  
> Cualquier agente de IA puede seguir este protocolo de forma autónoma.

---

## Prerrequisitos

Antes de crear una skill, lee:
- [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md) — reglas de nombre y categoría
- [`SKILL_TEMPLATE.md`](./SKILL_TEMPLATE.md) — template a usar
- [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md) — checklist de calidad

---

## Paso 1: Definir el scope de la skill

Una buena skill encapsula **una unidad coherente de trabajo**. Pregúntate:

- ¿Qué tarea específica resuelve?
- ¿Qué conocimiento de Coferlandia necesita un agente para hacerlo bien?
- ¿Es demasiado estrecha? (forzaría cargar múltiples skills para una tarea)
- ¿Es demasiado amplia? (difícil de activar con precisión)

**Señales de buen scope:**
- Una tarea que un agente haría de 2-5 pasos distintos
- Conocimiento específico de Coferlandia (schemas, APIs internas, convenciones de equipo)
- Un output format que debe ser consistente

**Señales de mal scope:**
- "Todo lo relacionado con X" → demasiado amplio
- Un solo comando bash → demasiado estrecho, úsalo inline

---

## Paso 2: Elegir nombre y categoría

1. Consulta [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md)
2. Elige la categoría correcta: `meta`, `engineering`, `data`, `content`, `design`, `ops`
3. Define el nombre en `lowercase-con-hyphens` (máximo 64 caracteres)
4. Verifica que no existe una skill con ese nombre en `skills/INDEX.md`

**Formato de ruta:** `skills/{categoria}/{nombre-skill}/`

---

## Paso 3: Crear la estructura de carpetas

```bash
mkdir -p skills/{categoria}/{nombre-skill}
# Si la skill tiene scripts:
mkdir -p skills/{categoria}/{nombre-skill}/scripts
# Si tiene referencias externas largas:
mkdir -p skills/{categoria}/{nombre-skill}/references
# Si tiene templates o recursos estáticos:
mkdir -p skills/{categoria}/{nombre-skill}/assets
```

---

## Paso 4: Crear SKILL.md

Copia el template de [`SKILL_TEMPLATE.md`](./SKILL_TEMPLATE.md) y completa cada sección.

### Frontmatter (obligatorio)

```yaml
---
name: {nombre-skill}          # DEBE coincidir con el nombre de la carpeta (ver NAMING_CONVENTIONS.md)
description: >               # Conciso: QUÉ hace + keywords del dominio. Se carga siempre en discovery.
  [Qué hace la skill, con keywords específicos del dominio. Mantenla tensa.]
when_to_use: >              # Reglas de activación detalladas. Campo oficial agentskills.io.
  [Cuándo activarla: "Actívala cuando el usuario pide X", casos no-obvios "aunque no diga Y".]
license: MIT
compatibility: >            # ENTORNO REQUERIDO (binarios, runtime, accesos), no marcas de agentes.
  Requiere {git / Python 3.11+ / acceso al repo / ...}
metadata:
  author: coferlandia
  version: "1.0"
  category: {categoria}
  status: active
  tested: "{fecha} — {cómo se probó}"   # obligatorio para status: active
---
```

> **Triggering:** `description` se carga durante discovery en *todas* las skills a la vez, así que
> consume presupuesto fijo de contexto. Mantenla corta (el "qué") y mueve las reglas de activación
> largas a `when_to_use`, que solo se evalúa al decidir la activación. Ver `vault/Skill_Format.md`.

### Cuerpo de instrucciones

Estructura recomendada:

```markdown
## Contexto

[Qué sabe el agente de Coferlandia gracias a esta skill que no sabría sin ella]

## Pasos

1. Paso concreto
2. Paso concreto
3. Paso concreto

## Gotchas

- [Error común 1 y cómo evitarlo]
- [Error común 2 y cómo evitarlo]

## Output esperado

[Template o descripción del formato de salida]

## Scripts disponibles (si aplica)

- **`scripts/nombre.py`** — Qué hace y cuándo ejecutarlo
```

### Reglas de contenido

**SÍ incluir:**
- Convenciones específicas de Coferlandia
- Gotchas y correcciones a errores típicos
- Templates de output concretos
- Checklists para multi-paso
- Cuándo cargar archivos de `references/` (con condición explícita)

**NO incluir:**
- Conocimiento general que cualquier LLM ya tiene
- Explicaciones de conceptos básicos
- Todo el edge-case handling (delega al juicio del agente cuando es razonable)

**Límite:** Objetivo <5000 tokens; tope duro ~500 líneas en SKILL.md. Material extenso → `references/`

---

## Paso 5: Escribir scripts (si aplica)

Si la skill necesita scripts, ponlos en `scripts/`. Requisitos mínimos:

1. **No pueden tener prompts interactivos** — el agente opera en shell no-interactivo
2. **Deben tener `--help`** documentado
3. **Mensajes de error descriptivos** — el agente usa el error para corregir su siguiente intento
4. **Output estructurado** — preferir JSON/CSV sobre texto libre
5. **Idempotentes** — el agente puede reintentarlos sin consecuencias
6. **Declarar dependencias inline** — usar PEP 723 para Python (`# /// script`), etc.

---

## Paso 6: Verificar calidad

La lista autoritativa está en [`QUALITY_STANDARDS.md`](./QUALITY_STANDARDS.md) — verifícala
completa (no se reproduce aquí para no duplicarla). Primero corre el validador mecánico:

```bash
python _protocol/scripts/validate_skill.py skills/{categoria}/{nombre-skill}
# debe salir con código 0 (sin errores)
```

---

## Paso 7: Actualizar el índice

**Obligatorio.** Agrega la skill a `skills/INDEX.md`. El **formato de fila está definido en la
cabecera de `INDEX.md`** (fuente de verdad única) — úsalo desde ahí, no lo copies aquí. En
resumen: `| [nombre-skill](./{categoria}/{nombre-skill}/) | Descripción breve | {status} |`.

---

## Paso 8: Commitear

Formato de commit:

```
skill({categoria}/{nombre-skill}): agregar skill de {qué hace}
```

Ejemplo:
```
skill(engineering/code-review): agregar skill de review con estándares Coferlandia
```

---

## Notas para el agente

- Si encuentras un error en una skill existente mientras trabajas, corrígelo y agrega un Gotcha
- Si el scope de lo que necesitas crear no encaja en ninguna categoría, propón una nueva en `Genesis_Plan.md`
- La skill `skills/meta/skill-factory/` existe para automatizar este proceso — úsala si está disponible
