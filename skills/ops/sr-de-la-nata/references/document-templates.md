# Plantillas del expediente — Sr de la Nata

> Plantillas exactas de cada documento del expediente. El `SKILL.md` describe **cuándo** y
> **por qué** crear cada uno; este archivo da el **formato**. Copiar la plantilla, completar los
> campos reales y no inventar campos extra. Las fechas se escriben absolutas (`YYYY-MM-DD`).

Estructura del expediente por proyecto:

```
Sr-de-la-Nata/
  README.md
  projects/
    {nombre-proyecto}/
      00_project_brief.md          07_evidence_register.md
      01_research_dossier.md       08_next_actions.md
      02_critical_evaluation.md    09_change_log.md
      03_project_definition.md     10_project_status.md
      04_original_plan.md          11_specialist_registry.md
      05_decision_log.md           12_tooling_recommendations.md
      06_risk_register.md          bitacora/  attachments/  references/  specialist-reports/
```

Nombre de carpeta de proyecto: corto, descriptivo, minúsculas, con guiones, sin espacios ni
caracteres problemáticos (ej. `agente-influencer-nomade`, `modulo-rendiciones`, `mineria-iot`).

---

## `README.md` (raíz `Sr-de-la-Nata/`)

Explica el sistema documental: propósito del Sr de la Nata; estructura de carpetas; flujo de
apertura de proyecto; flujo de seguimiento; y las reglas de bitácora, evidencias, decisiones,
cambios, especialistas y recomendaciones de herramientas. Crear una sola vez; mantener breve.

---

## `00_project_brief.md`

```md
# Project Brief

## Nombre del proyecto
## Fecha de apertura
## Descripción inicial
## Motivación
## Problema que intenta resolver
## Usuario o beneficiario objetivo
## Estado actual
## Recursos disponibles
## Restricciones conocidas
## Supuestos iniciales
## Dominios técnicos involucrados
## Preguntas abiertas
## Próximo paso sugerido
```

---

## `01_research_dossier.md`

```md
# Research Dossier

## Resumen ejecutivo
## Fecha de investigación

## Fuentes consultadas

| Fuente | Tipo | URL | Relevancia | Nota |
|---|---|---|---|---|

## Casos similares encontrados
## Casos de éxito
## Casos de fracaso o advertencias
## Competidores / referentes / alternativas
## Riesgos detectados
## Oportunidades detectadas
## Costos y complejidades probables
## Señales de mercado o adopción
## Experiencias de comunidad
## Lecciones aplicables
## Preguntas abiertas
## Conclusión de investigación
```

---

## `02_critical_evaluation.md`

```md
# Critical Evaluation

## Veredicto inicial

Viabilidad:
- [ ] Viable
- [ ] Viable con reducción
- [ ] Interesante pero inmaduro
- [ ] Mal enfocado
- [ ] Riesgoso
- [ ] Sobredimensionado
- [ ] Probablemente inviable
- [ ] Delirante en su forma actual
- [ ] Sin información suficiente

## Resumen brutalmente honesto
## Puntos fuertes
## Puntos débiles
## Supuestos peligrosos
## Riesgos principales
## Señales de sobredimensionamiento
## Señales de fantasía operativa
## Qué habría que reducir
## Qué habría que validar primero
## Condiciones mínimas para avanzar
## Recomendación concreta
## Preguntas críticas pendientes
```

---

## `03_project_definition.md`

```md
# Project Definition

## Objetivo final
## Objetivo de la primera etapa
## Alcance incluido
## Alcance excluido
## Usuario objetivo
## Resultado esperado
## Criterio de éxito
## Criterio de pausa o abandono
## Restricciones
## Dependencias
## Recursos disponibles
## Decisiones tomadas
## Decisiones pendientes
## Versión mínima viable
## Primer hito verificable
```

---

## `04_original_plan.md`

```md
# Plan Original del Proyecto

## Fecha de creación
## Nombre del proyecto
## Visión general
## Diagnóstico inicial
## Objetivo principal
## Objetivos secundarios
## Alcance
## Fuera de alcance
## Estrategia general

## Fases del proyecto
### Fase 1
### Fase 2
### Fase 3

## Hitos principales
## Primer entregable concreto
## Recursos necesarios
## Riesgos principales
## Validaciones necesarias
## Criterios de éxito
## Próximas acciones inmediatas
## Decisiones pendientes

## Notas de aprobación

Estado:
- [ ] Borrador
- [ ] Aprobado por el usuario
- [ ] Requiere revisión
```

> El plan original es la **línea base histórica**. Si cambia, registrar el cambio en
> `09_change_log.md` y, si corresponde, versionar; no reescribir el original en silencio.

---

## `05_decision_log.md`

```md
# Decision Log

| Fecha | Decisión | Motivo | Alternativas descartadas | Impacto | Autorizado por |
|---|---|---|---|---|---|
```

---

## `06_risk_register.md`

```md
# Risk Register

| Riesgo | Probabilidad | Impacto | Señales tempranas | Mitigación | Estado |
|---|---|---|---|---|---|
```

---

## `07_evidence_register.md`

```md
# Evidence Register

| Fecha | Evidencia | Tipo | Qué demuestra | Ubicación / referencia | Validada |
|---|---|---|---|---|---|
```

---

## `08_next_actions.md`

```md
# Next Actions

## Acción actual prioritaria

## Acciones pendientes

| Prioridad | Acción | Responsable | Estado | Evidencia esperada |
|---|---|---|---|---|

## Bloqueos
## Preguntas abiertas
## Próxima conversación sugerida
```

---

## `09_change_log.md`

```md
# Change Log

| Fecha | Cambio | Motivo | Impacto | Autorizado por | Documentos afectados |
|---|---|---|---|---|---|
```

---

## `10_project_status.md`

```md
# Project Status

## Estado general

Semáforo:
- [ ] Verde: avanza correctamente
- [ ] Amarillo: avanza con riesgo
- [ ] Rojo: estancado o desviado
- [ ] Gris: sin información suficiente

## Último avance real
## Próximo paso crítico
## Riesgo principal actual
## Decisiones pendientes
## Nivel de tracción
## Comentario ejecutivo
## Fecha de última actualización
```

---

## `11_specialist_registry.md`

```md
# Specialist Registry

## Skills detectados para este proyecto

| Fecha | Skill | Dominio | Motivo de convocatoria | Pregunta realizada | Resultado | Archivo generado |
|---|---|---|---|---|---|---|

## Skills útiles pero no disponibles

| Dominio | Skill deseado | Motivo | Prioridad |
|---|---|---|---|
```

---

## `12_tooling_recommendations.md`

```md
# Tooling Recommendations

## Objetivo

Registrar herramientas, MCP servers, Agent Skills o plugins recomendados para este proyecto,
con justificación, utilidad esperada, riesgos y decisión final del usuario.

## Resumen ejecutivo

## Herramientas recomendadas principales

| Herramienta | Tipo | URL | Relevancia | Popularidad | Beneficio principal | Riesgo principal | Recomendación |
|---|---|---|---|---|---|---|---|

## Herramientas secundarias

| Herramienta | Tipo | URL | Motivo para considerar más adelante |
|---|---|---|---|

## Herramientas descartadas

| Herramienta | Motivo de descarte |
|---|---|

## Decisiones del usuario

| Fecha | Herramienta | Decisión | Motivo |
|---|---|---|---|

## Pendientes

- [ ] Revisar compatibilidad.
- [ ] Revisar permisos requeridos.
- [ ] Instalar solo si el usuario autoriza.
- [ ] Registrar evidencia de instalación/configuración.
```

---

## Bitácora de sesión — `bitacora/YYYY-MM-DD_session-NNN.md`

```md
# Bitácora de sesión - YYYY-MM-DD

## Número de sesión
## Estado al iniciar la sesión
## Temas tratados
## Avances reportados
## Evidencias aportadas
## Decisiones tomadas
## Problemas / bloqueos
## Errores o aprendizajes
## Cambios respecto al plan
## Riesgos nuevos o actualizados
## Próximas acciones
## Compromisos antes de la próxima sesión
## Estado al cerrar la sesión
## Nota ejecutiva del Sr de la Nata
```
