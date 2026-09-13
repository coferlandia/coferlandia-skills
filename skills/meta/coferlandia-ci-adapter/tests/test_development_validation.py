import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
CLI = SKILL_ROOT / "scripts" / "coferlandia-ci-adapter-cli.py"
MODULE_PATH = SKILL_ROOT / "scripts" / "coferlandia_ci_adapter_cli" / "development.py"
SCHEMA = SKILL_ROOT.parents[2] / "_protocol" / "delivery" / "development-validation.schema.json"


def load_module():
    spec = importlib.util.spec_from_file_location("development_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample():
    return {
        "schema_version": 1,
        "repository": "example/repo",
        "documentation": ["AGENTS.md", "docs/development.md"],
        "working_directory": ".",
        "commands": [
            {"id": "unit", "command": "python -m unittest", "purpose": "Run Development tests"},
            {"id": "lint", "command": "python -m compileall -q .", "purpose": "Run static validation"},
        ],
        "required_services": [],
        "environment": ["CI_MODE"],
        "github": {
            "submission": {"mode": "existing-pr-events", "workflow": ".github/workflows/coferlandia-development-validation.yml"},
            "candidate_binding": "pull-request-head",
            "runner_labels": ["self-hosted", "Linux", "ARM64"],
            "shell": "bash",
            "gate": {"name": "Development Validation / Gate", "allowed_conclusions": ["success"]},
        },
    }


class RemoteDevelopmentAdapterTests(unittest.TestCase):
    def test_contract_validation_and_fingerprint_are_deterministic(self):
        module = load_module()
        contract = sample()
        module.validate_development_contract(contract)
        first = module.development_fingerprint(contract)
        reordered = json.loads(json.dumps(contract, sort_keys=True))
        self.assertEqual(first, module.development_fingerprint(reordered))
        module.validate_development_contract(dict(contract, fingerprint=first), verify_fingerprint=True)
        self.assertEqual(len(first), 64)

    def test_contract_rejects_unsafe_or_ambiguous_inputs(self):
        module = load_module()
        contract = sample(); contract["token"] = "not-allowed"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)
        contract = sample(); contract["github"]["candidate_binding"] = "merge-candidate"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)
        contract = sample(); contract["github"]["runner_labels"] = []
        with self.assertRaises(ValueError): module.validate_development_contract(contract)
        contract = sample(); contract["github"]["submission"]["workflow"] = "../unsafe.yml"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)
        contract = sample(); contract["github"]["gate"]["allowed_conclusions"] = ["success", "neutral"]
        with self.assertRaises(ValueError): module.validate_development_contract(contract)

    def test_schema_is_separate_from_qualification_profile(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        self.assertEqual(schema["properties"]["github"]["properties"]["candidate_binding"]["const"], "pull-request-head")
        self.assertNotIn("qualification_commands", json.dumps(schema))
        self.assertNotIn("merge_group", json.dumps(schema))

    def test_cli_materializes_exact_head_draft_workflow_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "development.json"
            source.write_text(json.dumps(sample()), encoding="utf-8")
            dry = subprocess.run([sys.executable, str(CLI), "development", "render", "--input", str(source), "--target-root", str(root), "--dry-run", "--json"], text=True, capture_output=True)
            self.assertEqual(dry.returncode, 0, dry.stderr or dry.stdout)
            contract_path = root / ".coferlandia" / "development" / "validation.json"
            workflow_path = root / ".github" / "workflows" / "coferlandia-development-validation.yml"
            self.assertFalse(contract_path.exists()); self.assertFalse(workflow_path.exists())
            first = subprocess.run([sys.executable, str(CLI), "development", "render", "--input", str(source), "--target-root", str(root), "--json"], text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr or first.stdout)
            first_contract = contract_path.read_text(encoding="utf-8")
            first_workflow = workflow_path.read_text(encoding="utf-8")
            second = subprocess.run([sys.executable, str(CLI), "development", "render", "--input", str(source), "--target-root", str(root), "--json"], text=True, capture_output=True)
            self.assertEqual(second.returncode, 0, second.stderr or second.stdout)
            self.assertEqual(first_contract, contract_path.read_text(encoding="utf-8"))
            self.assertEqual(first_workflow, workflow_path.read_text(encoding="utf-8"))
            for token in (
                "pull_request:", "converted_to_draft", "github.event.pull_request.draft == true",
                "permissions:", "contents: read", "ref: ${{ github.event.pull_request.head.sha }}",
                'actual="$(git rev-parse HEAD)"', 'test "$actual" = "$EXPECTED_SHA"',
                'runs-on: ["self-hosted", "Linux", "ARM64"]', 'name: "Development Validation / Gate"',
                "Development contract fingerprint:", 'tee -a "$GITHUB_STEP_SUMMARY"',
                "python -m unittest", "python -m compileall -q .",
            ):
                self.assertIn(token, first_workflow)
            for forbidden in ("pull_request_target", "contents: write", "READY_FOR_MERGE", "workflow_dispatch", "merge_group"):
                self.assertNotIn(forbidden, first_workflow)

    def test_pwsh_workflow_logs_candidate_identity_and_fingerprint(self):
        module = load_module()
        contract = sample()
        contract["github"]["shell"] = "pwsh"
        workflow = module.render_development_workflow(contract)
        self.assertIn("Write-Output $line", workflow)
        self.assertIn("Add-Content -Path $env:GITHUB_STEP_SUMMARY", workflow)
        self.assertIn("Development contract fingerprint:", workflow)
        self.assertIn("Candidate SHA: ${{ github.event.pull_request.head.sha }}", workflow)

    def test_cli_check_rejects_stale_fingerprint(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "development.json"
            source.write_text(json.dumps(sample()), encoding="utf-8")
            apply = subprocess.run([sys.executable, str(CLI), "development", "render", "--input", str(source), "--target-root", str(root), "--json"], text=True, capture_output=True)
            self.assertEqual(apply.returncode, 0, apply.stderr or apply.stdout)
            contract_path = root / ".coferlandia" / "development" / "validation.json"
            check = subprocess.run([sys.executable, str(CLI), "development", "check", "--contract", str(contract_path), "--expect-fingerprint", "0" * 64, "--json"], text=True, capture_output=True)
            self.assertEqual(check.returncode, 2)
            self.assertIn("expected fingerprint", check.stdout)


if __name__ == "__main__":
    unittest.main()
