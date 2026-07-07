#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "HISTORY.md",
    "TODO.md",
    "DECISIONS.md",
    "RUNBOOK.md",
    ".coferlandia/catalog/SOURCE_INDEX.md",
    ".coferlandia/catalog/OPEN_QUESTIONS.md",
    ".coferlandia/catalog/PROCESSING_RUNS.md",
]

REQUIRED_SECTIONS = {
    ".coferlandia/catalog/OPEN_QUESTIONS.md": [
        "# Open Questions",
        "## Open",
        "## Resolved",
        "## Archived",
    ],
    ".coferlandia/catalog/PROCESSING_RUNS.md": ["# Processing Runs"],
}

ARCHIVE_LINK_RE = re.compile(
    r"\[\[(.coferlandia/archive/[^\]]+)\]\]|\[[^\]]+\]\((.coferlandia/archive/[^)]+)\)"
)
SOURCE_INDEX_ARCHIVED_RE = re.compile(
    r"^\|\s*archived\s*\|\s*([^|]+)\|\s*([^|]+)\|",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a project documentation catalog created by project-documentation-archivist."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Path to the target project root. Default: current directory.",
    )
    return parser.parse_args()


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text


def has_catalog_status_processed(text: str) -> bool:
    if not has_frontmatter(text):
        return False
    header = text.split("\n---\n", 1)[0]
    return re.search(r"(?m)^catalog_status:\s*processed\s*$", header) is not None


def normalize_link_target(raw: str) -> str:
    return raw.split("#", 1)[0].strip()


def validate_required_files(root: Path, failures: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"Missing required file: {rel_path}")


def validate_required_sections(root: Path, failures: list[str]) -> None:
    for rel_path, headers in REQUIRED_SECTIONS.items():
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for header in headers:
            if header not in text:
                failures.append(f"Missing required section '{header}' in {rel_path}")


def validate_archive_frontmatter(root: Path, failures: list[str]) -> None:
    archive_root = root / ".coferlandia/archive"
    if not archive_root.exists():
        return
    for path in archive_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".txt", ".rst", ".adoc"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not has_catalog_status_processed(text):
            failures.append(
                "Archived text document missing catalog_status: processed frontmatter: "
                f"{path.relative_to(root)}"
            )


def validate_archive_links(root: Path, failures: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in ARCHIVE_LINK_RE.finditer(text):
            target = normalize_link_target(match.group(1) or match.group(2) or "")
            if not target:
                continue
            if not (root / target).exists():
                failures.append(f"Broken archive link in {rel_path}: {target}")


def validate_agents_file(root: Path, failures: list[str]) -> None:
    agents_path = root / "AGENTS.md"
    if not agents_path.exists():
        return

    text = agents_path.read_text(encoding="utf-8")
    required_headers = [
        "## Critical Instructions for Agents",
        "## Project Essentials",
        "## Documentation Index",
        "## Maintenance Notes",
    ]
    for header in required_headers:
        if header not in text:
            failures.append(f"Missing required section '{header}' in AGENTS.md")


def validate_source_index_vs_inbox(root: Path, failures: list[str]) -> None:
    source_index = root / ".coferlandia/catalog/SOURCE_INDEX.md"
    if not source_index.exists():
        return
    inbox = root / "docs/inbox"
    text = source_index.read_text(encoding="utf-8")
    for line in text.splitlines():
        match = SOURCE_INDEX_ARCHIVED_RE.match(line)
        if not match:
            continue
        original_path = match.group(1).strip().strip("`")
        archived_path = match.group(2).strip().strip("`")
        if original_path and (root / original_path).exists() and inbox in (root / original_path).parents:
            failures.append(
                "Source marked archived is still present in docs/inbox/: "
                f"{original_path} -> {archived_path}"
            )


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).resolve()
    failures: list[str] = []

    if not root.exists():
        print(f"Project root does not exist: {root}", file=sys.stderr)
        return 1

    validate_required_files(root, failures)
    validate_required_sections(root, failures)
    validate_archive_frontmatter(root, failures)
    validate_archive_links(root, failures)
    validate_agents_file(root, failures)
    validate_source_index_vs_inbox(root, failures)

    if failures:
        print("Documentation catalog validation failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Documentation catalog validation passed.")
    print(f"Project root: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
