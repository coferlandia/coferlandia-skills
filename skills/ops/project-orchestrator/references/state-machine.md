# State machine

States and allowed transitions are centrally defined in
`scripts/project_orchestrator_cli/state.py`. The v2 machine is Epic/task-oriented.

Main path:

```text
INITIALIZED
  -> CONFIG_VALIDATED
  -> CONTRACT_RESOLVED          # initial materialization already completed
  -> EPIC_WORKTREE_CREATING
  -> EPIC_WORKTREE_CREATED
  -> TASK_SELECTED
  -> CODING_RUNNING
  -> CODING_REPORTED
  -> COMPLETION_VERIFYING
  -> CANDIDATE_PREPARING
  -> CANDIDATE_COMMITTED
  -> REVIEW_WORKTREE_CREATING
  -> REVIEW_WORKTREE_CREATED
  -> REVIEW_RUNNING
  -> REVIEW_PASSED
  -> TASK_READY_FOR_MERGE
  -> ... next task ...
  -> HOLISTIC_REVIEW_WORKTREE_CREATING
  -> HOLISTIC_REVIEW_WORKTREE_CREATED
  -> HOLISTIC_REVIEW_RUNNING
  -> EPIC_READY_FOR_INTEGRATION
```

GitHub mode may then move to `PR_OPEN_AWAITING_MERGE_APPROVAL`; final delivery occurs only after an
explicit `integrate` command:

```text
EPIC_READY_FOR_INTEGRATION
  -> PR_OPEN_AWAITING_MERGE_APPROVAL   # GitHub mode
  -> INTEGRATING
  -> INTEGRATED
  -> ARCHIVING
  -> PROJECT_COMPLETED
```

Review changes use `FIXES_REQUIRED -> FIXING -> FIX_COMMIT_PREPARING -> CANDIDATE_COMMITTED`, then
create a fresh detached review worktree. Holistic findings use the corresponding
`HOLISTIC_FIX*` path. Fixes are additive commits; no v2 state implies `git commit --amend`.

Provider waits are durable and return to the recorded semantic state. Blocked/cancelled states
preserve the Epic implementation worktree/evidence by default. Important blockers include invalid
specification/config/authentication, invalid contract identity/linkage during initialization,
Git/base movement, merge conflicts, and no semantic progress. Later contract-body drift is not a
runtime state transition because the local snapshot is frozen before the run begins.

The controller persists state before external/Git side effects where needed so `status`, `resume`,
`retry`, and `integrate` can avoid duplicating completed operations. Invalid transitions are
rejected.
