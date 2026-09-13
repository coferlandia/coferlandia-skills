from __future__ import annotations

import json
from pathlib import Path

# Detect duplicate release identities even when GitHub's direct tag endpoint succeeds.
gh = Path('skills/ops/coferlandia-release-publisher/scripts/release_publisher/github_service.py')
text = gh.read_text(encoding='utf-8')
old = '''        if data:
            return self._normalize_release(data)
        # GitHub's release-by-tag endpoint omits draft releases. Fall back to the
        # paginated release collection so publication can resume from TAG + DRAFT
        # without creating a duplicate draft or moving the existing tag.
        matches = [release for release in self.list_releases(repository) if release.get("tag") == tag]
        if len(matches) > 1:
            raise ReleaseError(f"multiple GitHub Releases use tag {tag}")
        return matches[0] if matches else None
'''
new = '''        primary = self._normalize_release(data) if data else None
        # The direct endpoint omits drafts. Always inspect the collection as well so
        # recovery fails closed if another release object already uses the same tag.
        matches = [release for release in self.list_releases(repository) if release.get("tag") == tag]
        if primary is not None:
            conflicts = [release for release in matches if release.get("id") != primary.get("id")]
            if conflicts:
                raise ReleaseError(f"multiple GitHub Releases use tag {tag}")
            return primary
        if len(matches) > 1:
            raise ReleaseError(f"multiple GitHub Releases use tag {tag}")
        return matches[0] if matches else None
'''
if old not in text:
    raise SystemExit('release_by_tag hardened anchor not found')
text = text.replace(old, new, 1)
gh.write_text(text, encoding='utf-8')

# Test duplicate identity when the direct endpoint itself succeeds.
test = Path('skills/ops/coferlandia-release-publisher/tests/test_github_service_http.py')
t = test.read_text(encoding='utf-8')
insert = '''
    def test_release_by_tag_rejects_duplicate_when_direct_endpoint_succeeds(self) -> None:
        opener = FakeOpener([
            {"id": 40, "tag_name": "v1.2.0", "name": "Published", "draft": False, "prerelease": False, "assets": []},
            [
                {"id": 40, "tag_name": "v1.2.0", "name": "Published", "draft": False, "prerelease": False, "assets": []},
                {"id": 41, "tag_name": "v1.2.0", "name": "Draft", "draft": True, "prerelease": False, "assets": []},
            ],
        ])
        service = GitHubService(opener=opener, token="")
        with self.assertRaisesRegex(ReleaseError, "multiple GitHub Releases"):
            service.release_by_tag("coferlandia/demo", "v1.2.0")

'''
marker = '    def test_release_by_tag_rejects_ambiguous_draft_collection(self) -> None:\n'
if 'test_release_by_tag_rejects_duplicate_when_direct_endpoint_succeeds' not in t:
    if marker not in t:
        raise SystemExit('duplicate test insertion anchor not found')
    t = t.replace(marker, insert + marker, 1)
test.write_text(t, encoding='utf-8')

# Publisher metadata/version projection.
skill = Path('skills/ops/coferlandia-release-publisher/SKILL.md')
s = skill.read_text(encoding='utf-8')
s = s.replace('version: "1.1.3"', 'version: "1.1.4"', 1)
s = s.replace(
    'draft-resume idempotency, CLI contracts, optional GitHub-native publication transport policy, and configurable runner metadata covered by repository CI tests.',
    'draft-resume idempotency, duplicate release identity rejection, asset digest fallback verification, CLI contracts, optional GitHub-native publication transport policy, and configurable runner metadata covered by repository CI tests.',
    1,
)
skill.write_text(s, encoding='utf-8')

changelog = Path('skills/ops/coferlandia-release-publisher/CHANGELOG.md')
c = changelog.read_text(encoding='utf-8')
section = '''## 1.1.4 — 2026-09-13

### Fixed

- Fails closed when more than one GitHub Release object resolves to the same tag, including the case where the direct release-by-tag endpoint returns a published release while the collection also contains a conflicting draft.
- Verifies release asset and provenance digests by downloading asset bytes when GitHub omits digest metadata, avoiding dependence on a specific REST response shape.

### Compatibility

- Exact tag, commit, title, notes, prerelease and provenance identity semantics are unchanged. Matching partial releases remain idempotently resumable.

'''
if '## 1.1.4 — 2026-09-13' not in c:
    c = c.replace('# Changelog — coferlandia-release-publisher\n\n', '# Changelog — coferlandia-release-publisher\n\n' + section, 1)
changelog.write_text(c, encoding='utf-8')

# Tighten adapter changelog wording to match the actual authorization rule.
adapter_changelog = Path('skills/meta/coferlandia-ci-adapter/CHANGELOG.md')
a = adapter_changelog.read_text(encoding='utf-8')
a = a.replace(
    '- Adds an authorized text-only retry command for GitHub-native publication recovery. Retry resolves the latest prior immutable publication request from the same PR and replays it through the normal publisher path.',
    '- Adds an authorized text-only retry command for GitHub-native publication recovery. Retry resolves the latest prior syntactically valid request authored by a current repository admin/maintainer on the same PR and replays it through the normal publisher path.',
    1,
)
a = a.replace(
    '- Retry comments cannot supply or override release payload fields; actor authorization, merged-PR binding, exact target SHA validation, isolated control-plane execution and fail-closed publisher semantics remain unchanged.',
    '- Retry comments cannot supply or override release payload fields; both the retry actor and the replayed request author must have release authority, malformed/unauthorized candidate requests are skipped, and merged-PR binding, exact target SHA validation, isolated control-plane execution and fail-closed publisher semantics remain unchanged.',
    1,
)
adapter_changelog.write_text(a, encoding='utf-8')

# Release notes must describe both changed skills.
notes = Path('RELEASE-NOTES.md')
n = notes.read_text(encoding='utf-8')
row = '| coferlandia-release-publisher | 1.1.3 | 1.1.4 | Hardens partial-release recovery with duplicate release-identity rejection and digest verification fallback by downloaded asset bytes. |\n'
anchor = '| coferlandia-ci-adapter | 1.3.0 | 1.3.1 | Adds safe replay of the latest prior immutable publication request through a text-only authorized retry command. |\n'
if row not in n:
    if anchor not in n:
        raise SystemExit('release notes row anchor not found')
    n = n.replace(anchor, anchor + row, 1)
n = n.replace(
    '- Existing publication requests and policies remain valid. Retry is additive and never accepts release identity overrides.',
    '- Existing publication requests and policies remain valid. Retry is additive, accepts no release identity overrides, replays only prior authorized valid requests, and the publisher remains fail-closed on ambiguous release identity.',
    1,
)
notes.write_text(n, encoding='utf-8')

# Ensure plugin projection remains the intended patch version.
plugin = Path('.claude-plugin/plugin.json')
data = json.loads(plugin.read_text(encoding='utf-8'))
if data.get('version') != '2.11.1':
    raise SystemExit(f"unexpected plugin version: {data.get('version')}")
