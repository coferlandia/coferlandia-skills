# Architecture

`project-orchestrator-cli.py` is the sole public interface. The deterministic controller owns
source resolution/materialization, durable state transitions, Git, worktrees, commits, provider
retries, GitHub synchronization, final integration, archival, and cleanup. Models provide semantic
coding/completion/review/fix results only; they never own controller state or Git authority.

## Source boundary

The controller normalizes exactly one source into a v2 execution manifest:

- `--spec`: local direct plan -> one `DIRECT-PLAN` unit;
- `--epic`: GitHub Epic -> local materialized Epic/tasks;
- `--manifest`: local v2 manifest/task DAG.

GitHub-backed active contracts remain authoritative in GitHub. `materialization.py` projects them to
`.agent/work-items/` for workers and verifies source hashes/revisions before assignment. Workers do
not need GitHub access.

## Execution boundary

One Epic branch/worktree carries all execution units. Task dependencies are validated as a DAG and
executed serially. Candidate and review-fix commits are additive. Review always occurs from a
detached worktree at an immutable SHA. Passing a task marks it `ready_for_merge`; no task is merged
to `main` independently.

After all tasks pass, one holistic Epic review approves the final branch HEAD. GitHub mode then
opens one final PR; local fallback retains an equivalent explicit integration gate. `integrate`
is the only final delivery action.

## Components

- `work_items.py`: v2 manifest, Execution Strategy parsing, DAG validation/order.
- `materialization.py`: GitHub/local contract projection, hashing, freshness, archive paths.
- `github_service.py`: structured `gh` reads/writes for Issues, Projects, and PRs.
- `GitService`: argument-array Git operations and controlled staging.
- `RunStore`: atomic durable state/events and run locking.
- provider adapters: model/CLI execution boundary.
- `integration.py`: final traceability, PR/integration, archive, and cleanup.

Run state lives at `<git-common-dir>/project-orchestrator/runs/<run-id>/`; writes are atomic and
events are append-only. Execution adapters must use argument arrays, UTF-8, timeouts, redaction,
and never `shell=True`.
