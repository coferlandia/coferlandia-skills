---
name: logging-fidelity-checker
description: >
  Verifica que un resumen represente fielmente sus logs o resúmenes fuente: cobertura, conteos,
  cronología, referencias, omisiones e invenciones. Usar después de destilar y antes de reutilizar
  el resumen en períodos mayores o análisis. No usar para auditar instrumentación ni interpretar.
license: MIT
compatibility: >
  Requiere acceso de lectura al resumen y a sus fuentes, y Python 3.11+ para el verificador
  mecánico. Opera sobre summary-format-spec.md. El script check_summary.py importa el parser
  compartido aflog.py de la skill hermana agent-friendly-logging, que debe estar en el repo.
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); check_summary.py aprueba un resumen correcto (exit 0, hint aprobado) y rechaza uno degradado (exit 1: detecta coverage.complete con gap, conteos runs 5≠2 y decision 9≠2, y referencia no resoluble)."
---

## Contexto

Esta skill es el rol **fidelizador** de `agent-friendly-logging`. Un resumen solo es confiable si
representa fielmente sus fuentes; si no, toda la jerarquía superior y el análisis del Filósofo se
construyen sobre datos deformados. Tu función es **evaluar fidelidad, cobertura y trazabilidad** —
exclusivamente eso. No reinterpretás el sistema ni hacés análisis estratégico.

Lee primero `../agent-friendly-logging/references/summary-format-spec.md` (§5 define el veredicto,
§6 separa lo mecánico de lo que es a juicio).

## Pasos

1. **Reunir el resumen y sus fuentes** (los `sources` declarados en el meta del resumen).
2. **Correr el verificador mecánico primero.** `scripts/check_summary.py` cubre lo objetivo:
   bloque meta completo, `coverage.complete` consistente con `gaps` y con el span de las fuentes,
   `sources` que resuelven, `counts` recomputados desde NDJSON / sumados desde sub-resúmenes, y
   tokens `[ref: …]` que resuelven. Empieza por aquí: barato y elimina lo evidente.
3. **Aplicar juicio a lo que la máquina no ve.** Compara resumen ↔ fuentes para detectar:
   - **Omisiones** de hechos relevantes presentes en las fuentes.
   - **Alteraciones de significado** (el resumen dice algo que la fuente no dice).
   - **Generalizaciones excesivas** ("siempre/nunca" donde la fuente es matizada).
   - **Eventos excepcionales ocultos** por una agrupación (un error perdido en "1.000 ok").
   - **Datos inventados** o no respaldados por ninguna fuente.
   - **Opiniones presentadas como hechos** (el destilador no debe opinar).
   - **Errores cronológicos** y **períodos sin cobertura** no declarados.
4. **Declarar el alcance.** Si el volumen es grande, podés combinar verificación completa y
   muestreo, pero **indica explícitamente** qué verificaste al 100% y qué por muestreo (`scope`).
5. **Emitir el veredicto** (uno de los cuatro) con `findings` concretos por tipo y ubicación.
6. **Devolver al destilador** si hay desviaciones. El resumen solo es confiable tras `aprobado`
   (o `aprobado_con_observaciones`). El ciclo se repite hasta aprobar o declarar `no_verificable`.

## Gotchas

- **Aprobar sin declarar el alcance.** Un "aprobado" sin decir si fue verificación completa o por
   muestreo es engañoso. El `scope` es obligatorio.
- **Tratar el verificador mecánico como suficiente.** El script ve conteos y cobertura, no ve una
   omisión semántica ni un excepcional ahogado en una agrupación. Siempre complementá con juicio.
- **Reinterpretar el sistema.** No es tu trabajo decir por qué pasó algo ni si está bien; solo si
   el resumen **refleja** lo que dicen las fuentes. La interpretación es del Filósofo.
- **Findings vagos.** "El resumen no es fiel" no sirve. "counts.runs dice 5, las fuentes tienen 2"
   o "el error crítico de run-9b41dd#5 no aparece en la sección Errores" sí: accionable.
- **Aprobar un resumen que usa fuentes no aprobadas.** Si una `source` es un resumen con verdict
   distinto de aprobado, márcalo: la cadena de confianza se rompe.

## Output esperado

Archivo con bloque meta `fidelity-verdict` (ver spec §5) + prosa con los findings:

```json-meta
{
 "type":"fidelity-verdict","summary_ref":"summaries/hourly/2026-06-11-14.md",
 "verdict":"requiere_correccion",
 "scope":{"method":"mixto","coverage":"conteos 100% + muestreo 10% de eventos","notes":""},
 "findings":[
   {"type":"conteo","detail":"counts.runs=5 pero las fuentes tienen 2","where":"meta.counts"},
   {"type":"excepcion_oculta","detail":"error crítico no listado","where":"sección Errores"}
 ],
 "checked_at":"2026-06-11T15:05:00Z"
}
```

## Scripts disponibles

- **`scripts/check_summary.py`** — Verificación mecánica de fidelidad. Ejecutar como primer paso.
  Valida meta, cobertura, referencias y recomputa conteos desde las fuentes. Emite JSON; exit 0 si
  no hay errores, 1 si los hay. Devuelve además un `verdict_hint` orientativo (no reemplaza tu
  juicio).

```bash
python scripts/check_summary.py --help
python scripts/check_summary.py resumen.md --sources-dir . --recount
```

## Referencias

- Leer `../agent-friendly-logging/references/summary-format-spec.md` §5 (veredicto) y §6 (mecánico
  vs juicio) como la vara de evaluación.
