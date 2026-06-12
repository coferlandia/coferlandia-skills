#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verificación MECÁNICA de fidelidad de un resumen de período agent-friendly.

Cubre lo objetivo del formato definido en agent-friendly-logging/references/
summary-format-spec.md; el juicio semántico lo hace el agente logging-fidelity-checker.
Chequea:

  - el bloque meta ```json-meta existe y trae los campos obligatorios
  - coverage.complete es consistente con gaps y con el span de las sources
  - cada sources[].ref existe (relativo a --sources-dir)
  - counts recomputados desde NDJSON (sources kind=log) o sumados desde
    sub-resúmenes (kind=summary) coinciden con meta.counts          [--recount]
  - las sources de kind=summary están aprobadas (verdict)            [warning]
  - tokens [ref: token] del cuerpo resuelven cuando son verificables [warning]

El conteo de NDJSON reutiliza el parser compartido aflog.py de la skill hermana
agent-friendly-logging (que debe estar presente en el repo).

Salida: JSON a stdout. Diagnósticos a stderr.
Código de salida: 0 sin errores, 1 con errores, 2 en error de uso.

Uso:
  python check_summary.py <resumen.md> [--sources-dir DIR] [--recount] [--pretty]
  python check_summary.py --help

Ejemplos:
  python check_summary.py summaries/hourly/2026-06-11-14.md --sources-dir . --recount
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agent-friendly-logging" / "scripts"))
try:
    import aflog
except ModuleNotFoundError:  # pragma: no cover
    sys.stderr.write("error: no se encontró aflog.py; esta skill requiere la skill hermana "
                     "'agent-friendly-logging' en el mismo repo.\n")
    raise

META_RE = re.compile(r"```json-meta\s*\n(.*?)\n```", re.S)
REF_RE = re.compile(r"\[ref:\s*([^\]]+?)\s*\]")
RUNSEQ_RE = re.compile(r"^(.+)#(\d+)$")
META_REQUIRED = ["type", "system", "level", "period", "sources", "coverage", "counts"]
APPROVED = {"aprobado", "aprobado_con_observaciones"}


def extract_meta(text: str) -> tuple[dict | None, str]:
    m = META_RE.search(text)
    if not m:
        return None, "no se encontró el bloque ```json-meta"
    try:
        return json.loads(m.group(1)), ""
    except json.JSONDecodeError as e:
        return None, f"bloque json-meta inválido: {e.msg}"


def union_covers(period: dict, sources: list[dict]) -> tuple[bool, list[str]]:
    """¿La unión de los period de sources cubre [start,end] sin huecos?"""
    spans = sorted(((s.get("period") or {}).get("start"), (s.get("period") or {}).get("end"))
                   for s in sources if s.get("period"))
    spans = [(a, b) for a, b in spans if a and b]
    notes: list[str] = []
    if not spans:
        return False, ["ninguna source declara period; no se puede verificar cobertura"]
    cursor = period.get("start")
    end = period.get("end")
    if not cursor or not end:
        return False, ["period.start/end ausente"]
    ok = True
    if spans[0][0] > cursor:
        ok = False
        notes.append(f"hueco al inicio: {cursor}..{spans[0][0]}")
    for a, b in spans:
        if a > cursor:
            ok = False
            notes.append(f"hueco de cobertura: {cursor}..{a}")
        cursor = max(cursor, b)
    if cursor < end:
        ok = False
        notes.append(f"hueco al final: {cursor}..{end}")
    return ok, notes


def recompute_counts(sources: list[dict], base: Path) -> tuple[dict, list[str]]:
    """Recalcula runs/by_event_type/by_level/errors/anomalies desde las fuentes."""
    agg = {"runs": 0, "by_event_type": {}, "by_level": {}, "errors": 0, "anomalies": 0}
    problems: list[str] = []
    for s in sources:
        ref = s.get("ref", "")
        p = (base / ref)
        if s.get("kind") == "log":
            if not p.is_file():
                problems.append(f"source log no encontrada: {ref}")
                continue
            records, _ = aflog.load_ndjson(p)
            runs = aflog.group_runs(records)
            agg["runs"] += len(runs)
            _, events = aflog.headers_and_events(records)
            for e in events:
                et = e.get("event_type", "?")
                lvl = (e.get("level") or "?").lower()
                agg["by_event_type"][et] = agg["by_event_type"].get(et, 0) + 1
                agg["by_level"][lvl] = agg["by_level"].get(lvl, 0) + 1
                if lvl in ("error", "critical"):
                    agg["errors"] += 1
                if et == "anomaly":
                    agg["anomalies"] += 1
        elif s.get("kind") == "summary":
            if not p.is_file():
                problems.append(f"source summary no encontrada: {ref}")
                continue
            sub, err = extract_meta(p.read_text(encoding="utf-8"))
            if not sub:
                problems.append(f"sub-resumen sin meta válido: {ref} ({err})")
                continue
            c = sub.get("counts", {})
            agg["runs"] += c.get("runs", 0)
            agg["errors"] += c.get("errors", 0)
            agg["anomalies"] += c.get("anomalies", 0)
            for et, n in (c.get("by_event_type") or {}).items():
                agg["by_event_type"][et] = agg["by_event_type"].get(et, 0) + n
            for lvl, n in (c.get("by_level") or {}).items():
                agg["by_level"][lvl] = agg["by_level"].get(lvl, 0) + n
    return agg, problems


def check(summary_path: Path, sources_dir: Path, recount: bool) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    text = summary_path.read_text(encoding="utf-8")
    meta, err = extract_meta(text)
    if not meta:
        return {"ok": False, "verdict_hint": "no_verificable",
                "errors": [{"check": "meta", "detail": err}], "warnings": []}

    for f in META_REQUIRED:
        if f not in meta:
            errors.append({"check": "meta_field", "detail": f"meta sin campo obligatorio '{f}'"})

    period = meta.get("period") or {}
    sources = meta.get("sources") or []
    coverage = meta.get("coverage") or {}

    # cobertura
    covered, notes = union_covers(period, sources) if sources else (False, ["sin sources"])
    if coverage.get("complete") and coverage.get("gaps"):
        errors.append({"check": "coverage", "detail": "coverage.complete=true pero gaps no está vacío"})
    if coverage.get("complete") and not covered:
        errors.append({"check": "coverage", "detail": "coverage.complete=true pero las sources no cubren el período: "
                       + "; ".join(notes)})

    # sources resuelven + verdict aprobado
    for s in sources:
        ref = s.get("ref", "")
        if not (sources_dir / ref).exists():
            errors.append({"check": "source_ref", "detail": f"source no encontrada: {ref}"})
        if s.get("kind") == "summary" and s.get("verdict") and s["verdict"] not in APPROVED:
            warnings.append({"check": "source_verdict",
                             "detail": f"source summary '{ref}' con verdict '{s['verdict']}' (debería estar aprobado)"})

    # conteos
    if recount and sources:
        agg, problems = recompute_counts(sources, sources_dir)
        for p in problems:
            warnings.append({"check": "recount_source", "detail": p})
        declared = meta.get("counts") or {}
        for key in ("runs", "errors", "anomalies"):
            if key in declared and declared[key] != agg[key]:
                errors.append({"check": "count_mismatch",
                               "detail": f"counts.{key}: meta={declared[key]} recomputado={agg[key]}"})
        for et, n in (declared.get("by_event_type") or {}).items():
            if agg["by_event_type"].get(et, 0) != n:
                errors.append({"check": "count_mismatch",
                               "detail": f"counts.by_event_type.{et}: meta={n} recomputado={agg['by_event_type'].get(et, 0)}"})

    # referencias del cuerpo
    log_paths = [sources_dir / s["ref"] for s in sources
                 if s.get("kind") == "log" and (sources_dir / s["ref"]).is_file()]
    runseq_index = None
    for tok in set(REF_RE.findall(text)):
        m = RUNSEQ_RE.match(tok)
        if m:
            if runseq_index is None:
                runseq_index = set()
                for lp in log_paths:
                    recs, _ = aflog.load_ndjson(lp)
                    for e in recs:
                        if e.get("rec") == "event" and e.get("run_id") and e.get("seq") is not None:
                            runseq_index.add(f"{e['run_id']}#{e['seq']}")
            if tok not in runseq_index:
                warnings.append({"check": "ref_unresolved", "detail": f"[ref: {tok}] no resuelve en los logs fuente"})
        elif "#" in tok:
            continue  # ref a sección de sub-resumen: verificación a juicio
        else:
            if not any(s.get("ref", "").endswith(tok) for s in sources):
                warnings.append({"check": "ref_unresolved", "detail": f"[ref: {tok}] no coincide con ninguna source"})

    return {"ok": not errors,
            "verdict_hint": ("requiere_correccion" if errors
                             else "aprobado_con_observaciones" if warnings else "aprobado"),
            "summary": str(summary_path),
            "n_errors": len(errors), "n_warnings": len(warnings),
            "errors": errors, "warnings": warnings}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Verificación mecánica de fidelidad de un resumen de período agent-friendly.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("summary", help="Ruta al resumen .md")
    ap.add_argument("--sources-dir", default=".", help="Base para resolver sources[].ref (default: cwd)")
    ap.add_argument("--recount", action="store_true", help="Recalcular counts desde las fuentes y comparar")
    ap.add_argument("--pretty", action="store_true", help="JSON indentado")
    args = ap.parse_args()

    path = Path(args.summary)
    if not path.is_file():
        print(f"error: no existe el resumen '{args.summary}'", file=sys.stderr)
        return 2

    result = check(path, Path(args.sources_dir), args.recount)
    print(json.dumps(result, indent=2 if args.pretty else None, ensure_ascii=False))

    tag = "OK" if result["ok"] else "FAIL"
    print(f"[{tag}] {path}: hint={result.get('verdict_hint')} "
          f"{result.get('n_errors', 0)} errores, {result.get('n_warnings', 0)} advertencias", file=sys.stderr)
    for e in result.get("errors", []):
        print(f"   error:   {e['detail']}", file=sys.stderr)
    for w in result.get("warnings", []):
        print(f"   warning: {w['detail']}", file=sys.stderr)
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
