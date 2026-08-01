from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import CLI_VERSION
from .model import (
    ReleaseError,
    apply_readme_block,
    atomic_write,
    find_repo_root,
    latest_release,
    render_readme_block,
)
from .operations import (
    build_package,
    check_release,
    inspect_release,
    prepare_release,
    self_check,
)


def emit(payload: dict[str, Any], code: int = 0) -> int:
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic release maintenance for coferlandia-skills."
    )
    parser.add_argument("--repo", type=Path, help="repository root; otherwise auto-detected")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("version")
    commands.add_parser("capabilities")
    commands.add_parser("self-check")

    inspect = commands.add_parser("inspect")
    inspect.add_argument("--base", required=True)

    prepare = commands.add_parser("prepare")
    prepare.add_argument("--input", required=True, type=Path)

    check = commands.add_parser("check")
    check.add_argument("--base")
    check.add_argument("--release-ready", action="store_true")

    render = commands.add_parser("render-readme")
    render_mode = render.add_mutually_exclusive_group(required=True)
    render_mode.add_argument("--check", action="store_true")
    render_mode.add_argument("--write", action="store_true")

    package = commands.add_parser("package")
    package.add_argument("--output", required=True, type=Path)
    package.add_argument("--verify", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    arguments = parser.parse_args()
    try:
        root = arguments.repo.resolve() if arguments.repo else find_repo_root()
        if arguments.command == "version":
            return emit({"command": "version", "version": CLI_VERSION})
        if arguments.command == "capabilities":
            return emit(
                {
                    "command": "capabilities",
                    "capabilities": [
                        "inspect",
                        "prepare",
                        "check",
                        "render-readme",
                        "package",
                    ],
                }
            )
        if arguments.command == "self-check":
            result, code = self_check(root)
            return emit(result, code)
        if arguments.command == "inspect":
            return emit(inspect_release(root, arguments.base))
        if arguments.command == "prepare":
            return emit(prepare_release(root, arguments.input))
        if arguments.command == "check":
            result = check_release(root, arguments.base, arguments.release_ready)
            return emit(result, 0 if result["ok"] else 1)
        if arguments.command == "render-readme":
            release = latest_release(root)
            readme_path = root / "README.md"
            current = readme_path.read_text(encoding="utf-8")
            rendered = apply_readme_block(current, render_readme_block(release))
            if arguments.check:
                return emit(
                    {"command": "render-readme", "ok": current == rendered},
                    0 if current == rendered else 1,
                )
            atomic_write(readme_path, rendered)
            return emit(
                {
                    "command": "render-readme",
                    "ok": True,
                    "updated": current != rendered,
                }
            )
        if arguments.command == "package":
            result, code = build_package(root, arguments.output, arguments.verify)
            return emit(result, code)
    except (ReleaseError, OSError, ValueError, json.JSONDecodeError) as error:
        return emit(
            {
                "command": getattr(arguments, "command", None),
                "ok": False,
                "error": str(error),
            },
            1,
        )
    parser.error("unsupported command")
    return 2
