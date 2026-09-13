# Coferlandia Chat Prompts

First-class Chat controllers maintained centrally by `coferlandia-skills`.

| Prompt | Stage | Aliases | Terminal state |
|---|---|---|---|
| [`chat-coder`](./chat-coder.md) | Development | `chat coder`, `chat-coder` | `READY_FOR_CI` |
| [`ci`](./ci.md) | Qualification / GitHub-native | `ci`, `gh ci`, `github ci` | `READY_FOR_MERGE` |
| [`merge`](./merge.md) | Integration | `merge` | `COMPLETE`, `REQUALIFICATION_REQUIRED`, or `CLOSEOUT_BLOCKED` |
| [`chat-release`](./chat-release.md) | Release / GitHub-native | `chat release`, `chat-release` | `COMPLETE` or resumable release state |
| [`hotfix`](./hotfix.md) | Explicit emergency remediation | `hotfix` | `HOTFIX_COMPLETE`, resumable state, or `HOTFIX_BLOCKED` |

`local ci` intentionally resolves to the public [`local-ci`](../skills/engineering/local-ci/) Agent Skill rather than to `ci.md`. `local release` resolves to the public [`local-release`](../skills/engineering/local-release/) Agent Skill rather than to `chat-release.md`. The invocation surface owns the strategy: explicit Chat `ci` and `chat-release` are `GITHUB_NATIVE`; `local-ci` and `local-release` are `LOCAL`. No separate strategy router is required.

Development Qualification and Release Qualification are separate responsibilities. `READY_FOR_CI`/`READY_FOR_MERGE` belong to a development candidate; `READY_FOR_RELEASE` belongs to one exact release candidate. Formal Commit -> Release publication mechanics remain owned by `coferlandia-release-publisher` and may be composed by a release controller.

Integration closeout is explicit: after `merge` verifies that the qualified candidate reached the repository-approved authoritative target ref, it must verify the associated work item is closed, closing it directly when still open rather than depending on GitHub default-branch closing-keyword semantics. Failure to verify that closeout returns `CLOSEOUT_BLOCKED` instead of `COMPLETE`.

`hotfix` is intentionally a higher-level explicit emergency controller. It accepts an existing Issue or a free-form bug report, creates/reuses the primary work item, classifies `PERMANENT` versus `TEMPORARY_MITIGATION`, requires a permanent-fix follow-up Issue for temporary mitigations, and delegates Development/Qualification/Integration/publication to repository-approved owners. A normal bug report never implicitly selects the hotfix lane.

Composition is exact and left-to-right. Missing stages are never inserted and LOCAL/GITHUB_NATIVE strategies never fall back to each other automatically. Reaching a handoff state alone does not invoke its next controller. The machine-readable registry is [`registry.json`](./registry.json).
