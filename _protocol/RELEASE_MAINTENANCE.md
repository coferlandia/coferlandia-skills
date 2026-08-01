# Release Maintenance

This is the canonical repository policy for synchronizing public skill versions, plugin releases,
documentation, manifests, and package output.

## Two version axes

1. A public skill's `metadata.version` identifies the current behavioral contract of that skill.
2. `.claude-plugin/plugin.json` identifies one installable repository/plugin release.

A shipped public skill behavior change updates both axes: the skill version and one repository/plugin
release. A repository-local `.agents/**` change alone does not.

## Canonical artifacts

- `skills/<category>/<name>/SKILL.md`: current skill version and behavior.
- `skills/<category>/<name>/CHANGELOG.md`: history of that skill.
- `.claude-plugin/plugin.json`: current plugin release version.
- `RELEASE-NOTES.md`: repository release history.
- README managed block: concise latest-release projection.
- `skills/INDEX.md`: inventory and discovery only.

## Final-delivery gate

The gate applies before the final implementation/release commit, PR readiness, integration, or
package publication. It does not require every intermediate checkpoint commit to be release-ready.

Release-ready state requires:

- changed public skill behavior has an explicit version bump and changelog entry;
- the latest release-note section matches the plugin version;
- affected skills appear in the release table with their current versions;
- README's generated summary matches the latest release;
- `Unreleased` contains no undisclosed shipped work;
- skill validation, version check/audit, release-maintainer checks, and relevant tests pass;
- the verified plugin package contains shipped files and excludes local/private artifacts.

## Per-skill changelog format

```md
# Changelog — skill-name

## 1.2.0 — YYYY-MM-DD

### Changed

- Externally meaningful behavior change.
```

Use only applicable Added/Changed/Fixed/Deprecated/Removed/Security subsections. Newest first. The
top version must equal `SKILL.md` `metadata.version`.

## Repository release format

```md
## vX.Y.Z (YYYY-MM-DD)

### Skills

| Skill | Previous | Current | Summary |
|---|---:|---:|---|
```

Optional sections cover repository/protocol, plugin/packaging, and migration/compatibility.

## Enforcement

The repository-local `.agents/skills/coferlandia-release-maintainer/` skill owns semantic
classification and coordinates `_protocol/scripts/validate_skill.py`,
`_protocol/scripts/bump_version.py`, its deterministic CLI, CI, and package verification.
