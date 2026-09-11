# Coferlandia Chat Prompts

First-class Chat controllers maintained centrally by `coferlandia-skills`.

| Prompt | Stage | Aliases | Terminal state |
|---|---|---|---|
| [`chat-coder`](./chat-coder.md) | Development | `chat coder`, `chat-coder` | `READY_FOR_CI` |
| [`ci`](./ci.md) | Qualification / GitHub-native | `ci`, `gh ci`, `github ci` | `READY_FOR_MERGE` |
| [`merge`](./merge.md) | Integration | `merge` | `COMPLETE` or `REQUALIFICATION_REQUIRED` |
| [`chat-release`](./chat-release.md) | Release / GitHub-native | `chat release`, `chat-release` | `COMPLETE` or resumable release state |

`local ci` intentionally resolves to the public [`local-ci`](../skills/engineering/local-ci/) Agent Skill rather than to `ci.md`. `local release` resolves to the public [`local-release`](../skills/engineering/local-release/) Agent Skill rather than to `chat-release.md`. The invocation surface owns the strategy: explicit Chat `ci` and `chat-release` are `GITHUB_NATIVE`; `local-ci` and `local-release` are `LOCAL`. No separate strategy router is required.

Development Qualification and Release Qualification are separate responsibilities. `READY_FOR_CI`/`READY_FOR_MERGE` belong to a development candidate; `READY_FOR_RELEASE` belongs to one exact release candidate. Formal Commit -> Release publication mechanics remain owned by `coferlandia-release-publisher` and may be composed by a release controller.

Composition is exact and left-to-right. Missing stages are never inserted and LOCAL/GITHUB_NATIVE strategies never fall back to each other automatically. Reaching a handoff state alone does not invoke its next controller. The machine-readable registry is [`registry.json`](./registry.json).
