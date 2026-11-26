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

The `Issue:` identity must be the same controlling work-item identity bound by the source `READY_FOR_CI` and the pull request's repository-defined linkage. Integration must fail closed rather than merge or close a different work item when those identities diverge.

A compatible optional closeout extension may be added when the controlling work item is intentionally not complete at this delivery boundary:

```text
Work-item closeout: CLOSE | KEEP_OPEN
Closeout authority: NONE | <durable reference>
```

The absence of `Work-item closeout` preserves the v1 legacy meaning and is equivalent to `CLOSE`. `CLOSE` is the normal completed-work-item disposition and does not require a separate closeout authority. `KEEP_OPEN` requires a durable authority reference that explicitly applies to the same controlling work item and this delivery boundary. Labels, titles, branch names, milestone names, or inferred parent/umbrella semantics are not closeout authority.

Qualification may transport an explicitly authorized `KEEP_OPEN` disposition but must not invent one. Integration must revalidate the referenced authority immediately before merge. Contradictory, stale, missing, or ambiguous `KEEP_OPEN` authority fails closed before integration.

The handoff is stale if current candidate/profile/effective-base authority no longer matches the recorded qualification.
