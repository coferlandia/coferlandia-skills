#!/usr/bin/env python3
"""Flatten and overwrite this repository's skills in global Agent Skill directories."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


LEGACY_NAMES = (
    "coferlandia-software-dev",
    "coferlandia-project-skill-miner",
    "using-coferlandia-skills",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install repository skills as immediate child directories in global runtimes."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "skills",
        help="Canonical skills directory (default: this repository's skills directory).",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        action="append",
        help="Global skills directory; repeat for multiple runtimes (default: .agents and .codex).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print removals and copies without changing the filesystem.",
    )
    return parser.parse_args()


def default_destinations() -> list[Path]:
    home = Path.home()
    return [home / ".agents" / "skills", home / ".codex" / "skills"]


def discover_skills(source: Path) -> list[Path]:
    if not source.is_dir():
        raise ValueError(f"Skill source does not exist or is not a directory: {source}")
    skills = sorted(
        child
        for category in source.iterdir()
        if category.is_dir()
        for child in category.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )
    if not skills:
        raise ValueError(f"Skill source contains no category/skill directories: {source}")
    return skills


def remove_tree(path: Path, dry_run: bool) -> None:
    if not path.exists():
        return
    if dry_run:
        print(f"remove {path}")
        return
    shutil.rmtree(path)


def install(source: Path, destinations: list[Path], dry_run: bool = False) -> None:
    skills = discover_skills(source)
    for destination in destinations:
        for legacy_name in LEGACY_NAMES:
            remove_tree(destination / legacy_name, dry_run)
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)
        for skill in skills:
            target = destination / skill.name
            remove_tree(target, dry_run)
            if dry_run:
                print(f"copy {skill} -> {target}")
            else:
                shutil.copytree(skill, target)


def main() -> int:
    args = parse_args()
    destinations = args.destination or default_destinations()
    try:
        install(args.source.resolve(), [destination.resolve() for destination in destinations], args.dry_run)
    except (OSError, ValueError) as error:
        print(f"Global skill installation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
