# Changelog — coferlandia-release-publisher

## 1.1.2 — 2026-09-12

### Fixed

- Replaces the publisher runtime dependency on GitHub CLI with Python standard-library GitHub REST transport using `GITHUB_TOKEN` or `GH_TOKEN`.
- Preserves annotated-tag, draft Release, asset verification, publication, and fail-closed semantics.

## 1.1.1 — 2026-09-12

### Changed

- Accepts and validates repository publication runner metadata without changing exact Commit-to-Release semantics.

## 1.1 — 2026-09-12

### Added

- Optional validation for repository-declared `publication.github` transport metadata (`issue-comment`, `workflow-dispatch`, or `none`) while preserving repository-owned sibling publication fields.
- Explicit non-interactive GitHub Actions compatibility so a repository workflow can transport already-resolved release identity into the deterministic publisher without duplicating tag/Release mechanics.

### Compatibility

- Existing release policies remain compatible when `publication.github` is absent.
- Commit -> annotated tag -> draft GitHub Release -> verification -> publication semantics are unchanged.

## 1.0 — 2026-09-05

### Added

- Adds a generic Commit -> Release workflow backed by a deterministic JSON CLI for SemVer planning, exact annotated-tag identity, GitHub Release publication, idempotent recovery, optional artifacts/provenance, consistency verification, and machine-readable release resolution without deployment coupling.
