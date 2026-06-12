#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Reconstruye ejecuciones desde un log NDJSON agent-friendly.

Agrupa los eventos por `run_id`, los ordena por `seq`/`ts`, y emite por cada
corrida una línea de tiempo más un resumen de estados, decisiones, llamadas
externas, reintentos y anomalías, contrastando el resultado esperado con el real.
Captura también la correlación anidada (parent_run_id / sub-corridas, spec §3.5).

El parseo/agrupación viene del módulo compartido `aflog.py` de la skill
`agent-friendly-logging` (única implementación Python de esa lógica). Por eso este
script DEPENDE de que esa skill hermana esté presente en el mismo repo.

Expone HECHOS del log de forma navegable; la interpretación (el porqué) la hace el
agente analista.

Salida: JSON a stdout (parseable). Diagnósticos a stderr.
Código de salida: 0 si el archivo se pudo leer/parsear; 2 en error de uso.

Uso:
  python reconstruct_run.py <log.ndjson> [--run <run_id>] [--pretty]
  python reconstruct_run.py --help

Ejemplos:
  python reconstruct_run.py log.ndjson
  python reconstruct_run.py log.ndjson --run run-9b41dd --pretty
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Importar el parser canónico compartido de la skill hermana agent-friendly-logging.
# parents[2] = .../skills/engineering ; de ahí bajamos a agent-friendly-logging/scripts.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agent-friendly-logging" / "scripts"))
try:
    import aflog
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write("error: no se encontró aflog.py; esta skill requiere la skill hermana "
                     "'agent-friendly-logging' en el mismo repo.\n")
    raise


def reconstruct_run(run: dict) -> dict:
    evs = run["events"]
    oc = aflog.outcome_of(evs)
    timeline, decisions, externals, retries, anomalies = [], [], [], [], []
    for e in evs:
        et = e.get("event_type", "")
        timeline.append({"seq": e.get("seq"), "ts": e.get("ts"), "level": e.get("level"),
                         "component": e.get("component"), "event_type": et, "msg": e.get("msg")})
        if et == "decision":
            decisions.append({"seq": e.get("seq"), "decision": e.get("decision"),
                              "reason": e.get("reason"), "data": e.get("data")})
            if e.get("reason") is None:
                anomalies.append({"seq": e.get("seq"),
                                  "issue": "decision sin reason (causa no registrada)"})
        if et == "external_call":
            externals.append({"seq": e.get("seq"), "external": e.get("external")})
        if et in ("retry", "recovery"):
            retries.append({"seq": e.get("seq"), "event_type": et,
                            "attempt": e.get("attempt"), "reason": e.get("reason")})
        if et in ("anomaly", "warning"):
            anomalies.append({"seq": e.get("seq"), "event_type": et, "reason": e.get("reason"),
                              "expected": e.get("expected"), "actual": e.get("actual")})
    hdr = run["header"]
    return {
        "run_id": run["run_id"],
        "parent_run_id": run.get("parent_run_id"),
        "parent_in_file": run.get("parent_in_file"),
        "children": run.get("children", []),
        "context": {
            "system": hdr.get("system"), "objective": oc["objective"] or hdr.get("objective"),
            "scope": hdr.get("scope"), "depth": hdr.get("depth"),
            "variables_defined": list((hdr.get("variables") or {}).keys()),
        },
        "n_events": len(evs),
        "state_path": aflog.state_path(evs),
        "decisions": decisions,
        "external_calls": externals,
        "retries": retries,
        "anomalies": anomalies,
        "outcome": {"expected": oc["expected"], "actual": oc["actual"], "mismatch": oc["mismatch"],
                    "end_state": oc["end_state"], "end_cause": oc["cause"]},
        "timeline": timeline,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Reconstruye corridas desde un log NDJSON agent-friendly.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("log", help="Ruta al archivo NDJSON de log")
    ap.add_argument("--run", help="Reconstruir solo este run_id")
    ap.add_argument("--pretty", action="store_true", help="JSON indentado")
    args = ap.parse_args()

    path = Path(args.log)
    if not path.is_file():
        print(f"error: no existe el archivo '{args.log}'", file=sys.stderr)
        return 2

    records, warnings = aflog.load_ndjson(path)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)

    runs = aflog.group_runs(records)
    headers, events = aflog.headers_and_events(records)
    if args.run:
        runs = [r for r in runs if r["run_id"] == args.run]
        if not runs:
            print(f"warning: run_id '{args.run}' no encontrado", file=sys.stderr)

    result = {"n_headers": len(headers), "n_events": len(events), "n_runs": len(runs),
              "runs": [reconstruct_run(r) for r in runs]}
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
