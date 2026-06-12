---
name: logging-curator
description: >
  Rol curador del logging agent-friendly: decide qué sugerencias del crítico se incorporan,
  equilibrando dos riesgos opuestos —falta de información y crecimiento descontrolado del log—.
  Acepta lo que ayuda a responder preguntas reales, rechaza lo redundante, y mantiene la base de
  conocimiento acumulado (comportamientos normales, rangos, patrones, anomalías conocidas,
  hipótesis confirmadas/descartadas, variables útiles vs redundantes). Cierra el ciclo devolviendo
  cambios accionables al diseñador/instrumentador. Keywords: curaduría de logging, qué loguear,
  podar logs, base de conocimiento, gobernanza de observabilidad, evolución del logging.
when_to_use: >
  Actívala cuando haya un conjunto de sugerencias (del crítico o del análisis) y haya que DECIDIR
  cuáles aplicar sin inflar el log, o cuando haya que registrar conocimiento aprendido entre
  corridas (rangos normales, anomalías conocidas, hipótesis confirmadas). Es el paso 6 del ciclo
  de agent-friendly-logging y emite la orden de cambio al diseñador/instrumentador. Aplica aunque
  el usuario solo diga "qué de esto vale la pena loguear" o "esto está creciendo demasiado". No la
  uses para producir las sugerencias (logging-critic) ni para implementarlas (logging-instrumenter).
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura a la base de conocimiento del sistema (p. ej.
  logging-knowledge/) y a las sugerencias del crítico. Opera sobre el formato de
  agent-friendly-logging.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); decisiones de curaduría verificadas contra el formato de base de conocimiento del spec (§5.1)."
---

## Contexto

Esta skill es el rol **curador** de `agent-friendly-logging`. Es el guardián del equilibrio: un
log puede fallar por **defecto** (no registra lo necesario para entenderlo) o por **exceso**
(crece sin control y se vuelve ruido caro). El curador decide, sugerencia por sugerencia, qué
entra y qué no, con un criterio único: *¿esto ayuda a responder una pregunta real sobre el
funcionamiento del sistema?* Además, **acumula el conocimiento** que el ciclo va produciendo para
que no se pierda entre corridas.

Lee primero `../agent-friendly-logging/references/log-format-spec.md` (§5.1 define el formato de
la base de conocimiento; la distinción fact/interpretation/hypothesis es obligatoria).

## Pasos

1. **Recibir las propuestas** de dos fuentes: el **crítico** (deficiencias del logging detectadas)
   y el **filósofo** (nuevas variables o eventos que valdría observar), más las preguntas sin
   responder del analista. Clasifícalas en *agregar* / *quitar* / *aclarar*.
2. **Aplicar el criterio de valor a cada una.** Acepta una sugerencia de *agregar* solo si existe
   una pregunta real que hoy no se puede responder y este dato la responde. Acepta una de *quitar*
   si el dato no respondió ninguna pregunta en las últimas corridas. Ante duda en *agregar*,
   prefiere **diferir**: súbelo solo cuando una anomalía concreta lo exija (vía `depth`), no de
   forma permanente.
3. **Resolver el balance defecto/exceso explícitamente.** Por cada *agregar* aceptado, pregunta
   si algo se puede *quitar* a cambio. El log no debería crecer monótonamente.
4. **Emitir la orden de cambio.** Produce una lista accionable para `logging-designer`
   (si cambia el modelo de observación) y/o `logging-instrumenter` (si solo cambia el código),
   con aceptadas, rechazadas y diferidas, cada una con su razón.
5. **Actualizar la base de conocimiento** (§5.1 del spec). Registra lo aprendido, etiquetado y
   fechado: comportamientos normales, rangos habituales, patrones recurrentes, anomalías
   conocidas, problemas investigados, hipótesis confirmadas o descartadas, variables que
   demostraron ser útiles, e información redundante candidata a eliminar. Mantén separado el
   `kind` fact/interpretation/hypothesis.
6. **Cerrar el lazo.** Las aceptadas vuelven al diseñador/instrumentador; las próximas corridas
   producen información más útil. Ese es el ciclo de mejora continua.

## Gotchas

- **Aceptar todo lo que sugiere el crítico.** El crítico detecta; el curador modera. Aceptar cada
  *agregar* reproduce el problema del log inflado. Exige una pregunta real por cada adición.
- **No quitar nunca.** Un log solo crece si nadie poda. Revisa qué variables/eventos no
  respondieron ninguna pregunta en N corridas y propón quitarlos.
- **Perder el conocimiento entre corridas.** Si lo aprendido (que `stock_level` normal es 2..50,
  que tal anomalía ya se investigó) no se escribe en la base de conocimiento, el ciclo reaprende
  lo mismo cada vez. Persistirlo es parte del trabajo, no un extra.
- **Mezclar `kind` en la base de conocimiento.** Anotar una hipótesis como si fuera un rango
  confirmado corrompe la base. Etiqueta siempre y mueve hipótesis→hecho solo con evidencia.
- **Decidir sin trazar la razón.** Una sugerencia rechazada sin motivo registrado reaparecerá en
  la próxima crítica. Anota por qué se rechazó o difirió.

## Output esperado

```markdown
# Curaduría — {system} · ciclo {fecha}

## Decisiones
| sugerencia | decisión | razón |
|------------|----------|-------|
| add reason en decision/inventory | aceptar | responde "por qué decidió", pregunta abierta del análisis |
| add snapshot completo de payload | diferir | solo bajo depth=diagnostic ante anomalía; no permanente |
| quitar 2 eventos `phase` redundantes | aceptar | no respondieron ninguna pregunta en últimas corridas |

## Orden de cambio
- a logging-designer: definir variable order_qty en el modelo
- a logging-instrumenter: añadir reason en decision/inventory; colapsar phase→state_change

## Base de conocimiento actualizada (logging-knowledge/{system}.ndjson)
{"kind":"interpretation","date":"2026-06-11","topic":"rango_normal","statement":"stock_level normal 2..50","evidence":["run-8f2a1c#3","run-9b41dd#4"]}
{"kind":"hypothesis","date":"2026-06-11","topic":"latencia","statement":"picos de latencia en inventory-db bajo carga","evidence":["run-9b41dd#3"]}
```

## Referencias

- Leer `../agent-friendly-logging/references/log-format-spec.md` §5 (procedencia) y §5.1 (formato
  de la base de conocimiento) antes de registrar conocimiento.
