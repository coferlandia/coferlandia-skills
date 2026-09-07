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
```

Rules: execute left-to-right; verify each stage's preconditions; do not insert missing stages; do not switch CI strategy automatically; do not add merge unless requested. `local ci` is an Agent Skill, while `chat coder`, `gh ci`/`ci`, and `merge` are Chat prompts.
