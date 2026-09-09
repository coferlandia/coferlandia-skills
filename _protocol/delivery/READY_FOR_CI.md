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
Development validation: <fresh evidence for every applicable required development check>
Review Critical: 0
Review Important: 0
Next stage: Qualification
```

Validity requires all of the following:

- the recorded Candidate SHA equals the current PR head;
- development validation evidence was produced against that exact Candidate SHA;
- every applicable cheap deterministic development check required by repository-owned instructions, scripts, package metadata, CI profile, or executable workflow is fresh and passing;
- no applicable required development check is failing, skipped, unknown, or represented only by an older candidate's evidence;
- focused iteration tests are not used as a substitute for a broader cheap development suite when the repository defines one for the changed surface;
- Implementation is COMPLETE and Review Critical / Review Important are both zero.

A new head invalidates this handoff. Base movement does not retroactively change what was studied, but the selected Qualification strategy must reconcile current base/effective-candidate rules before producing `READY_FOR_MERGE`.

`READY_FOR_CI` proves source-candidate development readiness only. It does not prove that an effective or synthetic merge candidate passes Qualification, and it must never be treated as merge authority.
