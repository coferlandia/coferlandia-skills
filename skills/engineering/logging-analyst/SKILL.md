---
name: logging-analyst
description: >
  Reconstruye ejecuciones desde logs NDJSON, correlación, estados y decisiones; compara corridas y
  separa hechos, interpretaciones e hipótesis. Usar cuando haya que entender qué pasó, explicar un
  fallo, detectar anomalías o comparar ejecuciones. No usar para instrumentar logging ni para
  auditar la calidad del formato.
license: MIT
compatibility: >
  Requiere acceso de lectura a los archivos de log y Python 3.11+ para el script de
  reconstrucción. Opera sobre el formato NDJSON definido en agent-friendly-logging. El script
  importa el parser compartido aflog.py de esa skill hermana, que debe estar presente en el repo.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); reconstruct_run.py (importando el parser compartido aflog.py de la skill hermana vía __file__) probado sobre example-log.ndjson desde otro cwd: reconstruye run-8f2a1c y run-9b41dd, y enlaza parent_run_id/children en un log anidado sintético."
---

## Contexto

Esta skill es el rol **analista** de `agent-friendly-logging`. Toma logs ya generados y
**reconstruye qué hizo el sistema y por qué**, detecta dónde se desvió de lo esperado, y produce
explicaciones — separando lo que el log dice (hechos) de lo que el analista deduce
(interpretaciones) y de lo que aún no se confirma (hipótesis).

Lee primero `../agent-friendly-logging/references/log-format-spec.md`: el header te da el contexto
(qué es el sistema, qué significan las variables) y los `event_type` te dan la estructura para
reconstruir la corrida.

## Pasos

1. **Leer el header.** Antes de mirar eventos, lee el `header` del segmento: te dice qué sistema
   es, su objetivo, qué variables significan qué, y cómo se correlacionan los eventos. Sin esto,
   los eventos son ruido.
2. **Reconstruir la(s) corrida(s).** Agrupa eventos por `run_id`, ordénalos por `seq`/`ts`, y arma
   la línea de tiempo: estado inicial → transiciones → decisiones (con su `reason`) → llamadas
   externas/reintentos → resultado y causa de finalización. Usa `scripts/reconstruct_run.py` para
   automatizarlo.
3. **Contrastar esperado vs real.** Para cada `result`/`run_end`, compara `expected` con `actual`.
   Donde difieran, localiza la decisión o el evento que originó la divergencia.
4. **Detectar anomalías.** Marca valores fuera de rango (según `header.variables`), latencias
   altas en `external_call`, reintentos repetidos, transiciones inesperadas, o `run_end` con
   `cause` de error.
5. **Comparar corridas** (si aplica). Pon lado a lado una corrida normal y una anómala: ¿en qué
   evento divergen?, ¿qué variable o decisión cambió?
6. **Formular explicación e hipótesis — etiquetadas.** Escribe el informe distinguiendo `fact`
   (citando `run_id#seq`), `interpretation` y `hypothesis`. No presentes una hipótesis como hecho.
7. **Identificar lo que el log NO puede responder.** Anota las preguntas que quedaron sin
   respuesta por falta de datos: eso es el insumo de `logging-critic` y la justificación para
   recomendar subir `depth` (a `diagnostic`/`deep`, temporal y localizado) en la próxima corrida.

## Gotchas

- **Analizar sin leer el header.** Interpretar `decision:"backorder"` sin saber qué significa
  `decision` lleva a conclusiones inventadas. El header es el primer paso, no un opcional.
- **Presentar hipótesis como hechos.** "Falló por la base de datos" sin un evento que lo respalde
  es hipótesis, no hecho. Etiqueta o pierdes la confianza del que lee.
- **Confundir correlación temporal con causa.** Que un `warning` preceda al fallo no prueba que lo
  causó. Busca el `reason`/`cause` registrado; si no existe, dilo y propón cómo registrarlo.
- **Escribir conclusiones dentro del log del sistema.** El analista produce un artefacto separado;
  nunca contamina el log de hechos con interpretaciones.
- **Pedir más detalle sin justificarlo.** Recomendar subir a `deep` solo cuando una pregunta
  concreta no se puede responder con lo disponible — nómbrala.

## Output esperado

```markdown
# Análisis — {system} · corrida {run_id}

## Reconstrucción (hechos)
- [fact run-9b41dd#1] run_start: objetivo "reservar 8 u. SKU-77", estado received
- [fact run-9b41dd#3] external_call inventory-db get_stock latency=1820ms (alto)
- [fact run-9b41dd#4] decision=backorder, reason="stock_level(2) < order_qty(8)"
- [fact run-9b41dd#5] run_end estado=backordered, expected=confirmed / actual=backordered

## Anomalías
- Latencia inventory-db 1820ms supera el rango normal (~<300ms) [interpretation]

## Explicación
- [interpretation] La orden no se confirmó porque el stock (2) era menor a lo pedido (8).
- [hypothesis] La latencia alta sugiere contención en inventory-db; no hay evento que lo confirme.

## Comparación (si aplica)
- run-8f2a1c (ok) vs run-9b41dd (backorder): divergen en seq=3/4 por stock_level (5 vs 2).

## Preguntas sin responder → recomendación
- ¿Por qué stock_level cayó a 2? El log no registra el origen del stock.
  → Recomendar depth=diagnostic en component=inventory para la próxima corrida.
```

## Scripts disponibles

- **`scripts/reconstruct_run.py`** — Reconstruye corridas desde un log NDJSON. Ejecutar cuando
  tengas un archivo de log y quieras la línea de tiempo + resumen de decisiones/estados/anomalías
  por `run_id`, en vez de leerlo a mano. Emite JSON a stdout.

```bash
python scripts/reconstruct_run.py --help
python scripts/reconstruct_run.py path/al/log.ndjson                 # todas las corridas
python scripts/reconstruct_run.py path/al/log.ndjson --run run-9b41dd  # una corrida
```

Para **presentar** los hallazgos a un humano, usa el renderer canónico del orquestador en vez de
formatear a mano (evita que el resumen se desincronice del log):

```bash
python ../agent-friendly-logging/scripts/render_log.py path/al/log.ndjson --view both --run run-9b41dd
```

## Referencias

- Leer `../agent-friendly-logging/references/log-format-spec.md` para saber qué significan los
  `event_type` y la distinción fact/interpretation/hypothesis que tu informe debe respetar.
