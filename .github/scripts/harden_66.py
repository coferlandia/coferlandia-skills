from __future__ import annotations

from pathlib import Path


def patch_publication_adapter() -> None:
    path = Path('skills/meta/coferlandia-ci-adapter/scripts/coferlandia_ci_adapter_cli/publication.py')
    text = path.read_text(encoding='utf-8')
    step = text.index('      - name: Parse immutable publication request')

    import_anchor = "          from urllib.request import Request, urlopen\n"
    import_at = text.index(import_anchor, step)
    hardened_imports = (
        "          from urllib.error import HTTPError\n"
        "          from urllib.parse import quote\n"
        + import_anchor
    )
    text = text[:import_at] + hardened_imports + text[import_at + len(import_anchor):]

    start = text.index("          event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))\n", step)
    end = text.index("          request_path = Path(os.environ['RUNNER_TEMP']) / 'coferlandia-publication-request.json'\n", start)
    replacement = '''          def parse_request(candidate_body):
              if not isinstance(candidate_body, str) or candidate_body.count(marker) != 1:
                  raise ValueError('publication request must contain exactly one marker')
              tail = candidate_body.split(marker, 1)[1]
              matches = re.findall(r'```json\\s*(.+?)\\s*```', tail, re.S)
              if len(matches) != 1:
                  raise ValueError('publication request must contain exactly one JSON block')
              try:
                  request = json.loads(matches[0])
              except json.JSONDecodeError as exc:
                  raise ValueError('publication request JSON is invalid') from exc
              expected = {{'schema', 'target_sha', 'version', 'impact', 'title', 'notes'}}
              if not isinstance(request, dict) or set(request) != expected or request.get('schema') != 1:
                  raise ValueError('invalid publication request schema')
              if not re.fullmatch(r'[0-9a-f]{{40}}', request['target_sha']):
                  raise ValueError('target_sha must be an exact 40-character lowercase SHA')
              if not re.fullmatch(r'[0-9]+\\.[0-9]+\\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\\+[0-9A-Za-z.-]+)?', request['version']):
                  raise ValueError('version must be explicit SemVer without tag prefix')
              if request['impact'] not in {{'patch', 'minor', 'major'}}:
                  raise ValueError('impact must be patch, minor, or major')
              if not isinstance(request['title'], str) or not request['title'].strip():
                  raise ValueError('title must be non-empty')
              if not isinstance(request['notes'], str) or not request['notes'].strip():
                  raise ValueError('notes must be non-empty')
              return request

          event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
          body = event['comment']['body']
          request_comment_id = event['comment']['id']
          if body == retry_command:
              repo = os.environ['GITHUB_REPOSITORY']
              token = os.environ['GITHUB_TOKEN']
              issue_number = event['issue']['number']
              current_id = event['comment']['id']

              def api_json(url):
                  api_request = Request(url, headers={{
                      'Accept': 'application/vnd.github+json',
                      'Authorization': f'Bearer {{token}}',
                      'User-Agent': 'coferlandia-release-publication',
                      'X-GitHub-Api-Version': '2022-11-28',
                  }})
                  with urlopen(api_request, timeout=30) as response:
                      return json.load(response)

              def permission_for(login):
                  url = f'https://api.github.com/repos/{{repo}}/collaborators/{{quote(login, safe="")}}/permission'
                  try:
                      value = api_json(url)
                  except HTTPError as exc:
                      if exc.code in {{403, 404}}:
                          return None
                      raise
                  return value.get('permission')

              comments = []
              page = 1
              while True:
                  page_items = api_json(f'https://api.github.com/repos/{{repo}}/issues/{{issue_number}}/comments?per_page=100&page={{page}}')
                  if not isinstance(page_items, list):
                      raise SystemExit('GitHub issue comments response must be a list')
                  comments.extend(page_items)
                  if len(page_items) < 100:
                      break
                  page += 1

              request = None
              for comment in sorted(comments, key=lambda item: item.get('id', 0), reverse=True):
                  comment_id = comment.get('id', 0)
                  candidate_body = comment.get('body', '')
                  if comment_id >= current_id or marker not in candidate_body:
                      continue
                  author = (comment.get('user') or {{}}).get('login')
                  if not author or permission_for(author) not in {{'admin', 'maintain'}}:
                      continue
                  try:
                      candidate = parse_request(candidate_body)
                  except ValueError:
                      continue
                  request = candidate
                  request_comment_id = comment_id
                  break
              if request is None:
                  raise SystemExit('retry requested but no prior authorized valid publication request exists')
          else:
              try:
                  request = parse_request(body)
              except ValueError as exc:
                  raise SystemExit(str(exc)) from exc
'''
    text = text[:start] + replacement + text[end:]

    output_anchor = "              output.write(f\"version={{request['version']}}\\\\n\")\n"
    if output_anchor not in text:
        raise RuntimeError('request output anchor not found')
    text = text.replace(
        output_anchor,
        output_anchor + "              output.write(f\"request_comment_id={{request_comment_id}}\\\\n\")\n",
        1,
    )
    path.write_text(text, encoding='utf-8')


def patch_publisher_transport() -> None:
    path = Path('skills/ops/coferlandia-release-publisher/scripts/release_publisher/github_service.py')
    text = path.read_text(encoding='utf-8')
    old = '        return next((release for release in self.list_releases(repository) if release.get("tag") == tag), None)\n'
    new = (
        '        matches = [release for release in self.list_releases(repository) if release.get("tag") == tag]\n'
        '        if len(matches) > 1:\n'
        '            raise ReleaseError(f"multiple GitHub Releases use tag {tag}")\n'
        '        return matches[0] if matches else None\n'
    )
    if old not in text:
        raise RuntimeError('release_by_tag fallback anchor not found')
    text = text.replace(old, new, 1)

    old_download = '''    def download_text_asset(self, repository: str, asset_id: int) -> str:
        owner, repo = self._split(repository)
        raw = self._request_bytes(
            "GET",
            f"repos/{owner}/{repo}/releases/assets/{asset_id}",
            accept="application/octet-stream",
        )
        if raw is None:
            raise ReleaseError("GitHub asset download returned no response")
        return raw.decode("utf-8")
'''
    new_download = '''    def download_asset_bytes(self, repository: str, asset_id: int) -> bytes:
        owner, repo = self._split(repository)
        raw = self._request_bytes(
            "GET",
            f"repos/{owner}/{repo}/releases/assets/{asset_id}",
            accept="application/octet-stream",
        )
        if raw is None:
            raise ReleaseError("GitHub asset download returned no response")
        return raw

    def download_text_asset(self, repository: str, asset_id: int) -> str:
        return self.download_asset_bytes(repository, asset_id).decode("utf-8")
'''
    if old_download not in text:
        raise RuntimeError('asset download anchor not found')
    text = text.replace(old_download, new_download, 1)
    path.write_text(text, encoding='utf-8')


def patch_publisher_operations() -> None:
    path = Path('skills/ops/coferlandia-release-publisher/scripts/release_publisher/operations.py')
    text = path.read_text(encoding='utf-8')
    anchor = '''def _asset_digest(asset: dict[str, Any]) -> str | None:
    digest = asset.get("sha256")
    return digest if isinstance(digest, str) and len(digest) == 64 else None
'''
    helper = anchor + '''
def _resolved_asset_digest(github: GitHubService, repository: str, asset: dict[str, Any]) -> str | None:
    digest = _asset_digest(asset)
    if digest:
        return digest
    asset_id = asset.get("id")
    if not asset_id:
        return None
    return hashlib.sha256(github.download_asset_bytes(repository, int(asset_id))).hexdigest()
'''
    if anchor not in text:
        raise RuntimeError('asset digest anchor not found')
    text = text.replace(anchor, helper, 1)
    text = text.replace('_asset_digest(existing) != artifact["sha256"]', '_resolved_asset_digest(github, repository, existing) != artifact["sha256"]', 1)
    text = text.replace('_asset_digest(uploaded) != artifact["sha256"]', '_resolved_asset_digest(github, repository, uploaded) != artifact["sha256"]', 1)
    text = text.replace('_asset_digest(existing) != digest', '_resolved_asset_digest(github, plan.repository, existing) != digest', 1)
    text = text.replace('_asset_digest(uploaded) != digest', '_resolved_asset_digest(github, plan.repository, uploaded) != digest', 1)
    text = text.replace(
        'def _verify_manifest_artifacts(release: dict[str, Any], manifest: dict[str, Any] | None) -> list[str]:',
        'def _verify_manifest_artifacts(github: GitHubService, repository: str, release: dict[str, Any], manifest: dict[str, Any] | None) -> list[str]:',
        1,
    )
    text = text.replace('elif _asset_digest(asset) != expected:', 'elif _resolved_asset_digest(github, repository, asset) != expected:', 1)
    text = text.replace('elif _asset_digest(existing) != artifact["sha256"]:', 'elif _resolved_asset_digest(github, plan.repository, existing) != artifact["sha256"]:', 1)
    text = text.replace('errors.extend(_verify_manifest_artifacts(release, manifest))', 'errors.extend(_verify_manifest_artifacts(github, repository, release, manifest))', 1)
    path.write_text(text, encoding='utf-8')


def write_retry_runtime_test() -> None:
    path = Path('skills/meta/coferlandia-ci-adapter/tests/test_publication_retry_runtime.py')
    path.write_text(r'''from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import textwrap
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


class FakeResponse:
    def __init__(self, value): self.value = value
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return json.dumps(self.value).encode("utf-8")


class RetryRuntimeTests(unittest.TestCase):
    def _script(self):
        workflow = load_module().render_workflow(
            publisher_path=".agents/skills/coferlandia-release-publisher/scripts/coferlandia-release.py"
        )
        section = workflow.split("      - name: Parse immutable publication request", 1)[1]
        script = section.split("          python - <<'PY'\n", 1)[1].split("\n          PY", 1)[0]
        script = textwrap.dedent(script)
        return script.replace(
            "from urllib.request import Request, urlopen",
            "from urllib.request import Request\nurlopen = fake_urlopen",
        )

    def _request(self, title="Original"):
        payload = {
            "schema": 1,
            "target_sha": "a" * 40,
            "version": "1.0.0",
            "impact": "major",
            "title": title,
            "notes": "notes",
        }
        return "<!-- coferlandia-release-publication-request:v1 -->\n```json\n" + json.dumps(payload) + "\n```"

    def test_retry_skips_newer_malformed_and_unauthorized_requests(self):
        comments = [
            {"id": 100, "body": self._request("Authorized original"), "user": {"login": "good"}},
            {"id": 200, "body": self._request("Unauthorized override"), "user": {"login": "evil"}},
            {"id": 250, "body": "<!-- coferlandia-release-publication-request:v1 -->\n```json\n{bad}\n```", "user": {"login": "good"}},
        ]

        def fake_urlopen(request, timeout=30):
            url = request.full_url
            if "/issues/77/comments" in url:
                return FakeResponse(comments)
            if "/collaborators/good/permission" in url:
                return FakeResponse({"permission": "maintain"})
            if "/collaborators/evil/permission" in url:
                return FakeResponse({"permission": "read"})
            raise AssertionError(url)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            event = {
                "issue": {"number": 77},
                "comment": {"id": 300, "body": "Retry the existing Coferlandia publication request."},
            }
            event_path = temp / "event.json"
            output_path = temp / "out.txt"
            event_path.write_text(json.dumps(event), encoding="utf-8")
            old = os.environ.copy()
            try:
                os.environ.update({
                    "GITHUB_EVENT_PATH": str(event_path),
                    "GITHUB_REPOSITORY": "coferlandia/demo",
                    "GITHUB_TOKEN": "token",
                    "GITHUB_OUTPUT": str(output_path),
                    "RUNNER_TEMP": str(temp),
                })
                exec(self._script(), {"fake_urlopen": fake_urlopen})
            finally:
                os.environ.clear(); os.environ.update(old)
            resolved = json.loads((temp / "coferlandia-publication-request.json").read_text(encoding="utf-8"))
            self.assertEqual(resolved["title"], "Authorized original")
            self.assertIn("request_comment_id=100", output_path.read_text(encoding="utf-8"))

    def test_retry_fails_when_no_prior_authorized_valid_request_exists(self):
        comments = [{"id": 100, "body": self._request("No authority"), "user": {"login": "evil"}}]

        def fake_urlopen(request, timeout=30):
            if "/issues/77/comments" in request.full_url:
                return FakeResponse(comments)
            if "/collaborators/evil/permission" in request.full_url:
                return FakeResponse({"permission": "read"})
            raise AssertionError(request.full_url)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            event_path = temp / "event.json"
            event_path.write_text(json.dumps({
                "issue": {"number": 77},
                "comment": {"id": 300, "body": "Retry the existing Coferlandia publication request."},
            }), encoding="utf-8")
            old = os.environ.copy()
            try:
                os.environ.update({
                    "GITHUB_EVENT_PATH": str(event_path),
                    "GITHUB_REPOSITORY": "coferlandia/demo",
                    "GITHUB_TOKEN": "token",
                    "GITHUB_OUTPUT": str(temp / "out.txt"),
                    "RUNNER_TEMP": str(temp),
                })
                with self.assertRaisesRegex(SystemExit, "no prior authorized valid"):
                    exec(self._script(), {"fake_urlopen": fake_urlopen})
            finally:
                os.environ.clear(); os.environ.update(old)


if __name__ == "__main__":
    unittest.main()
''', encoding='utf-8')


def patch_publisher_tests() -> None:
    http_path = Path('skills/ops/coferlandia-release-publisher/tests/test_github_service_http.py')
    text = http_path.read_text(encoding='utf-8')
    if 'from release_publisher.model import ReleaseError' not in text:
        text = text.replace(
            'from release_publisher.github_service import GitHubService\n',
            'from release_publisher.github_service import GitHubService\nfrom release_publisher.model import ReleaseError\n',
            1,
        )
    test = '''
    def test_release_by_tag_rejects_ambiguous_draft_collection(self) -> None:
        not_found = HTTPError(
            "https://api.github.com/repos/coferlandia/demo/releases/tags/v1.2.0",
            404, "Not Found", hdrs=None, fp=io.BytesIO(b"{}"),
        )
        opener = FakeOpener([
            not_found,
            [
                {"id": 41, "tag_name": "v1.2.0", "name": "Draft A", "draft": True, "prerelease": False, "assets": []},
                {"id": 42, "tag_name": "v1.2.0", "name": "Draft B", "draft": True, "prerelease": False, "assets": []},
            ],
        ])
        service = GitHubService(opener=opener, token="")
        with self.assertRaisesRegex(ReleaseError, "multiple GitHub Releases"):
            service.release_by_tag("coferlandia/demo", "v1.2.0")

'''
    marker = '    def test_create_release_posts_explicit_draft_payload(self) -> None:\n'
    if 'test_release_by_tag_rejects_ambiguous_draft_collection' not in text:
        text = text.replace(marker, test + marker, 1)
    http_path.write_text(text, encoding='utf-8')

    pub_path = Path('skills/ops/coferlandia-release-publisher/tests/test_publication.py')
    text = pub_path.read_text(encoding='utf-8')
    extra = '''

class NoDigestGitHub(StatefulGitHub):
    def upload_asset(self, repository, release_id, path: Path, name=None):
        asset = super().upload_asset(repository, release_id, path, name)
        stored = next(item for item in self.releases if item["id"] == release_id)["assets"][-1]
        asset.pop("sha256", None)
        stored.pop("sha256", None)
        return asset

    def download_asset_bytes(self, repository, asset_id):
        return self.contents[asset_id].encode("utf-8")


class AssetDigestFallbackTests(unittest.TestCase):
    def test_provenance_publish_succeeds_when_asset_digest_metadata_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            git, github = StatefulGit(), NoDigestGitHub()
            policy = copy.deepcopy(DEFAULT_POLICY)
            inspection = inspect_release(root, "coferlandia/demo", "HEAD", policy, git=git, github=github)
            plan = build_plan(
                root, "coferlandia/demo", inspection, policy,
                impact="minor", version="1.0.0", title="Initial release",
                release_notes="Summary", provenance="optional", git=git, github=github,
            )
            result = publish_release(root, plan, git=git, github=github)
            self.assertEqual(result["status"], "published")
            self.assertEqual(result["release"]["consistency"], "pass")
'''
    if 'class AssetDigestFallbackTests' not in text:
        text = text.replace('\n\nif __name__ == "__main__":\n', extra + '\n\nif __name__ == "__main__":\n', 1)
    pub_path.write_text(text, encoding='utf-8')


def main() -> None:
    patch_publication_adapter()
    patch_publisher_transport()
    patch_publisher_operations()
    write_retry_runtime_test()
    patch_publisher_tests()


if __name__ == '__main__':
    main()
