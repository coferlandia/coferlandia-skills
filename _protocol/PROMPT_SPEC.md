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
- `prompts/registry.json` owns aliases, explicit composition semantics, and any declared standalone alias default sequence.
- A `composition.standalone_defaults` entry applies only when its source alias is the complete controlling expression. Its sequence must start with the same controller as the source alias and every referenced alias must exist.
- Explicit `+` composition always suppresses standalone default expansion and executes exactly left-to-right as written.
- A declared standalone default is alias-resolution semantics, not permission for one stage to absorb another stage's authority and not inference from `READY_*` handoff state.
- `implicit_stages: false` therefore prohibits undeclared/inferred stage insertion; it does not prohibit a validated standalone sequence explicitly declared in the registry before execution begins.
- `automatic_fallback: false` applies to standalone defaults as well: a resolved GITHUB_NATIVE sequence never silently falls back to LOCAL, and vice versa.
- Prompt bodies may reference shared `_protocol/delivery/` contracts instead of duplicating schemas.
- Repository-specific CI commands/workflow names belong in `.coferlandia/ci/profile.json` or equivalent repository-owned policy, not generic prompts.
- Prompt changes are validated by `_protocol/scripts/validate_prompt.py` and described in repository release notes.

## Distribution

The public prompt family ships with the Coferlandia plugin/package alongside public Agent Skills while remaining a semantically distinct artifact family. Repository vendoring or installation flows may materialize the catalog under a consumer prompt location such as `.agents/prompts/`.

Chat environments should load `prompts/BOOTSTRAP.md` and `prompts/registry.json` from the installed, vendored, or repository-addressable source, then load only the controller bodies selected by the resolved sequence.
