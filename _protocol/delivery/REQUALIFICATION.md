# Requalification Rules

| Change after evidence | READY_FOR_CI | READY_FOR_MERGE | Required action |
|---|---|---|---|
| PR head changes | stale | stale | refresh development/review evidence, then rerun selected Qualification |
| Material correction during Qualification | replaced | stale | new READY_FOR_CI, then same explicitly selected Qualification unless authority chooses otherwise |
| CI profile fingerprint changes | development-valid | stale | rerun selected Qualification |
| Relevant workflow/gate contract changes | development-valid | stale | rerun selected Qualification |
| Authoritative base changes | retained as historical development evidence | stale by default | reconcile/requalify unless profile proves an alternative effective-candidate rule |
| Current Merge Queue/merge_group becomes authoritative | unchanged | evaluate against current effective candidate | require qualification evidence for repository-defined effective candidate |
| Old/cancelled/superseded remote run | unchanged | invalid evidence | obtain current GitHub-native evidence |
| Local result belongs to another SHA | unchanged | invalid evidence | rerun Local CI |

`merge.md` never performs requalification. It returns `REQUALIFICATION_REQUIRED` with the exact invalidating identity/evidence and stops.
