# READY_FOR_CI v1

Default durable marker:

```html
<!-- coferlandia-ready-for-ci:v1 -->
```

Required fields:

```text
State: READY_FOR_CI
Schema: 1
Issue: <repository-scoped identity>
PR: <number>
Branch: <branch>
Candidate SHA: <exact PR head>
Base SHA studied: <exact authoritative base studied during development>
Implementation: COMPLETE
Development validation: <fresh evidence summary>
Review Critical: 0
Review Important: 0
Next stage: Qualification
```

Validity requires the recorded Candidate SHA to equal the current PR head. A new head invalidates this handoff. Base movement does not retroactively change what was studied, but the selected Qualification strategy must reconcile current base/effective-candidate rules before producing `READY_FOR_MERGE`.
