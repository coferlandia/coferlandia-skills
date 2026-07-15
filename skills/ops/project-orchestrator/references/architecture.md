# Architecture

`project-orchestrator-cli.py` is the sole public interface. Its deterministic
controller owns state transitions, Git, worktrees, commits, tests, retries, and
cleanup. `GitService`, `RunStore`, and provider adapters are dependency boundaries;
provider-specific logic must not enter the controller. Models receive structured
requests and return JSON plus Markdown evidence, never authority over controller state.

Run state lives at `<git-common-dir>/project-orchestrator/runs/<run-id>/`; writes are
atomic and events are append-only. Future execution adapters must use argument arrays,
UTF-8, timeouts, redaction, and no `shell=True`.
