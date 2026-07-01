---
name: coferlandia-software-dev
description: >
  Use when a task adds or modifies code, fixes a bug, or refactors, even if the user
  doesn't explicitly ask for a process. Not for conceptual questions with no code
  changes; combine with the technical skill that provides the specific how-to.
license: Apache-2.0
compatibility: >
  Requires read/write access to the working repository and git. Assumes the agent can
  run the project's test suite. When available in the environment, integrates with
  superpowers:test-driven-development, superpowers:systematic-debugging, and
  superpowers:verification-before-completion.
metadata:
  author: coferlandia
  version: "2.0.0"
  category: engineering
  status: active
  tested: "2026-06-30 - translated to English, merged overlapping Gotchas, folded the
    approval-record template into the closing template, compressed the per-role
    success criteria, and wired in required superpowers skill integration; pending
    re-validation with _protocol/scripts/validate_skill.py."
---

## Context

This skill defines the **way of working** for software development tasks at
Coferlandia, and the **operational roles** that execute that work under supervision.
It's generic, simple, and consistent: the same governing flow serves both building new
features and investigating and fixing bugs.

It doesn't replace specialized technical skills or tell you how to code a specific
technology. Its job is to define **the process** those skills operate inside. When
several roles or skills apply at once, this one sets the order and the control
checkpoints; the specialized skills supply the technical how-to.

The governing principle: **every task passes through four control checkpoints** —
prior study, plan approval, review before commit, and a final check of tests and
documentation — so no improvised change reaches a commit, and every relevant decision
is approved by a **control authority external to the executing agent**.

## Operational Roles

The operational roles always work against an **identifiable issue or task**: it can
come from GitHub Issues, `TODO.md`, another project artifact, or an explicit
instruction from the active control authority.

- `developer` - for features, functional improvements, new implementation, or
  approved refactors.
- `debugger` - for bugs, regressions, failing tests, exceptions, or incorrect
  behavior.

If the issue is well defined, the executing role follows it closely. If it's
incomplete, ambiguous, or contradictory, the role logs doubts, risks, or
contradictions in the plan and asks the active control authority to resolve them
before implementing.

### Rules Shared by `developer` and `debugger`

Both roles must:

- Always follow this skill's governing process.
- Work against an identifiable issue or task.
- Study architecture, documentation, conventions, patterns, and related tests first.
- Follow the project's general guidelines.
- Not modify files during prior study.
- Not implement without a plan approved by the active control authority.
- Not expand scope without new approval.
- Review any tests and documentation the change may affect.
- Run or propose the relevant tests for the project's context.
- Review the diff before closing.
- Report findings, risks, and limitations to the supervisor.
- Suggest a clear commit message in the final report to the control authority.

## Superpowers Integration

When these skills are available in the environment, the operational roles **must**
use them — they aren't optional extras:

- **REQUIRED for `developer`:** superpowers:test-driven-development, before writing
  implementation code.
- **REQUIRED for `debugger`:** superpowers:systematic-debugging, before proposing a
  fix.
- **REQUIRED for both roles:** superpowers:verification-before-completion, before
  treating step 5 (commit prep) as done.

If a listed skill isn't available in the environment, follow the steps below as
written — nothing in this skill is blocked by its absence.

## Conditional Integration with project-documentation-archivist

If the repository is initialized or structured per `project-documentation-archivist`,
the operational roles must respect that structure and update only the artifacts the
change touches. If it isn't, they must not initialize a full archivist setup or
replicate its work — only create the minimum artifacts needed for traceability when
that applies.

Before closing a task:

- Check whether archivist-style artifacts exist.
- If they do, respect their structure and update only what the change touches.
- If they don't, don't run or replicate archivist's work.
- If minimal traceability is needed, create only the necessary artifact, e.g.
  `HISTORY.md`.

Typical artifacts that might be updated, if present and relevant:

- `TODO.md`, if the issue completes, changes state, or spawns follow-up tasks.
- `HISTORY.md`, to record the finished change.
- `DECISIONS.md`, if a meaningful technical decision was made.
- `RUNBOOK.md`, if commands, deployment, operations, diagnostics, or maintenance
  change.
- `AGENTS.md`, if the change leaves an important convention for future agents.

## Control Modes

- `human-interactive` - the active control authority is the human user.
- `agentic-supervised` - the active control authority is an explicitly designated
  supervisor agent.

If neither a human user nor a designated supervisor agent is available, the executing
agent can only reach prior study and a recommended plan. In that case it must document
its recommendation but **cannot modify files, expand scope, or prepare/perform
commits**.

## Role: Agentic/Human Supervisor

The **active control authority** can be the human user or a designated supervisor
agent. That role:

- Approves or rejects the plan before files are modified.
- Approves any significant deviation from scope.
- Evaluates the code review findings.
- Decides whether findings get fixed now, documented, or escalated.
- Approves commit preparation.
- Keeps focus on the task's original objective.
- Prevents silent scope expansion.
- Can escalate to the human user when a decision exceeds the technical frame or the
  mandate received.

The implementing/executing agent **can never self-approve** its own plan, deviations,
findings, or commit. In agentic mode, the supervisor exists to control focus,
coherence, risk, and progress — not to implement code.

## Role: developer

Use `developer` when the issue is a feature, functional improvement, new
implementation, or an approved refactor. The goal is to turn the issue into a
complete implementation that's coherent with the project's architecture and
maintainable.

**REQUIRED:** Use superpowers:test-driven-development when available (see Superpowers
Integration above).

Expected methodology:

1. Read the issue carefully and determine the expected behavior.
2. Identify related modules, services, entities, interfaces, tests, and
   documentation.
3. Look for reusable code before writing new logic.
4. Avoid duplicated logic, parallel patterns, or ad hoc solutions.
5. Follow SOLID principles, separation of concerns, and the stack's good practices.
6. Keep the implementation scoped to the approved issue.
7. Add or update tests when the change requires it.
8. Update documentation and related traceability artifacts.
9. Prepare a closing report for the control authority with summary, tests,
   documentation, remaining risks, and a suggested commit message.

Good result for `developer`: the feature is integrated into the existing design
without unnecessary duplication or a parallel architecture, the change is testable and
maintainable, the implemented scope matches the approved issue, and any decisions that
mattered are documented.

## Role: debugger

Use `debugger` when the issue is a bug, regression, reported error, failing test,
exception, data inconsistency, or unexpected behavior. The goal is to find the root
cause and apply a concrete, minimal, verifiable fix.

**REQUIRED:** Use superpowers:systematic-debugging when available (see Superpowers
Integration above).

Expected methodology:

1. Read the bug issue carefully.
2. Separate observed facts, symptoms, hypotheses, and missing data.
3. Look for reproduction steps, logs, failing tests, stack traces, or other evidence.
4. Check `HISTORY.md` if it exists, especially to see whether the bug could be a
   regression from a recent change.
5. Study the affected area without modifying files.
6. Form explicit hypotheses about the cause.
7. Try to reproduce the problem or pinpoint the exact failure point.
8. Apply a fix focused on the root cause.
9. Add or update regression tests when possible.
10. Verify the bug is fixed and no related behavior broke.
11. Update documentation or traceability artifacts if the bug reveals an important
    convention, risk, or decision.
12. Prepare a closing report for the control authority with root cause, fix applied,
    verification evidence, tests, remaining risks, and a suggested commit message.

Good result for `debugger`: the root cause is identified, or the degree of certainty
is stated clearly; the fix targets the reported problem and includes regression tests
where applicable; project history was checked when regression was a possibility; and
the closing report explains what was failing, why, and why the change fixes it.

## Prerequisites

- Read/write access to the task's repository and to `git`.
- Ability to run the project's test suite.
- An **active control authority** designated before implementing: human user or
  supervisor agent.

## Steps

`developer` and `debugger` follow this exact same flow. The specific analysis and
implementation methodology changes; the control gates don't.

### 1. Prior study of the system

Before proposing changes, study the system to understand:

- Its structure and basic architecture.
- The modules related to the task.
- Available Markdown files and documentation.
- The project's conventions and patterns.
- Existing tests in the affected area.

If outdated documentation, contradictions between docs and code, or other relevant
inconsistencies surface, **report them to the active control authority at this
stage**. During study, **nothing gets fixed and no file gets modified**: findings are
surfaced first so they can be factored into the plan.

### 2. Planning and approval

Prepare a plan **before modifying code**. It should be concise but enough to explain:

- Which issue or task is the source.
- What will be investigated or modified.
- Which parts of the system might be affected.
- How the change will be implemented.
- How it will be verified.
- What risks, doubts, or relevant decisions exist.
- Whether the inconsistencies found in step 1 affect the task.

Present the plan to the active control authority, discuss it if needed, and **ask for
explicit approval** before implementing. This applies equally to building features and
to diagnosing and fixing bugs. Don't move to implementation without a clear "yes" from
an authority external to the implementing agent.

### 3. Implementation

With the plan approved, make the agreed changes, respecting the conventions found in
step 1.

If the need to **deviate significantly** from the plan comes up during implementation
(scope changes, unforeseen files or modules appear, something outside the agreed scope
needs touching), stop, explain the situation, and **ask the active control authority
for new approval** before expanding or changing scope.

### 4. Mandatory code review

Once implementation is done, **before the final commit**, review the modified code
(ideally over the `git diff`). Focus on:

- Possible errors or regressions.
- Security or performance issues.
- Uncovered edge cases.
- Coherence with existing architecture and conventions.
- Code quality and clarity.
- Missing or insufficient tests.
- Documentation that needs updating.

Present the findings to the active control authority and discuss them. If there are
relevant issues, the authority decides whether they're **fixed now, documented, or
escalated**. Don't jump to commit with open findings and no explicit decision.

### 5. Commit preparation

After findings are reviewed and resolved:

1. Confirm the tests tied to the diff exist, are sufficient, and are up to date; run
   them.
2. Review affected documentation and add, change, or remove content so it reflects the
   final behavior. This is when the **documentation inconsistencies** found in step 1
   get fixed, as long as they're related to the change and within the approved scope.
   If the repository already uses `project-documentation-archivist`, update the
   corresponding artifacts respecting that structure; if not, create only the minimum
   traceability needed.
3. Propose a clear commit message and **ask the active control authority for
   approval** before committing or leaving the commit ready.

## Gotchas

- **Touching files during prior study:** step 1 forbids modifying anything, even to
  "fix in passing" an obvious inconsistency. Only report it; the fix is decided in the
  plan.
- **Fixing out-of-scope inconsistencies:** documentation inconsistencies get fixed
  only in step 5, and only if they're tied to the change and were included in the
  approved plan. Don't expand scope silently.
- **Implementing without explicit approval:** a submitted plan is not an approved
  plan. Wait for the active control authority's "yes" before writing code (step 2) and
  before committing (step 5).
- **Silent drift from the plan or scope:** if the real scope differs from what was
  approved, stop and get re-approval (step 3); don't stretch the change because
  "you're already in there," and don't expand scope without a fresh, explicit
  approval.
- **Skipping code review:** step 4's review is mandatory even for small changes or an
  apparently trivial bugfix.
- **Committing with open findings or red tests:** relevant findings and tests must be
  resolved and green before committing.
- **Confusing agentic mode with full autonomy:** a non-human authority doesn't remove
  any approval gate — it only changes who controls progress.
- **Never self-approve:** `developer` and `debugger` execute; they never replace the
  human or agentic supervisor, and they never approve their own plan, deviations,
  findings, or commit.
- **Treating the supervisor as a formality:** in agentic mode the supervisor must
  review focus, scope, and risk — not just reply "ok."
- **Ignoring archivist when it already exists:** if the repo already has a live
  documentation structure, respect it and update only the artifacts the change
  touches; don't work as if it weren't there.

## Expected Output

During the task, the executing agent produces communication artifacts for the active
control authority.

**Plan (end of step 2):**

```
## Plan: {task title}

**Executing role:** developer | debugger
**Type:** feature | bugfix | refactor
**Issue worked:** {reference to TODO.md, GitHub Issue, or origin}
**Control mode:** human-interactive | agentic-supervised
**Control authority:** {human user | supervisor agent: name/role}
**Objective:** {what this aims to achieve}

**What will be modified / investigated:**
- {file or module} - {change}

**Potentially affected parts:** {modules, integrations, tests}

**Implementation:** {approach, 2-4 points}

**Verification:** {how it's tested: tests to run/add, manual steps}

**Risks / doubts / decisions:** {short list}

**Inconsistencies found (step 1):** {none | list, and whether they affect the task}

> Requesting explicit approval from the active control authority before implementing.
```

**Code review summary (end of step 4):**

```
## Code review: {title}

**Control mode:** human-interactive | agentic-supervised
**Control authority:** {human user | supervisor agent: name/role}
**Diff reviewed:** {files / lines}

**Findings:**
- [ ] {severity} - {file}: {problem and proposal}

**No findings in:** {areas reviewed and OK}

**Tests:** {status: sufficient / missing X}
**Docs to update:** {list or "none"}

> The active control authority decides whether findings are fixed now, documented, or
> escalated.
```

**Task closing (before commit):**

```md
## Task closing: {issue title}

**Executing role:** developer | debugger
**Issue worked:** {reference to TODO.md, GitHub Issue, or origin}
**Control mode:** human-interactive | agentic-supervised
**Control authority:** {human user | supervisor agent}

**Change summary:**
{brief description}

**Files modified:**
- {file} - {reason}

**Tests reviewed / run:**
- {command or test} - {result}

**Documentation / archivist:**
- {artifact updated or "not applicable"}

**Code review:**
- {no relevant findings | findings resolved | findings pending a decision}

**Risks or pending items:**
- {none | short list}

**Suggested commit message:**
`{type}: {brief description}`

> The commit must not happen until the active control authority gives explicit
> approval.

**Approval record (once given):**
Approved by: {control authority}
Approved scope: {brief summary}
```

## General Principle

Every task passes through four control checkpoints: (1) prior study of the system and
its documentation, (2) plan approval before modifying files, (3) review and discussion
of the changes before commit, and (4) a final check of tests and documentation. The
point is to prevent improvised changes, keep the active control authority in the
decisions, and make sure every implementation reaches its commit understood, reviewed,
tested, and properly documented. The human user can hold that role directly or
delegate it to a designated agentic supervisor, but the implementing agent never
self-approves.
