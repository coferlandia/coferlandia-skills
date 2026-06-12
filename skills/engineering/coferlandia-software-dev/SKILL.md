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
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0)."
---

## Contexto

Esta skill define la **forma de trabajo** para tareas de desarrollo de software en Coferlandia.
Es genérica, simple y consistente: el mismo flujo sirve para implementar funcionalidades nuevas
y para investigar y corregir errores.

No reemplaza a los skills técnicos especializados ni dice cómo programar una tecnología
concreta. Su función es definir **el proceso** que esos skills deben seguir durante cualquier
tarea de desarrollo. Cuando aplican varios skills a la vez, éste manda el orden y los puntos de
control; los especializados aportan el cómo técnico.

El principio rector: **toda tarea atraviesa cuatro instancias de control** —estudio previo,
aprobación del plan, revisión antes del commit, y verificación final de tests y documentación—
de modo que ningún cambio improvisado llegue al commit y el usuario quede involucrado en cada
decisión relevante.

## Prerequisitos

- Acceso de lectura/escritura al repositorio de la tarea y a `git`.
- Posibilidad de correr la suite de tests del proyecto.

## Pasos

### 1. Estudio previo del sistema

Antes de proponer cambios, estudiar el sistema para comprender:

- Su estructura y arquitectura básica.
- Los módulos relacionados con la tarea.
- Los archivos Markdown y la documentación disponible.
- Las convenciones y patrones del proyecto.
- Los tests existentes del área afectada.

Si aparecen documentación desactualizada, contradicciones entre documentos y código, o
inconsistencias relevantes, **informarlas al usuario en esta etapa**. Durante el estudio **no se
corrige nada ni se modifica ningún archivo**: primero se expone lo encontrado para que pueda
considerarse al armar el plan.

### 2. Planificación y aprobación

Preparar un plan **antes de modificar código**. Debe ser conciso pero suficiente para explicar:

- Qué se investigará o modificará.
- Qué partes del sistema podrían verse afectadas.
- Cómo se implementará el cambio.
- Cómo se verificará su funcionamiento.
- Qué riesgos, dudas o decisiones relevantes existen.
- Si las inconsistencias detectadas en el paso 1 afectan la tarea.

Presentar el plan al usuario, discutirlo si hace falta y **pedir su aprobación explícita** antes
de implementar. Esta regla aplica por igual al desarrollo de funcionalidades y al diagnóstico y
corrección de errores. No avanzar a implementación sin un "sí" claro.

### 3. Implementación

Con el plan aprobado, realizar los cambios acordados, respetando las convenciones detectadas en
el paso 1.

Si durante la implementación surge la necesidad de **desviarse significativamente** del plan
(cambia el alcance, aparecen archivos o módulos no previstos, hay que tocar algo fuera de lo
acordado), detenerse, explicar la situación y **pedir una nueva aprobación** antes de ampliar o
modificar el alcance.

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

Presentar los hallazgos al usuario y discutirlos. Si hay problemas relevantes, **resolverlos
antes** de considerar terminada la tarea. No saltar al commit con hallazgos abiertos.

### 5. Preparación del commit

Tras revisar y resolver los hallazgos:

1. Comprobar que los tests asociados al diff existan, sean suficientes y estén actualizados; correrlos.
2. Revisar la documentación afectada y agregar, modificar o eliminar contenido para que refleje el funcionamiento final. Éste es el momento de corregir las **inconsistencias documentales** detectadas en el paso 1, siempre que estén relacionadas con el cambio y dentro del alcance aprobado.
3. Proponer un nombre de commit claro y **pedir aprobación del usuario** antes de commitear.

## Gotchas

- **Tocar archivos durante el estudio previo:** en el paso 1 está prohibido modificar nada, incluso para "arreglar de paso" una inconsistencia obvia. Sólo se informa; la corrección se decide en el plan.
- **Corregir inconsistencias fuera de alcance:** las inconsistencias documentales se arreglan recién en el paso 5, y **sólo** si están ligadas al cambio y fueron incluidas en el plan aprobado. No expandir el alcance de forma silenciosa.
- **Implementar sin aprobación explícita:** un plan presentado no es un plan aprobado. Esperar el "sí" del usuario antes de escribir código (paso 2) y antes de commitear (paso 5).
- **Desvíos silenciosos del plan:** si el alcance real difiere del aprobado, frenar y re-aprobar (paso 3); no estirar el cambio "porque ya que estoy".
- **Saltarse la code review:** la revisión del paso 4 es obligatoria incluso en cambios chicos o en correcciones de un bug aparentemente trivial.
- **Commitear con hallazgos abiertos o tests rojos:** los hallazgos relevantes y los tests deben quedar resueltos y en verde antes del commit.

## Output esperado

Durante la tarea, el agente produce dos artefactos de comunicación con el usuario.

**Plan (final del paso 2):**

```
## Plan: {título de la tarea}

**Tipo:** feature | bugfix | refactor
**Objetivo:** {qué se busca lograr}

**Qué se modificará / investigará:**
- {archivo o módulo} — {cambio}

**Partes potencialmente afectadas:** {módulos, integraciones, tests}

**Implementación:** {enfoque en 2-4 puntos}

**Verificación:** {cómo se prueba: tests a correr/agregar, pasos manuales}

**Riesgos / dudas / decisiones:** {lista breve}

**Inconsistencias detectadas (paso 1):** {ninguna | lista, y si afectan la tarea}

> Pido tu aprobación explícita antes de implementar.
```

**Resumen de code review (final del paso 4):**

```
## Code review: {título}

**Diff revisado:** {archivos / nº de líneas}

**Hallazgos:**
- [ ] {severidad} — {archivo}: {problema y propuesta}

**Sin hallazgos en:** {áreas revisadas y OK}

**Tests:** {estado: suficientes / faltan X}
**Docs a actualizar:** {lista o "ninguna"}

> Resolvemos los hallazgos relevantes antes del commit.
```

## Principio general

Toda tarea atraviesa cuatro instancias de control: (1) estudio previo del sistema y su
documentación, (2) aprobación del plan antes de modificar archivos, (3) revisión y discusión de
los cambios antes del commit, y (4) verificación final de tests y documentación. El propósito es
evitar cambios improvisados, mantener al usuario en las decisiones y asegurar que cada
implementación llegue al commit comprendida, revisada, probada y correctamente documentada.
