# Coferlandia Chat Prompt Specification

`prompts/` is a first-class repository surface distinct from Agent Skills. Prompt files use simple YAML frontmatter:

```yaml
---
name: chat-coder
description: "What this Chat controller does and when to load it."
version: "1.0.0"
stage: development | qualification | integration | release | hotfix
status: active | deprecated
---
```

Rules:

- `name` matches the filename without `.md` and its registry `id`.
- `version` is `MAJOR.MINOR.PATCH` for this prompt family.
- `stage` is exactly one delivery responsibility.
- `release` is reserved for controllers that own a release-candidate lifecycle; it is distinct from ordinary candidate Integration and from Commit -> Release publication helpers.
- `hotfix` is reserved for explicitly invoked emergency-remediation orchestration. It may compose repository-approved Development, Qualification, Integration and publication surfaces, but it must preserve their authority boundaries and must not infer exceptional-lane authority from an ordinary bug report.
- `description` is discovery text, not the full workflow.
- `prompts/registry.json` owns aliases and composition semantics.
- Prompt bodies may reference shared `_protocol/delivery/` contracts instead of duplicating schemas.
- Repository-specific CI commands/workflow names belong in `.coferlandia/ci/profile.json` or equivalent repository-owned policy, not generic prompts.
- Prompt changes are validated by `_protocol/scripts/validate_prompt.py` and described in repository release notes.

## Distribution V1

The prompt family is repository-addressable. It is **not** an Agent Skill and is intentionally not copied into the `.plugin` package in V1. Chat environments load `prompts/BOOTSTRAP.md`/`registry.json` from the repository source. This distribution boundary may evolve independently without collapsing Prompt and Skill semantics.
