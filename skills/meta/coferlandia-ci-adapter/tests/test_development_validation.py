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


def sample_with_setup():
    contract = sample()
    contract["github"]["setup"] = [
        {
            "name": "Set up Python",
            "uses": "actions/setup-python@v7",
            "with": {"python-version": "3.12"},
        },
        {
            "name": "Set up Node",
            "uses": "actions/setup-node@v7",
            "with": {
                "cache-dependency-path": "apps/frontend/package-lock.json",
                "cache": "npm",
                "node-version": 22,
            },
        },
    ]
    return contract

def sample_with_dispatch():
    contract = sample()
    contract["github"]["submission"]["fallback"] = {
        "mode": "workflow-dispatch-exact-head",
        "control_ref": "dev",
    }
    return contract


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

    def test_existing_v1_contract_without_setup_remains_valid(self):
        module = load_module()
        contract = sample()
        module.validate_development_contract(contract)
        workflow = module.render_development_workflow(contract)
        self.assertNotIn("actions/setup-python", workflow)
        self.assertNotIn("actions/setup-node", workflow)

    def test_exact_head_dispatch_fallback_is_validated_fingerprinted_and_fail_closed(self):
        module = load_module()
        contract = sample_with_dispatch()
        module.validate_development_contract(contract)
        self.assertNotEqual(module.development_fingerprint(contract), module.development_fingerprint(sample()))

        workflow = module.render_development_workflow(contract)
        for token in (
            "workflow_dispatch:",
            "pr_number:",
            "candidate_sha:",
            "pull-requests: read",
            "Resolve exact candidate identity",
            "actions/github-script@v7",
            "expectedControlRef",
            "Development validation requires an open Draft PR",
            "candidate SHA mismatch",
            "ref: ${{ steps.identity.outputs.candidate_sha }}",
            "EXPECTED_SHA: ${{ steps.identity.outputs.candidate_sha }}",
        ):
            self.assertIn(token, workflow)
        self.assertIn('const expectedControlRef = "dev";', workflow)
        self.assertIn("const requestedSha = '${{ inputs.candidate_sha }}';", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotIn("READY_FOR_MERGE", workflow)

        unsafe = sample_with_dispatch()
        unsafe["github"]["submission"]["fallback"]["control_ref"] = "../dev"
        with self.assertRaises(ValueError):
            module.validate_development_contract(unsafe)

        unsafe = sample_with_dispatch()
        unsafe["github"]["submission"]["fallback"]["mode"] = "workflow-dispatch"
        with self.assertRaises(ValueError):
            module.validate_development_contract(unsafe)

    def test_label_trigger_validation_and_fingerprint(self):
        module = load_module()
        trigger = {"kind": "pull-request-label", "label": "development:validate",
                   "rerun_on_synchronize": True, "base_branches": ["dev"]}
        contract = sample()
        contract["github"]["submission"]["trigger"] = trigger.copy()
        module.validate_development_contract(contract)
        baseline = module.development_fingerprint(contract)
        self.assertNotEqual(baseline, module.development_fingerprint(sample()))
        for field, value in (("label", "another:label"), ("rerun_on_synchronize", False), ("base_branches", ["main"])):
            changed = json.loads(json.dumps(contract))
            changed["github"]["submission"]["trigger"][field] = value
            self.assertNotEqual(baseline, module.development_fingerprint(changed))
        invalid = [None, {}, dict(trigger, extra=True), dict(trigger, kind="other"),
                   dict(trigger, label=""), dict(trigger, label="a\nb"),
                   dict(trigger, label="${{ github.token }}"),
                   dict(trigger, rerun_on_synchronize="true"),
                   dict(trigger, base_branches=[]), dict(trigger, base_branches=["dev", "dev"]),
                   dict(trigger, base_branches=["*"]), dict(trigger, base_branches="dev")]
        invalid.extend({k: v for k, v in trigger.items() if k != field} for field in trigger)
        for value in invalid:
            with self.subTest(trigger=value):
                bad = sample()
                bad["github"]["submission"]["trigger"] = value
                with self.assertRaises(ValueError):
                    module.validate_development_contract(bad)
        for mode in ("fallback", "primary"):
            bad = sample_with_dispatch()
            if mode == "primary":
                bad["github"]["submission"] = {"mode": "workflow-dispatch-exact-head", "workflow": ".github/workflows/dev.yml", "control_ref": "dev"}
            bad["github"]["submission"]["trigger"] = trigger
            with self.assertRaises(ValueError):
                module.validate_development_contract(bad)

    def test_setup_actions_are_validated_fingerprinted_and_rendered_in_order(self):
        module = load_module()
        contract = sample_with_setup()
        module.validate_development_contract(contract)
        self.assertNotEqual(module.development_fingerprint(contract), module.development_fingerprint(sample()))

        workflow = module.render_development_workflow(contract)
        record_index = workflow.index("Record Development contract")
        python_index = workflow.index("Set up Python")
        node_index = workflow.index("Set up Node")
        command_index = workflow.index("Run Development tests")
        self.assertLess(record_index, python_index)
        self.assertLess(python_index, node_index)
        self.assertLess(node_index, command_index)
        self.assertIn('uses: "actions/setup-python@v7"', workflow)
        self.assertIn('python-version: "3.12"', workflow)
        self.assertIn('uses: "actions/setup-node@v7"', workflow)
        self.assertIn('cache: "npm"', workflow)
        self.assertIn('cache-dependency-path: "apps/frontend/package-lock.json"', workflow)
        self.assertIn("node-version: 22", workflow)

        cache_index = workflow.index('cache: "npm"')
        dependency_index = workflow.index('cache-dependency-path: "apps/frontend/package-lock.json"')
        node_version_index = workflow.index("node-version: 22")
        self.assertLess(cache_index, dependency_index)
        self.assertLess(dependency_index, node_version_index)

    def test_incremental_evidence_cache_requires_safe_label_trigger_and_emits_partial_save(self):
        module = load_module()
        contract = sample()
        contract["github"]["submission"]["trigger"] = {
            "kind": "pull-request-label", "label": "development:validate",
            "rerun_on_synchronize": True, "base_branches": ["dev"],
        }
        contract["github"]["evidence_cache"] = {
            "path": "artifacts/backend-suite-evidence.json",
            "prefix": "dev-suite-v1",
            "verify_command": "python scripts/evidence.py verify",
            "before_command_id": "unit",
        }
        module.validate_development_contract(contract)
        workflow = module.render_development_workflow(contract)
        self.assertIn("  actions: read", workflow)
        self.assertIn("GITHUB_TOKEN: ${{ github.token }}", workflow)
        self.assertIn("uses: actions/cache/restore@v6", workflow)
        self.assertIn("uses: actions/cache/save@v6", workflow)
        self.assertIn("uses: actions/upload-artifact@v7", workflow)
        self.assertIn("if: always()", workflow)
        self.assertLess(workflow.index("Verify prior Development evidence"), workflow.index("Run Development tests"))
        self.assertLess(workflow.index("Run Development tests"), workflow.index("Upload partial Development evidence"))
        self.assertNotIn("contents: write", workflow)
        bad = json.loads(json.dumps(contract))
        bad["github"]["evidence_cache"]["before_command_id"] = "missing"
        with self.assertRaises(ValueError): module.validate_development_contract(bad)
        bad = json.loads(json.dumps(contract))
        bad["github"]["evidence_cache"]["prefix"] = "bad-${{ secrets.x }}"
        with self.assertRaises(ValueError): module.validate_development_contract(bad)
        bad = json.loads(json.dumps(contract))
        bad["github"]["submission"].pop("trigger")
        with self.assertRaises(ValueError): module.validate_development_contract(bad)
        bad = json.loads(json.dumps(contract))
        bad["github"]["shell"] = "pwsh"
        with self.assertRaises(ValueError): module.validate_development_contract(bad)

    def test_evidence_cache_rejects_incompatible_submission_modes(self):
        module = load_module()
        for submission in (
            {"mode": "existing-pr-events",
             "workflow": ".github/workflows/coferlandia-development-validation.yml"},
            {"mode": "workflow-dispatch-exact-head",
             "workflow": ".github/workflows/coferlandia-development-validation.yml",
             "control_ref": "dev"},
        ):
            with self.subTest(mode=submission["mode"]):
                contract = sample()
                contract["github"]["submission"] = submission
                contract["github"]["evidence_cache"] = {
                    "path": "artifacts/backend-suite-evidence.json",
                    "prefix": "dev-suite-v1",
                    "verify_command": "python scripts/evidence.py verify",
                    "before_command_id": "unit",
                }
                with self.assertRaisesRegex(ValueError, "requires a labeled pull-request trigger"):
                    module.validate_development_contract(contract)

    def test_repository_development_workflow_matches_current_contract(self):
        module = load_module()
        root = SKILL_ROOT.parents[2]
        contract_path = root / ".coferlandia/development/validation.json"
        if not contract_path.is_file():
            self.skipTest("repository has no published Development contract")
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        module.validate_development_contract(contract, verify_fingerprint=True)
        workflow_path = root / contract["github"]["submission"]["workflow"]
        self.assertEqual(module.render_development_workflow(contract), workflow_path.read_text(encoding="utf-8"))

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

    def test_contract_rejects_unsafe_setup_actions(self):
        module = load_module()

        contract = sample_with_setup(); contract["github"]["setup"][0]["uses"] = "./.github/actions/setup"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)

        contract = sample_with_setup(); contract["github"]["setup"][0]["with"]["python-version"] = "$" + "{{ secrets.RUNTIME_VERSION }}"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)

        contract = sample_with_setup(); contract["github"]["setup"][0]["with"]["matrix"] = {"python": "3.12"}
        with self.assertRaises(ValueError): module.validate_development_contract(contract)

        contract = sample_with_setup(); contract["github"]["setup"][0]["with"]["access-token"] = "value"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)

        contract = sample_with_setup(); contract["github"]["setup"][1]["name"] = "Set up Python"
        with self.assertRaises(ValueError): module.validate_development_contract(contract)

    def test_schema_is_separate_from_qualification_profile_and_setup_is_optional(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], 1)
        github_schema = schema["properties"]["github"]
        self.assertEqual(github_schema["properties"]["candidate_binding"]["const"], "pull-request-head")
        self.assertIn("setup", github_schema["properties"])
        fallback_schema = github_schema["properties"]["submission"]["properties"]["fallback"]
        self.assertEqual(fallback_schema["properties"]["mode"]["const"], "workflow-dispatch-exact-head")
        self.assertIn("control_ref", fallback_schema["required"])
        trigger_schema = schema["$defs"]["pullRequestLabelTrigger"]
        self.assertEqual(set(trigger_schema["required"]), {"kind", "label", "rerun_on_synchronize", "base_branches"})
        self.assertFalse(trigger_schema["additionalProperties"])
        self.assertEqual(trigger_schema["properties"]["kind"]["const"], "pull-request-label")
        self.assertEqual(trigger_schema["properties"]["rerun_on_synchronize"]["type"], "boolean")
        self.assertTrue(trigger_schema["properties"]["base_branches"]["uniqueItems"])
        submission_schema = github_schema["properties"]["submission"]
        self.assertEqual(submission_schema["properties"]["trigger"], {"$ref": "#/$defs/pullRequestLabelTrigger"})
        pr_schema = submission_schema["oneOf"][0]
        self.assertIn("trigger", pr_schema["properties"])
        self.assertEqual(pr_schema["not"], {"required": ["trigger", "fallback"]})
        self.assertNotIn("setup", github_schema["required"])
        setup_item = github_schema["properties"]["setup"]["items"]
        self.assertEqual(set(setup_item["required"]), {"name", "uses"})
        self.assertFalse(setup_item["additionalProperties"])
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
