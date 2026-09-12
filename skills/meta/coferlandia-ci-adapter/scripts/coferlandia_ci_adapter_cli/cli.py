from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .profile import PROFILE_PATH, load_profile, profile_fingerprint, render_profile, atomic_write_json as atomic_write_profile
from .publication import (
    DEFAULT_WORKFLOW_PATH,
    RELEASE_POLICY_PATH,
    atomic_write_json,
    atomic_write_text,
    load_release_policy,
    publication_github,
    render_publication_policy,
    render_workflow,
)


def emit(payload: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Coferlandia repository CI and GitHub-native release publication adapter")
    sub = p.add_subparsers(dest="command", required=True)
    v = sub.add_parser("version")
    v.add_argument("--json", action="store_true")
    c = sub.add_parser("capabilities")
    c.add_argument("--json", action="store_true")

    prof = sub.add_parser("profile")
    prof_sub = prof.add_subparsers(dest="profile_command", required=True)
    for name in ("validate", "fingerprint"):
        sp = prof_sub.add_parser(name)
        sp.add_argument("--profile", required=True)
        sp.add_argument("--json", action="store_true")
    check = prof_sub.add_parser("check")
    check.add_argument("--profile", required=True)
    check.add_argument("--expect-fingerprint")
    check.add_argument("--json", action="store_true")
    render = prof_sub.add_parser("render")
    render.add_argument("--input", required=True)
    render.add_argument("--target-root", required=True)
    render.add_argument("--dry-run", action="store_true")
    render.add_argument("--json", action="store_true")

    publication = sub.add_parser("publication")
    publication_sub = publication.add_subparsers(dest="publication_command", required=True)
    publication_validate = publication_sub.add_parser("validate")
    publication_validate.add_argument("--policy", required=True)
    publication_validate.add_argument("--json", action="store_true")
    publication_render = publication_sub.add_parser("render")
    publication_render.add_argument("--policy", required=True)
    publication_render.add_argument("--target-root", required=True)
    publication_render.add_argument("--publisher-path", required=True)
    publication_render.add_argument("--workflow-path", default=DEFAULT_WORKFLOW_PATH.as_posix())
    publication_render.add_argument(
        "--runs-on",
        nargs="+",
        help="GitHub Actions runner label or labels for publication; defaults to ubuntu-latest",
    )
    publication_render.add_argument("--dry-run", action="store_true")
    publication_render.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    as_json = getattr(args, "json", False)
    try:
        if args.command == "version":
            emit({"ok": True, "version": __version__}, as_json)
            return 0
        if args.command == "capabilities":
            emit({
                "ok": True,
                "commands": [
                    "profile validate",
                    "profile fingerprint",
                    "profile check",
                    "profile render",
                    "publication validate",
                    "publication render",
                ],
                "profile_path": str(PROFILE_PATH),
                "release_policy_path": str(RELEASE_POLICY_PATH),
                "default_publication_workflow": DEFAULT_WORKFLOW_PATH.as_posix(),
            }, as_json)
            return 0

        if args.command == "publication":
            policy_path = Path(args.policy)
            policy = load_release_policy(policy_path)
            github = publication_github(policy)
            if args.publication_command == "validate":
                emit({"ok": True, "github": github}, as_json)
                return 0

            rendered_policy = render_publication_policy(
                policy,
                workflow_path=args.workflow_path,
                runs_on=args.runs_on,
            )
            workflow = render_workflow(
                publisher_path=args.publisher_path,
                runs_on=rendered_policy["publication"]["github"]["runs_on"],
            )
            target_root = Path(args.target_root).resolve()
            policy_target = (target_root / RELEASE_POLICY_PATH).resolve()
            workflow_target = (target_root / args.workflow_path).resolve()
            if target_root not in policy_target.parents or target_root not in workflow_target.parents:
                raise ValueError("publication target escapes target root")
            if not args.dry_run:
                atomic_write_json(policy_target, rendered_policy)
                atomic_write_text(workflow_target, workflow)
            emit({
                "ok": True,
                "dry_run": args.dry_run,
                "policy_path": str(policy_target),
                "workflow_path": str(workflow_target),
                "github": rendered_policy["publication"]["github"],
            }, as_json)
            return 0

        if args.profile_command == "validate":
            raw = json.loads(Path(args.profile).read_text(encoding="utf-8"))
            data = load_profile(Path(args.profile), verify_fingerprint="fingerprint" in raw)
            emit({"ok": True, "repository": data["repository"], "fingerprint": profile_fingerprint(data)}, as_json)
            return 0
        if args.profile_command == "fingerprint":
            data = load_profile(Path(args.profile))
            emit({"ok": True, "fingerprint": profile_fingerprint(data)}, as_json)
            return 0
        if args.profile_command == "check":
            data = load_profile(Path(args.profile), verify_fingerprint=True)
            fp = profile_fingerprint(data)
            if args.expect_fingerprint and fp != args.expect_fingerprint:
                raise ValueError(f"expected fingerprint {args.expect_fingerprint}, observed {fp}")
            emit({"ok": True, "fingerprint": fp}, as_json)
            return 0
        source = json.loads(Path(args.input).read_text(encoding="utf-8"))
        rendered = render_profile(source)
        target_root = Path(args.target_root).resolve()
        target = (target_root / PROFILE_PATH).resolve()
        if target_root not in target.parents:
            raise ValueError("profile target escapes target root")
        if not args.dry_run:
            atomic_write_profile(target, rendered)
        emit({"ok": True, "dry_run": args.dry_run, "path": str(target), "fingerprint": rendered["fingerprint"]}, as_json)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {"ok": False, "error": str(exc)}
        if as_json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
