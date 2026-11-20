# Changelog — coferlandia-deploy

## 1.0 — 2026-11-20

### Added

- Defines a generic immutable-release deployment boundary over a repository-declared deployment authority.
- Requires exact expected-SHA verification, fail-closed authority resolution and machine-readable terminal deployment evidence.
- Treats an already HEALTHY exact application/release/SHA identity as idempotent no-op success.
- Supports HOTFIX production stabilization without duplicating provider execution states or release-publication behavior.
