---
name: coferlandia-software-dev
description: >
  Define el proceso de control para desarrollo en Coferlandia: estudio previo, plan aprobado,
  implementación, code review, tests y preparación de commit. Usar cuando una tarea agregue o
  modifique código, corrija bugs o refactorice, aunque el usuario no pida explícitamente un
  proceso. Combinar con skills técnicos; no usar para preguntas conceptuales sin cambios.
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repositorio de trabajo y git. Asume que el agente
  puede correr la suite de tests del proyecto.
metadata:
  author: coferlandia
  version: "1.1"
  category: engineering
  status: active
  tested: "2026-06-25 — revalidada con _protocol/scripts/validate_skill.py (código 0) tras incorporar modos de control y supervisor externo."
---

## Contexto

Esta skill define la **forma de trabajo** para tareas de desarrollo de software en Coferlandia.
Es genérica, simple y consistente: el mismo flujo sirve para implementar funcionalidades nuevas
y para investigar y corregir errores.

No reemplaza a los skills técnicos especializados ni dice cómo programar una tecnología
concreta. Su función es definir **el proceso** que esos skills deben seguir durante cualquier
tarea de desarrollo. Cuando aplican varios roles o skills a la vez, éste manda el orden y los
puntos de control; los especializados aportan el cómo técnico.

El principio rector: **toda tarea atraviesa cuatro instancias de control** —estudio previo,
aprobación del plan, revisión antes del commit, y verificación final de tests y documentación—
de modo que ningún cambio improvisado llegue al commit y toda decisión relevante quede aprobada
por una **autoridad de control externa al agente ejecutor**.

## Modos de control

- `humano-interactivo` — la autoridad de control activa es el usuario humano.
- `agéntico-supervisado` — la autoridad de control activa es un agente supervisor explícitamente
  designado.

Si no hay usuario humano disponible ni agente supervisor designado, el agente ejecutor puede
llegar sólo hasta estudio previo y plan recomendado. En ese caso debe dejar documentado qué
recomienda hacer, pero **no puede modificar archivos, ampliar alcance ni preparar/realizar
commits**.

## Rol: Supervisor agéntico / humano

La **autoridad de control activa** puede ser el usuario humano o un agente supervisor designado.
Ese rol:

- Aprueba o rechaza el plan antes de modificar archivos.
- Aprueba cualquier desvío significativo del alcance.
- Evalúa los hallazgos de la code review.
- Decide si los hallazgos se corrigen ahora, se documentan o se escalan.
- Aprueba la preparación del commit.
- Mantiene el foco en el objetivo original de la tarea.
- Evita expansión silenciosa de alcance.
- Puede escalar al usuario humano cuando la decisión excede el marco técnico o el mandato
  recibido.

El agente implementador o ejecutor **nunca puede autoaprobar** su propio plan, sus desvíos, sus
hallazgos ni su commit. En modo agéntico, el supervisor existe para controlar foco, coherencia,
riesgo y avance; no para implementar código.

## Prerequisitos

- Acceso de lectura/escritura al repositorio de la tarea y a `git`.
- Posibilidad de correr la suite de tests del proyecto.
- Una **autoridad de control activa** designada antes de implementar: usuario humano o agente
  supervisor.

## Pasos

### 1. Estudio previo del sistema

Antes de proponer cambios, estudiar el sistema para comprender:

- Su estructura y arquitectura básica.
- Los módulos relacionados con la tarea.
- Los archivos Markdown y la documentación disponible.
- Las convenciones y patrones del proyecto.
- Los tests existentes del área afectada.

Si aparecen documentación desactualizada, contradicciones entre documentos y código, o
inconsistencias relevantes, **informarlas a la autoridad de control activa en esta etapa**.
Durante el estudio **no se corrige nada ni se modifica ningún archivo**: primero se expone lo
encontrado para que pueda considerarse al armar el plan.

### 2. Planificación y aprobación

Preparar un plan **antes de modificar código**. Debe ser conciso pero suficiente para explicar:

- Qué se investigará o modificará.
- Qué partes del sistema podrían verse afectadas.
- Cómo se implementará el cambio.
- Cómo se verificará su funcionamiento.
- Qué riesgos, dudas o decisiones relevantes existen.
- Si las inconsistencias detectadas en el paso 1 afectan la tarea.

Presentar el plan a la autoridad de control activa, discutirlo si hace falta y **pedir su
aprobación explícita** antes de implementar. Esta regla aplica por igual al desarrollo de
funcionalidades y al diagnóstico y corrección de errores. No avanzar a implementación sin un "sí"
claro de una autoridad externa al agente implementador.

### 3. Implementación

Con el plan aprobado, realizar los cambios acordados, respetando las convenciones detectadas en
el paso 1.

Si durante la implementación surge la necesidad de **desviarse significativamente** del plan
(cambia el alcance, aparecen archivos o módulos no previstos, hay que tocar algo fuera de lo
acordado), detenerse, explicar la situación y **pedir una nueva aprobación a la autoridad de
control activa** antes de ampliar o modificar el alcance.

### 4. Code review obligatoria

Cuando la implementación esté terminada, **pero antes del commit final**, revisar el código
modificado (idealmente sobre el `git diff`). Concentrarse en:

- Errores o regresiones posibles.
- Problemas de seguridad o de rendimiento.
- Casos límite no contemplados.
- Coherencia con la arquitectura y las convenciones existentes.
- Calidad y claridad del código.
- Pruebas faltantes o insuficientes.
- Documentación que deba actualizarse.

Presentar los hallazgos a la autoridad de control activa y discutirlos. Si hay problemas
relevantes, la autoridad decide si **se corrigen ahora, se documentan o se escalan**. No saltar
al commit con hallazgos abiertos sin esa decisión explícita.

### 5. Preparación del commit

Tras revisar y resolver los hallazgos:

1. Comprobar que los tests asociados al diff existan, sean suficientes y estén actualizados; correrlos.
2. Revisar la documentación afectada y agregar, modificar o eliminar contenido para que refleje el funcionamiento final. Éste es el momento de corregir las **inconsistencias documentales** detectadas en el paso 1, siempre que estén relacionadas con el cambio y dentro del alcance aprobado.
3. Proponer un nombre de commit claro y **pedir aprobación de la autoridad de control activa**
   antes de commitear o dejar listo el commit.

## Gotchas

- **Tocar archivos durante el estudio previo:** en el paso 1 está prohibido modificar nada, incluso para "arreglar de paso" una inconsistencia obvia. Sólo se informa; la corrección se decide en el plan.
- **Corregir inconsistencias fuera de alcance:** las inconsistencias documentales se arreglan recién en el paso 5, y **sólo** si están ligadas al cambio y fueron incluidas en el plan aprobado. No expandir el alcance de forma silenciosa.
- **Implementar sin aprobación explícita:** un plan presentado no es un plan aprobado. Esperar el "sí" de la autoridad de control activa antes de escribir código (paso 2) y antes de commitear (paso 5).
- **Desvíos silenciosos del plan:** si el alcance real difiere del aprobado, frenar y re-aprobar (paso 3); no estirar el cambio "porque ya que estoy".
- **Saltarse la code review:** la revisión del paso 4 es obligatoria incluso en cambios chicos o en correcciones de un bug aparentemente trivial.
- **Commitear con hallazgos abiertos o tests rojos:** los hallazgos relevantes y los tests deben quedar resueltos y en verde antes del commit.
- **Confundir modo agéntico con autonomía total:** que la autoridad no sea humana no elimina ninguna aprobación; sólo cambia quién controla el avance.
- **Autoaprobarse:** el agente implementador nunca puede aprobar su propio plan, sus desvíos, sus hallazgos ni su commit.
- **Avanzar sin autoridad de control designada:** sin usuario humano ni supervisor explícito, el trabajo se detiene en estudio previo y plan recomendado.
- **Escalar alcance sin nueva aprobación:** toda ampliación relevante del cambio requiere nueva aprobación explícita.
- **Usar al supervisor como formalidad:** en modo agéntico el supervisor debe revisar foco, alcance y riesgo, no sólo responder "ok".

## Output esperado

Durante la tarea, el agente ejecutor produce dos artefactos de comunicación con la autoridad de
control activa.

**Plan (final del paso 2):**

```
## Plan: {título de la tarea}

**Tipo:** feature | bugfix | refactor
**Modo de control:** humano-interactivo | agéntico-supervisado
**Autoridad de control:** {usuario humano | agente supervisor: nombre/rol}
**Objetivo:** {qué se busca lograr}

**Qué se modificará / investigará:**
- {archivo o módulo} — {cambio}

**Partes potencialmente afectadas:** {módulos, integraciones, tests}

**Implementación:** {enfoque en 2-4 puntos}

**Verificación:** {cómo se prueba: tests a correr/agregar, pasos manuales}

**Riesgos / dudas / decisiones:** {lista breve}

**Inconsistencias detectadas (paso 1):** {ninguna | lista, y si afectan la tarea}

> Solicito aprobación explícita de la autoridad de control activa antes de implementar.
```

**Resumen de code review (final del paso 4):**

```
## Code review: {título}

**Modo de control:** humano-interactivo | agéntico-supervisado
**Autoridad de control:** {usuario humano | agente supervisor: nombre/rol}
**Diff revisado:** {archivos / nº de líneas}

**Hallazgos:**
- [ ] {severidad} — {archivo}: {problema y propuesta}

**Sin hallazgos en:** {áreas revisadas y OK}

**Tests:** {estado: suficientes / faltan X}
**Docs a actualizar:** {lista o "ninguna"}

> La autoridad de control activa decide si los hallazgos se corrigen ahora, se documentan o se escalan.
```

**Registro de aprobación (cuando corresponda):**

```
**Aprobado por:** {autoridad de control}
**Alcance aprobado:** {resumen breve}
```

## Principio general

Toda tarea atraviesa cuatro instancias de control: (1) estudio previo del sistema y su
documentación, (2) aprobación del plan antes de modificar archivos, (3) revisión y discusión de
los cambios antes del commit, y (4) verificación final de tests y documentación. El propósito es
evitar cambios improvisados, mantener a la autoridad de control activa en las decisiones y
asegurar que cada implementación llegue al commit comprendida, revisada, probada y correctamente
documentada. El usuario humano puede ocupar ese rol directamente o delegarlo en un supervisor
agéntico designado, pero el agente implementador nunca se autoaprueba.
