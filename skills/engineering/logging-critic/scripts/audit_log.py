#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audita un log NDJSON agent-friendly y reporta gaps semánticos estructurales.

Chequea lo verificable mecánicamente del spec (references/log-format-spec.md). NO
juzga ambigüedad semántica (eso lo hace el agente crítico a juicio); detecta:

  - existe al menos un registro `header` y trae los campos obligatorios
  - el header NO se repite por evento (señal: varios `event_type:"header"`)
  - cada `event` tiene los campos técnicos: ts, level, component, run_id, msg
  - `level` pertenece al vocabulario declarado en el header
  - toda variable referida en `data`/`reason` está definida en header.variables
  - cada `decision` trae `reason` (causa registrada)
  - cada `result`/`run_end` trae `expected` y `actual`
  - cada corrida (run_id) tiene `run_start` y `run_end`
  - todo `event_type` pertenece al vocabulario del spec

El parseo viene del módulo compartido `aflog.py` de la skill `agent-friendly-logging`
(única implementación Python del parseo). Este script DEPENDE de esa skill hermana.

Salida: JSON a stdout. Diagnósticos a stderr.
Código de salida: 0 si no hay gaps (errores), 1 si los hay, 2 en error de uso.

Uso:
  python audit_log.py <log.ndjson> [--pretty]
  python audit_log.py --help
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Importar el parser canónico compartido de la skill hermana agent-friendly-logging.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agent-friendly-logging" / "scripts"))
try:
    import aflog
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write("error: no se encontró aflog.py; esta skill requiere la skill hermana "
                     "'agent-friendly-logging' en el mismo repo.\n")
    raise

HEADER_REQUIRED = ["system", "purpose", "objective", "scope", "correlation",
                   "depth", "levels", "variables"]
EVENT_REQUIRED = ["ts", "level", "component", "run_id", "msg"]
KNOWN_EVENT_TYPES = {
    "run_start", "input", "phase", "decision", "state_change", "external_call",
    "retry", "recovery", "warning", "anomaly", "result", "run_end", "header",
}
VALID_DEPTH = {"operational", "explanatory", "diagnostic", "deep"}
IDENT_RE = re.compile(r"\b([a-z][a-z0-9_]{2,})\s*\(")  # variable candidata en un reason de texto


def audit(numbered: list[tuple[int, dict]]) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []

    headers = [(n, r) for n, r in numbered if r.get("rec") == "header"]
    inline_headers = [(n, r) for n, r in numbered
                      if r.get("rec") == "event" and r.get("event_type") == "header"]
    events = [(n, r) for n, r in numbered if r.get("rec") == "event"]

    if not headers and not inline_headers:
        errors.append({"check": "header_present", "detail": "no hay registro header"})
    base_header = headers[-1][1] if headers else (inline_headers[-1][1] if inline_headers else {})

    for field in HEADER_REQUIRED:
        if field not in base_header:
            errors.append({"check": "header_field", "field": field,
                           "detail": f"header sin campo obligatorio '{field}'"})

    depth = base_header.get("depth")
    if depth and depth not in VALID_DEPTH:
        errors.append({"check": "depth", "detail": f"depth '{depth}' inválido {sorted(VALID_DEPTH)}"})

    valid_levels = set(base_header.get("levels") or [])
    declared_vars = set((base_header.get("variables") or {}).keys())

    if len(inline_headers) > 1:
        warnings.append({"check": "header_repeated",
                         "detail": f"{len(inline_headers)} headers inline; el header debe ir 1 vez por corrida/rotación"})

    runs: dict[str, dict] = {}
    for n, e in events:
        if e.get("event_type") == "header":
            continue
        rid = e.get("run_id", "<sin run_id>")
        r = runs.setdefault(rid, {"has_start": False, "has_end": False})

        for field in EVENT_REQUIRED:
            if e.get(field) in (None, ""):
                errors.append({"check": "event_field", "line": n, "run_id": rid,
                               "detail": f"evento sin campo técnico '{field}'"})

        lvl = e.get("level")
        if valid_levels and lvl not in valid_levels:
            errors.append({"check": "level_vocab", "line": n,
                           "detail": f"level '{lvl}' no está en levels del header"})

        et = e.get("event_type")
        if et and et not in KNOWN_EVENT_TYPES:
            warnings.append({"check": "event_type_vocab", "line": n,
                             "detail": f"event_type '{et}' fuera del vocabulario del spec"})

        if et == "decision" and e.get("reason") in (None, ""):
            errors.append({"check": "decision_reason", "line": n, "run_id": rid,
                           "detail": "decision sin reason (causa no registrada)"})

        if et in ("result", "run_end"):
            res = e.get("result") or {}
            if "expected" not in res or "actual" not in res:
                errors.append({"check": "expected_actual", "line": n, "run_id": rid,
                               "detail": f"{et} sin expected/actual"})

        if et == "run_start":
            r["has_start"] = True
        if et == "run_end":
            r["has_end"] = True

        used = set((e.get("data") or {}).keys()) if isinstance(e.get("data"), dict) else set()
        reason = e.get("reason")
        if isinstance(reason, str):
            used |= set(IDENT_RE.findall(reason))
        for v in used:
            if declared_vars and v not in declared_vars:
                warnings.append({"check": "undefined_variable", "line": n, "variable": v,
                                 "detail": f"variable '{v}' usada en evento pero no definida en header.variables"})

    for rid, r in runs.items():
        if not r["has_start"]:
            warnings.append({"check": "run_start", "run_id": rid, "detail": "corrida sin run_start"})
        if not r["has_end"]:
            warnings.append({"check": "run_end", "run_id": rid, "detail": "corrida sin run_end"})

    return {
        "ok": not errors,
        "n_headers": len(headers) + len(inline_headers),
        "n_events": len(events),
        "n_runs": len(runs),
        "n_errors": len(errors),
        "n_warnings": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Audita gaps semánticos de un log NDJSON agent-friendly.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("log", help="Ruta al archivo NDJSON de log")
    ap.add_argument("--pretty", action="store_true", help="JSON indentado")
    args = ap.parse_args()

    path = Path(args.log)
    if not path.is_file():
        print(f"error: no existe el archivo '{args.log}'", file=sys.stderr)
        return 2

    numbered, parse_warns = aflog.iter_records(path)
    for w in parse_warns:
        print(f"warning: {w}", file=sys.stderr)

    result = audit(numbered)
    result["warnings"].extend({"check": "parse", "detail": w} for w in parse_warns)
    result["n_warnings"] = len(result["warnings"])

    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))

    tag = "OK" if result["ok"] else "FAIL"
    print(f"[{tag}] {path}: {result['n_errors']} errores, {result['n_warnings']} advertencias",
          file=sys.stderr)
    for e in result["errors"]:
        print(f"   error:   {e.get('detail')}", file=sys.stderr)
    for w in result["warnings"]:
        print(f"   warning: {w.get('detail')}", file=sys.stderr)

    return 1 if result["n_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
