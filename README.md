# coferlandia-skills

Coferlandia's [Agent Skills](https://agentskills.io) repository. The agentskills.io
specification is the canonical source for the format; this repo only adds local
conventions.

## For AI agents

Read [`AGENTS.md`](./AGENTS.md) — everything needed to use and create skills.

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

### Codex and Gemini CLI

Codex and Gemini CLI consume these skills as Agent Skills installed under
`~/.agents/skills`, not as plugins or extensions. Both formats only discover immediate
child skills and don't support this repo's category level
(`skills/<category>/<skill>`).

In Coferlandia's dev environment, each skill installs as a junction to its canonical
directory — live editing, no copies. No Codex marketplace or Gemini extension ships
while doing so would require duplicating or restructuring the skills tree.

## License

Apache License 2.0 — see [`LICENSE`](./LICENSE). Skills here are provided "as is,"
without warranty of any kind. They encode process and judgment, not certified
procedures: read a skill fully and verify its behavior before relying on it for
anything consequential.

---

*Built for agents. By agents.*
