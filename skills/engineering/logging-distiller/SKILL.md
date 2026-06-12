---
name: logging-distiller
description: >
  Rol destilador del logging agent-friendly: convierte logs NDJSON (o resúmenes menores ya
  validados) en un resumen factual, compacto, completo y trazable de un período configurable
  —una hora, un día, una semana, un mes, o cualquier intervalo—. Ordena cronológicamente, agrupa
  repetidos conservando cantidades, preserva estados/decisiones/errores/métricas y mantiene
  referencias a la evidencia original. Solo describe hechos: no diagnostica, no opina, no formula
  hipótesis. Produce un Markdown con bloque meta. Keywords: destilar logs, resumen de período,
  compactar, resumen horario/diario/semanal, destilación jerárquica, rollup de logs.
when_to_use: >
  Actívala cuando haya que COMPACTAR un volumen de logs o resúmenes en un resumen de período:
  "resumí los logs de hoy/esta hora/esta semana", "armá un rollup", "necesito un resumen factual
  del período", o como paso previo a un análisis profundo que no puede leer millones de líneas.
  Es el paso de destilación del ciclo de conocimiento de agent-friendly-logging. Aplica tanto
  desde logs crudos como desde resúmenes menores ya aprobados por logging-fidelity-checker. NO la
  uses para interpretar/diagnosticar (eso es logging-philosopher) ni para verificar un resumen
  (logging-fidelity-checker). Pensada para ejecutarse incluso con un modelo barato: el método es
  estricto y debe seguirse al pie de la letra.
license: MIT
compatibility: >
  Requiere acceso de lectura a los logs/resúmenes fuente y de escritura para el resumen Markdown.
  Opera sobre los formatos definidos en agent-friendly-logging (log-format-spec.md y
  summary-format-spec.md). Apta para modelos de baja capacidad si se sigue el método literal.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); formato de salida verificado contra summary-format-spec.md y aprobado por check_summary.py sobre el log de ejemplo (counts recomputados coinciden, cobertura completa)."
---

## Contexto

Esta skill es el rol **destilador** de `agent-friendly-logging`. El log crudo no escala: nadie
analiza un mes leyendo millones de líneas. El destilador **compacta un período preservando todos
los hechos significativos y sus referencias**, para que un humano o el Filósofo trabajen sobre
información concentrada sin perder la trazabilidad a la evidencia.

Es un rol **metódico y conservador**: describe fielmente qué ocurrió. **No diagnostica, no opina,
no recomienda, no formula hipótesis.** Eso es de `logging-philosopher`. Tu objetivo no es conservar
cada línea, sino preservar todo hecho necesario para reconstruir el panorama completo.

Lee primero `../agent-friendly-logging/references/summary-format-spec.md` — define el bloque meta,
las secciones canónicas, la jerarquía y la sintaxis de referencias. No redefinas el formato.

## Prerequisitos

- Las fuentes: logs NDJSON crudos, o resúmenes menores con `verdict: aprobado` (nunca uses
  resúmenes no verificados — propaga errores hacia arriba).
- El período a cubrir (inicio y fin) y el `level` (hourly/daily/weekly/monthly/custom).

## Pasos (seguir al pie de la letra)

1. **Comprender el contexto.** Lee el `header` del log (o el meta de los resúmenes fuente):
   sistema, propósito, variables y su significado. Sin esto no podés resumir con fidelidad.
2. **Delimitar el período y las fuentes.** Determina `period.start/end` y reúne las `sources`.
   Verifica que la unión de sus períodos cubra el intervalo. Si falta material, **anótalo como
   `gap`**; el período NO es completo.
3. **Ordenar cronológicamente** todos los acontecimientos.
4. **Agrupar repetidos conservando la cantidad.** "240 decisiones `reserve`" en vez de 240 líneas.
   Pero **nunca escondas un evento excepcional dentro de una agrupación**: los únicos/raros van
   listados aparte (sección Errores/excepciones).
5. **Preservar lo significativo:** estados y transiciones; decisiones y sus condiciones (`reason`);
   errores, advertencias y excepciones; métricas, valores y variaciones (rangos, p50/p95/max);
   resultados exitosos/fallidos/incompletos; interrupciones o períodos sin información.
6. **Mantener referencias.** Cada hecho significativo lleva `[ref: …]` a su evidencia (run#seq,
   archivo, o sección de sub-resumen). Es lo que hace el resumen trazable y verificable.
7. **Escribir el bloque meta** (json-meta) con `period`, `sources`, `coverage`, `counts` (y
   `metrics` si aplica). Los `counts` deben ser exactos: el Fidelizador los recomputa.
8. **Escribir el cuerpo** en las secciones canónicas del spec, en orden, **solo con hechos**.
9. **Si destilás desde resúmenes** (jerárquico): registra cada fuente en `sources` con su
   `verdict`, **suma sus conteos**, y hereda sus `gaps` (si una sub-fuente es incompleta, el
   período superior tampoco es completo).
10. **Entregar al Fidelizador.** El resumen no es confiable hasta que `logging-fidelity-checker`
    lo apruebe.

## Gotchas

- **Esconder un evento excepcional en una agrupación.** "1.000 requests ok" que oculta 1 error
   crítico es una falla grave de destilación. Los excepcionales se listan aparte, siempre.
- **Opinar o diagnosticar.** "El sistema está degradado" es interpretación, no hecho. Tu salida
   es factual; la interpretación es del Filósofo. Si lo escribís, el Fidelizador lo marca como
   `opinion_como_hecho`.
- **Declarar completo un período con huecos.** Si falta una fuente o hay un silencio, `coverage.
   complete=false` y el `gap` va listado. Mentir cobertura corrompe toda la jerarquía superior.
- **Perder los conteos al agrupar.** Agrupar sin conservar la cantidad destruye un hecho. "varias
   decisiones" no sirve; "240 decisiones" sí.
- **Soltar las referencias.** Un hecho sin `[ref: …]` no es trazable y el Fidelizador lo observa.
- **Usar resúmenes no aprobados como fuente.** Propaga errores hacia los períodos mayores. Solo
   fuentes crudas o resúmenes `aprobado`.

## Output esperado

Un archivo Markdown con el formato de `summary-format-spec.md`: bloque ```json-meta``` + cuerpo en
las 11 secciones canónicas. Esquema mínimo:

````markdown
# Resumen hourly — {system} — {label}

```json-meta
{ "type":"period-summary", "system":"...", "level":"hourly",
  "period":{...}, "sources":[...], "coverage":{"complete":true,"gaps":[]},
  "counts":{"runs":N,"by_event_type":{...},"by_level":{...},"errors":N,"anomalies":N} }
```

## Período y cobertura
## Panorama general
## Cronología
## Eventos agrupados con conteos
## Estados y transiciones
## Decisiones
## Errores, advertencias y excepciones
## Métricas, valores y variaciones
## Resultados
## Interrupciones / períodos sin información
## Fuentes y trazabilidad
````

## Referencias

- Leer `../agent-friendly-logging/references/summary-format-spec.md` al empezar: define el formato
  exacto que debés producir (meta, secciones, jerarquía, referencias).
- Leer `../agent-friendly-logging/references/log-format-spec.md` §5 para la disciplina de hechos
  (el destilador emite solo `fact`).
