# Release Policy Contract

The policy file is optional. `--policy <path>` has highest priority; otherwise the CLI reads `.coferlandia/release/policy.json` when present. Absence means safe generic defaults and never creates a file.

## Schema v1

```json
{
  "schema_version": 1,
  "versioning": {
    "scheme": "semver",
    "tag_prefix": "v"
  },
  "release_refs": [],
  "tag": {
    "type": "annotated",
    "signing": "optional"
  },
  "validation": {
    "required_github_checks": []
  },
  "github_release": {
    "enabled": true,
    "immutability": "observe"
  },
  "provenance": {
    "manifest": "optional"
  }
}
```

## Semantics

- `versioning.scheme`: generic v1 supports only `semver`.
- `tag_prefix`: commonly `v`; it is separate from the semantic version itself.
- `release_refs`: allowed integration/maintenance refs. Empty means the GitHub repository default branch. A simple branch name is normalized to `refs/heads/<name>`.
- `tag.type`: v1 requires `annotated`.
- `tag.signing`: `disabled`, `optional`, or `required`. `required` uses local Git signing and publication fails if the signing environment cannot create the tag.
- `validation.required_github_checks`: exact check-run names required to be `completed/success` for the target commit. Empty means no generic remote-check requirement is invented.
- `github_release.enabled`: must be true in generic v1.
- `github_release.immutability`: `disabled`, `observe`, or `required`. `required` uses GitHub's repository immutable-releases status endpoint as a publication preflight. `observe` records the setting when permission permits but does not block merely because it is unobservable.
- `provenance.manifest`: `disabled`, `optional`, or `required`. In v1 both `optional` and `required` generate/verify the manifest during publication; `required` expresses repository policy rather than making the manifest the primary authority.

## Local publication skill precedence

This JSON policy configures the generic deterministic engine. It does not replace semantic repository-local skill precedence. The agent first checks whether a repository-local contract explicitly owns final Commit -> published Release. If so, that stronger publication contract owns the operation instead of this generic workflow.

A repository-local release-preparation/versioning gate that stops before tags/GitHub Releases may compose before this publisher; it does not automatically replace it.

## Unsupported or ambiguous schemes

If published GitHub Release history does not conform to the configured SemVer/tag-prefix model, generic v1 fails rather than mixing version schemes. Use a stronger repository-local publication contract for a deliberate legacy scheme/migration.
