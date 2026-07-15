---
name: project-orchestrator
description: >
  Use ONLY when the user explicitly requests project-orchestrator or explicitly asks
  to execute an approved development specification through the project orchestrator.
  Do not activate for a specification, implementation plan, feature, bug fix, review,
  phase execution, or generic mention of project management or orchestration.
license: Apache-2.0
compatibility: Requires Python 3.11+, Git with worktree support, and configured Codex and/or OpenCode CLIs in the target repository.
metadata:
  author: coferlandia
  version: "1.1"
  category: ops
  status: active
  tested: "2026-07-14 - unittest smoke/integration tests, fake-provider lifecycle, schema validation, and compileall."
---

## Context

This is explicit-invocation-only, deterministic control for an approved `.md` or
`.txt` development specification. It owns Git, worktrees, commits, state, retries,
and reports; models provide only semantic analysis, coding, verification, review, and
fixing. Reuse `software-development` roles rather than duplicating them.

## Steps

1. Read the complete approved specification. If a material ambiguity needs external
   authority, stop with `BLOCKED_BY_SPECIFICATION`; do not redesign scope.
2. From the target repository, run `python {skill}/scripts/project-orchestrator-cli.py doctor --json`, then `init-config` if needed and `validate-config`.
3. Run `run --spec <path> --dry-run --json`; inspect manifest, branches, worktrees,
   lifecycle, and provider resolution before a mutating run.
4. Start with `run --spec <path> --json`. Use `status`, `resume`, `retry`, `cancel`,
   and ownership-safe `cleanup` only through the same CLI.
5. Report the generated Markdown and JSON state. A blocked or cancelled run preserves
   implementation worktrees, candidate commits, and evidence by default.

## Onboarding dependencies

Install or expose these tools before a real run:

- Python 3.11+ and Git with `worktree` support.
- Codex CLI, authenticated with `codex login status`; headless servers use
  `CODEX_HOME` and `codex login --device-auth`. Keep `CODEX_HOME` outside the
  repository when possible.
- OpenCode CLI 1.18+ for fallback execution; verify with `opencode --version` and
  `opencode models`.
- The configured Codex model IDs are `gpt-5.4-mini` for normal roles and
  `gpt-5.6-luna` for the reviewer. The configured OpenCode fallback is
  `opencode/big-pickle` (OpenCode requires the `provider/model` form).

Run `doctor --json` after onboarding. It must report the executable, version,
authentication state when detectable, and configured model resolution before starting
an execution.

The controller assigns one implementation worktree per phase and a detached immutable
review worktree per candidate. Coding and fix agents must use the assigned
implementation worktree; reviewers must use the assigned detached worktree. Only the
controller may perform Git lifecycle operations. It commits only after completion
checks, amends after validated fixes, and merges only the exact reviewed approved SHA.

## Gotchas

- **Accidental activation:** a plan alone is not an invocation. Require the explicit
  `project-orchestrator` request.
- **Approval drift:** any post-review change invalidates approval. Create a new
  candidate and a fresh detached review; never merge a stale approval.
- **Provider outage:** persist and use the configured five-minute recovery loop; do
  not convert temporary quota or capacity failures into a semantic blocker.

## Expected Output

```text
Run: {run-id}
State: {state}
Phase: {phase-id}
Candidate / approved SHA: {sha | none}
Worktrees: implementation={path}; review={path | none}
Next action or blocker: {detail}
Reports: {run-state directory}
```

## Output Location

Runtime artifacts go under the target Git common directory at
`project-orchestrator/runs/{run-id}/`; this is an operational exception to the
repository artifact convention. See `_protocol/ARTIFACT_OUTPUT_CONVENTIONS.md`.

## Scripts Available

- **`scripts/project-orchestrator-cli.py`** - the only public tool interface. Run
  `python scripts/project-orchestrator-cli.py --help` for the command surface.

## References

- Read `references/architecture.md` when designing or auditing controller boundaries.
- Read `references/configuration.md` when configuring roles, models, or providers.
- Read `references/agent-protocol.md` before producing or validating agent results.
- Read `references/state-machine.md` when resuming, retrying, or diagnosing a run.
- Read `references/candidate-commit-lifecycle.md` before reviewing, amending, or merging.
- Read `references/failure-classification.md` or `references/recovery.md` for failures.
- Read `references/troubleshooting.md` when CLI validation or Git safety checks fail.
