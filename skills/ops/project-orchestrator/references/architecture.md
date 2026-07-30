# Architecture

`project-orchestrator-cli.py` is the sole public interface. The deterministic controller owns
source resolution, one-time contract-store initialization, durable state transitions, Git,
worktrees, commits, provider retries, GitHub operational traceability, final integration, archival,
and cleanup. Models provide semantic coding/completion/review/fix results only; they never own
controller state or Git authority.

## Source boundary

The controller normalizes exactly one source into a v2 execution manifest:

- `--spec`: local direct plan -> one `DIRECT-PLAN` unit;
- `--epic`: GitHub Epic -> one frozen local Epic/analysis/task snapshot;
- `--manifest`: local v2 manifest/task DAG, optionally published once when Tracking is GitHub.

Before a run creates its Epic worktree, Initial Contract Materialization ensures the missing GitHub
or filesystem counterpart exists. GitHub-only contracts produce `EPIC.md`, canonical `ANALYSIS.md`
when applicable, `manifest.json`, and task files. Local GitHub-tracked contracts produce marked,
retry-safe Epic/task Issues and one marked canonical analysis comment. Existing dual
representations are checked only for identity and parent linkage.

After this boundary, workers use the frozen local snapshot. Contract bodies are not re-fetched,
compared, refreshed, merged, or propagated automatically. Operational Issue comments, Project
fields, commit references, PR creation, closure, and archival continue independently.

## Execution boundary

One Epic branch/worktree carries all execution units. Task dependencies are validated as a DAG and
executed serially. Candidate and review-fix commits are additive. Review always occurs from a
detached worktree at an immutable SHA. Passing a task marks it `ready_for_merge`; no task is merged
to `main` independently.

After all tasks pass, one holistic Epic review approves the final branch HEAD. GitHub mode then
opens one final PR; local fallback retains an equivalent explicit integration gate. `integrate`
is the only final delivery action.

## Components

- `work_items.py`: v2 manifest, tracking/origin metadata, Execution Strategy parsing, DAG validation/order.
- `contract_initialization.py`: one-time local-to-GitHub initialization, identity recovery, and dry-run preflight.
- `materialization.py`: one-time GitHub-to-local snapshots, canonical analysis extraction, passive provenance, archive paths.
- `github_service.py`: structured `gh` reads/writes for Issues, Projects, and PRs.
- `GitService`: argument-array Git operations and controlled staging.
- `RunStore`: atomic durable state/events and run locking.
- provider adapters: model/CLI execution boundary.
- `integration.py`: final traceability, PR/integration, archive, and cleanup.

Run state lives at `<git-common-dir>/project-orchestrator/runs/<run-id>/`; writes are atomic and
events are append-only. Execution adapters must use argument arrays, UTF-8, timeouts, redaction,
and never `shell=True`.
