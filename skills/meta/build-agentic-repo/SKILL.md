---
name: build-agentic-repo
description: >
  Diseña, audita o refactoriza un repositorio "agéntico autoritativo": uno que un agente de
  IA puede leer, navegar y extender solo (sin instrucciones del humano), porque cada regla
  vive en un único lugar, las afirmaciones son verificables y la estructura se explica a sí
  misma. Produce la arquitectura de carpetas, el entry point para agentes, el índice como
  fuente de verdad y los invariantes verificables por máquina.
  Actívala cuando el usuario quiera: crear un repo para que lo mantengan agentes; arreglar un
  repo donde la documentación se contradice o se duplica; hacer que un repo de skills, prompts,
  playbooks o convenciones sea "auto-mantenible"; o auditar por qué dos agentes producen
  resultados distintos leyendo los mismos docs. Aplica aunque el usuario no diga "agéntico":
  basta con "documentación que no se contradiga", "que cualquier agente pueda contribuir",
  "single source of truth", "repo auto-documentado" o "evitar duplicación entre los .md".
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repo y git. La validación opcional usa Python 3.11+.
metadata:
  author: coferlandia
  version: "1.0"
  category: meta
  status: active
  tested: "2026-06-11 — validada estructuralmente con _protocol/scripts/validate_skill.py; description activada con el prompt 'cómo hago que mi repo no se contradiga entre agentes' sin nombrar la skill."
---

## Qué construye esta skill

Un **repositorio agéntico autoritativo** es uno donde un agente de IA puede llegar sin contexto
previo, entender el repo leyendo un solo archivo de entrada, encontrar lo que necesita por
disclosure progresivo, y extender el repo sin introducir contradicciones — porque la
arquitectura hace que contradecirse sea *difícil*, no solo *desaconsejado*.

Esta skill aporta el método para diseñarlo y los anti-patrones concretos que lo rompen. No es
teoría: cada gotcha viene de un fallo real observado en repos de este tipo (incluido este).

El error central que evita: **documentar la misma regla en varios lugares.** Cuando una regla
vive en N archivos, la próxima edición deja N−1 copias obsoletas, y un agente no tiene forma de
saber cuál es la autoritativa. La duplicación no es un problema de estilo — es la causa raíz de
casi toda contradicción en estos repos.

## Principio rector: una fuente de verdad por regla

Toda regla, formato o convención tiene **exactamente un archivo dueño**. Cualquier otro archivo
que la necesite la **enlaza**, no la copia.

```
MAL                                  BIEN
─────────────────────────            ─────────────────────────
naming explicado en 6 archivos       naming vive en NAMING.md
→ editas 1, los otros 5 mienten      → los demás dicen "ver NAMING.md"
→ el agente no sabe cuál creer       → una edición, una verdad
```

Prueba rápida para detectar violaciones: busca cualquier regla concreta (un límite, un formato,
una lista de valores válidos) con `grep` por el repo. Si aparece redactada en más de un archivo,
es deuda de duplicación: consolídala en el dueño y reemplaza el resto por un link de una línea.

## Pasos

### 1. Definir las dos puertas de entrada

Un repo agéntico tiene dos lectores con necesidades distintas:

1. **Entry point para agentes** (p. ej. `AGENTS.md`): lo primero que lee un agente. Debe
   contener el mapa del repo, cómo descubrir contenido y cómo contribuir — y **enlazar** a las
   reglas, nunca reproducirlas. Mantenlo corto: es índice, no manual.
2. **Overview para humanos** (`README.md`): por qué existe el repo y dónde mirar.

### 2. Diseñar para disclosure progresivo

Estructura el repo en niveles de costo creciente de contexto, de modo que el agente cargue solo
lo que necesita:

```
Nivel 1  Descubrimiento   → entry point + índice (siempre cargado, manténlo barato)
Nivel 2  Activación       → el documento/skill específico (cargado al elegirlo)
Nivel 3  Ejecución        → references/, scripts/, assets/ (cargados on-demand, con condición)
```

Regla operativa: cuando un archivo referencie material de Nivel 3, indica **cuándo** cargarlo
("lee `references/x.md` si la API devuelve no-200"), nunca "ver `references/` para más".

### 3. Establecer el índice como única fuente de verdad del inventario

Un solo archivo (p. ej. `INDEX.md`) lista qué existe y su estado. Define su **formato de fila
una vez** ahí mismo, en una nota de cabecera. El protocolo de contribución manda actualizar
**solo** ese índice. No crees catálogos espejo que haya que sincronizar a mano: un espejo es,
por definición, una segunda fuente de verdad que se desincroniza en la próxima edición.

Si quieres una vista alternativa (p. ej. para Obsidian), genérala desde el índice o márcala
explícitamente como derivada: *"vista de navegación — el estado real está en INDEX.md"*.

### 4. Hacer cada afirmación verificable

No pongas en un estándar criterios que un agente no pueda comprobar leyendo el repo. "Fue
probado con un agente real" es inverificable si no queda registro. Para cada criterio de calidad,
elige una de dos:

- **Hazlo verificable:** añade un campo donde conste la evidencia (`tested: "<fecha> — <cómo>"`).
- **Hazlo automático:** un script que lo chequee (ver paso 5).

Si no puede ser ninguna de las dos, probablemente no debería ser un criterio obligatorio.

### 5. Codificar los invariantes en un validador, no en prosa

Los checklists en prosa se ignoran y envejecen. Mueve todo invariante mecánico a un script
ejecutable (`scripts/validate_*.py`) que un agente pueda correr y cuyo output use para
corregirse. Invariantes típicos de estos repos:

- el `name`/id del frontmatter coincide con el nombre de la carpeta,
- los campos requeridos del frontmatter están presentes y dentro de límites,
- el archivo no excede el tope de tamaño,
- no hay secretos ni PII (regex-scan),
- toda entrada del índice apunta a una carpeta que existe (y viceversa).

El validador convierte "calidad por revisión a ojo" en "calidad verificable por máquina".

### 6. Dar reglas de desempate donde el agente debe elegir

Cualquier punto donde un agente elige entre opciones (categoría, ubicación, nombre) necesita una
regla determinista de desempate. Sin ella, dos agentes eligen distinto y el repo se vuelve
inconsistente. Ejemplo: *"si encaja en dos categorías, elige por el artefacto que produce;
ante empate, la primera en esta lista."*

### 7. Reconciliar unidades y límites

Un límite expresado en dos unidades distintas ("<500 líneas" en un archivo, "<5000 tokens" en
otro) obliga al agente a adivinar cuál manda. Da un objetivo y un tope duro juntos, en un solo
lugar: *"objetivo <5000 tokens; tope ~500 líneas."*

### 8. Documentar el protocolo de contribución como secuencia ejecutable

El "cómo agregar algo" debe ser una lista de pasos accionables que terminen en: correr el
validador y actualizar el índice. Es el lazo que mantiene el repo coherente a medida que crece.

## Gotchas

- **Duplicar una regla "por conveniencia del lector".** Es la trampa más común y la más cara.
  Repetir el formato de naming en el entry point "para que sea cómodo" crea la sexta copia que
  mañana contradice a las otras cinco. Enlaza siempre; la comodidad no justifica una segunda
  fuente de verdad.
- **Catálogos espejo.** Un archivo que se declara "espejo de X" es deuda garantizada: nada lo
  sincroniza salvo disciplina humana, que falla. Genera la vista o márcala como derivada.
- **Rutas relativas sin verificar.** Un link `../skills/...` escrito desde un archivo que ya
  está dentro de `skills/` apunta a la nada. Verifica las rutas relativas desde la ubicación
  real del archivo que las contiene, no desde la raíz mental del repo.
- **Criterios de calidad inverificables.** "Debe estar probado" sin un campo de evidencia ni un
  script es decoración: nadie puede chequearlo y todos lo marcan como cumplido. Hazlo verificable
  o automático, o quítalo.
- **Metadata de marketing.** Listar en `compatibility` agentes/plataformas que nunca se probaron
  es afirmar sin evidencia. `compatibility` describe el **entorno requerido** (binarios, runtime,
  accesos), no una lista de marcas compatibles.
- **Triggering fuera del campo canónico.** agentskills.io define `description` como el lugar
  para explicar qué hace la skill y cuándo usarla. No inventes campos de frontmatter: mantén la
  descripción concisa y mueve el detalle operativo al cuerpo.
- **Entry point que crece hasta ser un manual.** Si el archivo de entrada empieza a contener las
  reglas en vez de enlazarlas, dejó de ser índice. Recórtalo: su trabajo es enrutar, no enseñar.

## Output esperado

### Si la tarea es crear/estructurar un repo

```
repo/
├── AGENTS.md          # entry point: mapa + cómo descubrir + cómo contribuir (solo links a reglas)
├── README.md          # overview para humanos
├── _protocol/         # dueños de las reglas (un dueño por regla)
│   ├── NAMING.md          # única fuente del naming
│   ├── QUALITY.md         # única fuente del checklist
│   └── scripts/
│       └── validate_*.py  # invariantes mecánicos
└── <contenido>/
    └── INDEX.md       # única fuente del inventario; define su formato de fila en cabecera
```

### Si la tarea es auditar un repo existente

```markdown
## Auditoría de repo agéntico: <nombre>

### Duplicaciones detectadas (violan "una fuente de verdad")
- Regla "<X>" aparece en: <archivo A>, <archivo B>, <archivo C> → consolidar en <dueño>

### Contradicciones activas
- <archivo A> dice <V1>; <archivo B> dice <V2> para la misma regla

### Afirmaciones inverificables
- Criterio "<...>" sin campo de evidencia ni script

### Rutas/links rotos
- <archivo>: link <ruta> no resuelve

### Plan de consolidación (orden por impacto)
1. ...
```

## Scripts y validación

Si el repo tiene un validador, córrelo antes de dar por terminada cualquier contribución:

```bash
python _protocol/scripts/validate_skill.py <carpeta>   # debe salir con código 0
```

Para construir uno desde cero, ver paso 5: empieza por los invariantes mecánicos y haz que el
script emita JSON a stdout y diagnósticos a stderr, para que un agente pueda parsear el resultado
y corregirse.
