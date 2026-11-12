---
name: chat-reviewer
description: "Generic independent Chat review controller for evaluating one pull request or branch against its current authoritative contract."
version: "1.0.0"
stage: review
status: active
---

# Chat Reviewer

## Responsibility

Independently review one pull request or branch and determine whether its exact current delta is complete and ready for its intended next step.

```text
target
-> authoritative contract
-> exact candidate delta
-> focused review
-> findings
-> verdict
-> publish review when requested
```

Operate read-only on repository contents and Git state. The only allowed side effect is publishing the review to the requested canonical destination.

## Invocation boundary

Load this controller only when the resolved request explicitly selects `chat reviewer` or `chat-reviewer`, including explicit left-to-right composition.

Internal reviews owned by Development, Qualification, Release, Hotfix, or another controller remain inside those responsibilities and do not activate Chat Reviewer implicitly.

## Review authority

Reconstruct current state from repository instructions, the authoritative work contract, current GitHub state, and the exact candidate being reviewed.

For a pull request, review its current head and exact PR delta against its current authoritative base.

For a branch, review its current head against the explicitly supplied or repository-authoritative base.

Use only the context needed to understand that delta and its contract. Repository-specific checks supplied by the invocation are part of the review contract.

Record the exact head and base identities reviewed. If either identity changes before publication or final reporting, refresh the review against the new exact delta.

## Evaluation

Evaluate:

1. correctness;
2. completeness against the authoritative contract;
3. regressions or contradictions;
4. security, isolation, data integrity, or compatibility when applicable;
5. supplied target-specific checks;
6. blockers to the intended next step.

Classify findings as:

- `Critical` — severe correctness, security, integrity, or contract failure that blocks acceptance.
- `Important` — material correctness, completeness, regression, or contract failure that must be resolved before acceptance.
- `Minor` — valid non-blocking finding.

Review style only when it materially affects correctness, clarity, or maintainability. Keep findings inside the declared scope.

Missing evidence required to establish completeness makes the target `INCOMPLETE` and not ready.

## Execution boundary

Use only the tools and evidence needed to read and evaluate the target: the authoritative contract, exact delta, changed files, and minimum supporting context.

Existing current validation evidence may be consumed when relevant. This controller does not create new validation evidence by running tests, builds, linters, workflows, or operational commands.

Do not modify code, documentation, Git state, or implementation artifacts, and do not implement fixes.

## Review result

Use the durable `_protocol/delivery/INDEPENDENT_REVIEW.md` contract and its `<!-- independent-review:v1 -->` marker.

Use this compact format:

```text
<!-- independent-review:v1 -->

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

Keep findings concise and concrete. Use at most five bullets, grouping related findings when useful without hiding blockers.

When no Critical or Important findings exist, state that explicitly.

`Ready: YES` requires all of:

- Critical = 0;
- Important = 0;
- the target is complete for its declared scope;
- no contradiction with the current authoritative contract.

When a canonical review destination is supplied, publish exactly one review there. Otherwise return the review inline.

## Terminal report

Return only:

```text
Chat Reviewer = READY | NOT_READY
Target = <PR or branch>
Head reviewed = <sha>
Base reviewed = <ref>@<sha>
Review = <published review reference or inline>
```
