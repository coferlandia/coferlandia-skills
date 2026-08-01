# Release Model

## Canonical ownership

| Information | Owner |
|---|---|
| Current behavior of one public skill | that skill's shipped files |
| Current skill version | `SKILL.md` `metadata.version` |
| Skill version history | that skill's `CHANGELOG.md` |
| Current plugin release version | declared plugin manifest field(s) |
| Repository release history | `RELEASE-NOTES.md` |
| Latest human summary | generated README managed block |
| Inventory/category/status/discovery summary | `skills/INDEX.md` |
| Release policy | `_protocol/RELEASE_MAINTENANCE.md` |
| Semantic decisions | this repository-local skill |
| Mechanical checks/render/package | release-maintainer CLI |

## Shipped versus local

Shipped by the plugin:

- `.claude-plugin/**`
- `skills/**`
- `_protocol/**`
- `README.md`, `AGENTS.md`, `SKILLS-GUIDE.md`, `RELEASE-NOTES.md`, `LICENSE`

Repository-local only:

- `.agents/**`
- `.agent/**`
- `.git/**`, worktrees, caches, temporary plans, generated packages

A local-only change does not require a plugin release by itself. Any changed public skill behavior or
other shipped contract does.

## Final-delivery boundary

Intermediate implementation commits may precede release preparation. The final branch state must be
self-consistent and pass the gate before PR readiness or integration. One repository release may
aggregate multiple skill changes; select the highest material impact.
