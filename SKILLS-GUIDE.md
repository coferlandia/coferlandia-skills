# Coferlandia Skills Guide

A human-oriented guide for deciding which skill fits a task. It explains selection, ownership, and composition without duplicating lifecycle metadata.

Use [`skills/INDEX.md`](./skills/INDEX.md) as the canonical inventory for skill names, categories, status, and location.

## Selection principles

- Choose the narrowest skill that owns the required outcome.
- Compose skills only when the task crosses responsibility boundaries.
- Planning defines work; development changes code; review validates it; orchestration controls execution and Git.
- Durable project knowledge, operational work state, and cross-project architecture memory have different owners.

## Skill System

| Skill | Use when | Delivers | Boundary |
|---|---|---|---|
| [`using-project-skills`](./skills/meta/using-project-skills/) | Installed project skills may apply to the current task. | Correct skill discovery and invocation before work begins. | Routes the task; it does not perform the domain work. |
| [`skill-repository-versioning`](./skills/meta/skill-repository-versioning/) | A skill-repository change is being prepared for commit or release. | Reconciled index, skill versions, repository version, and release metadata. | Does not design or validate the skill's domain behavior. |
| [`project-skill-miner`](./skills/meta/project-skill-miner/) | A project contains recurring operational procedures worth preserving as local skills. | Evidence-based skill proposals and approved project-local skills. | Rejects speculative or obsolete procedures unsupported by current project evidence. |
| [`coferlandia-skill-toolsmith`](./skills/meta/coferlandia-skill-toolsmith/) | A skill should become more deterministic, economical, and automation-friendly. | One unified Python CLI plus a skill contract rewired around it. | Explicit invocation only; semantic judgment remains with the model. |
| [`coferlandia-config-toolsmith`](./skills/meta/coferlandia-config-toolsmith/) | A project's existing configuration should become safe and economical for agents and developers to operate through one standard interface. | A native or Python-fallback configuration CLI, static contract, adapters, candidate ledger, generated agent handbook, and conformance tests. | Explicit invocation only; it adapts existing native stores and never creates a shadow configuration source. |

## Project Knowledge and Architecture

| Skill | Use when | Delivers | Boundary |
|---|---|---|---|
| [`project-documentation-archivist`](./skills/content/project-documentation-archivist/) | Project documentation is fragmented, stale, missing, or mixed with work history. | Canonical present-state documentation, agent constraints, decisions, runbooks, and source traceability. | GitHub owns active work state; the Architect owns cross-project architecture memory. |
| [`the-architect`](./skills/engineering/the-architect/) | An initiative has material architectural risk, shared contracts, migrations, security, reliability, or reusable-component implications. | Architecture Preflight, a passed or blocked Architecture Gate, concise addenda, and durable architecture evidence. | Not for routine localized work, generic review, or in-project documentation maintenance. |

## Software Delivery

| Skill | Use when | Delivers | Boundary |
|---|---|---|---|
| [`coferlandia-project-manager`](./skills/ops/coferlandia-project-manager/) | A rough idea, requirement, document, or bug cluster must become a coherent initiative. | Initiative WHAT/WHY, scope, acceptance criteria, execution strategy, and one authoritative Epic or local contract. | Does not perform technical decomposition, implementation, review, or Git integration. |
| [`software-development`](./skills/engineering/software-development/) | Code work needs analysis, implementation, debugging, executable-plan execution, fixes, or independent review. | Bounded role execution through Analyst, Developer, Debugger, Coding Agent, Fix Agent, and Code Reviewer. | Does not own portfolio planning or orchestrated Git lifecycle operations. |
| [`project-orchestrator`](./skills/ops/project-orchestrator/) | An approved direct plan or Analyst task graph must run through a controlled delivery lifecycle. | Contract materialization, claims, Git/worktrees, commits, reviews, traceability, final PR, explicit integration, and cleanup. | Executes approved contracts; it does not silently re-plan or redesign them. |

## Configuration Operations

| Skill | Use when | Delivers | Boundary |
|---|---|---|---|
| [`coferlandia-config-devops`](./skills/ops/coferlandia-config-devops/) | A user describes a configuration outcome in natural language after Config Toolsmith has prepared the repository. | Config Operator Execute Mode for direct CLI operation and control-tower Guide Mode for exact remote instructions, with plans, hashes, validation, activation, and rollback. | Consumes the generated contract and CLI; it does not edit native files directly, invent fields, promote candidates, or change adapters. |

## Evidence and Critical Reasoning

| Skill | Use when | Delivers | Boundary |
|---|---|---|---|
| [`sagan-scientific-debunker`](./skills/content/sagan-scientific-debunker/) | A claim, article, report, or news item requires scientific scrutiny. | Evidence map, source-quality assessment, calibrated confidence, and traceable conclusions. | Does not manufacture certainty or advocate beyond the available evidence. |

## Common compositions

```text
Controlled delivery:     Project Manager -> optional Architect -> Analyst/direct plan -> Orchestrator -> development roles
Knowledge recovery:      Archivist -> optional Project Skill Miner
Skill mechanization:     Existing skill -> Skill Toolsmith -> Skill Repository Versioning
Configuration tooling:   Config Toolsmith -> Config DevOps
```

Every component remains independently invokable. Composition is required only when responsibility crosses skill boundaries.

## Canonical documents

- [`skills/INDEX.md`](./skills/INDEX.md) is the only inventory and status catalog.
- Each skill's `SKILL.md` is its complete operational contract.
- This guide explains selection and composition; it does not redefine behavior.
- [`AGENTS.md`](./AGENTS.md) remains the entry point for agents maintaining or consuming the repository.
