# Agent protocol

Every attempt stores `request.json`, `instructions.md`, `agent-result.json`,
`agent-report.md`, events, stdout, stderr, and execution evidence beneath the run.
JSON is authoritative and includes protocol version, run/phase/attempt IDs, role,
provider, model, worktree, base/candidate SHA, status, requirements, changed files,
tests, documentation, remaining work, findings, blockers, deviations, commit-message
suggestion, and evidence links. Markdown is human-readable only; never request
chain-of-thought. Validate results with `validate-result` before a state transition.
