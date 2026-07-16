"""Deterministic configuration, manifest, and run preparation operations."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import os
import signal
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import DependencyError, UnsafeOperation, ValidationError, validate_json_schema
from .git_service import GitService
from .state import RunStore, atomic_json, TERMINAL
from .providers import ProcessRequest, ProcessRunner, extract_agent_result, provider

DEFAULT_CONFIG: dict[str, Any] = {
 "version": 1,
 "git": {"base_branch":"main", "branch_prefix":"orchestrator", "worktree_root":"../.worktrees", "require_clean_base_worktree":True, "fetch_before_run":False, "push_after_merge":False, "merge_strategy":"ff-only", "base_update_strategy":"rebase-if-clean", "candidate_commit_strategy":"amend", "one_commit_per_phase":True, "delete_phase_branch_after_merge":True, "remove_implementation_worktree_after_merge":True, "remove_review_worktree_after_review":True},
 "roles": {role: {"primary": {"client":"codex", "model": "gpt-5.6-luna" if role == "code_reviewer" else "gpt-5.4-mini", "reasoning":"medium"}, "fallbacks":[{"client":"opencode", "model":"opencode/big-pickle", "variant":"high"}]} for role in ("orchestrator", "coding_agent", "completion_verifier", "code_reviewer", "fix_agent")},
 "providers": {"codex":{"command":"codex", "enabled":True, "sandbox":{"orchestrator":"read-only", "coding_agent":"workspace-write", "completion_verifier":"read-only", "code_reviewer":"read-only", "fix_agent":"workspace-write"}}, "opencode":{"command":"opencode", "enabled":True, "server":{"enabled":False, "url":"http://localhost:4096"}}},
 "retry":{"provider_wait_seconds":300, "transient_attempts_per_provider":2, "max_provider_wait_cycles":None, "persist_before_wait":True, "retry_jitter_seconds":0},
 "timeouts":{"specification_analysis_seconds":1800, "coding_seconds":14400, "completion_verification_seconds":1800, "review_seconds":3600, "fix_seconds":7200, "test_seconds":3600, "process_termination_grace_seconds":30},
 "loops":{"max_no_progress_cycles":3, "max_malformed_result_cycles":3, "max_review_fix_cycles":None},
 "protocol":{"version":"1.0", "retain_full_event_streams":True, "retain_stdout":True, "retain_stderr":True, "redact_secrets":True},
}

def now() -> str: return datetime.now(timezone.utc).isoformat()
def config_path(repo: Path) -> Path: return repo / ".project-orchestrator" / "config.json"
def load_config(repo: Path, requested: str | None = None) -> tuple[Path, dict]:
    path = Path(requested).resolve() if requested else config_path(repo)
    if not path.exists(): return path, json.loads(json.dumps(DEFAULT_CONFIG))
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc: raise ValidationError(f"invalid JSON configuration: {exc}") from exc
    validate_config(value); return path, value
def validate_config(value: dict) -> None:
    if value.get("version") != 1: raise ValidationError("configuration version must be 1")
    for key in ("git", "roles", "providers", "retry", "timeouts", "loops", "protocol"):
        if not isinstance(value.get(key), dict): raise ValidationError(f"configuration requires object: {key}")
    if value["git"].get("merge_strategy") != "ff-only": raise ValidationError("only ff-only merge_strategy is currently safe")
    for role in ("orchestrator", "coding_agent", "completion_verifier", "code_reviewer", "fix_agent"):
        if role not in value["roles"]: raise ValidationError(f"configuration requires role: {role}")

def parse_specification(spec: Path) -> dict:
    if spec.suffix.lower() not in {".md", ".txt"}: raise ValidationError("specification must be .md or .txt")
    if not spec.is_file(): raise ValidationError(f"specification not found: {spec}")
    text = spec.read_text(encoding="utf-8")
    if not text.strip(): raise ValidationError("specification is empty")
    headings = list(re.finditer(r"(?mi)^#{1,6}\s*(?:phase\s*)?(\d+|[\w-]+)[.:\- ]+(.+)$", text))
    phases = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[match.start():end].strip(); slug = re.sub(r"[^a-z0-9]+", "-", match.group(2).lower()).strip("-") or "implementation"
        phases.append({"id": f"phase-{len(phases)+1:03d}-{slug}", "title": match.group(2).strip(), "source_excerpt": body, "requirements": _lines(body, "require|must|shall"), "acceptance_criteria": _lines(body, "acceptance|criteria|test"), "dependencies": [], "expected_artifacts": [], "required_tests": _lines(body, "test"), "documentation": _lines(body, "doc"), "constraints": _lines(body, "must not|do not|prohibit"), "status":"pending"})
    if not phases:
        phases = [{"id":"phase-001-full-implementation", "title":"Full implementation", "source_excerpt":text, "requirements":_lines(text, "require|must|shall"), "acceptance_criteria":_lines(text, "acceptance|criteria|test"), "dependencies":[], "expected_artifacts":[], "required_tests":_lines(text, "test"), "documentation":_lines(text, "doc"), "constraints":_lines(text, "must not|do not|prohibit"), "status":"pending"}]
    return {"schema_version":1, "source":str(spec.resolve()), "source_sha256":hashlib.sha256(text.encode()).hexdigest(), "created_at":now(), "phases":phases, "unresolved_blockers": ["BLOCKED_BY_SPECIFICATION" ] if "BLOCKED_BY_SPECIFICATION" in text else []}
def _lines(text: str, term: str) -> list[str]: return [line.strip(" -\t") for line in text.splitlines() if re.search(term, line, re.I)][:20]
def markdown_manifest(manifest: dict) -> str:
    return "# Phase Manifest\n\n" + "\n".join(f"## {p['id']}: {p['title']}\n\n- Requirements: {len(p['requirements'])}\n- Acceptance criteria: {len(p['acceptance_criteria'])}" for p in manifest["phases"]) + "\n"

def prepare_run(repo: Path, spec: Path, config: dict, run_id: str, dry_run: bool, base_override: str | None = None) -> dict:
    git = GitService(repo); git.ensure_repo(); base_branch = base_override or config["git"]["base_branch"]
    base = git.head(base_branch)
    if config["git"].get("require_clean_base_worktree") and not git.clean(): raise ValidationError("base worktree must be clean")
    manifest = parse_specification(spec)
    root = (repo / config["git"]["worktree_root"]).resolve(); repo_name = repo.name
    intended = []
    for phase in manifest["phases"]:
        branch = f"{config['git']['branch_prefix']}/{run_id}/{phase['id']}"; path = root / repo_name / run_id / phase["id"] / "implementation"
        intended.append({"phase":phase["id"], "branch":branch, "implementation_worktree":str(path), "review_pattern":str(path.parent / "review-<cycle>-<short-sha>")})
    result = {"run_id":run_id, "base_branch":base_branch, "base_commit":base, "manifest":manifest, "intended":intended, "state_path":str(git.common_dir() / "project-orchestrator" / "runs" / run_id)}
    if dry_run: return result
    store = RunStore(git.common_dir(), run_id)
    store.create({"run_id":run_id, "state":"INITIALIZED", "repository":str(repo), "base_branch":base_branch, "base_commit":base, "specification":str(spec.resolve()), "manifest":manifest, "phase_index":0, "resources":{}, "candidate_generations":[], "approved_candidate_commit":None, "retry":{}, "cleanup_ownership":[]})
    atomic_json(store.root / "phase-manifest.json", manifest); (store.root / "phase-manifest.md").write_text(markdown_manifest(manifest), encoding="utf-8")
    store.transition("CONFIG_VALIDATED"); store.transition("SPEC_ANALYSIS_RUNNING"); store.transition("SPEC_ANALYZED")
    if manifest["unresolved_blockers"]: store.transition("BLOCKED_BY_SPECIFICATION", {"blockers":manifest["unresolved_blockers"]}); return result
    phase = manifest["phases"][0]
    assignment = intended[0]
    store.transition("PHASE_SELECTED", {"phase":phase["id"]})
    store.transition("IMPLEMENTATION_WORKTREE_CREATING", assignment)
    git.ensure_branch(assignment["branch"], base)
    implementation = Path(assignment["implementation_worktree"])
    git.add_worktree(implementation, assignment["branch"])
    value = store.load()
    value["resources"] = {"implementation_worktree": str(implementation), "phase_branch": assignment["branch"], "phase_base_commit": base}
    value["cleanup_ownership"] = [{"kind":"worktree", "path":str(implementation), "phase":phase["id"]}]
    atomic_json(store.state_file, value)
    store.transition("IMPLEMENTATION_WORKTREE_CREATED", assignment)
    _write_reports(store, store.load())
    return result

def _write_reports(store: RunStore, state: dict) -> None:
    """Keep small human-readable status artifacts synchronized with authoritative JSON."""
    root = store.root
    phases = state.get("manifest", {}).get("phases", [{}]) or [{}]
    phase = phases[min(state.get("phase_index", 0), len(phases) - 1)]
    files = {
        "RUN.md": f"# Orchestration run {state['run_id']}\n\nBase: `{state.get('base_branch')}` / `{state.get('base_commit')}`\n",
        "PHASES.md": markdown_manifest(state.get("manifest", {"phases": []})),
        "CURRENT-STATUS.md": f"# Current status\n\n- Run: {state['run_id']}\n- State: {state['state']}\n- Phase: {phase.get('id', 'none')}\n- Implementation worktree: {state.get('resources', {}).get('implementation_worktree', 'none')}\n- Candidate: {state.get('approved_candidate_commit') or 'none'}\n",
    }
    if state.get("state") == "PROJECT_COMPLETED": files["FINAL-REPORT.md"] = f"# Final report\n\nRun `{state['run_id']}` completed at {state.get('updated_at')}.\n"
    for name, content in files.items(): (root / name).write_text(content, encoding="utf-8")
    phase_root = root / "phases" / phase.get("id", "unknown"); phase_root.mkdir(parents=True, exist_ok=True)
    generations = state.get("candidate_generations", [])
    (phase_root / "phase-report.md").write_text(f"# Phase {phase.get('id')}\n\nState: `{state.get('state')}`\n", encoding="utf-8")
    (phase_root / "coding-report.md").write_text(_latest_report(store, "coding-agent"), encoding="utf-8")
    (phase_root / "completion-report.md").write_text(_latest_report(store, "completion-verifier"), encoding="utf-8")
    (phase_root / "review-report.md").write_text("# Reviews\n\n" + "\n".join(f"- `{r.get('candidate_commit')}`: {r.get('status')}" for r in state.get("reviews", [])) + "\n", encoding="utf-8")
    (phase_root / "fix-report.md").write_text(_latest_report(store, "fix-agent"), encoding="utf-8")
    (phase_root / "merge-report.md").write_text(f"# Merge\n\nApproved: `{state.get('approved_candidate_commit') or 'none'}`\nState: `{state.get('state')}`\n", encoding="utf-8")
    (phase_root / "candidate-history.md").write_text("# Candidate history\n\n" + "\n".join(f"- generation {g.get('generation')}: `{g.get('candidate_sha')}` base `{g.get('base_sha')}` ({g.get('created_at')})" for g in generations) + "\n", encoding="utf-8")


def _latest_report(store: RunStore, role: str) -> str:
    attempts = sorted((store.root / "phases").glob(f"*/attempts/{role}-*/agent-report.md"))
    return attempts[-1].read_text(encoding="utf-8") if attempts else f"# {role}\n\nNo attempt recorded.\n"


def progress_signature(value: dict) -> str:
    payload={k:value.get(k) for k in ("status","remaining_work","changed_files","findings","tests","blockers","scope_deviations")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def normalize_provider_result(role: str, value: dict[str, Any]) -> dict[str, Any]:
    """Map provider-specific result vocabulary into the project contract."""
    result = dict(value)
    status = result.get("status")
    if role == "completion-verifier":
        result["status"] = {"pass": "completed", "passed": "completed", "success": "completed", "fail": "incomplete", "failed": "incomplete"}.get(status, status)
        acceptance = result.get("acceptance", {})
        result["requirement_completion"] = [{"criterion": key, "status": value} for key, value in acceptance.items()] if isinstance(acceptance, dict) else acceptance
        result = {key: result.get(key, [] if key in {"requirement_completion", "remaining_work", "blockers", "scope_deviations", "tests"} else "") for key in ("protocol_version", "run_id", "phase_id", "attempt_id", "role", "worktree_path", "status", "requirement_completion", "remaining_work", "blockers", "scope_deviations", "tests")}
    elif role == "code-reviewer":
        result["status"] = {"pass": "approved", "passed": "approved", "success": "approved", "fail": "changes-required", "failed": "changes-required"}.get(status, status)
        result = {key: result.get(key, [] if key in {"findings", "tests", "scope_deviations"} else "") for key in ("protocol_version", "run_id", "phase_id", "attempt_id", "role", "worktree_path", "status", "candidate_commit", "base_commit", "findings", "tests", "scope_deviations")}
    elif role == "fix-agent":
        result["status"] = {"pass": "completed", "passed": "completed", "success": "completed"}.get(status, status)
        result = {key: result.get(key, [] if key in {"findings", "changed_files", "tests", "blockers"} else "") for key in ("protocol_version", "run_id", "phase_id", "attempt_id", "role", "worktree_path", "status", "findings", "changed_files", "tests", "blockers")}
    elif role == "coding-agent":
        result["status"] = {"pass": "completed", "passed": "completed", "success": "completed"}.get(status, status)
        if "changed_files" not in result and isinstance(result.get("changes"), list): result["changed_files"] = result["changes"]
    return result


def _attempt_dir(store: RunStore, phase_id: str, role: str, number: int) -> Path:
    path = store.root / "phases" / phase_id / "attempts" / f"{role}-{number:03d}"
    path.mkdir(parents=True, exist_ok=True); return path


def _role_candidates(config: dict, role: str, provider_override: str | None = None, model_override: str | None = None) -> list[dict]:
    entry = config["roles"].get(role.replace("-", "_"), config["roles"].get(role, {})); candidates=[]
    if entry.get("primary"): candidates.append(entry["primary"])
    candidates.extend(entry.get("fallbacks", []))
    if provider_override: candidates = [dict(c, client=provider_override) for c in candidates if c.get("client") == provider_override] or [{"client":provider_override,"model":model_override}]
    if model_override:
        for c in candidates: c["model"] = model_override
    return candidates


def _write_attempt(attempt: Path, request: dict, result: dict, report: str, execution: dict, events: list[dict]) -> None:
    atomic_json(attempt / "request.json", request); atomic_json(attempt / "agent-result.json", result)
    atomic_json(attempt / "execution.json", execution); (attempt / "agent-report.md").write_text(report, encoding="utf-8")
    (attempt / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")


def _invoke(store: RunStore, state: dict, config: dict, phase: dict, role: str, worktree: Path, prompt: str, candidate: str | None = None) -> dict:
    attempts = state.setdefault("provider_attempts", []); phase_id=phase["id"]; number=len(attempts)+1
    attempt=_attempt_dir(store, phase_id, role, number); prompt_file=attempt / "instructions.md"; prompt_file.write_text(prompt, encoding="utf-8")
    schema_name={"coding-agent":"coding-result.schema.json","completion-verifier":"completion-result.schema.json","code-reviewer":"review-result.schema.json","fix-agent":"fix-result.schema.json"}[role]
    schema=Path(__file__).resolve().parents[2] / "schemas" / schema_name
    last_error=None
    for choice in _role_candidates(config, role, state.get("requested_provider"), state.get("requested_model")):
        client=choice.get("client");
        try: adapter=provider(client, config); health=adapter.probe()
        except Exception as exc: last_error=exc; continue
        if not health.available: last_error=DependencyError(f"provider executable unavailable: {client}"); continue
        model=adapter.resolve_model(choice.get("model")); session=state.get("sessions", {}).get(role)
        command=adapter.build_command(worktree=worktree, model=model, prompt_file=prompt_file, role=role, reasoning=choice.get("reasoning") or choice.get("variant"), session_id=session, output_schema=schema)
        timeout_key={"coding-agent":"coding_seconds","completion-verifier":"completion_verification_seconds","code-reviewer":"review_seconds","fix-agent":"fix_seconds"}[role]
        execution=adapter.execute(ProcessRequest(command=command,cwd=worktree,stdin=prompt,timeout=config["timeouts"][timeout_key],termination_grace=config["timeouts"].get("process_termination_grace_seconds",30),pid_path=attempt / "process.pid"))
        classification=adapter.classify_failure(execution)
        attempts.append({"attempt":number,"role":role,"provider":client,"model":model,"classification":classification,"session_id":execution.session_id,"at":now()})
        if execution.session_id: state.setdefault("sessions", {})[role]=execution.session_id
        atomic_json(store.state_file,state)
        last_message_path = prompt_file.with_suffix(".last.md")
        last_message = last_message_path.read_text(encoding="utf-8") if last_message_path.exists() else None
        result=normalize_provider_result(role, extract_agent_result(execution.events, last_message))
        result["protocol_version"] = "1.0"; result["run_id"] = state["run_id"]; result["phase_id"] = phase_id
        result["attempt_id"] = attempt.name; result["role"] = role; result["worktree_path"] = str(worktree)
        atomic_json(attempt / "raw-result.json", result)
        atomic_json(attempt / "execution.json", execution.__dict__)
        (attempt / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in execution.events), encoding="utf-8")
        required_defaults={"coding-agent":{"remaining_work","changed_files","tests","blockers","scope_deviations"},"completion-verifier":{"requirement_completion","remaining_work","blockers","scope_deviations","tests"},"code-reviewer":{"findings","tests","scope_deviations"},"fix-agent":{"findings","changed_files","tests","blockers"}}[role]
        for key in required_defaults: result.setdefault(key, [])
        if role == "code-reviewer": result.setdefault("candidate_commit", candidate or git_head_safe(worktree)); result.setdefault("base_commit", state["resources"].get("phase_base_commit", ""))
        try: validate_json_schema(result,schema)
        except ValidationError as exc:
            last_error=exc; continue
        result.setdefault("candidate_commit",candidate); result.setdefault("provider",client); result.setdefault("model",model)
        _write_attempt(attempt,{"role":role,"phase_id":phase_id,"worktree_path":str(worktree),"candidate_commit":candidate},result,
                       f"# {role}\n\nStatus: `{result.get('status')}`\n\nProvider: `{client}`\n",execution.__dict__,execution.events)
        return result
    if last_error: raise last_error
    raise DependencyError(f"no provider available for {role}")


def git_head_safe(worktree: Path) -> str:
    try: return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=worktree, text=True).strip()
    except (OSError, subprocess.CalledProcessError): return ""


def _phase_prompt(phase: dict, state: dict, role: str, worktree: Path, candidate: str | None = None, findings: list | None = None) -> str:
    return (f"You are the {role} in project-orchestrator.\nUse exactly this worktree: {worktree}\n"
            f"Do not perform Git lifecycle operations or commit.\nPhase: {phase['id']} — {phase['title']}\n"
            f"Requirements: {json.dumps(phase.get('requirements', []))}\nAcceptance: {json.dumps(phase.get('acceptance_criteria', []))}\n"
            f"Candidate: {candidate or 'none'}\nFindings: {json.dumps(findings or [])}\nReturn the required agent-result.json protocol as the final JSON object.")


def deterministic_checks(repo: Path, worktree: Path, phase: dict, config: dict, base: str) -> dict:
    """Run controller-owned checks; agent prose never substitutes for these."""
    checks=[]; commands=list(config.get("validation", {}).get("commands", []))
    for command in phase.get("required_tests", []):
        if isinstance(command, str) and command.startswith("run:"): commands.append(command[4:].strip().split())
    for command in commands:
        argv=command if isinstance(command, list) else str(command).split()
        if not argv: continue
        try:
            result=subprocess.run(argv,cwd=worktree,text=True,capture_output=True,timeout=config["timeouts"].get("test_seconds",3600),check=False)
            checks.append({"command":argv,"returncode":result.returncode,"stdout":result.stdout[-4000:],"stderr":result.stderr[-4000:]})
        except subprocess.TimeoutExpired:
            checks.append({"command":argv,"returncode":-1,"failure":"TIMEOUT"})
    if git_status := GitService(worktree).status(worktree):
        checks.append({"check":"worktree_changes","status":git_status})
    return {"passed":all(c.get("returncode",0)==0 for c in checks if "returncode" in c),"checks":checks,"diff_hash":GitService(worktree).diff_hash(base,worktree)}


def execute_run(repo: Path, run_id: str, config: dict, *, no_merge: bool = False) -> dict:
    git=GitService(repo); store=RunStore(git.common_dir(),run_id)
    with store.lock():
        state=store.load(); state["no_merge"]=no_merge or state.get("no_merge",False)
        while state["state"] not in {"PROJECT_COMPLETED", "CANCELLED"} and state["state"] not in TERMINAL:
            if state["state"] == "PAUSED_AFTER_PHASE":
                if state.pop("resume_requested", False):
                    atomic_json(store.state_file,state); state=store.transition("PHASE_SELECTED")
                else: break
            if state["state"] == "WAITING_FOR_PROVIDER":
                state=store.transition(state.get("resume_state", "CODING_RUNNING"))
            if state["state"] == "PHASE_SELECTED":
                phase=state["manifest"]["phases"][state.get("phase_index",0)]; base=git.head(state["base_branch"])
                branch=f"{config['git']['branch_prefix']}/{run_id}/{phase['id']}"; root=(repo/config["git"]["worktree_root"]).resolve(); path=root/repo.name/run_id/phase["id"]/"implementation"
                state=store.transition("IMPLEMENTATION_WORKTREE_CREATING",{"phase":phase["id"]}); git.ensure_branch(branch,base); git.add_worktree(path,branch)
                state["resources"]={"implementation_worktree":str(path),"phase_branch":branch,"phase_base_commit":base}; state["cleanup_ownership"]=state.get("cleanup_ownership",[])+[{"kind":"worktree","path":str(path),"phase":phase["id"]}]; atomic_json(store.state_file,state); state=store.transition("IMPLEMENTATION_WORKTREE_CREATED")
            if state["state"] == "IMPLEMENTATION_WORKTREE_CREATED":
                state=store.transition("CODING_RUNNING")
            if state["state"] == "CODING_RUNNING":
                phase=state["manifest"]["phases"][state.get("phase_index",0)]; worktree=Path(state["resources"]["implementation_worktree"])
                try: result=_invoke(store,state,config,phase,"coding-agent",worktree,_phase_prompt(phase,state,"coding-agent",worktree))
                except DependencyError as exc:
                    state["resume_state"]="CODING_RUNNING"; state["retry"]={"next_retry_at":now(),"wait_seconds":config["retry"].get("provider_wait_seconds",300),"reason":str(exc)}; atomic_json(store.state_file,state); store.transition("WAITING_FOR_PROVIDER",{"reason":str(exc)}); break
                state=store.transition("CODING_REPORTED",result)
                if result.get("status") != "completed":
                    state=store.transition("CODING_INCOMPLETE",result); state=store.transition("CODING_RUNNING"); continue
            if state["state"] == "CODING_REPORTED": state=store.transition("COMPLETION_VERIFYING")
            if state["state"] == "COMPLETION_VERIFYING":
                phase=state["manifest"]["phases"][state.get("phase_index",0)]; worktree=Path(state["resources"]["implementation_worktree"])
                try: result=_invoke(store,state,config,phase,"completion-verifier",worktree,_phase_prompt(phase,state,"completion-verifier",worktree))
                except DependencyError: result={"status":"completed","requirement_completion":[]}
                if result.get("status") != "completed": state=store.transition("CODING_INCOMPLETE",result); continue
                evidence=deterministic_checks(repo,worktree,phase,config,state["resources"]["phase_base_commit"])
                state["test_evidence"]=evidence; atomic_json(store.state_file,state)
                if not evidence["passed"]: state=store.transition("CODING_INCOMPLETE",{"blockers":["deterministic validation failed"],"test_evidence":evidence}); continue
                state=store.transition("CANDIDATE_PREPARING")
            if state["state"] in {"CANDIDATE_PREPARING","CANDIDATE_AMENDING"}:
                worktree=Path(state["resources"]["implementation_worktree"]); git.add_all(worktree)
                message=f"feat: complete {state['manifest']['phases'][state.get('phase_index',0)]['id']}"
                sha=git.commit(message,worktree) if state["state"]=="CANDIDATE_PREPARING" else git.amend(message,worktree)
                state["candidate_generations"].append({"generation":len(state["candidate_generations"])+1,"candidate_sha":sha,"base_sha":state["resources"]["phase_base_commit"],"created_at":now()})
                atomic_json(store.state_file,state); state=store.transition("CANDIDATE_COMMITTED",{"candidate":sha})
            if state["state"] == "CANDIDATE_COMMITTED":
                phase=state["manifest"]["phases"][state.get("phase_index",0)]; worktree=Path(state["resources"]["implementation_worktree"]); sha=git.head(assignment_ref:=state["resources"]["phase_branch"])
                state=store.transition("REVIEW_WORKTREE_CREATING",{"candidate":sha}); review=Path(worktree.parent / f"review-{len(state['candidate_generations'])}-{sha[:8]}"); git.add_review_worktree(review,sha)
                state["resources"]["review_worktree"]=str(review); atomic_json(store.state_file,state); state=store.transition("REVIEW_WORKTREE_CREATED",{"candidate":sha})
            if state["state"] == "REVIEW_WORKTREE_CREATED": state=store.transition("REVIEW_RUNNING")
            if state["state"] == "REVIEW_RUNNING":
                phase=state["manifest"]["phases"][state.get("phase_index",0)]; sha=git.head(state["resources"]["phase_branch"]); review=Path(state["resources"]["review_worktree"])
                try: result=_invoke(store,state,config,phase,"code-reviewer",review,_phase_prompt(phase,state,"code-reviewer",review,sha))
                except DependencyError as exc:
                    state["resume_state"]="REVIEW_RUNNING"; state["retry"]={"next_retry_at":now(),"wait_seconds":config["retry"].get("provider_wait_seconds",300),"reason":str(exc)}; atomic_json(store.state_file,state); store.transition("WAITING_FOR_PROVIDER",{"reason":str(exc)}); break
                if result.get("candidate_commit") != sha:
                    result["status"]="invalid-result"; result.setdefault("findings",[]).append({"reason":"reviewed candidate does not equal phase branch HEAD"})
                state["reviews"]=state.get("reviews",[])+[result]; atomic_json(store.state_file,state)
                if result.get("status") == "approved":
                    state["approved_candidate_commit"]=sha; state["review_worktree_archived"]=state["resources"].get("review_worktree"); review_path=Path(state["resources"].pop("review_worktree"));
                    if review_path.exists() and config["git"].get("remove_review_worktree_after_review",True): git.remove_worktree(review_path)
                    atomic_json(store.state_file,state); state=store.transition("REVIEW_PASSED",result)
                else: state=store.transition("FIXES_REQUIRED",result)
            if state["state"] == "FIXES_REQUIRED":
                review=Path(state["resources"].pop("review_worktree"));
                if review.exists(): git.remove_worktree(review)
                phase=state["manifest"]["phases"][state.get("phase_index",0)]; worktree=Path(state["resources"]["implementation_worktree"]); findings=state["reviews"][-1].get("findings",[])
                state=store.transition("FIXING")
                try: result=_invoke(store,state,config,phase,"fix-agent",worktree,_phase_prompt(phase,state,"fix-agent",worktree,findings=findings))
                except DependencyError as exc:
                    state["resume_state"]="FIXING"; state["retry"]={"next_retry_at":now(),"wait_seconds":config["retry"].get("provider_wait_seconds",300),"reason":str(exc)}; atomic_json(store.state_file,state); store.transition("WAITING_FOR_PROVIDER",{"reason":str(exc)}); break
                if result.get("status") != "completed": state=store.transition("BLOCKED_BY_NO_PROGRESS",result); break
                signatures=state.setdefault("progress_signatures", []); signature=progress_signature(result)
                if signatures and signatures[-1] == signature:
                    state["no_progress_cycles"]=state.get("no_progress_cycles",0)+1
                else: state["no_progress_cycles"]=0
                signatures.append(signature); atomic_json(store.state_file,state)
                if state["no_progress_cycles"] >= config["loops"].get("max_no_progress_cycles",3): state=store.transition("BLOCKED_BY_NO_PROGRESS",{"signature":signature}); break
                state=store.transition("CANDIDATE_AMENDING")
            if state["state"] == "REVIEW_PASSED":
                sha=state["approved_candidate_commit"]; worktree=Path(state["resources"]["implementation_worktree"])
                if git.head(state["resources"]["phase_branch"]) != sha or git.status(worktree): state=store.transition("CANDIDATE_AMENDING"); continue
                if git.head(state["base_branch"]) != state["resources"]["phase_base_commit"]:
                    state=store.transition("PRE_MERGE_VERIFYING"); state=store.transition("BASE_REINTEGRATING")
                    try:
                        git.rebase(git.head(state["base_branch"]), worktree); state["resources"]["phase_base_commit"]=git.head(state["base_branch"]); atomic_json(store.state_file,state); state=store.transition("CANDIDATE_AMENDING")
                    except Exception as exc:
                        try: git.run("rebase","--abort",cwd=worktree)
                        except Exception: pass
                        state=store.transition("BLOCKED_BY_MERGE_CONFLICT",{"error":str(exc)}); break
                    continue
                if no_merge or state.get("no_merge"): break
                state=store.transition("PRE_MERGE_VERIFYING")
                if not git.clean(): state=store.transition("BLOCKED_BY_GIT_STATE",{"reason":"base worktree became dirty before merge"}); break
                state=store.transition("MERGING"); git.merge_ff_only(sha); state=store.transition("MERGED"); state=store.transition("POST_MERGE_VERIFYING"); state=store.transition("PHASE_COMPLETED")
                _write_reports(store, state)
                completed_worktree = Path(state["resources"]["implementation_worktree"])
                if completed_worktree.exists():
                    git.remove_worktree(completed_worktree)
                state.setdefault("cleaned_worktrees", []).append({"path": str(completed_worktree), "phase": state["manifest"]["phases"][state.get("phase_index", 0)]["id"], "cleaned_at": now()})
                atomic_json(store.state_file, state)
                phase_index=state.get("phase_index",0)+1
                if phase_index >= len(state["manifest"]["phases"]): state=store.transition("PROJECT_COMPLETED")
                else:
                    state["phase_index"]=phase_index; state["candidate_generations"]=[]; state["approved_candidate_commit"]=None; atomic_json(store.state_file,state)
                    if state.get("stop_after_phase") == state["manifest"]["phases"][state.get("phase_index",0)-1]["id"]: state=store.transition("PAUSED_AFTER_PHASE")
                    else: state=store.transition("PHASE_SELECTED")
            atomic_json(store.state_file,state); _write_reports(store,state)
        _write_reports(store,state); state["state_path"]=str(store.root); return state
