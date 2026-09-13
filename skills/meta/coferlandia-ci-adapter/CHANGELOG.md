# Changelog — coferlandia-ci-adapter

## 1.2.0 — 2026-09-12

### Added

- Adds a separate repository-owned remote Development validation contract at `.coferlandia/development/validation.json`.
- Adds deterministic validation, fingerprinting and materialization of Draft-PR GitHub Actions Development workflows bound to the exact pull-request head SHA.
- Adds repository-owned runner labels, shell, working directory, commands, required services and environment-name declarations for Development validation.
- Adds bounded Chat Coder bootstrap support: when local Development checks cannot execute and no remote Development surface exists, Chat Coder may delegate only the missing Development adaptation to this skill.

### Boundaries

- `.coferlandia/ci/profile.json` remains Qualification-only.
- Remote Development validation is source-candidate evidence only and never emits `READY_FOR_MERGE`, performs Qualification, publishes, deploys or merges.
- Generated workflows do not inject secret values and grant candidate code only `contents: read` GitHub permission.

### Compatibility

- Existing repositories using only the CI profile or release publication adaptation remain compatible, including repository-configurable publication runners introduced in 1.1.1.

## 1.1.1 — 2026-09-12

### Changed

- Makes the GitHub-native publication runner repository-configurable while preserving ubuntu-latest as the compatible default and keeping publication separate from Qualification.

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
