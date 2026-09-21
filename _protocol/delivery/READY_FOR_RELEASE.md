# READY_FOR_RELEASE v1

Default durable marker:

```html
<!-- coferlandia-ready-for-release:v1 -->
```

Required fields:

```text
State: READY_FOR_RELEASE
Schema: 1
Source ref: <release source ref>
Target ref: <release target ref>
Release candidate SHA: <exact candidate SHA>
Qualified base SHA: <authoritative target/base SHA used by qualification>
Effective candidate: <release candidate or repository-defined synthetic candidate>
Qualification strategy: LOCAL | GITHUB_NATIVE
CI profile fingerprint: <sha256>
Qualification evidence: <strategy-specific durable evidence>
Included work: <durable release manifest/reference>
Review Critical: 0
Review Important: 0
Next stage: Release integration
```

When repository policy materializes/freezes a candidate independently of the mutable source ref, also record these repository-declared identity extensions:

```text
Source snapshot SHA: <exact source SHA selected at candidate initialization>
Candidate ref: <stable candidate ref/work-surface head>
```

For live-source mode, `Source ref` itself remains candidate authority and those extension fields may be omitted or `Candidate ref` may be recorded as `NONE`.

`READY_FOR_RELEASE` proves that one exact release candidate is qualified for integration into its declared target ref. It is not publication authority by itself and does not create a tag, GitHub Release, deployment, or production mutation.

Both qualification strategies emit the same identity envelope. Only `Qualification evidence` is strategy-specific: LOCAL names the repository-declared commands/results; GITHUB_NATIVE names the authoritative workflow/check/run identities and conclusions.

The handoff is stale when the exact release candidate SHA/ref, qualified base/target authority, CI profile fingerprint, effective candidate, release manifest, required work-surface identity, or required review state no longer matches authoritative repository state.

For a repository-declared materialized/frozen candidate, later advancement of the original source ref alone does **not** stale the handoff while the source snapshot, candidate ref/SHA, target/base, manifest, profile/gates and review remain unchanged. For live-source mode, source-head movement changes candidate identity and therefore stales the handoff.

A stale handoff must never authorize integration or publication.
