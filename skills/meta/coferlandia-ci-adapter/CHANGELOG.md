# Changelog — coferlandia-ci-adapter

## 1.1.0 — 2026-09-12

### Added

- Optional GitHub-native release publication adaptation kept separate from `.coferlandia/ci/profile.json`.
- Deterministic rendering of `.coferlandia/release/policy.json` `publication.github` plus a Chat-compatible `issue_comment` publication workflow that delegates exact Commit -> Release mechanics to `coferlandia-release-publisher`.
- Publication-policy validation, safe repository-relative publisher paths, durable versioned request markers, exact release identity transport, actor authorization, merged-PR checks, and no deployment or LOCAL fallback.

### Compatibility

- Existing repositories using only the CI profile contract remain unchanged; publication adaptation is explicit and opt-in.

## 1.0.0 — 2026-09-07

### Added

- Repository-study workflow that produces one minimal CI profile shared by Chat GitHub-native CI and the generic Local CI skill.
- Deterministic profile validation, secret-field rejection, canonical SHA-256 fingerprinting, drift checking, dry-run and atomic rendering.