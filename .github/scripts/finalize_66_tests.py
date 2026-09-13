from pathlib import Path

# Existing transport tests must provide the collection response now that release_by_tag
# always checks for conflicting release objects with the same tag.
path = Path('skills/ops/coferlandia-release-publisher/tests/test_github_service.py')
text = path.read_text(encoding='utf-8')
old = '''        opener = FakeOpener([
            {"full_name": "coferlandia/demo", "default_branch": "main"},
            {"tag_name": "v1.2.0", "name": "Release", "draft": False, "prerelease": False, "assets": []},
        ])
'''
new = '''        release_payload = {"id": 7, "tag_name": "v1.2.0", "name": "Release", "draft": False, "prerelease": False, "assets": []}
        opener = FakeOpener([
            {"full_name": "coferlandia/demo", "default_branch": "main"},
            release_payload,
            [release_payload],
        ])
'''
if old not in text:
    raise SystemExit('test_github_service payload anchor not found')
path.write_text(text.replace(old, new, 1), encoding='utf-8')

path = Path('skills/ops/coferlandia-release-publisher/tests/test_github_service_http.py')
text = path.read_text(encoding='utf-8')
old = '''        opener = FakeOpener([
            {"full_name": "coferlandia/demo", "default_branch": "main"},
            {"tag_name": "v1.2.0", "name": "Release", "draft": False, "prerelease": False, "assets": []},
        ])
'''
new = '''        release_payload = {"id": 7, "tag_name": "v1.2.0", "name": "Release", "draft": False, "prerelease": False, "assets": []}
        opener = FakeOpener([
            {"full_name": "coferlandia/demo", "default_branch": "main"},
            release_payload,
            [release_payload],
        ])
'''
if old not in text:
    raise SystemExit('test_github_service_http payload anchor not found')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
