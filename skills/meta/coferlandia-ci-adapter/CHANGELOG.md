# Changelog — coferlandia-ci-adapter

## 1.1.1 — 2026-09-12

### Fixed

- Publication workflows no longer assume `ubuntu-latest` is available for every repository.
- Added explicit repository-specific `publication.github.runs_on` validation and deterministic workflow rendering, including self-hosted multi-label runners.
- `publication render` now accepts `--runs-on <label> [<label> ...]` and preserves existing runner policy when the flag is omitted.

### Compatibility

- Existing publication policies without `runs_on` remain valid and continue to default to `ubuntu-latest`.
- `.coferlandia/ci/profile.json` remains Qualification-only; publication runner selection is not inferred from CI profile state.

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
