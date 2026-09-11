# Coferlandia Delivery Prompt Bootstrap

Resolve short delivery requests through [`registry.json`](./registry.json), then load only the requested controller bodies.

Examples:

```text
aplica chat coder a #123
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

Rules: ordinary composed delivery executes left-to-right; verify each stage's preconditions; do not insert missing stages; do not switch CI strategy automatically; do not add merge unless requested. `local ci` and `local release` are Agent Skills; `chat coder`, `gh ci`/`ci`, `merge`, `chat release`, and `hotfix` are Chat prompts. `hotfix` is an explicit high-level emergency-remediation controller and never activates implicitly from an ordinary bug report.

Qualification surface ownership is deterministic: explicit `ci` selects development `GITHUB_NATIVE`, `local ci` selects development `LOCAL`, `chat release` selects release `GITHUB_NATIVE`, and `local release` selects release `LOCAL`. Reaching `READY_FOR_CI`, `READY_FOR_MERGE`, or `READY_FOR_RELEASE` does not by itself select or invoke another controller.
