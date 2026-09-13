Strengthen the generic Chat `merge` Integration controller so an already-associated work item is explicitly closed after verified integration into the PR's authoritative target ref, including repositories whose development target is not the default branch (for example `dev`).

Acceptance criteria:
- preserve repository-owned target-ref policy; do not hardcode `dev`;
- after verified merge/integration, explicitly close the associated open Issue/work item instead of relying on GitHub `Closes`/`Fixes`/`Resolves` default-branch semantics;
- if Issue closeout is required but unavailable/fails, do not report COMPLETE;
- preserve optional GitHub Project Done projection separately;
- add prompt regression coverage;
- ship as a compatible patch release and update release metadata.