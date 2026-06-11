---
tags: [privacidad, seguridad, coferlandia]
created: 2026-06-11
priority: crítico
---

# Privacidad y Seguridad

> Este repositorio es **público**. Las reglas de privacidad son absolutas y no negociables.

---

## Regla de Oro

> Si no publicarías ese dato en Twitter, no va en ninguna skill.

---

## Qué NUNCA puede estar en una skill

| Tipo de dato | Ejemplos | Acción |
|-------------|---------|--------|
| Credenciales | API keys, tokens, passwords, OAuth secrets | Eliminar. Usar variables de entorno. |
| PII | Nombres reales, emails, teléfonos, RUT, pasaporte | Eliminar. Usar datos ficticios en ejemplos. |
| Datos internos sensibles | URLs de producción, IPs, nombres de hosts | Reemplazar con placeholders. |
| Datos de negocio confidenciales | Revenue real, datos de clientes, contratos | No van. Nunca. |

---

## Cómo referenciar configuración privada

**Mal (nunca hacer esto):**
```yaml
metadata:
  api_url: https://internal.coferlandia.com/api/v2
  db_password: s3cr3t_password_real
```

**Bien (usar placeholders):**
```yaml
metadata:
  api_url: "{COFERLANDIA_API_URL}"
  # Configurar COFERLANDIA_API_URL en variables de entorno o CLAUDE.md local (no commitear)
```

**En instrucciones:**
```markdown
## Pasos
1. Exportar la variable: `export COFERLANDIA_API_URL=https://tu-endpoint.com`
2. Ejecutar: `python scripts/query.py --endpoint $COFERLANDIA_API_URL`
```

---

## Protocolo de revisión de seguridad

Todo agente que cree o modifique una skill debe hacer este scan explícito antes del commit:

- [ ] ¿Contiene strings que parecen API keys o tokens? (patrones: `sk-`, `ghp_`, UUIDs largos, strings de 32+ chars alfanuméricos)
- [ ] ¿Contiene emails con dominios reales?
- [ ] ¿Contiene URLs con dominios internos o de producción?
- [ ] ¿Contiene nombres de personas reales?
- [ ] ¿Contiene números que parecen documentos de identidad, teléfonos, o tarjetas?

Si alguna respuesta es sí → eliminar el dato y reemplazar con placeholder antes de commitear.

---

## Si se encuentra un secreto en el repo

1. NO hacer más commits hasta resolver
2. Eliminar el secreto del archivo
3. Commitear: `security: eliminar credencial expuesta de skill/{nombre}`
4. Notificar al equipo para rotar el secreto comprometido
5. Verificar el git history — si el secreto ya fue pusheado, debe rotarse

---

## Datos ficticios en ejemplos

Cuando una skill necesita mostrar ejemplos con datos parecidos a reales, usar:

- **Emails:** `usuario@example.com`, `agente@coferlandia.test`
- **Nombres:** `Juan Ejemplo`, `María Test`
- **URLs:** `https://api.coferlandia.example.com`
- **IDs:** `usr_00000000`, `proj_XXXXXXXX`
- **Tokens:** `{API_KEY}`, `{AUTH_TOKEN}`

---

## Links

- [[Genesis_Plan]] — El plan fundacional
- [[Philosophy]] — Por qué la privacidad es un valor, no una restricción
