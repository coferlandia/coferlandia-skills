# State machine

States and allowed transitions are centrally defined in `scripts/project_orchestrator_cli/state.py`.
The controller persists before worktree creation, candidate commit/amend, merge, waiting,
or cleanup. Invalid transitions are rejected. Important terminal states include
`PROJECT_COMPLETED`, `CANCELLED`, `BLOCKED_BY_SPECIFICATION`,
`BLOCKED_BY_MERGE_CONFLICT`, and `BLOCKED_BY_NO_PROGRESS`. `status`, `resume`, and
`retry` read this durable state; a restart must not duplicate Git actions.
