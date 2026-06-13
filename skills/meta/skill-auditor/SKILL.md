---
name: skill-auditor
description: >
  Revisa, mejora y modifica skills existentes en coferlandia-skills sin romper su comportamiento.
  Usa cuando: una skill no se activa correctamente, las instrucciones producen resultados
  inconsistentes, hay que mejorar la description para mejor triggering, agregar gotchas tras
  errores en producción, hacer un audit de calidad del repositorio, o cambiar/refactorizar/
  extender/corregir una skill ya creada de forma conservadora. Activa también cuando el usuario
  pide "mejorar X skill", "la skill Y no funciona bien", "revisar las skills", "agregar algo a la
  skill Z", "refactorizar la skill", o "cambiar el comportamiento de una skill sin romper lo que ya
  hace". Para crear una skill desde cero, usar skill-factory en su lugar.
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repo y git. La validación usa Python 3.11+.
metadata:
  author: coferlandia
  version: "1.1"
  category: meta
  status: active
  tested: "2026-06-13 — validada con validate_skill.py (exit 0); activada con el prompt 'agregá un modo de modificación cuidadosa a una skill sin romperla' y con 'auditá la calidad de las skills', ambos enrutaron al modo correcto"
---

## Contexto

Esta skill **audita y modifica** skills existentes en `coferlandia-skills`. Tiene dos
responsabilidades distintas y dos modos:

- **Modo auditoría** — trabajo de calidad, mayormente de lectura: descriptions que activan bien,
  instrucciones procedurales claras, gotchas con errores reales. Barato y de bajo riesgo.
- **Modo cirugía** — modificación estructural de una skill que ya funciona: agregar capacidades,
  corregir comportamiento, refactorizar, integrar con otras skills. Caro y con riesgo de regresión.

**Principio central:** no se modifica un skill sin haberlo entendido. La calidad de una intervención
no se mide por cuántos cambios hace, sino por cuántos cambios innecesarios evita y por la precisión
de los que sí decide hacer. Para crear una skill nueva desde cero, esta no es la skill — usar
`skills/meta/skill-factory/`.

**⚠️ Seguridad obligatoria:** Al revisar o modificar skills, verificar que no contengan secretos,
PII ni datos confidenciales (ver `_protocol/QUALITY_STANDARDS.md` → sección Seguridad). Si se
encuentran, eliminarlos inmediatamente y hacer commit separado: `security: eliminar {tipo de dato}
de skill/{nombre}`.

## Paso 0 — Clasificar el cambio (gate de proporcionalidad)

Antes de tocar nada, decidir el carril. Es la decisión más importante de esta skill.

- **Carril rápido** — cambio trivial, localizado y reversible que NO altera qué hace la skill:
  corregir un typo, agregar un gotcha, ajustar el wording de la `description`, aclarar un paso ya
  existente, bump de versión. → Aplicar directo (ver Modo auditoría), validar, commit. No requiere
  protocolo quirúrgico.

- **Carril quirúrgico** — el cambio toca el **propósito**, el **alcance**, el **flujo operativo**,
  los **contratos con otras skills**, o **elimina/altera comportamiento existente**. → Seguir el
  Modo cirugía completo.

**Regla:** ante la duda, subir de carril, nunca bajar. Un cambio que parece cosmético pero cambia
cuándo se activa la skill es quirúrgico, no rápido.

---

## Modo auditoría

### Audit de una skill específica

1. Leer `_protocol/QUALITY_STANDARDS.md` completo
2. Leer la skill objetivo (`skills/{categoria}/{nombre}/SKILL.md`)
3. Evaluar cada punto del checklist de QUALITY_STANDARDS.md
4. Documentar los puntos que fallan
5. Hacer las correcciones necesarias (carril rápido; si una corrección resulta ser estructural,
   pasar a Modo cirugía)
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

---

## Modo cirugía

Para cambios del carril quirúrgico. Las fases son obligatorias en orden; cada una produce una
salida breve. No saltarse la 1 ni la 5.

1. **Entender.** Leer la skill objetivo completa + sus `references/`, `tests/` y scripts +
   `_protocol/QUALITY_STANDARDS.md`. Mapear: propósito declarado, responsabilidades, flujo,
   entradas/salidas, dependencias con otras skills, **contratos implícitos** que otros agentes
   esperan, comportamientos que deben preservarse, ambigüedades y contradicciones. No proponer nada
   hasta poder explicar qué hace hoy la skill.

2. **Criticar la necesidad.** ¿El cambio pertenece a *esta* skill? Considerar alternativas: (a) no
   modificar, (b) ajustar documentación, (c) crear una skill nueva (`skill-factory`), (d) cirugía
   mínima. Recomendar una y justificar. Ser honesto: si no conviene modificar, decirlo.

3. **Aclarar (solo lo crítico).** Si falta información sin la cual el cambio es peligroso, preguntar:
   qué debe preservarse, qué debe cambiar, qué nunca debe cambiar, cuál es el criterio de éxito. Si
   el usuario ya dio suficiente, no preguntar por preguntar — avanzar documentando supuestos.

4. **Mapa de impacto.** Listar: partes afectadas, partes intocables, comportamientos preservados vs
   modificados, riesgo de regresión, riesgo de sobrealcance, compatibilidad con usos actuales y con
   otras skills.

5. **Plan quirúrgico (gate de aprobación).** Cambios propuestos, cambios descartados (y por qué),
   justificación de cada uno, criterios de aceptación y de rechazo. **Esperar OK del usuario** antes
   de aplicar, salvo que haya pedido explícitamente avanzar sin revisión.

6. **Aplicar.** Cambiar solo lo necesario; preservar el estilo original cuando es correcto; no
   introducir responsabilidades nuevas sin justificación; no borrar contenido útil; bump de
   `version`. No mezclar cambios cosméticos con funcionales en el mismo commit.

7. **Revisión posterior.** Releer el resultado buscando: regresiones, contradicciones o ambigüedades
   nuevas, pérdida de intención original, sobreingeniería, duplicación. Emitir veredicto: *Aprobado*
   / *Aprobado con observaciones* / *Requiere ajustes* / *No recomendable*.

8. **Cerrar.** Correr `validate_skill.py` (exit 0); si cambió `status` o `description`, actualizar
   `skills/INDEX.md`; commit `skill(categoria/nombre): {qué cambió}`; registrar los criterios con los
   que se evaluará el resultado en uso.

### Cuándo frenar (no es rechazo definitivo: pedir aclaración, alternativa o dividir)

- No se entiende el propósito actual de la skill.
- El pedido contradice el diseño central, o parece pertenecer a otra skill.
- El cambio puede romper comportamientos importantes y faltan definiciones críticas.
- La mejora aumenta demasiado el alcance, o no hay forma clara de evaluar el resultado.

## Gotchas

- **El gate de proporcionalidad es lo primero.** No metas un typo ni un gotcha por el protocolo
  quirúrgico de 8 fases: eso es sobreingeniería y contradice el propósito de la skill. Pero un cambio
  que altera *cuándo se activa* la skill es quirúrgico aunque parezca de una línea.
- **El error más común es confundir cirugía con rediseño.** Si te encontrás reescribiendo la skill
  entera por preferencia estilística, parar: eso no es una modificación, es un skill nuevo.
- **No mezclar cosmético con funcional en un commit.** Separar siempre el cambio de comportamiento
  del reformateo, o la revisión se vuelve imposible.
- **Eliminar comportamiento requiere aprobación explícita.** Borrar una restricción o un paso "que
  parecía redundante" es la causa #1 de regresiones silenciosas.
- **Los gotchas son la parte más valiosa de una skill.** Priorizarlos cuando haya que cortar
  contenido para llegar al límite de tamaño (~500 líneas / <5000 tokens).
- **Nunca cortar el contexto específico de Coferlandia.** Si algo parece redundante pero captura una
  convención interna, mantenerlo.
- **La description NO debe mencionar el nombre de la skill.** El agente ya sabe el nombre — la
  description describe la tarea del usuario, no el nombre de la herramienta.
- **Al agregar un gotcha, usar el error real.** "La tabla X usa soft deletes" es útil. "Maneja los
  edge cases correctamente" no lo es.

## Output esperado

### Resumen de auditoría

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

### Resumen de cirugía

```
## Cirugía: {nombre-skill}

### Carril
Quirúrgico — {qué propósito/flujo/contrato toca}

### Entender
Propósito actual: {...}
Comportamientos a preservar: {...}
Contratos con otras skills: {...}

### Crítica de necesidad
Alternativas: no tocar / doc / skill nuevo / cirugía mínima
Recomendación: {...}

### Mapa de impacto
Afectado: {...} · Intocable: {...} · Riesgo de regresión: {...}

### Plan quirúrgico  [aprobado por usuario: sí/no]
Cambios: {...} · Descartados: {...} · Criterios de aceptación: {...}

### Modificación aplicada
{secciones tocadas, version bump}

### Revisión posterior
Veredicto: Aprobado / Aprobado con observaciones / Requiere ajustes / No recomendable
```
