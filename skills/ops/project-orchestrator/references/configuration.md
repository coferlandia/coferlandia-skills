# Configuration

Run `init-config` to create `.project-orchestrator/config.json` without overwriting an
existing file, then `validate-config`. `config.example.json` documents defaults:
role-specific primary/fallback provider/model/reasoning, Git strategy, timeouts,
retry cycles, and protocol retention. Never put credentials in this file; use native
provider authentication or environment variables. Models are probed/resolved at run
time and unavailable providers are fallback candidates, not success signals.
