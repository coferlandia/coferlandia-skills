# READY_FOR_MERGE v1

Default durable marker:

```html
<!-- coferlandia-ready-for-merge:v1 -->
```

Required fields:

```text
State: READY_FOR_MERGE
Schema: 1
Issue: <repository-scoped identity>
PR: <number>
Candidate SHA: <exact PR head>
Qualified base SHA: <authoritative base used by qualification>
Effective candidate: <PR head or repository-defined synthetic candidate>
Qualification strategy: LOCAL | GITHUB_NATIVE
CI profile fingerprint: <sha256>
Qualification evidence: <strategy-specific durable evidence>
Review Critical: 0
Review Important: 0
Next stage: Merge
```

Both strategies emit the same identity envelope. Only `Qualification evidence` is strategy-specific. LOCAL evidence names executed commands/results for the exact candidate; GITHUB_NATIVE evidence names workflow/check/run identities and conclusions.

The handoff is stale if current candidate/profile/effective-base authority no longer matches the recorded qualification.
