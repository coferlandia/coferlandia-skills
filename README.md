# coferlandia-skills

Portable [Agent Skills](https://agentskills.io) repository. The agentskills.io
specification is the canonical source for the format; this repo only adds local
conventions.

## For AI agents

Read [`AGENTS.md`](./AGENTS.md) â€” everything needed to use and create skills.

## Structure

```
skills/          Skills, organized by category
_protocol/       Protocol for creating and maintaining skills
AGENTS.md        Entry point for agents
```

## Available skills

See [`skills/INDEX.md`](./skills/INDEX.md).

## Releases

Current version and changelog: [`RELEASE-NOTES.md`](./RELEASE-NOTES.md).

## Install

### Claude Code

```powershell
claude plugin marketplace add diegocofre/coferlandia-skills
claude plugin install coferlandia-skills@coferlandia
```

### GitHub Copilot CLI

```powershell
copilot plugin marketplace add diegocofre/coferlandia-skills
copilot plugin install coferlandia-skills@coferlandia
```

Claude Code and Copilot CLI share the marketplace declared in `.claude-plugin/`.

### Global Agent Skills

Codex, Gemini CLI, and other Agent Skill runtimes consume these skills as immediate
children of a global skills directory. The repository keeps its category organization,
then flattens it during installation.

Run the installer from the repository root to overwrite the current user's global
installations. It removes the old Coferlandia-branded names and does not retain backups:

```powershell
python _protocol/scripts/install_global_skills.py
```

Use `--dry-run` to inspect removals and copies first, or `--destination PATH` to target
one runtime explicitly. Repeat `--destination` to update more than one runtime.

## License

Apache License 2.0 â€” see [`LICENSE`](./LICENSE). Skills here are provided "as is,"
without warranty of any kind. They encode process and judgment, not certified
procedures: read a skill fully and verify its behavior before relying on it for
anything consequential.

---

*Built for agents. By agents.*
