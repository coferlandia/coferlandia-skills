import importlib.util
import json
import re
from types import SimpleNamespace
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ROOT = SKILL_ROOT.parents[2]
MODULE_PATH = SKILL_ROOT / "scripts" / "coferlandia_ci_adapter_cli" / "development.py"
CONTRACT_PATH = ROOT / ".coferlandia" / "development" / "validation.json"


def load_module():
    spec = importlib.util.spec_from_file_location("development_module_lifecycle", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def current_contract():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    contract.pop("fingerprint", None)
    return contract


class DevelopmentWorkflowLifecycleTests(unittest.TestCase):
    def test_legacy_pr_events_remain_supported_for_compatible_contracts(self):
        module = load_module()
        contract = current_contract()
        contract["github"].pop("evidence_cache", None)
        contract["github"]["submission"] = {
            "mode": "existing-pr-events",
            "workflow": ".github/workflows/coferlandia-development-validation.yml",
            "fallback": {
                "mode": "workflow-dispatch-exact-head",
                "control_ref": "dev",
            },
        }
        workflow = module.render_development_workflow(contract)

        self.assertIn(
            "types: [opened, synchronize, reopened, converted_to_draft, ready_for_review, closed]",
            workflow,
        )
        self.assertIn(
            "github.event.pull_request.draft == true && github.event.action != 'ready_for_review' && github.event.action != 'closed'",
            workflow,
        )
        self.assertIn('run-name: "Development Validation / PR #${{ github.event.pull_request.number || inputs.pr_number }} candidate:${{ github.event.pull_request.head.sha || inputs.candidate_sha }}"', workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("group: coferlandia-development-", workflow)
        self.assertIn("cancel-in-progress: true", workflow)

    def test_label_trigger_lifecycle_and_concurrency_admission(self):
        module = load_module()
        for rerun in (True, False):
            contract = current_contract()
            contract["github"]["submission"] = {
                "mode": "existing-pr-events",
                "workflow": ".github/workflows/coferlandia-development-validation.yml",
                "trigger": {"kind": "pull-request-label", "label": "development:validate",
                            "rerun_on_synchronize": rerun, "base_branches": ["dev", "main"]},
            }
            workflow = module.render_development_workflow(contract)
            self.assertNotIn("\nconcurrency:", workflow)
            self.assertIn("    concurrency:\n      group: coferlandia-development-${{ github.event.pull_request.number }}\n      cancel-in-progress: true", workflow)
            self.assertNotIn("workflow_dispatch:", workflow)
            self.assertIn('branches: ["dev", "main"]', workflow)
            self.assertIn("persist-credentials: false", workflow)
            self.assertIn("ref: ${{ github.event.pull_request.head.sha }}", workflow)
            self.assertIn("permissions:\n  contents: read\n", workflow)
            fingerprint = module.development_fingerprint(contract)
            self.assertIn('run-name: "Development Validation / PR #${{ github.event.pull_request.number }} candidate:${{ github.event.pull_request.head.sha }} fingerprint:' + fingerprint + '"', workflow)
            # Execute the emitted eligibility expression against lifecycle payloads.
            # Job-level concurrency is admitted only after this condition passes.
            expression = workflow.split("    if: >-\n", 1)[1].split("    concurrency:", 1)[0].strip()
            expression = expression.replace("&&", "and").replace("||", "or")
            expression = expression.replace("github.event.pull_request.labels.*.name", "label_names")
            expression = re.sub(r"\btrue\b", "True", expression)
            expression = " ".join(expression.splitlines())
            for action in ("opened", "labeled", "synchronize", "reopened", "converted_to_draft", "ready_for_review", "closed", "unlabeled", "edited"):
                for draft in (True, False):
                    for state in ("open", "closed"):
                        for base in ("dev", "main", "other"):
                            for requested in (True, False):
                                for added in ("development:validate", "unrelated"):
                                    with self.subTest(rerun=rerun, action=action, draft=draft, state=state, base=base, requested=requested, added=added):
                                        ns = SimpleNamespace
                                        github = ns(event_name="pull_request", event=ns(action=action, label=ns(name=added), pull_request=ns(draft=draft, state=state, base=ns(ref=base))))
                                        actual = eval(expression, {"__builtins__": {}}, {"github": github, "label_names": ["development:validate"] if requested else [], "contains": lambda values, value: value in values, "fromJSON": json.loads})
                                        eligible_action = (action == "labeled" and added == "development:validate") or action in ("reopened", "converted_to_draft") or (action == "synchronize" and rerun)
                                        expected = draft and state == "open" and base in ("dev", "main") and requested and eligible_action
                                        self.assertEqual(actual, expected)

    def test_primary_exact_head_dispatch_has_no_automatic_draft_pr_submission(self):
        module = load_module()
        contract = current_contract()
        contract["github"].pop("evidence_cache", None)
        contract["github"]["submission"] = {
            "mode": "workflow-dispatch-exact-head",
            "workflow": ".github/workflows/coferlandia-development-validation.yml",
            "control_ref": "dev",
        }

        module.validate_development_contract(contract)
        workflow = module.render_development_workflow(contract)

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("pr_number:", workflow)
        self.assertIn("candidate_sha:", workflow)
        self.assertIn('run-name: "Development Validation / PR #${{ inputs.pr_number }} candidate:${{ inputs.candidate_sha }}"', workflow)
        self.assertIn('const expectedControlRef = "dev";', workflow)
        self.assertIn("group: coferlandia-development-${{ inputs.pr_number }}", workflow)
        self.assertNotIn("  pull_request:\n", workflow)
        self.assertNotIn("github.event.pull_request.draft", workflow)
        self.assertNotIn("github.event.pull_request.number", workflow)
        self.assertNotIn("github.event.pull_request.head.sha", workflow)


if __name__ == "__main__":
    unittest.main()
