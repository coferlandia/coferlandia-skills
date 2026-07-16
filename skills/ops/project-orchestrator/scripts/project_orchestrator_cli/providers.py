"""Provider adapters and safe non-interactive process execution."""
from __future__ import annotations
import json, os, shutil, signal, subprocess, sys, time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable
from .contracts import DependencyError, ValidationError

@dataclass
class ProviderHealth:
    name: str; available: bool; command: str; detail: str
    authenticated: bool | None = None; model: str | None = None
    version: str | None = None; models: list[str] = field(default_factory=list)

@dataclass
class ProcessRequest:
    command: list[str]; cwd: Path; timeout: float; stdin: str = ""
    env: dict[str, str] | None = None; stdout_path: Path | None = None
    stderr_path: Path | None = None; events_path: Path | None = None
    termination_grace: float = 30
    pid_path: Path | None = None

@dataclass
class ProcessResult:
    returncode: int; stdout: str; stderr: str
    events: list[dict[str, Any]] = field(default_factory=list)
    session_id: str | None = None; timed_out: bool = False; failure_class: str = "SUCCESS"


def extract_agent_result(events: list[dict[str, Any]], last_message: str | None = None) -> dict[str, Any]:
    """Extract the controller contract from provider protocol events."""
    candidates: list[Any] = [last_message] if last_message else []

    def visit(value: Any) -> None:
        candidates.append(value)
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for event in reversed(events):
        visit(event)
    for candidate in candidates:
        if isinstance(candidate, dict) and (candidate.get("role") in {"coding-agent", "completion-verifier", "code-reviewer", "fix-agent"} or any(key in candidate for key in ("acceptance", "summary", "findings", "changed_files", "requirement_completion"))):
            return candidate
        if isinstance(candidate, str):
            texts = [candidate.strip()]
            start, end = candidate.find("{"), candidate.rfind("}")
            if start >= 0 and end > start:
                texts.append(candidate[start:end + 1])
            for text in texts:
                try:
                    value = json.loads(text)
                except (TypeError, json.JSONDecodeError):
                    continue
                if isinstance(value, dict) and (value.get("role") in {"coding-agent", "completion-verifier", "code-reviewer", "fix-agent"} or any(key in value for key in ("acceptance", "summary", "findings", "changed_files", "requirement_completion"))):
                    return value
    return {}

class ProcessRunner:
    def __init__(self, popen: Callable[..., subprocess.Popen[str]] | None = None): self.popen = popen or subprocess.Popen
    def execute(self, request: ProcessRequest) -> ProcessResult:
        try:
            p = self.popen(request.command, cwd=request.cwd, env=request.env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=os.name != "nt")
        except FileNotFoundError: return ProcessResult(127, "", "command not found", failure_class="COMMAND_NOT_FOUND")
        except OSError as exc: return ProcessResult(126, "", str(exc), failure_class="PROCESS_CRASH")
        if request.pid_path:
            request.pid_path.write_text(str(p.pid), encoding="utf-8")
        try: out, err = p.communicate(request.stdin, timeout=request.timeout); timed = False
        except subprocess.TimeoutExpired as exc:
            self._terminate(p, request.termination_grace); tail_out, tail_err = p.communicate()
            out, err, timed = (exc.output or "") + (tail_out or ""), (exc.stderr or "") + (tail_err or ""), True
        if request.pid_path:
            try: request.pid_path.unlink()
            except FileNotFoundError: pass
        events, session = self.normalize_events(out)
        if request.stdout_path: request.stdout_path.write_text(out, encoding="utf-8")
        if request.stderr_path: request.stderr_path.write_text(err, encoding="utf-8")
        if request.events_path: request.events_path.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        code = p.returncode if p.returncode is not None else 1
        return ProcessResult(code, out, err, events, session, timed, "TIMEOUT" if timed else ("SUCCESS" if code == 0 else "PROCESS_CRASH"))
    @staticmethod
    def normalize_events(output: str) -> tuple[list[dict[str, Any]], str | None]:
        events=[]; session=None
        for line in output.splitlines():
            try: event=json.loads(line)
            except json.JSONDecodeError: continue
            if isinstance(event, dict): events.append(event); session=session or event.get("session_id") or event.get("sessionId")
        return events, session
    @staticmethod
    def _terminate(p: subprocess.Popen[str], grace: float) -> None:
        try:
            if os.name != "nt": os.killpg(p.pid, signal.SIGTERM)
            else: p.terminate()
            p.wait(timeout=grace)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                if os.name != "nt": os.killpg(p.pid, signal.SIGKILL)
                else: p.kill()
            except ProcessLookupError: pass

class AgentProvider:
    name="base"
    def __init__(self, command: str, runner: ProcessRunner | None = None): self.command,self.runner=command,runner or ProcessRunner()
    def command_argv(self, *args: str) -> list[str]:
        if self.command.lower().endswith(".py"):
            return [sys.executable, self.command, *args]
        return [self.command, *args]
    def probe(self):
        found=shutil.which(self.command)
        if not found: return ProviderHealth(self.name,False,self.command,"command not found")
        version=""
        try:
            result=subprocess.run(self.command_argv("--version"),text=True,capture_output=True,timeout=10,check=False)
            version=(result.stdout or result.stderr).strip().splitlines()[0] if (result.stdout or result.stderr) else None
        except (OSError, subprocess.TimeoutExpired): pass
        return ProviderHealth(self.name,True,self.command,"available",version=version)
    def resolve_model(self, requested):
        if not requested: raise ValidationError(f"{self.name} model is required")
        return requested
    def build_command(self, **kwargs): raise NotImplementedError
    def execute(self, request): return self.runner.execute(request)
    def classify_failure(self, result):
        if result.failure_class != "SUCCESS": return result.failure_class
        if result.returncode == 0 and result.events: return "SUCCESS"
        if result.returncode == 0: return "MISSING_OUTPUT"
        text=(result.stderr+result.stdout).lower()
        if "rate limit" in text or "quota" in text: return "RATE_LIMIT"
        if "auth" in text or "unauthorized" in text: return "AUTHENTICATION_FAILURE"
        if "model" in text and "not" in text: return "MODEL_NOT_FOUND"
        return "PROCESS_CRASH"

class CodexProvider(AgentProvider):
    name="codex"
    def probe(self):
        health=super().probe()
        if health.available:
            try:
                result=subprocess.run(self.command_argv("login","status"),text=True,capture_output=True,timeout=10,check=False)
                health.authenticated=result.returncode == 0 and "logged in" in (result.stdout + result.stderr).lower()
            except (OSError, subprocess.TimeoutExpired): pass
        return health
    def build_command(self, *, worktree, model, prompt_file, role, reasoning=None, session_id=None, output_schema=None):
        c=self.command_argv("exec") + (["resume",session_id] if session_id else []) + ["--cd",str(worktree),"--model",model,"--json","--output-last-message",str(prompt_file.with_suffix(".last.md"))]
        if output_schema: c += ["--output-schema",str(output_schema)]
        if reasoning: c += ["-c",f"model_reasoning_effort={reasoning}"]
        return c + ["--sandbox","workspace-write" if role in {"coding-agent","fix-agent"} else "read-only","-"]

class OpenCodeProvider(AgentProvider):
    name="opencode"
    def probe(self):
        health=super().probe()
        if health.available:
            try:
                result=subprocess.run([self.command,"models"],text=True,capture_output=True,timeout=20,check=False)
                health.models=[line.strip() for line in result.stdout.splitlines() if "/" in line]
            except (OSError, subprocess.TimeoutExpired): pass
            try:
                result=subprocess.run([self.command,"providers","list"],text=True,capture_output=True,timeout=20,check=False)
                text=(result.stdout + result.stderr).lower()
                health.authenticated=result.returncode == 0 and "credentials" in text
            except (OSError, subprocess.TimeoutExpired): pass
        return health
    def resolve_model(self, requested):
        if requested == "bigpickle": return "opencode/big-pickle"
        if requested and "/" not in requested: return f"opencode/{requested}"
        return super().resolve_model(requested)
    def build_command(self, *, worktree, model, prompt_file, role, reasoning=None, session_id=None, output_schema=None):
        c=[self.command,"run","--dir",str(worktree),"--model",model,"--agent",role,"--format","json","--auto","--file",str(prompt_file)]
        return c + (["--continue",session_id] if session_id else [])

def provider(name, config, runner=None):
    entry=config.get("providers",{}).get(name)
    if not entry or not entry.get("enabled",True): raise DependencyError(f"provider is not enabled: {name}")
    if name=="codex": return CodexProvider(entry.get("command","codex"),runner)
    if name=="opencode": return OpenCodeProvider(entry.get("command","opencode"),runner)
    raise ValidationError(f"unknown provider: {name}")
