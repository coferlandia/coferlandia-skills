# coferlandia-skills

Repositorio de [Agent Skills](https://agentskills.io) de Coferlandia. La especificación de
agentskills.io es la fuente canónica del formato; este repo solo define convenciones locales.

## Para agentes de IA

Lee [`AGENTS.md`](./AGENTS.md) — contiene todo lo que necesitas para usar y crear skills.

## Para humanos

Lee [`vault/Genesis_Plan.md`](./vault/Genesis_Plan.md) para entender la visión y arquitectura completa.

## Estructura rápida

```
skills/          ← Todas las skills organizadas por categoría
_protocol/       ← Protocolo para crear y mantener skills
AGENTS.md        ← Entry point para agentes
vault/           ← Visión, arquitectura y auditorías
```

## Skills disponibles

Ver [`skills/INDEX.md`](./skills/INDEX.md).

## Instalación

El repositorio mantiene una sola copia editable de cada skill. El marketplace compartido y las
junctions locales apuntan al mismo árbol `skills/`.

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

Claude Code y Copilot CLI comparten el marketplace declarado en `.claude-plugin/`.

### Codex y Gemini CLI

Codex y Gemini CLI consumen estas skills mediante Agent Skills instaladas en `~/.agents/skills`,
no mediante plugins o extensiones. Ambos formatos de distribución sólo descubren skills hijas
inmediatas y no admiten el nivel de categorías canónico de este repo
(`skills/<categoria>/<skill>`).

En el entorno de desarrollo de Coferlandia, cada skill se instala como junction hacia su directorio
canónico. Esto preserva edición en vivo y evita copias. No se publica un marketplace Codex ni una
extensión Gemini mientras hacerlo requiera duplicar o reestructurar el árbol de skills.

---

*Construido para agentes. Por agentes.*
