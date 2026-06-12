# QUALITY_STANDARDS.md

> Checklist de calidad para skills de coferlandia-skills.  
> **Fuente de verdad única del checklist de calidad.** Otros archivos enlazan aquí en vez de
> reproducir la lista. **Todo agente debe verificar estos criterios antes de hacer commit.**
> Lo mecánico de este checklist está automatizado en `_protocol/scripts/validate_skill.py`.

El formato base pertenece a
[agentskills.io/specification](https://agentskills.io/specification). Las reglas de este archivo
son extensiones locales. El runner integral es
`skills/meta/coferlandia-skill-testing/scripts/test_skills.py`.

---

## ⚠️ Seguridad y Privacidad — CRÍTICO

Estas reglas son **no negociables**. Este repositorio es público.

- [ ] **Cero secretos** — La skill NO contiene API keys, tokens, passwords, ni credenciales de ningún tipo
- [ ] **Cero datos personales** — La skill NO contiene nombres reales de personas, emails, teléfonos, documentos de identidad, ni ningún dato personal identificable (PII)
- [ ] **Cero datos sensibles de negocio** — La skill NO expone IPs internas, URLs de producción privadas, nombres de bases de datos reales, ni información que no deba ser pública
- [ ] **Referencias genéricas** — Si la skill menciona sistemas internos, usa placeholders descriptivos (`{DATABASE_URL}`, `{API_ENDPOINT}`) nunca valores reales
- [ ] **No asumir contexto privado** — Las instrucciones de la skill funcionan sin que el agente tenga acceso a información privada hardcodeada

> **Regla de oro:** Si no publicarías ese dato en Twitter, no va en la skill.

### Cómo manejar referencias a sistemas internos

```yaml
# MAL — nunca hacer esto
metadata:
  api_endpoint: https://internal.coferlandia.com/api/v2
  db_host: postgres-prod-01.coferlandia.internal

# BIEN — usar placeholders
metadata:
  api_endpoint: "{COFERLANDIA_API_ENDPOINT}"
  # Configurar en variables de entorno o CLAUDE.md del proyecto
```

Si la skill necesita datos de configuración privados, instrúyela a leerlos de variables de entorno o de un archivo de configuración local (nunca del repositorio).

---

## Formato y Estructura

- [ ] El `name` cumple las reglas de [`NAMING_CONVENTIONS.md`](./NAMING_CONVENTIONS.md) y coincide con el nombre de la carpeta
- [ ] `description` tiene entre 1 y 1024 caracteres
- [ ] `category` es una de: `meta`, `engineering`, `data`, `content`, `design`, `ops`
- [ ] `status` es uno de: `draft`, `active`, `deprecated`
- [ ] `SKILL.md` cumple el límite de tamaño: **objetivo <5000 tokens; tope duro ~500 líneas** (material extenso → `references/`)
- [ ] La skill vive en `skills/{category}/{name}/SKILL.md`

---

## Descripción (Triggering)

- [ ] La `description` incluye keywords explícitos del dominio (herramientas, formatos, verbos de acción)
- [ ] La `description` indica cuándo usar la skill ("Usa cuando...", "Activar cuando el usuario pide...")
- [ ] La `description` menciona casos no-obvios donde aplica, aunque el usuario no use los términos exactos
- [ ] La `description` NO es genérica ("Esta skill ayuda con X") — debe ser específica y accionable
- [ ] El frontmatter no agrega campos fuera de agentskills.io; triggering vive en `description`

---

## Instrucciones

- [ ] Las instrucciones son **procedurales** (cómo hacerlo paso a paso), no declarativas (qué producir)
- [ ] Cada paso es una acción concreta que el agente puede ejecutar
- [ ] La skill enseña un **método reusable** para una clase de problemas, no una solución puntual
- [ ] Existe sección `## Gotchas` con al menos 1 entrada real y concreta
- [ ] Los Gotchas son errores específicos (no consejos genéricos como "maneja errores correctamente")
- [ ] Si hay un output format esperado, existe un **template concreto** (no solo descripción en prosa)
- [ ] Las referencias a `references/` o `assets/` especifican **cuándo** cargarlas, no solo que existen

---

## Contenido — Qué NO debe estar en la skill

- [ ] No contiene conocimiento general que cualquier LLM ya tiene
- [ ] No explica conceptos básicos del dominio (el agente ya los sabe)
- [ ] No cubre todos los edge cases — delega al juicio del agente cuando es razonable
- [ ] No tiene instrucciones contradictorias entre sí

---

## Scripts (si aplica)

- [ ] Los scripts NO tienen prompts interactivos (preguntas al usuario en runtime)
- [ ] Los scripts tienen flag `--help` con: descripción, flags disponibles, ejemplos de uso
- [ ] Los mensajes de error son descriptivos: qué falló + qué se esperaba + qué intentar
- [ ] El output es estructurado (JSON, CSV, TSV) — no texto libre difícil de parsear
- [ ] Los datos van a stdout; los diagnósticos/logs van a stderr
- [ ] Los scripts son idempotentes (pueden reintentarse sin consecuencias)
- [ ] Las dependencias están declaradas inline (PEP 723 para Python, etc.)
- [ ] Scripts destructivos tienen flag `--dry-run` o `--confirm`
- [ ] **Los scripts NO hardcodean secretos, tokens ni datos privados**

---

## Índice y Documentación

- [ ] `skills/INDEX.md` fue actualizado con esta skill
- [ ] La entrada en INDEX.md incluye: nombre, descripción breve, categoría, status
- [ ] El commit sigue el formato: `skill({category}/{name}): descripción`

---

## Test mínimo (verificable)

Una skill no puede marcarse `active` sin evidencia registrada de prueba. El criterio "fue
probada" es inverificable si no queda rastro, así que se registra en el frontmatter:

- [ ] Corrió `_protocol/scripts/validate_skill.py {carpeta}` y salió con código 0
- [ ] Se activó con un prompt natural (sin nombrar la skill) y el output cumplió el formato
- [ ] El resultado quedó registrado en `metadata.tested` con fecha y cómo se probó, p. ej.:
  ```yaml
  metadata:
    status: active
    tested: "2026-06-11 — validada con validate_skill.py; activada con el prompt '...'"
  ```

Si una skill `active` no tiene `metadata.tested`, el validador la marca con un warning.
- [ ] Existe `tests/cases.json` con al menos un prompt positivo y uno negativo

---

## Niveles de status

| Status | Significado |
|--------|-------------|
| `draft` | En desarrollo, no usar en producción |
| `active` | Probada y lista para usar |
| `deprecated` | Reemplazada por otra skill; no usar |
