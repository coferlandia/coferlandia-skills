---
name: coferlandia-software-dev
description: >
  Define el proceso de control para desarrollo en Coferlandia: estudio previo, plan aprobado,
  implementacion, code review, tests y preparacion de commit, con roles operativos developer y
  debugger bajo autoridad de control activa. Usar cuando una tarea agregue o modifique codigo,
  corrija bugs o refactorice, aunque el usuario no pida explicitamente un proceso. Combinar con
  skills tecnicos; no usar para preguntas conceptuales sin cambios.
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repositorio de trabajo y git. Asume que el agente
  puede correr la suite de tests del proyecto.
metadata:
  author: coferlandia
  version: "1.2"
  category: engineering
  status: active
  tested: "2026-06-25 - revalidada con _protocol/scripts/validate_skill.py (codigo 0) tras incorporar autoridad de control activa y roles developer/debugger."
---

## Contexto

Esta skill define la **forma de trabajo** para tareas de desarrollo de software en Coferlandia y
los **roles operativos** que ejecutan ese trabajo bajo supervision. Es generica, simple y
consistente: el mismo flujo rector sirve para implementar funcionalidades nuevas y para investigar
y corregir errores.

No reemplaza a los skills tecnicos especializados ni dice como programar una tecnologia concreta.
Su funcion es definir **el proceso** que esos skills deben seguir durante cualquier tarea de
desarrollo. Cuando aplican varios roles o skills a la vez, este manda el orden y los puntos de
control; los especializados aportan el como tecnico.

El principio rector: **toda tarea atraviesa cuatro instancias de control** - estudio previo,
aprobacion del plan, revision antes del commit, y verificacion final de tests y documentacion - de
modo que ningun cambio improvisado llegue al commit y toda decision relevante quede aprobada por
una **autoridad de control externa al agente ejecutor**.

## Roles operativos

Los roles operativos de esta skill trabajan siempre sobre un **issue o tarea identificable**:
puede venir de GitHub Issues, `TODO.md`, otro artefacto del proyecto o una instruccion explicita
de la autoridad de control activa.

- `developer` - para features, mejoras funcionales, implementacion nueva o refactor aprobado.
- `debugger` - para bugs, regresiones, tests fallidos, excepciones o comportamientos incorrectos.

Si el issue esta bien definido, el rol ejecutor debe seguirlo cuidadosamente. Si esta incompleto,
ambiguo o contradictorio, debe registrar dudas, riesgos o contradicciones en el plan y pedir
resolucion a la autoridad de control activa antes de implementar.

### Reglas comunes para developer y debugger

Ambos roles deben:

- Respetar siempre el proceso rector de esta skill.
- Trabajar con un issue o tarea identificable.
- Estudiar primero arquitectura, documentacion, convenciones, patrones y tests relacionados.
- Seguir los lineamientos generales del proyecto.
- No modificar archivos durante el estudio previo.
- No implementar sin plan aprobado por la autoridad de control activa.
- No ampliar alcance sin nueva aprobacion.
- Revisar tests y documentacion que puedan haber sido afectados por el cambio.
- Ejecutar o proponer los tests relevantes segun el contexto del proyecto.
- Realizar code review sobre el diff antes del cierre.
- Informar hallazgos, riesgos y limitaciones al supervisor.
- Sugerir un nombre claro de commit en el mensaje final a la autoridad de control.

## Integracion condicional con project-documentation-archivist

Si el repositorio esta inicializado o estructurado segun `project-documentation-archivist`, los
roles operativos deben respetar esa estructura y actualizar solo los artefactos que correspondan
al cambio. Si no lo esta, no deben inicializar archivist completo ni replicar su trabajo; solo
deben crear los artefactos minimos necesarios para dejar trazabilidad cuando corresponda.

Antes de cerrar una tarea:

- Verificar si existen artefactos tipicos de archivist.
- Si existen, respetar su estructura y actualizar solo lo que corresponda al cambio.
- Si no existen, no ejecutar ni replicar el trabajo de archivist.
- Si hace falta trazabilidad minima, crear solo el artefacto necesario, por ejemplo `HISTORY.md`.

Artefactos tipicos que podrian actualizarse si existen y aplica:

- `TODO.md`, si el issue se completa, cambia de estado o genera tareas posteriores.
- `HISTORY.md`, para registrar el cambio terminado.
- `DECISIONS.md`, si se tomo una decision tecnica relevante.
- `RUNBOOK.md`, si cambian comandos, despliegue, operacion, diagnostico o mantenimiento.
- `AGENTS.md`, si el cambio deja una convencion importante para futuros agentes.

## Modos de control

- `humano-interactivo` - la autoridad de control activa es el usuario humano.
- `agentico-supervisado` - la autoridad de control activa es un agente supervisor explicitamente
  designado.

Si no hay usuario humano disponible ni agente supervisor designado, el agente ejecutor puede
llegar solo hasta estudio previo y plan recomendado. En ese caso debe dejar documentado que
recomienda hacer, pero **no puede modificar archivos, ampliar alcance ni preparar/realizar
commits**.

## Rol: Supervisor agentico / humano

La **autoridad de control activa** puede ser el usuario humano o un agente supervisor designado.
Ese rol:

- Aprueba o rechaza el plan antes de modificar archivos.
- Aprueba cualquier desvio significativo del alcance.
- Evalua los hallazgos de la code review.
- Decide si los hallazgos se corrigen ahora, se documentan o se escalan.
- Aprueba la preparacion del commit.
- Mantiene el foco en el objetivo original de la tarea.
- Evita expansion silenciosa de alcance.
- Puede escalar al usuario humano cuando la decision excede el marco tecnico o el mandato
  recibido.

El agente implementador o ejecutor **nunca puede autoaprobar** su propio plan, sus desvios, sus
hallazgos ni su commit. En modo agentico, el supervisor existe para controlar foco, coherencia,
riesgo y avance; no para implementar codigo.

## Rol: developer

El rol `developer` se usa cuando el issue corresponde a una feature, mejora funcional,
implementacion nueva o refactor aprobado. Su objetivo es convertir el issue en una implementacion
completa, coherente con la arquitectura del proyecto y mantenible.

Metodologia esperada:

1. Leer cuidadosamente el issue y determinar el comportamiento esperado.
2. Identificar modulos, servicios, entidades, interfaces, tests y documentacion relacionados.
3. Buscar codigo reutilizable antes de crear logica nueva.
4. Evitar duplicacion de logica, patrones paralelos o soluciones ad hoc.
5. Seguir principios SOLID, separacion de responsabilidades y buenas practicas del stack usado.
6. Mantener la implementacion acotada al issue aprobado.
7. Agregar o actualizar tests cuando el cambio lo requiera.
8. Actualizar documentacion y artefactos de trazabilidad relacionados.
9. Preparar un cierre para la autoridad de control con resumen, tests, documentacion, riesgos
   remanentes y nombre sugerido de commit.

Criterios de buen resultado para `developer`:

- La feature queda integrada al diseno existente.
- No se duplica logica innecesariamente.
- El cambio es testeable y mantenible.
- La solucion no introduce arquitectura paralela.
- El alcance implementado coincide con el issue aprobado.
- Las decisiones relevantes quedan documentadas cuando aplica.

## Rol: debugger

El rol `debugger` se usa cuando el issue corresponde a un bug, regresion, error reportado, test
fallido, excepcion, inconsistencia de datos o comportamiento inesperado. Su objetivo es encontrar
la causa raiz y aplicar una correccion concreta, minima y verificable.

Si esta disponible en el entorno, debe usar o apoyarse en el skill
`superpowers/systematic-debugging`.

Metodologia esperada:

1. Leer cuidadosamente el issue de bug.
2. Separar hechos observados, sintomas, hipotesis y datos faltantes.
3. Buscar pasos de reproduccion, logs, tests fallidos, stack traces o evidencia disponible.
4. Revisar `HISTORY.md` si existe, especialmente para detectar si el bug puede ser una regresion
   causada por un cambio reciente.
5. Estudiar el area afectada sin modificar archivos.
6. Formular hipotesis explicitas sobre la causa.
7. Intentar reproducir el problema o identificar el punto exacto de falla.
8. Aplicar un fix enfocado en la causa raiz.
9. Agregar o actualizar tests de regresion cuando sea posible.
10. Verificar que el bug queda corregido y que no se rompen comportamientos relacionados.
11. Actualizar documentacion o artefactos de trazabilidad si el bug revela una convencion, riesgo
    o decision importante.
12. Preparar un cierre para la autoridad de control con causa raiz, fix aplicado, evidencia de
    verificacion, tests, riesgos remanentes y nombre sugerido de commit.

Criterios de buen resultado para `debugger`:

- La causa raiz queda identificada o se explicita claramente el grado de certeza.
- El fix esta enfocado en el problema reportado.
- Se agregan tests de regresion cuando aplica.
- Se revisa la historia del proyecto cuando hay indicios de regresion.
- El cierre explica que fallaba, por que fallaba y por que el cambio lo corrige.

## Prerequisitos

- Acceso de lectura/escritura al repositorio de la tarea y a `git`.
- Posibilidad de correr la suite de tests del proyecto.
- Una **autoridad de control activa** designada antes de implementar: usuario humano o agente
  supervisor.

## Pasos

Los roles `developer` y `debugger` siguen exactamente este mismo flujo. Cambia la metodologia
especifica de analisis e implementacion, pero no cambian los gates de control.

### 1. Estudio previo del sistema

Antes de proponer cambios, estudiar el sistema para comprender:

- Su estructura y arquitectura basica.
- Los modulos relacionados con la tarea.
- Los archivos Markdown y la documentacion disponible.
- Las convenciones y patrones del proyecto.
- Los tests existentes del area afectada.

Si aparecen documentacion desactualizada, contradicciones entre documentos y codigo, o
inconsistencias relevantes, **informarlas a la autoridad de control activa en esta etapa**.
Durante el estudio **no se corrige nada ni se modifica ningun archivo**: primero se expone lo
encontrado para que pueda considerarse al armar el plan.

### 2. Planificacion y aprobacion

Preparar un plan **antes de modificar codigo**. Debe ser conciso pero suficiente para explicar:

- Que issue o tarea se esta tomando como fuente.
- Que se investigara o modificara.
- Que partes del sistema podrian verse afectadas.
- Como se implementara el cambio.
- Como se verificara su funcionamiento.
- Que riesgos, dudas o decisiones relevantes existen.
- Si las inconsistencias detectadas en el paso 1 afectan la tarea.

Presentar el plan a la autoridad de control activa, discutirlo si hace falta y **pedir su
aprobacion explicita** antes de implementar. Esta regla aplica por igual al desarrollo de
funcionalidades y al diagnostico y correccion de errores. No avanzar a implementacion sin un "si"
claro de una autoridad externa al agente implementador.

### 3. Implementacion

Con el plan aprobado, realizar los cambios acordados, respetando las convenciones detectadas en el
paso 1.

Si durante la implementacion surge la necesidad de **desviarse significativamente** del plan
(cambia el alcance, aparecen archivos o modulos no previstos, hay que tocar algo fuera de lo
acordado), detenerse, explicar la situacion y **pedir una nueva aprobacion a la autoridad de
control activa** antes de ampliar o modificar el alcance.

### 4. Code review obligatoria

Cuando la implementacion este terminada, **pero antes del commit final**, revisar el codigo
modificado (idealmente sobre el `git diff`). Concentrarse en:

- Errores o regresiones posibles.
- Problemas de seguridad o de rendimiento.
- Casos limite no contemplados.
- Coherencia con la arquitectura y las convenciones existentes.
- Calidad y claridad del codigo.
- Pruebas faltantes o insuficientes.
- Documentacion que deba actualizarse.

Presentar los hallazgos a la autoridad de control activa y discutirlos. Si hay problemas
relevantes, la autoridad decide si **se corrigen ahora, se documentan o se escalan**. No saltar
al commit con hallazgos abiertos sin esa decision explicita.

### 5. Preparacion del commit

Tras revisar y resolver los hallazgos:

1. Comprobar que los tests asociados al diff existan, sean suficientes y esten actualizados; correrlos.
2. Revisar la documentacion afectada y agregar, modificar o eliminar contenido para que refleje el funcionamiento final. Este es el momento de corregir las **inconsistencias documentales** detectadas en el paso 1, siempre que esten relacionadas con el cambio y dentro del alcance aprobado. Si el repositorio ya usa `project-documentation-archivist`, actualizar los artefactos correspondientes respetando esa estructura; si no la usa, crear solo la trazabilidad minima necesaria cuando aplique.
3. Proponer un nombre de commit claro y **pedir aprobacion de la autoridad de control activa** antes de commitear o dejar listo el commit.

## Gotchas

- **Tocar archivos durante el estudio previo:** en el paso 1 esta prohibido modificar nada, incluso para "arreglar de paso" una inconsistencia obvia. Solo se informa; la correccion se decide en el plan.
- **Corregir inconsistencias fuera de alcance:** las inconsistencias documentales se arreglan recien en el paso 5, y **solo** si estan ligadas al cambio y fueron incluidas en el plan aprobado. No expandir el alcance de forma silenciosa.
- **Implementar sin aprobacion explicita:** un plan presentado no es un plan aprobado. Esperar el "si" de la autoridad de control activa antes de escribir codigo (paso 2) y antes de commitear (paso 5).
- **Desvios silenciosos del plan:** si el alcance real difiere del aprobado, frenar y re-aprobar (paso 3); no estirar el cambio "porque ya que estoy".
- **Saltarse la code review:** la revision del paso 4 es obligatoria incluso en cambios chicos o en correcciones de un bug aparentemente trivial.
- **Commitear con hallazgos abiertos o tests rojos:** los hallazgos relevantes y los tests deben quedar resueltos y en verde antes del commit.
- **Confundir modo agentico con autonomia total:** que la autoridad no sea humana no elimina ninguna aprobacion; solo cambia quien controla el avance.
- **Confundir rol ejecutor con autoridad de control:** `developer` y `debugger` ejecutan; nunca reemplazan al supervisor humano o agentico ni se autoaprueban.
- **Autoaprobarse:** el agente implementador nunca puede aprobar su propio plan, sus desvios, sus hallazgos ni su commit.
- **Avanzar sin autoridad de control designada:** sin usuario humano ni supervisor explicito, el trabajo se detiene en estudio previo y plan recomendado.
- **Escalar alcance sin nueva aprobacion:** toda ampliacion relevante del cambio requiere nueva aprobacion explicita.
- **Usar al supervisor como formalidad:** en modo agentico el supervisor debe revisar foco, alcance y riesgo, no solo responder "ok".
- **Ignorar archivist cuando ya existe:** si el repo ya tiene estructura documental viva, hay que respetarla y actualizar solo los artefactos afectados; no trabajar como si no existiera.

## Output esperado

Durante la tarea, el agente ejecutor produce tres artefactos de comunicacion con la autoridad de
control activa.

**Plan (final del paso 2):**

```
## Plan: {titulo de la tarea}

**Rol ejecutor:** developer | debugger
**Tipo:** feature | bugfix | refactor
**Issue trabajado:** {referencia a TODO.md, GitHub Issue u origen}
**Modo de control:** humano-interactivo | agentico-supervisado
**Autoridad de control:** {usuario humano | agente supervisor: nombre/rol}
**Objetivo:** {que se busca lograr}

**Que se modificara / investigara:**
- {archivo o modulo} - {cambio}

**Partes potencialmente afectadas:** {modulos, integraciones, tests}

**Implementacion:** {enfoque en 2-4 puntos}

**Verificacion:** {como se prueba: tests a correr/agregar, pasos manuales}

**Riesgos / dudas / decisiones:** {lista breve}

**Inconsistencias detectadas (paso 1):** {ninguna | lista, y si afectan la tarea}

> Solicito aprobacion explicita de la autoridad de control activa antes de implementar.
```

**Resumen de code review (final del paso 4):**

```
## Code review: {titulo}

**Modo de control:** humano-interactivo | agentico-supervisado
**Autoridad de control:** {usuario humano | agente supervisor: nombre/rol}
**Diff revisado:** {archivos / n de lineas}

**Hallazgos:**
- [ ] {severidad} - {archivo}: {problema y propuesta}

**Sin hallazgos en:** {areas revisadas y OK}

**Tests:** {estado: suficientes / faltan X}
**Docs a actualizar:** {lista o "ninguna"}

> La autoridad de control activa decide si los hallazgos se corrigen ahora, se documentan o se escalan.
```

**Cierre de tarea (antes del commit):**

```md
## Cierre de tarea: {titulo del issue}

**Rol ejecutor:** developer | debugger
**Issue trabajado:** {referencia a TODO.md, GitHub Issue u origen}
**Modo de control:** humano-interactivo | agentico-supervisado
**Autoridad de control:** {usuario humano | agente supervisor}

**Resumen del cambio:**
{descripcion breve}

**Archivos modificados:**
- {archivo} - {motivo}

**Tests revisados / ejecutados:**
- {comando o test} - {resultado}

**Documentacion / archivist:**
- {artefacto actualizado o "no aplico"}

**Code review:**
- {sin hallazgos relevantes | hallazgos resueltos | hallazgos pendientes para decision}

**Riesgos o pendientes:**
- {ninguno | lista breve}

**Nombre sugerido de commit:**
`{tipo}: {descripcion breve}`

> El commit no debe realizarse hasta recibir aprobacion explicita de la autoridad de control activa.
```

**Registro de aprobacion (cuando corresponda):**

```
**Aprobado por:** {autoridad de control}
**Alcance aprobado:** {resumen breve}
```

## Principio general

Toda tarea atraviesa cuatro instancias de control: (1) estudio previo del sistema y su
documentacion, (2) aprobacion del plan antes de modificar archivos, (3) revision y discusion de
los cambios antes del commit, y (4) verificacion final de tests y documentacion. El proposito es
evitar cambios improvisados, mantener a la autoridad de control activa en las decisiones y
asegurar que cada implementacion llegue al commit comprendida, revisada, probada y correctamente
documentada. El usuario humano puede ocupar ese rol directamente o delegarlo en un supervisor
agentico designado, pero el agente implementador nunca se autoaprueba.
