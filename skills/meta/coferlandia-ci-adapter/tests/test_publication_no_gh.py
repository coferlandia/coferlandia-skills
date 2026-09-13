from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE = SKILL_ROOT / "scripts" / "coferlandia_ci_adapter_cli" / "publication.py"


def load_module():
    spec = importlib.util.spec_from_file_location("publication_module", MODULE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PublicationWorkflowTests(unittest.TestCase):
    def test_generated_workflow_uses_python_rest_not_gh_cli(self) -> None:
        module = load_module()
        workflow = module.render_workflow(
            publisher_path=".agents/skills/coferlandia-release-publisher/scripts/coferlandia-release.py",
            runs_on=["self-hosted", "Linux", "ARM64", "coferlandia-ci", "docker"],
        )
        self.assertNotIn("gh api", workflow)
        self.assertNotIn("GH_TOKEN", workflow)
        self.assertIn("GITHUB_TOKEN", workflow)
        self.assertIn("from urllib.request import Request, urlopen", workflow)
        self.assertIn("merge_sha=${{ steps.authority.outputs.merge_sha }}", workflow.replace('MERGE_SHA: ${{ steps.authority.outputs.merge_sha }}', 'merge_sha=${{ steps.authority.outputs.merge_sha }}'))
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertLess(workflow.index("actions/setup-python@v5"), workflow.index("Require release authority"))
        self.assertIn('runs-on: ["self-hosted","Linux","ARM64","coferlandia-ci","docker"]', workflow)
        self.assertNotIn("deploy", workflow.lower())


if __name__ == "__main__":
    unittest.main()
