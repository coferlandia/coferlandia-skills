#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audita Agent Skills contra agentskills.io y las reglas de coferlandia-skills.

Uso:
  python test_skills.py <repo-o-skill> [--pretty]
  python test_skills.py --help

La salida JSON va a stdout y los diagnosticos resumidos a stderr.
Codigos de salida: 0 sin errores, 1 con errores, 2 para errores de uso.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CANONICAL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
VALID_CATEGORIES = {"meta", "engineering", "data", "content", "design", "ops"}
VALID_STATUS = {"draft", "active", "deprecated"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INDEX_RE = re.compile(r"\]\(\./[^/]+/([^/{][^/]*)/\)")
SECRET_PATTERNS = {
    "openai-key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github-token": re.compile(r"\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}\b"),
    "aws-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\r\n")
    data: dict = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            i += 1
            continue
        key, value = match.groups()
        value = value.strip()
        if key == "metadata" and not value:
            metadata = {}
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                child = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*)$", lines[i])
                if child:
                    metadata[child.group(1)] = unquote(child.group(2).strip())
                i += 1
            data[key] = metadata
            continue
        if value in {">", "|", ">-", "|-", ">+", "|+"}:
            chunks = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                chunks.append(lines[i].strip())
                i += 1
            data[key] = " ".join(part for part in chunks if part)
            continue
        data[key] = unquote(value)
        i += 1
    return data, body


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def issue(code: str, message: str, path: Path, severity: str = "error") -> dict:
    return {
        "code": code,
        "severity": severity,
        "path": str(path),
        "message": message,
    }


def audit_skill(skill_dir: Path, repo_root: Path | None = None) -> dict:
    skill_dir = Path(skill_dir)
    repo_root = Path(repo_root) if repo_root else find_repo_root(skill_dir)
    issues: list[dict] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        issues.append(issue("structure.missing-skill-md", "Falta SKILL.md", skill_dir))
        return result("skill", skill_dir, issues)

    text = skill_file.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    if not frontmatter:
        issues.append(issue("frontmatter.invalid", "Frontmatter ausente o invalido", skill_file))
        return result("skill", skill_dir, issues)

    for field in sorted(set(frontmatter) - CANONICAL_FIELDS):
        issues.append(
            issue(
                "frontmatter.unknown-field",
                f"Campo no canonico '{field}'; agentskills.io no lo define",
                skill_file,
            )
        )

    name = str(frontmatter.get("name", ""))
    description = str(frontmatter.get("description", ""))
    if not name:
        issues.append(issue("frontmatter.missing-name", "Falta name", skill_file))
    elif not NAME_RE.fullmatch(name) or len(name) > 64:
        issues.append(issue("frontmatter.invalid-name", f"name invalido: {name}", skill_file))
    elif name != skill_dir.name:
        issues.append(
            issue(
                "frontmatter.name-folder-mismatch",
                f"name '{name}' no coincide con carpeta '{skill_dir.name}'",
                skill_file,
            )
        )
    if not description or len(description) > 1024:
        issues.append(
            issue(
                "frontmatter.invalid-description",
                "description debe tener entre 1 y 1024 caracteres",
                skill_file,
            )
        )
    elif not re.search(r"\b(usar|usa|use|cuando|activar|activa)\b", description, re.I):
        issues.append(
            issue(
                "description.missing-trigger",
                "description debe explicar cuando usar la skill",
                skill_file,
            )
        )

    compatibility = str(frontmatter.get("compatibility", ""))
    if compatibility and len(compatibility) > 500:
        issues.append(
            issue(
                "frontmatter.invalid-compatibility",
                "compatibility excede 500 caracteres",
                skill_file,
            )
        )

    metadata = frontmatter.get("metadata", {})
    if metadata and not isinstance(metadata, dict):
        issues.append(issue("frontmatter.invalid-metadata", "metadata debe ser un mapa", skill_file))
        metadata = {}
    category = metadata.get("category")
    status = metadata.get("status")
    expected_category = skill_dir.parent.name
    if category not in VALID_CATEGORIES:
        issues.append(issue("metadata.invalid-category", f"category invalida: {category}", skill_file))
    elif category != expected_category:
        issues.append(
            issue(
                "metadata.category-path-mismatch",
                f"category '{category}' no coincide con '{expected_category}'",
                skill_file,
            )
        )
    if status not in VALID_STATUS:
        issues.append(issue("metadata.invalid-status", f"status invalido: {status}", skill_file))
    if status == "active" and not metadata.get("tested"):
        issues.append(issue("behavior.missing-tested", "Skill active sin metadata.tested", skill_file))
    if status == "active":
        issues.extend(check_behavior_cases(skill_dir))

    if len(text.splitlines()) > 500:
        issues.append(issue("content.too-long", "SKILL.md excede 500 lineas", skill_file))
    if not re.search(r"^##\s+Gotchas\b", body, re.M | re.I):
        issues.append(issue("content.missing-gotchas", "Falta seccion ## Gotchas", skill_file))

    issues.extend(check_links(skill_dir, text))
    issues.extend(check_scripts(skill_dir))
    issues.extend(check_sensitive_data(skill_dir))
    return result("skill", skill_dir, issues)


def check_behavior_cases(skill_dir: Path) -> list[dict]:
    path = skill_dir / "tests" / "cases.json"
    if not path.is_file():
        return [
            issue(
                "behavior.missing-cases",
                "Skill active sin tests/cases.json con prompts positivos y negativos",
                skill_dir,
            )
        ]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [issue("behavior.invalid-cases", f"cases.json invalido: {exc}", path)]
    positive = data.get("positive")
    negative = data.get("negative")
    if (
        not isinstance(positive, list)
        or not isinstance(negative, list)
        or not positive
        or not negative
        or not all(isinstance(prompt, str) and prompt.strip() for prompt in positive + negative)
    ):
        return [
            issue(
                "behavior.invalid-cases",
                "cases.json requiere listas no vacias positive y negative",
                path,
            )
        ]
    return []


def check_links(skill_dir: Path, text: str) -> list[dict]:
    issues = []
    for target in LINK_RE.findall(text):
        clean = target.split("#", 1)[0].strip()
        if not clean or clean.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if "{" in clean or "}" in clean:
            continue
        destination = (skill_dir / clean).resolve()
        if not destination.exists():
            issues.append(
                issue("links.broken", f"Link local no resuelve: {target}", skill_dir / "SKILL.md")
            )
    return issues


def check_scripts(skill_dir: Path) -> list[dict]:
    issues = []
    for script in sorted((skill_dir / "scripts").glob("*.py")):
        text = script.read_text(encoding="utf-8")
        if "# /// script" not in text:
            issues.append(issue("script.missing-pep723", "Script Python sin bloque PEP 723", script))
        if "argparse" not in text and "--help" not in text:
            issues.append(issue("script.missing-help", "Script sin contrato --help", script))
        try:
            compile(text, str(script), "exec")
        except SyntaxError as exc:
            issues.append(issue("script.syntax-error", f"Error de sintaxis: {exc.msg}", script))
    return issues


def check_sensitive_data(skill_dir: Path) -> list[dict]:
    issues = []
    for path in skill_dir.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                issues.append(issue("security.possible-secret", f"Posible secreto: {label}", path))
    return issues


def audit_repository(repo_root: Path) -> dict:
    repo_root = Path(repo_root)
    skills_root = repo_root / "skills"
    skill_dirs = sorted(path.parent for path in skills_root.rglob("SKILL.md"))
    issues: list[dict] = []
    for skill_dir in skill_dirs:
        issues.extend(audit_skill(skill_dir, repo_root)["issues"])
    issues.extend(check_index(skills_root, skill_dirs))
    issues.extend(check_repository_links(repo_root))
    return result("repository", repo_root, issues, len(skill_dirs))


def check_index(skills_root: Path, skill_dirs: list[Path]) -> list[dict]:
    index = skills_root / "INDEX.md"
    if not index.is_file():
        return [issue("index.missing", "Falta skills/INDEX.md", skills_root)]
    text = index.read_text(encoding="utf-8")
    indexed = set(INDEX_RE.findall(text))
    actual = {path.name for path in skill_dirs}
    issues = [
        issue("index.missing-skill", f"Skill no indexada: {name}", index)
        for name in sorted(actual - indexed)
    ]
    issues.extend(
        issue("index.stale-entry", f"Entrada sin skill: {name}", index)
        for name in sorted(indexed - actual)
    )
    return issues


def check_repository_links(repo_root: Path) -> list[dict]:
    issues = []
    for document in sorted(repo_root.rglob("*.md")):
        if document.name == "SKILL.md" or ".git" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        for target in LINK_RE.findall(text):
            clean = target.split("#", 1)[0].strip()
            if (
                not clean
                or clean.startswith(("http://", "https://", "mailto:", "#"))
                or "{" in clean
                or "}" in clean
            ):
                continue
            if not (document.parent / clean).resolve().exists():
                issues.append(
                    issue("links.broken", f"Link local no resuelve: {target}", document)
                )
    return issues


def find_repo_root(path: Path) -> Path:
    for parent in [path, *path.parents]:
        if (parent / "skills" / "INDEX.md").is_file():
            return parent
    return path


def result(scope: str, path: Path, issues: list[dict], skills: int = 1) -> dict:
    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {
        "ok": errors == 0,
        "scope": scope,
        "path": str(path),
        "skills": skills,
        "errors": errors,
        "warnings": warnings,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Raiz del repo o carpeta de una skill")
    parser.add_argument("--pretty", action="store_true", help="Indenta el JSON de salida")
    args = parser.parse_args()
    target = Path(args.target).resolve()
    if (target / "skills").is_dir():
        report = audit_repository(target)
    else:
        report = audit_skill(target)
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None))
    print(
        f"[{'OK' if report['ok'] else 'FAIL'}] {report['skills']} skills, "
        f"{report['errors']} errores, {report['warnings']} advertencias",
        file=sys.stderr,
    )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
