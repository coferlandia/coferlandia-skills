# coferlandia-skills

Operational contracts for AI agents working on real software projects.

Coferlandia Skills turns general-purpose models into specialized collaborators with explicit responsibilities, bounded authority, deterministic tooling, and auditable outcomes. The repository follows the [Agent Skills](https://agentskills.io) specification and adds local conventions for composition, lifecycle, evidence, and execution.

## Is this library for you?

Use Coferlandia Skills when you:

- run AI agents against real repositories, documentation, Git, or GitHub;
- need repeatable workflows rather than one-off prompts;
- want planning, architecture, implementation, review, and integration to remain separate;
- need durable decisions, traceability, and safe coordination across agents.

It is probably not the right fit when you only need short prompt snippets, expect unsupervised publication without evidence or control gates, or want a hosted development platform rather than a portable skill library.

## Operating philosophy

- **Skills are operational contracts, not prompt fragments.** Each skill defines activation conditions, authority, boundaries, outputs, and completion criteria.
- **Semantic judgment and deterministic control are separated.** Models reason and produce domain work; code owns mechanical state, validation, and lifecycle operations where reliability matters.
- **Every responsibility has one owner.** Planning, architecture, implementation, review, integration, and durable knowledge are not silently duplicated.
- **Autonomy remains supervised and traceable.** Human or agentic control authorities may approve work, but consequential decisions and evidence remain inspectable.
- **Skills compose without becoming inseparable.** They support complete workflows while remaining independently useful.

## Natural skill families

| Family | Purpose |
|---|---|
| **Skill System** | Discover, create, version, mine, and mechanize skills. |
| **Project Knowledge and Architecture** | Preserve durable project knowledge and govern material architectural decisions across projects. |
| **Software Delivery** | Turn an initiative into an executable contract, implement it, review it, and integrate it under explicit control. |
| **Configuration Operations** | Standardize existing project configuration and operate it safely from agent or guided workflows. |
| **Evidence and Critical Reasoning** | Evaluate claims through explicit evidence, confidence, and source traceability. |

See the [Skills Guide](./SKILLS-GUIDE.md) for the human-oriented catalog, selection guidance, boundaries, and expected outcomes.

## Typical software-delivery flow

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

The workflow is modular. The Project Manager, Architect, development roles, Archivist, and Orchestrator can also be invoked independently when the task requires only one responsibility.

## Documentation map

| Document | Purpose |
|---|---|
| [`README.md`](./README.md) | Human-facing value proposition and operating model. |
| [`SKILLS-GUIDE.md`](./SKILLS-GUIDE.md) | Executive guide for deciding which skills are useful. |
| [`skills/INDEX.md`](./skills/INDEX.md) | Canonical inventory, category, status, and location of every skill. |
| [`AGENTS.md`](./AGENTS.md) | Entry point and maintenance rules for AI agents. |
| Each `SKILL.md` | Complete operational contract for one skill. |
| Each `CHANGELOG.md` | Version history for one public skill. |

## Repository structure

```text
skills/          Public skills, organized by category
_protocol/       Protocol for creating, validating, and releasing skills
.agents/skills/  Repository-local skills that are not shipped in the plugin
AGENTS.md        Entry point for agents
```

## Releases

<!-- coferlandia-latest-release:start -->
## Latest release

**v2.3.0 — 2026-08-03**

| Changed skill | Version | Main change |
|---|---:|---|
| coferlandia-config-toolsmith | 1.0.0 | Adds an explicit agentic-plus-deterministic process that discovers a project's existing configuration, builds a static contract and standardized native-or-fallback CLI, records ambiguous candidates, generates agent documentation, and preserves the project's native stores as the only runtime source of truth. |
| coferlandia-config-devops | 1.0.0 | Adds Config Operator Execute Mode and control-tower Guide Mode for converting natural-language configuration intent into exact prepare/apply/activate/rollback operations through the Toolsmith-generated interface. |

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

Claude Code and Copilot CLI share the marketplace declared in `.claude-plugin/`.

### Global Agent Skills

Codex, Gemini CLI, and other Agent Skill runtimes consume these skills as immediate children of a global skills directory. The repository keeps its category organization, then flattens it during installation.

Run the installer from the repository root to overwrite the current user's global installations. It removes old Coferlandia-branded names and does not retain backups:

```powershell
python _protocol/scripts/install_global_skills.py
```

Use `--dry-run` to inspect removals and copies first, or `--destination PATH` to target one runtime explicitly. Repeat `--destination` to update more than one runtime.

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE). Skills are provided "as is," without warranty. They encode process and judgment, not certified procedures; read a skill fully and verify its behavior before relying on it for consequential work.

---

*Built for agents. By agents.*
