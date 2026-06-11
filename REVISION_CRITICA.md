# Revisión crítica — coferlandia-skills

> Objetivo: que cualquier agente que llegue al repo pueda producir skills de alta calidad
> siguiendo instrucciones claras y sin contradicciones.
> Fecha: 2026-06-11 · Spec de referencia validada: [agentskills.io/specification](https://agentskills.io/specification)

---

## Veredicto

La arquitectura es sólida y la intención ("para y por agentes") está bien ejecutada en el
*tono*. El problema no es lo que dice cada archivo por separado — es que **la misma regla está
escrita en 4–6 lugares con versiones distintas**, y algunas ya divergieron. Un agente que siga
`HOW_TO_CREATE_SKILLS.md` y otro que siga `skill-factory` producirán resultados diferentes hoy.
Eso rompe la promesa central del repo.

Los hallazgos están ordenados por impacto. Los de **Bloque A** causan output incorrecto o
divergente y deberían arreglarse antes de crear más skills. Los de **Bloque B** suben el techo
de calidad.

---

## Bloque A — Contradicciones que rompen la consistencia

### A1. El formato de entrada en INDEX.md está definido de 3 maneras distintas

- `skills/INDEX.md` (real, en uso): 3 columnas → `Skill | Descripción | Status`
- `HOW_TO_CREATE_SKILLS.md` Paso 7: 4 columnas + ruta `../skills/{cat}/...`
- `skill-factory` Paso 7: 3 columnas + ruta `./categoria/...`

Las tres no pueden ser correctas. Además la ruta de HOW_TO (`../skills/`) **está rota**: `INDEX.md`
vive *dentro* de `skills/`, así que el link relativo correcto es `./{categoria}/{nombre}/`, no
`../skills/`. Un agente que copie HOW_TO literalmente genera links muertos.

**Fix:** definir el formato de fila de INDEX en UN solo lugar (`NAMING_CONVENTIONS.md` o un
`INDEX.md` con instrucción de cabecera) y que HOW_TO y skill-factory **enlacen** a esa definición
en vez de repetirla. Decidir si la columna `categoría` va o no (el índice ya agrupa por sección,
así que la columna es redundante → recomiendo 3 columnas).

### A2. La regla de naming y el checklist de calidad están duplicados textualmente

Las reglas del `name` aparecen completas en `AGENTS.md`, `Genesis_Plan.md §4`, `NAMING_CONVENTIONS.md`,
`SKILL_TEMPLATE.md`, `QUALITY_STANDARDS.md` y `vault/Skill_Format.md`. El checklist de calidad
aparece en `Genesis_Plan §7`, `QUALITY_STANDARDS.md`, `HOW_TO Paso 6`, `SKILL_TEMPLATE.md` y
`skill-factory`. Esto **ya** produjo la divergencia de A1.

Cada copia es un punto donde la próxima edición dejará a las demás obsoletas — y un agente no
sabe cuál es la autoritativa.

**Fix (DRY):** una sola fuente de verdad por regla. `NAMING_CONVENTIONS.md` es dueño del naming;
`QUALITY_STANDARDS.md` es dueño del checklist. El resto cita una frase corta + link. Donde haya
un "checklist mínimo" embebido (HOW_TO, skill-factory, template), reemplazarlo por: *"Verificar
contra `QUALITY_STANDARDS.md` — es la lista autoritativa."*

### A3. El catálogo tiene dos fuentes de verdad que se sincronizan a mano

`vault/Skill_Catalog.md` se declara explícitamente "espejo de `skills/INDEX.md`", y `vault/Roadmap.md`
+ los checkboxes de fase también listan skills. Pero el protocolo de creación solo manda actualizar
`INDEX.md`. Resultado garantizado: el espejo y el roadmap quedan desactualizados apenas se cree la
segunda skill, y `Architecture.md` afirma que el vault "refleja el estado del repo" cuando nada lo
mantiene.

**Fix:** declarar `skills/INDEX.md` como única fuente de verdad y degradar el vault a navegación
("ver INDEX.md para el estado real"), **o** añadir al protocolo un paso explícito de sincronizar el
espejo. Lo primero es más robusto: menos lugares que mantener = menos drift.

### A4. El repo viola su propio estándar de "tested" desde el día uno

`QUALITY_STANDARDS.md` exige, para marcar `active`: *"La skill fue probada al menos una vez con un
agente real"* que *"activó sin mencionar el nombre"*. Pero `skill-factory` ya está `active` v1.0 en
Genesis sin ningún registro de prueba, y `skill-auditor` —que es el mecanismo de calidad del repo—
está en `draft`. La promesa de "alta calidad" descansa hoy en una skill no probada y otra en borrador.

Además el criterio es **inverificable por un agente**: no hay ningún campo ni archivo donde conste
que la prueba ocurrió. Un agente no puede chequear "¿se probó esto?" leyendo los archivos.

**Fix:** o (a) volver `skill-factory` a `draft` hasta que haya una corrida real registrada, o
(b) hacer el criterio verificable: añadir a `metadata` un campo como `tested: "2026-06-11 — activada
con prompt 'crea una skill para X'"`. Sin evidencia registrable, el criterio es decorativo.

---

## Bloque B — Mejoras que suben el techo de calidad

### B1. Falta un ejemplo completo "gold standard"

`SKILL_TEMPLATE.md` es un esqueleto con `{llaves}`. La propia filosofía del repo dice que *"el
agente pattern-matchea mejor contra ejemplos concretos"* — pero no hay ni un SKILL.md realista
completo para imitar. Un esqueleto enseña la *forma*; un ejemplo bueno enseña el *nivel*.

**Fix:** designar una skill como referencia ejemplar (las meta-skills sirven) y enlazarla desde
HOW_TO: *"Para ver el nivel esperado, estudia `skills/meta/skill-factory/SKILL.md`."* Mejor aún:
un ejemplo end-to-end con scripts/references en `_protocol/EXAMPLE_SKILL/`.

### B2. No se usa el campo oficial `when_to_use` (ni se explica `allowed-tools`)

La spec de agentskills.io define un campo `when_to_use` dedicado a las reglas de activación, y
`allowed-tools` para restringir herramientas (seguridad). El repo mete *todo* el triggering en
`description` y nunca menciona `when_to_use`. Dado cuánto énfasis pone en "buena description para
triggering", ignorar el campo que la spec creó justo para eso es una oportunidad perdida — y ayuda
con B6 (descriptions más cortas).

**Fix:** documentar `when_to_use` como campo recomendado para reglas de activación extensas, dejando
`description` para el "qué hace" conciso. Documentar `allowed-tools` en la sección de seguridad.

### B3. `compatibility` se usa mal — promete agentes no probados

Todos los templates hardcodean `compatibility: Claude Code, VS Code, GitHub Copilot, Cursor` en cada
skill. Según la spec, `compatibility` describe el **entorno requerido** (p. ej. "requiere git y
python 3.11"), no una lista de marcas de agentes. Listar 4 agentes que nunca se probaron es,
irónicamente, el mismo pecado de "afirmar sin evidencia" que A4 — y contradice el ethos de honestidad
del repo.

**Fix:** usar `compatibility` para requisitos reales de runtime. Si se quiere declarar agentes
soportados, que sea solo los efectivamente probados.

### B4. Las categorías no tienen regla de desempate

`ux-copy` aparece en `design` (tabla Genesis) pero la definición de `content` incluye "comunicación";
`deploy-checklist` encaja igual en `ops` y en `engineering`. Un agente eligiendo categoría tiene
ambigüedad real y no hay tie-break.

**Fix:** una línea de orden de prioridad en `NAMING_CONVENTIONS.md`, p. ej.: *"Si una skill encaja
en dos categorías, elige por el artefacto que produce (código→engineering, texto→content,
proceso→ops). Ante empate, la que aparezca primero en esta lista."*

### B5. El límite de tamaño está dado en dos unidades inconsistentes

El protocolo dice "<500 líneas"; el vault dice "<5000 tokens". No son equivalentes (500 líneas
densas superan 5000 tokens) y un agente no sabe cuál manda.

**Fix:** unificar: *"Objetivo <5000 tokens; tope duro ~500 líneas. Lo que sobre va a `references/`."*

### B6. La seguridad se predica pero no se automatiza

El repo defiende scripts con output estructurado, pero el "scan de privacidad" (regex para `sk-`,
`ghp_`, emails, etc.) está descrito en prosa y se ejecuta a mano. Para un repo público que llama a
esto "no negociable", debería existir un script ejecutable.

**Fix:** añadir `_protocol/scripts/validate_skill.py` (PEP 723, `--help`, salida JSON) que chequee:
`name`==carpeta, campos de frontmatter presentes, conteo de líneas, y el regex-scan de secretos/PII.
Eso convierte el Bloque A2 y la seguridad de "checklist a ojo" a "verificable por máquina", que es
justo lo que el repo exige de sus propias skills.

### B7. Descriptions vs. presupuesto de discovery

Toda `description` se carga siempre durante discovery (~100 tokens × N skills). El repo pide
descriptions ricas (qué + cuándo + keywords + casos no obvios) sin advertir que, a escala, eso
infla el costo fijo de discovery de *todas* las skills a la vez.

**Fix:** nota breve: mantener `description` tensa; empujar reglas de activación largas a `when_to_use`
(ver B2), que no siempre se carga.

---

## Resumen accionable

| # | Hallazgo | Impacto | Esfuerzo |
|---|----------|---------|----------|
| A1 | Formato de INDEX definido 3 veces (uno con link roto) | Alto | Bajo |
| A2 | Naming + checklist duplicados → drift | Alto | Medio |
| A3 | Catálogo/roadmap/vault sin sync automático | Alto | Bajo |
| A4 | "tested" exigido pero inverificable y ya violado | Alto | Bajo |
| B1 | Falta ejemplo gold-standard completo | Medio | Medio |
| B2 | No se usa `when_to_use` ni `allowed-tools` | Medio | Bajo |
| B3 | `compatibility` mal usado (agentes no probados) | Medio | Bajo |
| B4 | Categorías sin regla de desempate | Medio | Bajo |
| B5 | 500 líneas vs 5000 tokens sin reconciliar | Bajo | Bajo |
| B6 | Scan de seguridad no automatizado | Medio | Medio |
| B7 | Descriptions vs presupuesto de discovery | Bajo | Bajo |

**Principio que resuelve la mayoría:** *una fuente de verdad por regla.* Hoy el repo se documenta a
sí mismo varias veces; debería documentarse una vez y enlazar. Eso solo elimina A1, A2 y la mitad de
A3, y hace que las contradicciones futuras sean casi imposibles.
