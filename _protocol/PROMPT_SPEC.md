# Coferlandia Chat Prompt Specification

`prompts/` is a first-class repository surface distinct from Agent Skills. Prompt files use simple YAML frontmatter:

```yaml
---
name: chat-coder
description: "What this Chat controller does and when to load it."
version: "1.0.0"
stage: development | qualification | integration
status: active | deprecated
---
```

Rules:

- `name` matches the filename without `.md` and its registry `id`.
- `version` is SemVer-like `MAJOR.MINOR.PATCH` for this prompt family.
- `stage` is exactly one delivery responsibility.
- `description` is discovery text, not the full workflow.
- `prompts/registry.json` owns aliases and composition semantics.
- Prompt bodies may reference shared `_protocol/delivery/` contracts instead of duplicating schemas.
- Repository-specific CI commands/workflow names belong in `.coferlandia/ci/profile.json`, not generic prompts.
- Prompt changes are validated by `_protocol/scripts/validate_prompt.py`.
