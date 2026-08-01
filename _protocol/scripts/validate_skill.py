#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate Coferlandia skills and their public changelog/version contract."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_CATEGORIES = {"meta", "engineering", "data", "content", "design", "ops"}
VALID_STATUS = {"draft", "active", "deprecated"}
MAX_LINES = 500
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CHANGELOG_VERSION_RE = re.compile(r"^##\s+v?(?P<version>[^\s—-]+)\s*(?:[—-]|\()", re.M)
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
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b")
ALLOWED_EMAIL_DOMAINS = {
    "example.com", "example.org", "example.net", "coferlandia.test",
    "coferlandia.example.com", "agente.example.com",
}


def parse_frontmatter(text: str) -> dict:
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
        match = re.match(r"^(\S[^:]*):\s*(.*)$", line)
        if not match:
            i += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if key == "metadata" and value == "":
            metadata: dict = {}
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                sub = re.match(r"^\s+(\S[^:]*):\s*(.*)$", lines[i])
                if sub:
                    metadata[sub.group(1).strip()] = sub.group(2).strip().strip('"').strip("'")
                i += 1
            data["metadata"] = metadata
            continue
        if value in (">", "|", ">-", "|-", ">+", "|+"):
            collected = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                collected.append(lines[i].strip())
                i += 1
            data[key] = " ".join(item for item in collected if item).strip()
            continue
        data[key] = value.strip('"').strip("'")
        i += 1
    return data


def is_public_skill(skill_dir: Path) -> bool:
    return len(skill_dir.parents) >= 2 and skill_dir.parents[1].name == "skills"


def validate_changelog(skill_dir: Path, version: str | None, errors: list[str]) -> None:
    if not is_public_skill(skill_dir):
        return
    path = skill_dir / "CHANGELOG.md"
    if not path.is_file():
        errors.append("Falta CHANGELOG.md para la skill pública")
        return
    text = path.read_text(encoding="utf-8")
    expected_heading = f"# Changelog — {skill_dir.name}"
    if not text.startswith(expected_heading):
        errors.append(f"CHANGELOG.md debe comenzar con '{expected_heading}'")
    match = CHANGELOG_VERSION_RE.search(text)
    if not match:
        errors.append("CHANGELOG.md no contiene una versión reconocible")
    elif version and match.group("version") != version:
        errors.append(
            f"CHANGELOG.md versión '{match.group('version')}' no coincide con metadata.version '{version}'"
        )


def validate_skill(skill_dir: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return {"skill": str(skill_dir), "ok": False, "errors": ["No existe SKILL.md en la carpeta"], "warnings": []}

    text = skill_file.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    folder = skill_dir.name
    name = frontmatter.get("name", "")
    if not name:
        errors.append("Falta el campo `name` en el frontmatter")
    else:
        if name != folder:
            errors.append(f"`name` ('{name}') no coincide con la carpeta ('{folder}')")
        if not NAME_RE.match(name):
            errors.append(f"`name` ('{name}') viola las reglas de naming")
        if len(name) > 64:
            errors.append(f"`name` excede 64 caracteres ({len(name)})")

    description = frontmatter.get("description", "")
    if not description:
        errors.append("Falta el campo `description`")
    elif not 1 <= len(description) <= 1024:
        errors.append(f"`description` tiene {len(description)} chars (debe ser 1..1024)")

    metadata = frontmatter.get("metadata", {}) if isinstance(frontmatter.get("metadata"), dict) else {}
    version = metadata.get("version")
    if not version:
        errors.append("Falta metadata.version")
    category = metadata.get("category")
    if category and category not in VALID_CATEGORIES:
        errors.append(f"category '{category}' no es válida ({sorted(VALID_CATEGORIES)})")
    status = metadata.get("status")
    if status and status not in VALID_STATUS:
        errors.append(f"status '{status}' no es válido ({sorted(VALID_STATUS)})")
    if status == "active" and not metadata.get("tested"):
        warnings.append("status=active sin campo `tested` — criterio no verificable")

    validate_changelog(skill_dir, version, errors)

    line_count = text.count("\n") + 1
    if line_count > MAX_LINES:
        errors.append(f"SKILL.md tiene {line_count} líneas (tope {MAX_LINES})")

    for label, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            errors.append(f"Posible secreto detectado ({label})")
    for match in EMAIL_RE.finditer(text):
        if match.group(1).lower() not in ALLOWED_EMAIL_DOMAINS:
            warnings.append(f"Email con dominio real: {match.group(0)} (usar dominios de ejemplo)")

    return {
        "skill": str(skill_dir),
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "lines": line_count,
        "version": version,
        "changelog": str(skill_dir / "CHANGELOG.md") if is_public_skill(skill_dir) else None,
    }


def discover(root: Path) -> list[Path]:
    return sorted(path.parent for path in root.rglob("SKILL.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Carpetas de skill a validar")
    parser.add_argument("--all", metavar="ROOT", help="Descubre y valida todas las skills bajo ROOT")
    args = parser.parse_args()

    targets: list[Path] = []
    if args.all:
        targets.extend(discover(Path(args.all)))
    targets.extend(Path(path) for path in args.paths)
    if not targets:
        parser.print_help(sys.stderr)
        return 2

    results = [validate_skill(target) for target in targets]
    failures = sum(1 for result in results if not result["ok"])
    print(json.dumps({"validated": len(results), "failed": failures, "results": results}, indent=2, ensure_ascii=False))
    for result in results:
        tag = "OK " if result["ok"] else "FAIL"
        print(f"[{tag}] {result['skill']}", file=sys.stderr)
        for error in result.get("errors", []):
            print(f"   error:   {error}", file=sys.stderr)
        for warning in result.get("warnings", []):
            print(f"   warning: {warning}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
