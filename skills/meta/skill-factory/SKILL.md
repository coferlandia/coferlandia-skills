---
name: skill-factory
description: >
  Crea una nueva Agent Skill en el repositorio coferlandia-skills siguiendo el protocolo
  completo del repo. Usa esta skill cuando: el usuario pide crear una skill nueva, agregar
  una skill al repositorio, definir una skill para un proceso o tarea de Coferlandia, o
  capturar un workflow recurrente como skill reutilizable. Activa incluso si el usuario
  no menciona explícitamente "skill" — basta con que pida "automatizar X", "crear un
  protocolo para Y", o "que los agentes puedan hacer Z de forma consistente".
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repo y git. La validación opcional usa Python 3.11+.
metadata:
  author: coferlandia
  version: "1.1"
  category: meta
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0)."
---

## Contexto

Esta skill guía la creación de nuevas skills en `coferlandia-skills`, un repositorio
público de Agent Skills en formato [agentskills.io](https://agentskills.io).

El repositorio sigue la filosofía "para y por agentes": cualquier agente debe poder
crear una skill correctamente leyendo solo el protocolo del repo, sin instrucciones
adicionales del humano.

**⚠️ Seguridad obligatoria:** Este repositorio es PÚBLICO. Ninguna skill puede contener
secretos, credenciales, datos personales (PII), ni información confidencial de ningún tipo.

## Pasos

### 1. Leer el protocolo

Antes de crear nada, leer estos archivos en orden:

1. `_protocol/NAMING_CONVENTIONS.md` — reglas de nombre y categoría
2. `_protocol/HOW_TO_CREATE_SKILLS.md` — protocolo completo
3. `_protocol/SKILL_TEMPLATE.md` — template a usar

### 2. Definir el scope

Conversar con el usuario (o inferir del contexto) para precisar:

- **¿Qué tarea específica resuelve la skill?**
- **¿Qué conocimiento de Coferlandia necesita el agente?** (APIs, convenciones, schemas, flujos internos)
- **¿En qué categoría va?** (`meta`, `engineering`, `data`, `content`, `design`, `ops`)
- **¿Cómo se llamará?** (seguir reglas de naming: lowercase, hyphens, máx 64 chars)

Si el scope no está claro, hacer máximo 2 preguntas al usuario antes de proceder con una propuesta.

### 3. Crear la estructura

```bash
# Crear directorios (ajustar {categoria} y {nombre-skill})
mkdir -p skills/{categoria}/{nombre-skill}
# Opcional según necesidad:
mkdir -p skills/{categoria}/{nombre-skill}/scripts
mkdir -p skills/{categoria}/{nombre-skill}/references
mkdir -p skills/{categoria}/{nombre-skill}/assets
```

### 4. Escribir SKILL.md

Usar el template de `_protocol/SKILL_TEMPLATE.md`.

Prioridades al escribir el cuerpo:

1. **Contexto específico de Coferlandia** — lo que el agente no sabría sin la skill
2. **Pasos procedurales** — cómo hacerlo, no qué hacer
3. **Gotchas reales** — errores concretos que un agente cometería
4. **Template de output** — si hay un formato esperado, darlo como ejemplo concreto

### 5. Verificar seguridad y privacidad (CRÍTICO)

Antes de guardar, hacer un scan explícito:

- [ ] ¿Contiene API keys, tokens, passwords? → **Eliminar. Nunca.**
- [ ] ¿Contiene nombres reales de personas, emails, teléfonos? → **Eliminar. Usar placeholders.**
- [ ] ¿Contiene URLs internas de producción? → **Reemplazar con `{COFERLANDIA_API_URL}` u similar.**
- [ ] ¿Contiene nombres de bases de datos, hosts, IPs reales? → **Reemplazar con placeholders.**
- [ ] ¿Contiene información que no debería ser pública? → **Eliminar.**

**Regla de oro:** Si no publicarías ese dato en Twitter, no va en la skill.

### 6. Verificar calidad

Ejecutar el checklist de `_protocol/QUALITY_STANDARDS.md`.

Mínimo obligatorio:
- [ ] `name` en frontmatter == nombre de carpeta (exacto)
- [ ] `description` tiene keywords explícitos de cuándo activarla
- [ ] Instrucciones son procedurales
- [ ] Existe sección Gotchas con al menos 1 entrada
- [ ] Sin secretos ni PII de ningún tipo
- [ ] SKILL.md dentro del límite (objetivo <5000 tokens; tope ~500 líneas)

### 7. Actualizar el índice

Agregar la nueva skill a `skills/INDEX.md` usando el **formato de fila definido en la cabecera de
ese archivo** (fuente de verdad única — no inventar otro formato aquí):

```markdown
| [nombre-skill](./{categoria}/{nombre-skill}/) | Descripción breve en una línea | {status} |
```

### 8. Commitear

```bash
git add skills/{categoria}/{nombre-skill}/ skills/INDEX.md
git commit -m "skill({categoria}/{nombre-skill}): {descripción breve en imperativo}"
```

## Gotchas

- **El `name` del frontmatter debe coincidir exactamente con el nombre de la carpeta.** Si no coinciden, los agentes que validan con `skills-ref` reportarán error.
- **La `description` es el mecanismo de activación.** Una description genérica ("esta skill ayuda con X") hace que la skill no se active en el momento correcto. Incluir keywords específicos y condiciones de activación explícitas.
- **No incluir conocimiento que el agente ya tiene.** Las instrucciones deben agregar valor, no repetir lo que cualquier LLM sabe.
- **Las instrucciones deben ser un método, no una solución específica.** La skill debe funcionar para cualquier instancia del tipo de tarea, no solo para el ejemplo concreto.
- **Revisar privacidad antes del commit, no después.** El repositorio es público — una vez pusheado, un secreto expuesto es un incidente de seguridad.

## Output esperado

Una carpeta con la siguiente estructura mínima:

```
skills/{categoria}/{nombre-skill}/
└── SKILL.md          # Con frontmatter válido + instrucciones completas
```

Y `skills/INDEX.md` actualizado con una línea nueva para la skill.

## Validación opcional

Si `skills-ref` está disponible en el entorno:

```bash
# Instalar si no está disponible
npx skills-ref@latest validate skills/{categoria}/{nombre-skill}

# Debe devolver: ✓ Valid skill
```
