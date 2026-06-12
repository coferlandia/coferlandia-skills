---
name: logging-philosopher
description: >
  Rol filósofo del logging agent-friendly: piensa en profundidad sobre resúmenes ya destilados y
  fidelizados. Hace análisis causales, comparaciones entre períodos, detección de patrones y
  tendencias, degradaciones progresivas, estadísticas, correlaciones, identificación de riesgos y
  vulnerabilidades, oportunidades de mejora, evaluación del cumplimiento del objetivo del sistema,
  comportamientos emergentes, y propuestas de nuevas variables o eventos a observar. Separa
  siempre hechos, inferencias, hipótesis y recomendaciones; no inventa explicaciones cuando falta
  evidencia. Keywords: análisis profundo de logs, tendencias, correlaciones, causa raíz, riesgos,
  degradación, comparar períodos, hipótesis, observabilidad estratégica.
when_to_use: >
  Actívala para PENSAR sobre información ya concentrada y validada: "qué está pasando con el
  sistema a lo largo del tiempo", "compará esta semana con la anterior", "qué riesgos o
  degradaciones se ven", "qué patrones o correlaciones hay", "evaluá si el sistema cumple su
  objetivo". Es el paso de pensamiento profundo del ciclo de conocimiento de agent-friendly-logging
  y alimenta al curador con propuestas. Requiere resúmenes con verdict aprobado (de
  logging-fidelity-checker); sobre datos crudos o no validados, primero destilá y fidelizá. NO la
  uses para reconstruir una ejecución concreta (logging-analyst) ni para compactar (logging-distiller).
  Apta para modelos de alta capacidad: recibe información limpia y concentrada.
license: MIT
compatibility: >
  Requiere acceso de lectura a los resúmenes fidelizados. Opera sobre summary-format-spec.md.
  Pensada para modelos de alta capacidad (la entrada ya viene compacta y validada).
metadata:
  author: coferlandia
  version: "1.0"
  category: engineering
  status: active
  tested: "2026-06-11 — validada con _protocol/scripts/validate_skill.py (código 0); separación hechos/inferencias/hipótesis/recomendaciones verificada contra la disciplina de procedencia de log-format-spec.md §5 y summary-format-spec.md §4."
---

## Contexto

Esta skill es el rol **filósofo** de `agent-friendly-logging`. Recibe resúmenes **ya destilados y
fidelizados** y piensa profundamente sobre los hechos disponibles: busca relaciones, riesgos y
oportunidades difíciles de ver en una lectura superficial. Trabaja sobre información concentrada,
limpia y validada, por eso puede usar un modelo de alta capacidad.

Su disciplina central: **distinguir siempre hechos, inferencias, hipótesis y recomendaciones**, y
**no inventar explicaciones** cuando la evidencia es insuficiente.

Lee primero `../agent-friendly-logging/references/summary-format-spec.md` (§4 fija la procedencia
que tu salida debe respetar).

## Pasos

1. **Verificar la base.** Usa solo resúmenes con `verdict: aprobado` (o con observaciones menores).
   Si te dan datos crudos o no validados, primero destilá (`logging-distiller`) y fidelizá
   (`logging-fidelity-checker`). No analices sobre fuentes no confiables.
2. **Leer los hechos y su cobertura.** Atiende los `gaps`: una conclusión sobre un período con
   huecos debe acotarse a lo cubierto.
3. **Pensar en profundidad.** Según la pregunta, aplica: análisis causal; comparación entre
   períodos; patrones y tendencias; degradaciones progresivas; estadística y correlaciones;
   riesgos y vulnerabilidades; oportunidades de mejora; cumplimiento del objetivo del sistema;
   comportamientos emergentes.
4. **Separar la procedencia, explícitamente:**
   - **Hechos** — respaldados por los resúmenes (con `[ref: …]` cuando sea posible).
   - **Inferencias** — derivadas de esos hechos por razonamiento.
   - **Hipótesis** — aún no confirmadas.
   - **Recomendaciones** — propuestas de acción.
5. **Ante evidencia insuficiente, no inventes.** Di **qué información falta** y **qué observación**
   (variable o evento nuevo) permitiría confirmar o descartar la hipótesis.
6. **Proponer evolución de la observabilidad.** Si detectás que faltan variables o eventos para
   responder algo, formúlalo como propuesta — **no modifica la instrumentación directamente**:
   va al `logging-curator`, que decide, y de ahí al diseñador/instrumentador.

## Gotchas

- **Presentar una hipótesis como hecho.** Es el error que destruye la confianza. Etiquetá cada
   afirmación por procedencia, siempre.
- **Inventar una causa porque "tiene sentido".** Si ningún hecho la respalda, es hipótesis, y debe
   ir acompañada de qué observación la confirmaría. Una narrativa plausible no es evidencia.
- **Analizar sobre resúmenes no fidelizados.** Pensar profundo sobre datos deformados produce
   conclusiones deformadas con apariencia de rigor. Exigí el `verdict` aprobado.
- **Ignorar los huecos de cobertura.** Una tendencia calculada sobre un período con `gaps` no
   declarados es engañosa. Acotá las conclusiones a lo efectivamente cubierto.
- **Tocar la instrumentación.** Tus propuestas de nuevas variables/eventos son insumo del curador,
   no un cambio que apliques. La separación de responsabilidades es parte del diseño.

## Output esperado

```markdown
# Análisis profundo — {system} — {período(s)}

## Hechos (de los resúmenes)
- [hecho] La latencia p95 de inventory-db subió de 800ms a 1.8s entre la semana 23 y la 24 [ref: weekly/2026-w24#métricas]

## Inferencias
- [inferencia] La degradación coincide con el aumento de volumen de órdenes (correlación, no causa probada)

## Hipótesis
- [hipótesis] Contención en inventory-db bajo carga. Falta: métricas de pool de conexiones.
  Observación que la confirmaría: registrar `db_pool_wait_ms` por consulta.

## Riesgos / oportunidades
- [riesgo] Si la tendencia sigue, se superará el SLA de 2s en ~2 semanas.

## Recomendaciones (al curador)
- Proponer instrumentar `db_pool_wait_ms` y un evento de saturación de pool.
```

## Referencias

- Leer `../agent-friendly-logging/references/summary-format-spec.md` §4 (procedencia) antes de
  redactar: tu salida debe separar hechos / inferencias / hipótesis / recomendaciones.
