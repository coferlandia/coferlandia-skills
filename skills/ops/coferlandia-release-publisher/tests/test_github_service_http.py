from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from release_publisher.github_service import GitHubService


class FakeResponse:
    def __init__(self, payload: object) -> None:
        self.payload = payload

    def read(self) -> bytes:
        if isinstance(self.payload, bytes):
            return self.payload
        return json.dumps(self.payload).encode("utf-8")

    def close(self) -> None:
        pass


class FakeOpener:
    def __init__(self, payloads: list[object]) -> None:
        self.payloads = list(payloads)
        self.requests = []

    def __call__(self, request, timeout=30):
        self.requests.append(request)
        return FakeResponse(self.payloads.pop(0))


class GitHubServiceHttpTests(unittest.TestCase):
    def test_repository_and_release_calls_use_http_transport(self) -> None:
        opener = FakeOpener([
            {"full_name": "coferlandia/demo", "default_branch": "main"},
            {"tag_name": "v1.2.0", "name": "Release", "draft": False, "prerelease": False, "assets": []},
        ])
        service = GitHubService(opener=opener, token="")
        info = service.repository_info("coferlandia/demo")
        release = service.release_by_tag("coferlandia/demo", "v1.2.0")
        self.assertEqual(info["default_branch"], "main")
        self.assertEqual(release["tag"], "v1.2.0")
        self.assertEqual(opener.requests[0].method, "GET")
        self.assertIn("/repos/coferlandia/demo", opener.requests[0].full_url)

    def test_create_release_posts_explicit_draft_payload(self) -> None:
        opener = FakeOpener([{"id": 42, "tag_name": "v1.2.0", "draft": True, "assets": []}])
        service = GitHubService(opener=opener, token="")
        release = service.create_draft_release("coferlandia/demo", "v1.2.0", "Demo", "Notes", False)
        request = opener.requests[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertTrue(release["draft"])
        self.assertEqual(request.method, "POST")
        self.assertTrue(payload["draft"])
        self.assertFalse(payload["prerelease"])
        self.assertEqual(payload["tag_name"], "v1.2.0")
        self.assertNotIn("target_commitish", payload)

    def test_service_exposes_no_destructive_release_delete(self) -> None:
        self.assertFalse(hasattr(GitHubService, "delete_release"))
        self.assertFalse(hasattr(GitHubService, "move_tag"))


if __name__ == "__main__":
    unittest.main()
