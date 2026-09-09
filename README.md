# coferlandia-skills

Operational contracts and reusable Chat delivery controllers for AI agents working on real software projects.

Coferlandia Skills turns general-purpose models into specialized collaborators with explicit responsibilities, bounded authority, deterministic tooling, and auditable outcomes. The repository follows the [Agent Skills](https://agentskills.io) specification for its public skills and additionally maintains a small public Chat prompt family for Development, Qualification, and Integration.

## Is this library for you?

Use Coferlandia Skills when you:

- run AI agents against real repositories, documentation, Git, or GitHub;
- need repeatable workflows rather than one-off prompts;
- want planning, architecture, implementation, review, Qualification, and Integration to remain separate;
- need durable decisions, traceability, and safe coordination across agents.

It is probably not the right fit when you only need isolated prompt snippets, expect unsupervised publication without evidence or control gates, or want a hosted development platform rather than portable contracts.

## Operating philosophy

- **Agent Skills are operational contracts, not prompt fragments.** Each skill defines activation conditions, authority, boundaries, outputs, and completion criteria.
- **Chat delivery controllers are first-class but distinct.** `chat-coder`, `ci`, and `merge` are centrally maintained prompts for Chat execution surfaces; local Qualification is a skill.
- **Semantic judgment and deterministic control are separated.** Models reason and produce domain work; code owns mechanical state, validation, and lifecycle operations where reliability matters.
- **Every responsibility has one owner.** Planning, architecture, implementation, Qualification, Integration, release publication, and durable knowledge are not silently duplicated.
- **Autonomy remains supervised and traceable.** Human or agentic control authorities may approve work, but consequential decisions and evidence remain inspectable.
- **Controllers compose without becoming inseparable.** They support complete workflows while remaining independently useful.

## Natural skill families

| Family | Purpose |
|---|---|
| **Skill System** | Discover, create, version, mine, adapt, and mechanize skills/contracts. |
| **Project Knowledge and Architecture** | Preserve durable project knowledge and govern material architectural decisions across projects. |
| **Software Delivery** | Turn an initiative into an executable contract, implement it, qualify an exact candidate, review it, and integrate it under explicit control. |
| **Configuration Operations** | Standardize existing project configuration and operate it safely from agent or guided workflows. |
| **Evidence and Critical Reasoning** | Evaluate claims through explicit evidence, confidence, and source traceability. |

See the [Skills Guide](./SKILLS-GUIDE.md) for the human-oriented catalog, selection guidance, boundaries, and expected outcomes.

## Chat delivery flow

```text
Issue
  |
  v
chat-coder (Chat Development)
  |
READY_FOR_CI
  |
  +---------------------------+
  |                           |
  v                           v
ci prompt                  local-ci skill
GITHUB_NATIVE              LOCAL
  |                           |
  +--------- READY_FOR_MERGE -+
               |
               v
            merge prompt
               |
            COMPLETE
```

Both Qualification strategies consume one repository-owned `.coferlandia/ci/profile.json` produced/maintained by `coferlandia-ci-adapter`. They are alternatives, not fallback paths.

## Typical orchestrated software-delivery flow

```text
Idea, requirement, or bug cluster
                |
                v
Coferlandia Project Manager
WHAT, WHY, scope, acceptance criteria, execution strategy
                |
                v
Optional Architecture Gate
                |
                v
Analyst decomposition or direct executable plan
                |
                v
Project Orchestrator
                |
                v
Coding Agent -> Independent Review -> Fixes
                |
                v
Holistic Review -> Pull Request -> Explicit Integration
```

The workflows are modular. The Project Manager, Architect, development roles, Archivist, Orchestrator, Chat prompts, CI strategies, and release publisher can be invoked independently when the task requires only one responsibility.

## Documentation map

| Document | Purpose |
|---|---|
| [`README.md`](./README.md) | Human-facing value proposition and operating model. |
| [`SKILLS-GUIDE.md`](./SKILLS-GUIDE.md) | Executive guide for deciding which skills/controllers are useful. |
| [`skills/INDEX.md`](./skills/INDEX.md) | Canonical inventory, category, status, and location of every Agent Skill. |
| [`prompts/INDEX.md`](./prompts/INDEX.md) | Public Chat delivery prompt catalog. |
| [`prompts/registry.json`](./prompts/registry.json) | Machine-readable Chat aliases/composition registry. |
| [`AGENTS.md`](./AGENTS.md) | Entry point and maintenance rules for AI agents. |
| Each `SKILL.md` | Complete operational contract for one Agent Skill. |
| Each skill `CHANGELOG.md` | Version history for one public skill. |

## Repository structure

```text
skills/          Public Agent Skills, organized by category
prompts/         Public Chat delivery controllers, shipped alongside skills
_protocol/       Shared creation, validation, delivery, and release protocol
.agents/skills/  Repository-local skills that are not shipped in the plugin
AGENTS.md        Entry point for agents
```

## Releases

<!-- coferlandia-latest-release:start -->
## Latest release

**v2.6.5 — 2026-09-09**

[Read the complete release notes](./RELEASE-NOTES.md)
<!-- coferlandia-latest-release:end -->

## Install

### Claude Code

```powershell
claude plugin marketplace add coferlandia/coferlandia-skills
claude plugin install coferlandia-skills@coferlandia
```

### GitHub Copilot CLI

```powershell
copilot plugin marketplace add coferlandia/coferlandia-skills
copilot plugin install coferlandia-skills@coferlandia
```

Claude Code and Copilot CLI share the marketplace declared in `.claude-plugin/`. The generated plugin package includes both public Agent Skills and the public `prompts/` catalog.

### Global Agent Skills

Codex, Gemini CLI, and other Agent Skill runtimes consume these skills as immediate children of a global skills directory. The repository keeps its category organization, then flattens it during installation.

Run the installer from the repository root to overwrite the current user's global installations. It removes old Coferlandia-branded names and does not retain backups:

```powershell
python _protocol/scripts/install_global_skills.py
```

Use `--dry-run` to inspect removals and copies first, or `--destination PATH` to target one runtime explicitly. Repeat `--destination` to update more than one runtime.

### Chat prompts

The `prompts/` family is a separate public artifact family from Agent Skills, but it ships in the same Coferlandia plugin/package. Repository vendoring or installation flows that materialize Coferlandia under `.agents/` should install the prompt catalog under the target prompt location (for example `.agents/prompts/`) as well as the Agent Skills catalog under the target skill location.

Load `prompts/BOOTSTRAP.md`/`prompts/registry.json` when a Chat environment wants short controller names and composition.

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE). Skills and prompts are provided "as is," without warranty. They encode process and judgment, not certified procedures; read the applicable contract fully and verify its behavior before relying on it for consequential work.

---

*Built for agents. By agents.*
