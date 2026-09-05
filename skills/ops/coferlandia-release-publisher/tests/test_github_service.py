from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from release_publisher.github_service import GitHubService


class FakeRunner:
    def __init__(self, responses: list[tuple[int, object]]) -> None:
        self.responses = list(responses)
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(args)
        code, payload = self.responses.pop(0)
        stdout = payload if isinstance(payload, str) else json.dumps(payload)
        return subprocess.CompletedProcess(args, code, stdout, "" if code == 0 else "failure")


class GitHubServiceTests(unittest.TestCase):
    def test_reads_repository_and_release_as_json(self) -> None:
        runner = FakeRunner([
            (0, {"name": "demo", "nameWithOwner": "coferlandia/demo", "defaultBranchRef": {"name": "main"}}),
            (0, {"tag_name": "v1.2.0", "name": "Release", "draft": False, "prerelease": False, "assets": []}),
        ])
        service = GitHubService(runner=runner)
        info = service.repository_info("coferlandia/demo")
        release = service.release_by_tag("coferlandia/demo", "v1.2.0")
        self.assertEqual(info["default_branch"], "main")
        self.assertEqual(release["tag"], "v1.2.0")
        self.assertFalse(release["draft"])

    def test_invalid_json_fails_explicitly(self) -> None:
        service = GitHubService(runner=FakeRunner([(0, "not-json")]))
        with self.assertRaises(RuntimeError):
            service.repository_info("coferlandia/demo")

    def test_create_release_is_draft_and_does_not_create_tag(self) -> None:
        runner = FakeRunner([(0, {"id": 42, "tag_name": "v1.2.0", "draft": True})])
        service = GitHubService(runner=runner)
        result = service.create_draft_release("coferlandia/demo", "v1.2.0", "Demo", "Notes", False)
        self.assertTrue(result["draft"])
        call = runner.calls[0]
        joined = " ".join(call)
        self.assertIn("/releases", joined)
        self.assertIn("draft=true", joined)
        self.assertNotIn("target_commitish", joined)

    def test_service_exposes_no_destructive_release_delete(self) -> None:
        self.assertFalse(hasattr(GitHubService, "delete_release"))
        self.assertFalse(hasattr(GitHubService, "move_tag"))


if __name__ == "__main__":
    unittest.main()
