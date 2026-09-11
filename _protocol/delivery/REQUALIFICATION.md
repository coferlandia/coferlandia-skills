# Requalification Rules

| Change after evidence | READY_FOR_CI | READY_FOR_MERGE | READY_FOR_RELEASE | Required action |
|---|---|---|---|---|
| Development PR head changes | stale | stale | n/a unless it is also the release candidate | refresh development/review evidence, then rerun selected development Qualification |
| Material correction during development Qualification | replaced | stale | n/a unless release candidate changes | new READY_FOR_CI, then same explicitly selected development Qualification unless authority chooses otherwise |
| Release candidate/source SHA changes | n/a | n/a | stale | rebuild/currentize release manifest and rerun the same explicitly selected release Qualification |
| CI profile fingerprint changes | development-valid | stale | stale | rerun the selected development or release Qualification that owns the affected handoff |
| Relevant workflow/gate contract changes | development-valid | stale | stale | rerun the selected Qualification |
| Authoritative development base changes | retained as historical development evidence | stale by default | n/a unless it changes release authority | reconcile/requalify unless profile proves an alternative effective-candidate rule |
| Release target/base changes | n/a | n/a | stale | reconcile release topology/manifest and rerun release Qualification |
| Release manifest/included-work identity changes | n/a | n/a | stale | rebuild/currentize manifest and rerun release Qualification |
| Current Merge Queue/merge_group becomes authoritative | unchanged | evaluate against current effective candidate | evaluate when repository release policy uses it | require qualification evidence for repository-defined effective candidate |
| Old/cancelled/superseded remote run | unchanged | invalid evidence | invalid GITHUB_NATIVE evidence | obtain current GitHub-native evidence |
| Local result belongs to another SHA | unchanged | invalid evidence | invalid LOCAL evidence | rerun the corresponding LOCAL Qualification |
| Required review state becomes non-green | unchanged until development refresh | stale | stale | resolve review findings and requalify the exact current candidate |

`merge.md` never performs requalification. It returns `REQUALIFICATION_REQUIRED` with the exact invalidating identity/evidence and stops.

`chat-release` and `local-release` also fail closed on stale release evidence. They may reconstruct current release state, but they must not treat a stale `READY_FOR_RELEASE` handoff as integration or publication authority. Product/development corrections create a new release candidate and return through the repository's normal development flow before release Qualification runs again.
