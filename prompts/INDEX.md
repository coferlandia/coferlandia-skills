# Coferlandia Chat Prompts

First-class Chat controllers maintained centrally by `coferlandia-skills`.

| Prompt | Stage | Aliases | Terminal state |
|---|---|---|---|
| [`chat-coder`](./chat-coder.md) | Development | `chat coder`, `chat-coder` | `READY_FOR_CI` |
| [`ci`](./ci.md) | Qualification / GitHub-native | `ci`, `gh ci`, `github ci` | `READY_FOR_MERGE` |
| [`merge`](./merge.md) | Integration | `merge` | `COMPLETE` or `REQUALIFICATION_REQUIRED` |

`local ci` intentionally resolves to the public [`local-ci`](../skills/engineering/local-ci/) Agent Skill rather than to `ci.md`.

Composition is exact and left-to-right. Missing stages are never inserted and qualification strategies never fall back to each other automatically. The machine-readable registry is [`registry.json`](./registry.json).
