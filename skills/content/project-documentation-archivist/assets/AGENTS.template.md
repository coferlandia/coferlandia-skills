# AGENTS.md

## Critical Instructions for Agents

- Read this file before modifying the project.
- Review `README.md`, `DECISIONS.md`, and `RUNBOOK.md` before structural or high-risk changes.
- Do not change public contracts, schemas, migrations, integrations, or critical configuration without checking the related documentation first.
- Run confirmed validation commands before considering a change complete.
- Register contradictions, missing confirmations, and open doubts in
  `docs/catalog/OPEN_QUESTIONS.md`.

## Project Essentials

Brief agent-oriented summary of the project. Keep only the information needed to act safely.

### Architecture

- Main architecture pattern:
- Core modules or services:
- Important boundaries:

### Main Conventions

- Naming:
- Folder organization:
- Testing pattern:
- Configuration rule:

### Sensitive Areas

- Public contracts:
- Database or migrations:
- Security or authentication:
- Third-party integrations:

### Validation Commands

- Install:
- Build:
- Test:
- Lint:
- Typecheck:
- Run:
- Other:

If a command is not confirmed, mark it as pending and register the uncertainty in
`docs/catalog/OPEN_QUESTIONS.md`.

## Documentation Index

### Start Here

- `README.md`: general project overview for humans.
- `AGENTS.md`: minimum operational guidance for agents before acting.

### Project Memory

- `HISTORY.md`: verified historical changes.
- `DECISIONS.md`: technical decisions and rationale.
- `TODO.md`: pending work and next actions.

### Operations

- `RUNBOOK.md`: operations, troubleshooting, and routine procedures.

### Unresolved Knowledge

- `docs/catalog/OPEN_QUESTIONS.md`: unresolved questions and contradictions.

### Code Map

- `src/`: application code.
- `tests/`: automated tests.
- `docs/`: extended documentation.
- `scripts/`: automation and maintenance helpers.

### External References

- Add only trusted external references that are confirmed and useful for agents.

## Maintenance Notes

- Keep this file brief, operational, and agent-oriented.
- Add new critical knowledge without deleting existing semantic content.
- Reorganize for clarity before adding length.
- Move deep detail into specific documentation instead of bloating this file.
- Keep links relative and verifiable.
- Register contradictions and missing confirmations in `docs/catalog/OPEN_QUESTIONS.md`.
