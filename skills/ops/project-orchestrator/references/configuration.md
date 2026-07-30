# Configuration

Run `init-config` to create `.project-orchestrator/config.json` without overwriting an existing
file, then run `validate-config`.

Configuration schema version 2 covers:

- Epic-scoped Git/worktree behavior;
- role-specific primary/fallback provider, model, and reasoning settings;
- retry and timeout policy;
- deterministic validation commands;
- protocol/evidence retention;
- optional GitHub Project coordinates and logical-to-Project `Status` mapping.

Retired v1 phase fields such as `one_commit_per_phase`, `candidate_commit_strategy: amend`, and
per-phase merge/worktree cleanup are not v2 execution semantics. `load_config` can normalize a v1
file for migration, but new configuration must use v2.

GitHub Project configuration is optional. A representative block is:

```json
{
  "github_project": {
    "owner": "diegocofre",
    "number": 2,
    "status_mapping": {
      "pending": "Todo",
      "in_progress": "In Progress",
      "review": "Review",
      "blocked": "Blocked",
      "done": "Done"
    }
  }
}
```

Project fields are projections only; they never redefine Epic/task contracts. Project mutations
require `gh` authentication with sufficient project scope. Local `--spec` and `--manifest`
execution remain available without GitHub.

Never put credentials in config. Use native provider/GitHub authentication or environment
variables. Providers are probed/resolved at run time; an unavailable provider is a fallback/retry
condition, never a success signal.
