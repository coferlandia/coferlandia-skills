#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Renderiza un log NDJSON agent-friendly como Markdown legible para humanos.

Implementa la PROYECCIÓN HUMANA CANÓNICA del spec §6 (mismo layout que el
dashboard en vivo). Vista DERIVADA del NDJSON: solo lee, no inventa. Si falta un
campo (p. ej. el `reason` de una decisión), la celda queda vacía — el gap se ve.

El parseo/agrupación viene del módulo compartido `aflog.py` (misma carpeta), que
es la única implementación Python de esa lógica. Aquí solo se formatea a Markdown.

Vistas:
  digest    (default) ficha por corrida: header + variables + estados +
            decisiones + alertas + desenlace
  timeline  tabla evento-a-evento
  both      digest seguido de timeline

Salida: Markdown a stdout. Diagnósticos a stderr.
Código de salida: 0 si se pudo leer/parsear; 2 en error de uso.

Uso:
  python render_log.py <log.ndjson> [--view digest|timeline|both] [--run <run_id>]
  python render_log.py --help

Ejemplos:
  python render_log.py log.ndjson
  python render_log.py log.ndjson --view both --run run-9b41dd > informe.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import aflog  # módulo compartido en la misma carpeta (single source del parseo)


def md(v) -> str:
    """Escapa lo mínimo para no romper una celda de tabla Markdown."""
    if v is None:
        return ""
    return str(v).replace("|", "\\|").replace("\n", " ").strip()


def render_digest(run: dict) -> list[str]:
    evs, hdr = run["events"], run["header"]
    oc = aflog.outcome_of(evs)
    mark = "❌" if oc["mismatch"] else "✅"
    label = "no confirmada" if oc["mismatch"] else "ok"
    out = [f"### {md(hdr.get('system', 'sistema'))} · {md(run['run_id'])} · "
           f"depth={md(hdr.get('depth', '?'))}  {mark} {label}"]
    if run.get("parent_run_id"):
        out.append(f"↳ sub-corrida de `{md(run['parent_run_id'])}`")
    if run.get("children"):
        out.append("sub-corridas: " + ", ".join(f"`{md(c)}`" for c in run["children"]))
    out.append(f"**Objetivo:** {md(oc['objective'] or hdr.get('objective'))} · "
               f"**Scope:** {md(hdr.get('scope'))}")
    out.append("")

    variables = hdr.get("variables") or {}
    if variables:
        out += ["| variable | significado | unidad | valores |",
                "|----------|-------------|--------|---------|"]
        for name, meta in variables.items():
            meta = meta or {}
            vals = " · ".join(meta.get("values", [])) if meta.get("values") else meta.get("range", "")
            out.append(f"| {md(name)} | {md(meta.get('meaning'))} | "
                       f"{md(meta.get('unit') or '—')} | {md(vals)} |")
        out.append("")

    sp = aflog.state_path(evs)
    if sp:
        out += ["**Estados:** " + " → ".join(md(s) for s in sp), ""]

    decisions = [e for e in evs if e.get("event_type") == "decision"]
    if decisions:
        out += ["| seq | decisión | porqué (reason) |", "|-----|----------|-----------------|"]
        for e in decisions:
            out.append(f"| {md(e.get('seq'))} | {md(e.get('decision'))} | {md(e.get('reason'))} |")
        out.append("")

    alerts = [e for e in evs if aflog.event_marker(e)]
    for e in alerts:
        out.append(f"{aflog.event_marker(e)} seq {md(e.get('seq'))} · "
                   f"{md(e.get('event_type'))} {md(e.get('component'))} — {md(aflog.key_facts(e))}")
    if alerts:
        out.append("")

    if oc["expected"] is not None or oc["actual"] is not None:
        out.append(f"**Desenlace:** esperado `{md(oc['expected'])}` / real `{md(oc['actual'])}`"
                   + (f" — causa: {md(oc['cause'])}" if oc["cause"] else ""))
    out.append("")
    return out


def render_timeline(run: dict) -> list[str]:
    evs, hdr = run["events"], run["header"]
    out = [f"#### Timeline · {md(hdr.get('system', 'sistema'))} · {md(run['run_id'])}", "",
           "| | seq | hora | nivel | componente | tipo | mensaje | datos |",
           "|-|-----|------|-------|------------|------|---------|-------|"]
    for e in evs:
        mk = aflog.event_marker(e)
        if not mk and aflog.outcome_of([e])["mismatch"]:
            mk = "❌"
        out.append(f"| {mk} | {md(e.get('seq'))} | {aflog.short_time(e.get('ts'))} | "
                   f"{md(e.get('level'))} | {md(e.get('component'))} | {md(e.get('event_type'))} | "
                   f"{md(e.get('msg'))} | {md(aflog.key_facts(e))} |")
    out.append("")
    return out


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(
        description="Renderiza un log NDJSON agent-friendly como Markdown (proyección canónica §6).",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("log", help="Ruta al archivo NDJSON de log")
    ap.add_argument("--view", choices=["digest", "timeline", "both"], default="digest",
                    help="Vista a renderizar (default: digest)")
    ap.add_argument("--run", help="Renderizar solo este run_id")
    args = ap.parse_args()

    path = Path(args.log)
    if not path.is_file():
        print(f"error: no existe el archivo '{args.log}'", file=sys.stderr)
        return 2

    records, warns = aflog.load_ndjson(path)
    for w in warns:
        print(f"warning: {w}", file=sys.stderr)

    runs = aflog.group_runs(records)
    if args.run:
        runs = [r for r in runs if r["run_id"] == args.run]
        if not runs:
            print(f"warning: run_id '{args.run}' no encontrado", file=sys.stderr)

    lines: list[str] = []
    for run in runs:
        if args.view in ("digest", "both"):
            lines += render_digest(run)
        if args.view in ("timeline", "both"):
            lines += render_timeline(run)
        lines += ["---", ""]
    print("\n".join(lines).rstrip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
