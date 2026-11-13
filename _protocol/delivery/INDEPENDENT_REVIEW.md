# Independent Review Contract

Independent Chat reviews use this durable marker:

```html
<!-- independent-review:v1 -->
```

A review is bound to one exact target delta and must record:

```text
Target: PR #NNN | branch <name>
Head reviewed: <sha>
Base reviewed: <ref>@<sha>
Critical: <count>
Important: <count>
Minor: <count>
Completeness: COMPLETE | INCOMPLETE
Ready: YES | NO

Findings:

- <concrete finding with file/line when applicable>
```

Semantics:

- `Critical` and `Important` are blocking severities.
- `Minor` is non-blocking.
- `Completeness: COMPLETE` means the declared target scope is fully satisfied by the reviewed delta and available evidence.
- `Ready: YES` requires Critical = 0, Important = 0, complete scope, and no contradiction with the current authoritative contract.
- Missing evidence required to establish completeness produces `INCOMPLETE` and `Ready: NO`.
- A head or base identity change makes the prior verdict stale for the new delta.
- Published reviews are evidence only; they do not grant Git, Qualification, Integration, release, or deployment authority.
