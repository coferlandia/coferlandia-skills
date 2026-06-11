#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Valida una o más skills de coferlandia-skills contra los invariantes mecánicos.

Chequea, por cada skill:
  - existe SKILL.md
  - el campo `name` del frontmatter coincide con el nombre de la carpeta
  - `name` cumple las reglas de naming (lowercase, [a-z0-9-], sin -- ni - al borde, <=64)
  - `description` está presente y tiene 1..1024 caracteres
  - `metadata.category` (si existe) es una categoría válida
  - `metadata.status` (si existe) es draft|active|deprecated
  - SKILL.md no excede el tope de líneas (~500)
  - no hay secretos ni PII evidentes (regex-scan)

Salida: JSON a stdout (parseable por un agente). Diagnósticos a stderr.
Código de salida: 0 si todas las skills son válidas, 1 si alguna falla.

Uso:
  python validate_skill.py <ruta-skill-o-carpeta> [<ruta> ...]
  python validate_skill.py --all <ruta-raiz-skills>
  python validate_skill.py --help

Ejemplos:
  python _protocol/scripts/validate_skill.py skills/meta/build-agentic-repo
  python _protocol/scripts/validate_skill.py --all skills
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_CATEGORIES = {"meta", "engineering", "data", "content", "design", "ops"}
VALID_STATUS = {"draft", "active", "deprecated"}
MAX_LINES = 500
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # lowercase, hyphen-separated, sin -- ni bordes

# Patrones de secretos / PII. Conservadores: priorizan no dar falsos negativos en lo obvio.
SECRET_PATTERNS = {
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "github_pat": re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    "github_fine": re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic_secret_assign": re.compile(
        r"(?i)(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"]?[A-Za-z0-9/+_\-]{12,}"
    ),
}
# Emails con dominio real (se excluyen dominios de ejemplo permitidos).
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
ALLOWED_EMAIL_DOMAINS = {"example.com", "example.org", "example.net", "coferlandia.test",
                         "coferlandia.example.com", "agente.example.com"}


def parse_frontmatter(text: str) -> dict:
    """Parser mínimo de frontmatter YAML (sin dependencias).

    Soporta el subconjunto usado por las skills: claves escalares de nivel 0,
    bloques `>` o `|` multilínea, y un bloque `metadata:` con claves indentadas.
    No es un parser YAML completo; suficiente para validar invariantes.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end].strip("\n")
    data: dict = {}
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\S[^:]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if key == "metadata" and val == "":
            meta: dict = {}
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                sub = re.match(r"^\s+(\S[^:]*):\s*(.*)$", lines[i])
                if sub:
                    meta[sub.group(1).strip()] = sub.group(2).strip().strip('"').strip("'")
                i += 1
            data["metadata"] = meta
            continue
        if val in (">", "|", ">-", "|-", ">+", "|+"):
            collected = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                collected.append(lines[i].strip())
                i += 1
            data[key] = " ".join(c for c in collected if c).strip()
            continue
        data[key] = val.strip('"').strip("'")
        i += 1
    return data


def validate_skill(skill_dir: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    md = skill_dir / "SKILL.md"

    if not md.is_file():
        return {"skill": str(skill_dir), "ok": False,
                "errors": ["No existe SKILL.md en la carpeta"], "warnings": []}

    text = md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    folder = skill_dir.name

    name = fm.get("name", "")
    if not name:
        errors.append("Falta el campo `name` en el frontmatter")
    else:
        if name != folder:
            errors.append(f"`name` ('{name}') no coincide con la carpeta ('{folder}')")
        if not NAME_RE.match(name):
            errors.append(f"`name` ('{name}') viola las reglas de naming")
        if len(name) > 64:
            errors.append(f"`name` excede 64 caracteres ({len(name)})")

    desc = fm.get("description", "")
    if not desc:
        errors.append("Falta el campo `description`")
    elif not (1 <= len(desc) <= 1024):
        errors.append(f"`description` tiene {len(desc)} chars (debe ser 1..1024)")

    meta = fm.get("metadata", {}) if isinstance(fm.get("metadata"), dict) else {}
    cat = meta.get("category")
    if cat and cat not in VALID_CATEGORIES:
        errors.append(f"category '{cat}' no es válida ({sorted(VALID_CATEGORIES)})")
    status = meta.get("status")
    if status and status not in VALID_STATUS:
        errors.append(f"status '{status}' no es válido ({sorted(VALID_STATUS)})")
    if status == "active" and not meta.get("tested"):
        warnings.append("status=active sin campo `tested` — criterio no verificable")

    n_lines = text.count("\n") + 1
    if n_lines > MAX_LINES:
        errors.append(f"SKILL.md tiene {n_lines} líneas (tope {MAX_LINES})")

    for label, pat in SECRET_PATTERNS.items():
        if pat.search(text):
            errors.append(f"Posible secreto detectado ({label})")
    for m in EMAIL_RE.finditer(text):
        if m.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
            warnings.append(f"Email con dominio real: {m.group(0)} (usar dominios de ejemplo)")

    return {"skill": str(skill_dir), "ok": not errors,
            "errors": errors, "warnings": warnings, "lines": n_lines}


def discover(root: Path) -> list[Path]:
    return sorted(p.parent for p in root.rglob("SKILL.md"))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Valida skills de coferlandia-skills contra invariantes mecánicos.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("paths", nargs="*", help="Carpetas de skill a validar")
    ap.add_argument("--all", metavar="ROOT",
                    help="Descubre y valida todas las skills bajo ROOT")
    args = ap.parse_args()

    targets: list[Path] = []
    if args.all:
        targets.extend(discover(Path(args.all)))
    for p in args.paths:
        targets.append(Path(p))
    if not targets:
        ap.print_help(sys.stderr)
        return 2

    results = [validate_skill(t) for t in targets]
    n_fail = sum(1 for r in results if not r["ok"])
    summary = {"validated": len(results), "failed": n_fail, "results": results}
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    for r in results:
        tag = "OK " if r["ok"] else "FAIL"
        print(f"[{tag}] {r['skill']}", file=sys.stderr)
        for e in r.get("errors", []):
            print(f"   error:   {e}", file=sys.stderr)
        for w in r.get("warnings", []):
            print(f"   warning: {w}", file=sys.stderr)

    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
