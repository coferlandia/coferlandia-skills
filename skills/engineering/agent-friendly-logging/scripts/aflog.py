#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Parser y proyección canónica de logs NDJSON agent-friendly (biblioteca compartida).

Es la ÚNICA implementación del parseo/agrupación en Python: fuente de verdad del
código de lectura. La importan:
  - render_log.py (mismo paquete)                 -> Markdown
  - logging-analyst/scripts/reconstruct_run.py    -> JSON de reconstrucción
  - logging-critic/scripts/audit_log.py           -> auditoría de gaps semánticos
El dashboard.html replica esta lógica en JS (única copia JS, ligada al mismo spec).

Contrato de formato: agent-friendly-logging/references/log-format-spec.md.
Esta lib NO emite Markdown ni JSON de salida: solo parsea y proyecta semántica
(texto plano / estructuras Python). El formateo vive en cada consumidor.

Uso como CLI (smoke test / resumen rápido):
  python aflog.py <log.ndjson>          # resumen JSON de corridas a stdout
  python aflog.py --help
"""
from __future__ import annotations

import json
from pathlib import Path

# Vocabularios del spec (§3.2, §6.1). Fuente de verdad de estos conjuntos.
ERROR_LEVELS = {"error", "critical"}
WARN_LEVELS = {"warn", "warning"}
ALERT_TYPES = {"warning", "anomaly"}
STATE_TYPES = {"state_change", "phase", "run_start", "run_end"}
LEVEL_ORDER = {"debug": 0, "info": 1, "warn": 2, "warning": 2, "error": 3, "critical": 4}


# ---------------------------------------------------------------- carga NDJSON
def iter_records(path: str | Path) -> tuple[list[tuple[int, dict]], list[str]]:
    """Devuelve ([(lineno, record)], warnings). Conserva el número de línea para
    que un consumidor (p. ej. el auditor) pueda localizar el gap."""
    out: list[tuple[int, dict]] = []
    warnings: list[str] = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append((n, json.loads(line)))
        except json.JSONDecodeError as e:
            warnings.append(f"línea {n}: JSON inválido ({e.msg}) — se omite")
    return out, warnings


def load_ndjson(path: str | Path) -> tuple[list[dict], list[str]]:
    """(records, warnings) sin número de línea."""
    numbered, warns = iter_records(path)
    return [r for _, r in numbered], warns


def headers_and_events(records: list[dict]) -> tuple[list[dict], list[dict]]:
    headers = [r for r in records if r.get("rec") == "header"]
    events = [r for r in records if r.get("rec") == "event" and r.get("event_type") != "header"]
    return headers, events


# ----------------------------------------------------------- agrupar corridas
def _first(events: list[dict], field: str):
    for e in events:
        if e.get(field) is not None:
            return e.get(field)
    return None


def group_runs(records: list[dict]) -> list[dict]:
    """Agrupa eventos por run_id, ordena por seq/ts y adjunta su header.
    Captura correlación anidada (parent_run_id) y enlaza hijos (spec §3.5)."""
    headers, events = headers_and_events(records)
    header_by_run = {h["run_id"]: h for h in headers if h.get("run_id")}
    base = headers[-1] if headers else {}

    runs: dict[str, list[dict]] = {}
    for ev in events:
        runs.setdefault(ev.get("run_id", "unknown"), []).append(ev)

    out: list[dict] = []
    for rid, evs in runs.items():
        evs = sorted(evs, key=lambda e: (e.get("seq", 0), e.get("ts", "")))
        hdr = header_by_run.get(rid, base)
        corr = hdr.get("correlation") or {}
        out.append({
            "run_id": rid,
            "events": evs,
            "header": hdr,
            "parent_run_id": _first(evs, "parent_run_id") or corr.get("parent_run_id"),
        })

    ids = {r["run_id"] for r in out}
    for r in out:
        r["children"] = sorted(c["run_id"] for c in out if c.get("parent_run_id") == r["run_id"])
        # parent fuera del archivo: lo marcamos para que el consumidor lo note
        r["parent_in_file"] = r["parent_run_id"] in ids if r["parent_run_id"] else None
    return out


# -------------------------------------------------------- proyección semántica
def outcome_of(events: list[dict]) -> dict:
    expected = actual = cause = end_state = objective = None
    for e in events:
        if e.get("event_type") == "run_start" and e.get("objective") is not None:
            objective = e["objective"]
        res = e.get("result")
        if isinstance(res, dict):
            expected = res.get("expected", expected)
            actual = res.get("actual", actual)
        if e.get("event_type") == "run_end":
            end_state = e.get("state", end_state)
            cause = e.get("cause", cause)
    mismatch = expected is not None and actual is not None and expected != actual
    return {"expected": expected, "actual": actual, "cause": cause,
            "end_state": end_state, "objective": objective, "mismatch": mismatch}


def state_path(events: list[dict]) -> list[str]:
    path: list[str] = []
    for e in events:
        if e.get("event_type") in STATE_TYPES:
            s = e.get("to_state") or e.get("state")
            if s and (not path or path[-1] != s):
                path.append(s)
    return path


def event_marker(e: dict) -> str:
    """Marcador determinista del spec §6.1 (sin criterio humano)."""
    lvl = (e.get("level") or "").lower()
    et = (e.get("event_type") or "").lower()
    if lvl in ERROR_LEVELS:
        return "🔴"
    if lvl in WARN_LEVELS or et in ALERT_TYPES:
        return "⚠"
    return ""


def short_time(ts) -> str:
    """ISO-8601 -> HH:MM:SS.mmm (la fecha vive en la ficha de header)."""
    if ts is None:
        return ""
    if "T" not in str(ts):
        return str(ts)
    return str(ts).split("T", 1)[1].rstrip("Z").split("+")[0]


def key_facts(e: dict) -> str:
    """Proyección compacta evento -> datos clave (texto plano, sin formato) según §6.3."""
    et = e.get("event_type")
    if et == "decision":
        d, r = e.get("decision"), e.get("reason")
        return f"{d} ← {r}" if r else (d or "")
    if et == "state_change":
        s = f"{e.get('from_state')} → {e.get('to_state')}"
        return s + (f" ({e.get('reason')})" if e.get("reason") else "")
    if et == "external_call":
        x = e.get("external") or {}
        return f"{x.get('service')}/{x.get('op')} {x.get('status', '')} {x.get('latency_ms', '')}ms".strip()
    if et in ("retry", "recovery"):
        return f"intento {e.get('attempt')}/{e.get('max_attempts', '?')} {e.get('reason', '')}".strip()
    if et == "anomaly":
        return f"esperado {e.get('expected')} / real {e.get('actual')}"
    if et in ("result", "run_end"):
        r = e.get("result") or {}
        base = f"esperado {r.get('expected')} / real {r.get('actual')}"
        return base + (f" · {e.get('cause')}" if e.get("cause") else "")
    if et == "run_start":
        return f"obj: {e.get('objective', '')}"
    return json.dumps(e["data"], ensure_ascii=False) if e.get("data") else ""


# ----------------------------------------------------------------------- CLI
def _main() -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(
        description="Parser canónico de logs NDJSON agent-friendly. CLI = resumen de corridas.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("log", help="Ruta al archivo NDJSON")
    args = ap.parse_args()
    path = Path(args.log)
    if not path.is_file():
        print(f"error: no existe el archivo '{args.log}'", file=sys.stderr)
        return 2
    records, warns = load_ndjson(path)
    for w in warns:
        print(f"warning: {w}", file=sys.stderr)
    runs = group_runs(records)
    summary = [{
        "run_id": r["run_id"], "n_events": len(r["events"]),
        "parent_run_id": r["parent_run_id"], "children": r["children"],
        "state_path": state_path(r["events"]), "outcome": outcome_of(r["events"]),
    } for r in runs]
    print(json.dumps({"n_runs": len(runs), "runs": summary}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
