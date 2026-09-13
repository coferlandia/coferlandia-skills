from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

DEVELOPMENT_CONTRACT_PATH = Path(".coferlandia/development/validation.json")
DEFAULT_DEVELOPMENT_WORKFLOW_PATH = Path(".github/workflows/coferlandia-development-validation.yml")
ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
FORBIDDEN_KEY_PARTS = {"secret", "password", "passwd", "token", "credential", "private_key"}
ALLOWED_TOP = {
    "schema_version",
    "repository",
    "documentation",
    "working_directory",
    "commands",
    "required_services",
    "environment",
    "github",
    "fingerprint",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _scan_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if any(part in normalized for part in FORBIDDEN_KEY_PARTS):
                raise ValueError(f"forbidden secret-bearing key at {path}.{key}")
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_forbidden(child, f"{path}[{index}]")


def _validate_relative_path(value: str, label: str) -> None:
    _require(isinstance(value, str) and value, f"{label} is required")
    path = Path(value)
    _require(not path.is_absolute(), f"{label} must be repository-relative")
    _require(".." not in path.parts, f"{label} must not escape the repository")


def _validate_commands(commands: object) -> None:
    _require(isinstance(commands, list) and commands, "commands must be a non-empty list")
    ids: list[str] = []
    for item in commands:
        _require(isinstance(item, dict), "command entries must be objects")
        _require(set(item) == {"id", "command", "purpose"}, "command fields are invalid")
        for key in ("id", "command", "purpose"):
            _require(isinstance(item[key], str) and item[key], f"command {key} must be a non-empty string")
        ids.append(item["id"])
    _require(len(ids) == len(set(ids)), "command ids must be unique")


def validate_development_contract(contract: dict, *, verify_fingerprint: bool = False) -> None:
    _require(isinstance(contract, dict), "development contract must be an object")
    unknown = set(contract) - ALLOWED_TOP
    _require(not unknown, f"unknown top-level fields: {sorted(unknown)}")
    _scan_forbidden(contract)
    _require(contract.get("schema_version") == 1, "schema_version must be 1")

    repository = contract.get("repository")
    _require(
        isinstance(repository, str) and repository.count("/") == 1 and all(repository.split("/")),
        "repository must be owner/name",
    )
    docs = contract.get("documentation")
    _require(
        isinstance(docs, list) and all(isinstance(item, str) and item for item in docs),
        "documentation must be a string list",
    )
    _require(len(docs) == len(set(docs)), "documentation entries must be unique")

    working_directory = contract.get("working_directory")
    _validate_relative_path(working_directory, "working_directory")
    _validate_commands(contract.get("commands"))

    services = contract.get("required_services")
    _require(
        isinstance(services, list) and all(isinstance(item, str) and item for item in services),
        "required_services must be a string list",
    )
    _require(len(services) == len(set(services)), "required_services entries must be unique")

    environment = contract.get("environment")
    _require(
        isinstance(environment, list)
        and all(isinstance(item, str) and ENV_NAME_RE.fullmatch(item) for item in environment),
        "environment must contain variable names only, never NAME=value or secret values",
    )
    _require(len(environment) == len(set(environment)), "environment entries must be unique")

    github = contract.get("github")
    _require(
        isinstance(github, dict)
        and set(github) == {"submission", "candidate_binding", "runner_labels", "shell", "gate"},
        "github fields are invalid",
    )
    submission = github["submission"]
    _require(
        isinstance(submission, dict) and set(submission) == {"mode", "workflow"},
        "github.submission fields are invalid",
    )
    _require(submission["mode"] == "existing-pr-events", "development submission mode must be existing-pr-events")
    _validate_relative_path(submission["workflow"], "github.submission.workflow")
    workflow = Path(submission["workflow"])
    _require(
        workflow.parts[:2] == (".github", "workflows") and workflow.suffix in {".yml", ".yaml"},
        "development workflow must live under .github/workflows and be YAML",
    )
    _require(github["candidate_binding"] == "pull-request-head", "github.candidate_binding must be pull-request-head")
    labels = github["runner_labels"]
    _require(
        isinstance(labels, list) and labels and all(isinstance(item, str) and item.strip() for item in labels),
        "github.runner_labels must be a non-empty string list",
    )
    _require(len(labels) == len(set(labels)), "github.runner_labels entries must be unique")
    _require(github["shell"] in {"bash", "pwsh"}, "github.shell must be bash or pwsh")

    gate = github["gate"]
    _require(isinstance(gate, dict) and set(gate) == {"name", "allowed_conclusions"}, "github.gate fields are invalid")
    _require(isinstance(gate["name"], str) and gate["name"], "github.gate.name is required")
    allowed = gate["allowed_conclusions"]
    _require(
        isinstance(allowed, list) and allowed and all(isinstance(item, str) and item for item in allowed),
        "github.gate.allowed_conclusions must be non-empty",
    )
    _require(allowed == ["success"], "development gate currently allows only success")

    if "fingerprint" in contract:
        _require(
            isinstance(contract["fingerprint"], str) and SHA256_RE.fullmatch(contract["fingerprint"]) is not None,
            "fingerprint must be sha256 hex",
        )
        if verify_fingerprint:
            _require(contract["fingerprint"] == development_fingerprint(contract), "development contract fingerprint mismatch")


def canonical_development_contract(contract: dict) -> dict:
    clean = json.loads(json.dumps(contract))
    clean.pop("fingerprint", None)
    return clean


def development_fingerprint(contract: dict) -> str:
    clean = canonical_development_contract(contract)
    validate_development_contract(clean)
    payload = json.dumps(clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_development_contract(path: Path, *, verify_fingerprint: bool = False) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_development_contract(data, verify_fingerprint=verify_fingerprint)
    return data


def render_development_contract(source: dict) -> dict:
    clean = canonical_development_contract(source)
    validate_development_contract(clean)
    clean["fingerprint"] = development_fingerprint(clean)
    return clean


def _yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _indent_command(command: str, spaces: int = 10) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line for line in command.splitlines())


def render_development_workflow(contract: dict) -> str:
    rendered = render_development_contract(contract)
    github = rendered["github"]
    fingerprint = rendered["fingerprint"]
    runs_on = json.dumps(github["runner_labels"], ensure_ascii=False)
    shell = github["shell"]
    gate_name = _yaml_string(github["gate"]["name"])
    working_directory = _yaml_string(rendered["working_directory"])

    if shell == "bash":
        identity = 'actual="$(git rev-parse HEAD)"\ntest "$actual" = "$EXPECTED_SHA"'
    else:
        identity = '$actual = (git rev-parse HEAD).Trim()\nif ($actual -ne $env:EXPECTED_SHA) { throw "candidate SHA mismatch: expected $env:EXPECTED_SHA observed $actual" }'

    lines = [
        "name: Coferlandia Development Validation", "", "on:", "  pull_request:",
        "    types: [opened, synchronize, reopened, converted_to_draft]", "", "permissions:",
        "  contents: read", "", "concurrency:",
        "  group: coferlandia-development-${{ github.event.pull_request.number }}",
        "  cancel-in-progress: true", "", "jobs:", "  validation:", f"    name: {gate_name}",
        "    if: github.event.pull_request.draft == true", f"    runs-on: {runs_on}", "    steps:",
        "      - name: Check out exact PR head", "        uses: actions/checkout@v4", "        with:",
        "          ref: ${{ github.event.pull_request.head.sha }}", "          fetch-depth: 0",
        "          persist-credentials: false", "      - name: Verify exact candidate identity",
        f"        shell: {shell}", "        env:", "          EXPECTED_SHA: ${{ github.event.pull_request.head.sha }}",
        "        run: |", _indent_command(identity), "      - name: Record Development contract",
        f"        shell: {shell}", "        run: |",
    ]
    if shell == "bash":
        summary = (
            f'echo "Development contract fingerprint: {fingerprint}" >> "$GITHUB_STEP_SUMMARY"\n'
            'echo "Candidate SHA: ${{ github.event.pull_request.head.sha }}" >> "$GITHUB_STEP_SUMMARY"'
        )
    else:
        summary = (
            f'Add-Content -Path $env:GITHUB_STEP_SUMMARY -Value "Development contract fingerprint: {fingerprint}"\n'
            'Add-Content -Path $env:GITHUB_STEP_SUMMARY -Value "Candidate SHA: ${{ github.event.pull_request.head.sha }}"'
        )
    lines.append(_indent_command(summary))
    for command in rendered["commands"]:
        lines.extend([
            f"      - name: {_yaml_string(command['purpose'])}", f"        shell: {shell}",
            f"        working-directory: {working_directory}", "        run: |", _indent_command(command["command"]),
        ])
    lines.append("")
    return "\n".join(lines)


def atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(value)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise
