---
name: logging-instrumenter
description: >
  Rol instrumentador del logging agent-friendly: implementa o adapta el logging de un sistema
  según el modelo de observación del diseñador, emitiendo el header explicativo una vez por
  corrida/rotación y eventos NDJSON estructurados (con event_type, reason, expected/actual,
  correlación), sin alterar el comportamiento funcional del sistema. Agnóstico del lenguaje.
  Keywords: instrumentar logging, structured logging, NDJSON, logger, emitir eventos, header de
  log, correlation id, rotación, adaptar logging existente.
when_to_use: >
  Actívala cuando haya que ESCRIBIR o MODIFICAR el código de logging: implementar el modelo de
  observación, migrar logs de texto plano a eventos estructurados, agregar header explicativo,
  o instrumentar decisiones/estados/llamadas externas que faltan. Es el paso 2 del ciclo de
  agent-friendly-logging y se reactiva cuando el curador aprueba cambios. Requiere un modelo de
  observación (de logging-designer); si no existe, primero diseña. No la uses para decidir QUÉ
  loguear (eso es logging-designer) ni para leer logs (logging-analyst).
license: MIT
compatibility: >
  Requiere acceso de lectura/escritura al repositorio del sistema y su toolchain para verificar
  que la build/tests siguen pasando. Agnóstico del lenguaje; el formato NDJSON lo define
  agent-friendly-logging.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); salida de ejemplo verificada contra el spec y parseada por audit_log.py."
---

## Contexto

Esta skill es el rol **instrumentador** de `agent-friendly-logging`. Toma el modelo de
observación del diseñador y lo vuelve código de logging real, **sin cambiar lo que el sistema
hace**: solo cambia lo que *registra*. Es agnóstica del lenguaje — la guía es sobre qué emitir y
cómo estructurarlo, no sobre una librería concreta.

Lee primero `../agent-friendly-logging/references/log-format-spec.md`: define el header, los
campos de evento y el vocabulario de `event_type` que debes emitir.

## Prerequisitos

- Un **modelo de observación** (output de `logging-designer`). Sin él, no instrumentes: diseña primero.
- Capacidad de correr build/tests del sistema para confirmar que no cambiaste el comportamiento.

## Pasos

1. **Elegir el mecanismo de emisión.** Usa el logger del lenguaje/proyecto (structlog, pino,
   zap, slog, Serilog, logging+JSON, etc.). Configúralo para emitir **una línea NDJSON por
   registro**. No inventes un logger nuevo si el proyecto ya tiene uno; adáptalo.
2. **Emitir el header una sola vez.** Al iniciar una corrida (o al abrir/rotar archivo), escribe
   el registro `header` con los datos del modelo. **Nunca por evento.** Si el agregador no
   soporta un "primer registro" especial, emite el header como un evento `event_type:"header"`
   con los mismos campos, pero que aparezca una vez.
3. **Instrumentar el flujo en orden de ejecución:** `run_start` (con `objective`, `inputs`,
   estado inicial) → `phase`/`state_change` en cada transición → `decision` con su `reason` en
   cada bifurcación de negocio → `external_call`/`retry`/`recovery` en dependencias →
   `warning`/`anomaly` ante condiciones fuera de rango → `run_end` con `state` final y `cause`.
4. **Propagar la correlación.** Asegura que `run_id` (y secundarios como `order_id`) viaje por
   todo el flujo y aparezca en cada evento. Añade `seq` monótono por corrida para ordenar.
5. **Registrar el porqué cuando el sistema lo conoce.** En cada `decision`/`state_change`, incluye
   `reason` con la condición concreta (`"stock_level(2) < order_qty(8)"`), no una glosa vaga.
6. **Respetar la profundidad.** Condiciona los eventos por nivel (`depth`): los `diagnostic`/`deep`
   detrás de un flag que se pueda activar/desactivar sin redeploy si es posible.
7. **Configurar la rotación** por tiempo y/o tamaño, y garantizar que **cada archivo nuevo
   reabra con su header** (autocontenido).
8. **Verificar sin tocar el comportamiento.** Corre los tests: el sistema debe comportarse igual.
   Pasa una corrida real por `logging-critic`/`audit_log.py` para confirmar que el log es legible.
9. **(Opcional, recomendado) Entregar la vista en vivo.** Si el sistema quiere mostrar el log a
   humanos, copia `../agent-friendly-logging/assets/dashboard.html` junto al sistema y apúntalo a
   la URL donde se sirve el NDJSON (`dashboard.html?src=<url-del-log>`). Es un archivo único sin
   dependencias que solo lee el log. No es obligatorio: su ausencia no degrada el logging.

## Gotchas

- **Cambiar el comportamiento funcional al instrumentar.** Logging no debe alterar control de
  flujo, timing crítico ni efectos. Evita logging que lance excepciones, bloquee, o reordene
  operaciones. Si un `reason` requiere recalcular algo costoso, reusa el valor ya computado.
- **Repetir el header en cada evento.** Una vez por corrida/rotación. Repetirlo es ruido caro.
- **Loguear secretos o PII.** Nunca emitas tokens, passwords, datos personales, ni payloads
  completos con datos sensibles. Registra el dato que explica la decisión, no el dato crudo
  sensible. Enmascara (`****`) cuando dudes.
- **`reason` decorativo.** `reason:"regla de negocio"` no explica nada. La condición concreta y
  los valores que la disparan, sí.
- **Texto libre en vez de campos.** Meter todo en `msg` impide que un agente filtre por
  `event_type`/`decision`/`state`. Usa los campos estructurados del spec; `msg` es el complemento
  legible, no el contenedor de los datos.
- **NDJSON inválido.** Un objeto multi-línea, comas colgantes o logs entremezclados de varios
  hilos rompen el parseo línea-a-línea. Garantiza una línea = un JSON válido, escritura atómica
  por línea.

## Output esperado

Un diff de instrumentación sobre el sistema (no archivos nuevos de negocio) que produzca, por
corrida, un registro `header` seguido de eventos. El **ejemplo canónico completo** (header con
todos sus campos + eventos) vive en `../agent-friendly-logging/references/example-log.ndjson` — no
lo reproduzcas aquí; basta con que tu salida coincida con ese formato. Un evento típico:

```json
{"rec":"event","ts":"...","level":"info","component":"inventory","run_id":"run-8f2a1c","seq":3,"event_type":"decision","msg":"Stock suficiente, se reserva","decision":"reserve","reason":"stock_level(5) >= order_qty(3)","data":{"stock_level":5,"order_qty":3}}
```

Acompáñalo de una nota: qué se instrumentó, qué `depth` quedó por defecto, y confirmación de que
los tests del sistema siguen pasando.

## Referencias

- Leer `../agent-friendly-logging/references/log-format-spec.md` antes de emitir: define campos
  obligatorios del header/evento y el vocabulario de `event_type`.
- Ver `../agent-friendly-logging/references/example-log.ndjson` como referencia de salida correcta.
