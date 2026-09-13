# Coferlandia Delivery Prompt Bootstrap

Resolve short delivery requests through [`registry.json`](./registry.json), then load the resolved controller bodies.

A standalone alias may declare a default controller sequence in the registry. Explicit `+` composition always overrides that standalone default and executes exactly as written.

Examples:

```text
aplica chat coder a #123
aplica chat dev a #123
aplica gh ci a #123
aplica local ci a #123
aplica merge a #123
aplica chat coder + gh ci + merge a #123
aplica chat coder + local ci + merge a #123
aplica chat release
aplica local release
hotfix #123
hotfix: <free-form bug report>
```

Rules: standalone `chat coder` / `chat-coder` resolves by default to `chat-coder -> ci (GITHUB_NATIVE) -> merge`; `chat dev` / `chat-dev` resolves only the Development controller and stops at `READY_FOR_CI`. Explicit controller compositions execute left-to-right without applying standalone defaults, inserting missing stages, or changing Qualification strategy. Do not switch CI strategy automatically. `local ci` and `local release` are Agent Skills; `chat-coder`, `gh ci`/`ci`, `merge`, `chat-release`, and `hotfix` are Chat prompts. `hotfix` is an explicit high-level emergency-remediation controller and never activates implicitly from an ordinary bug report.

For the standalone Chat Coder default, `READY_FOR_CI` and `READY_FOR_MERGE` are internal durable handoffs rather than user-facing stop points. Continue through the resolved sequence without asking for confirmation. Return `COMPLETE` after verified Integration, `WAITING_CI` only when authoritative GitHub Actions remain non-terminal beyond the active execution, or a precise blocked state with the exact stage and reason. Never report success while a required GitHub gate is pending, stale, skipped, cancelled, or red.

Normalize the final user-facing status for standalone Chat Coder so the user never has to infer where the workflow stopped. Preserve the underlying controller state as evidence:

```text
Chat Coder = COMPLETE
Issue = <identity> / closed
PR = <number> / merged
Merge SHA = <sha>
```

or, when external CI is still authoritative but non-terminal:

```text
Chat Coder = WAITING_CI
Stage = Qualification
Issue = <identity>
PR = <number>
Candidate SHA = <sha>
Run/check = <authoritative identifier>
Current status = <non-terminal status>
Next action = resume the same Chat Coder request; do not require a different controller command
```

or, for any condition that prevents safe continuation:

```text
Chat Coder = BLOCKED
Stage = Development | Qualification | Integration
Controller state = <exact underlying state>
Issue = <identity>
PR = <number or NONE>
Candidate SHA = <sha or NONE>
Reason = <specific blocker>
Next action = <specific action required>
```

Qualification surface ownership remains deterministic: resolved `ci` selects development `GITHUB_NATIVE`, `local ci` selects development `LOCAL`, `chat release` selects release `GITHUB_NATIVE`, and `local release` selects release `LOCAL`. Reaching `READY_FOR_CI`, `READY_FOR_MERGE`, or `READY_FOR_RELEASE` by itself does not select or invoke another controller.
