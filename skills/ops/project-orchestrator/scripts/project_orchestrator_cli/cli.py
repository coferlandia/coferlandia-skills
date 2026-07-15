"""Argument parsing and command dispatch; orchestration mechanics stay in modules."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import uuid
import signal
from pathlib import Path
from typing import Any

from .contracts import EXIT_ARGUMENTS, Envelope, OrchestratorError, ValidationError, failure, validate_json_schema
from .engine import DEFAULT_CONFIG, config_path, load_config, prepare_run, validate_config, execute_run
from .git_service import GitService
from .providers import provider
from .state import RunStore, TERMINAL, atomic_json, utcnow

COMMANDS = [
 {"name":"doctor","mutating":False,"supports_dry_run":False,"supports_json":True}, {"name":"init-config","mutating":True,"supports_dry_run":False,"supports_json":True}, {"name":"validate-config","mutating":False,"supports_dry_run":False,"supports_json":True}, {"name":"providers.list","mutating":False,"supports_dry_run":False,"supports_json":True}, {"name":"providers.probe","mutating":False,"supports_dry_run":False,"supports_json":True}, {"name":"run","mutating":True,"supports_dry_run":True,"supports_json":True}, {"name":"resume","mutating":True,"supports_dry_run":False,"supports_json":True}, {"name":"status","mutating":False,"supports_dry_run":False,"supports_json":True}, {"name":"retry","mutating":True,"supports_dry_run":False,"supports_json":True}, {"name":"cancel","mutating":True,"supports_dry_run":False,"supports_json":True}, {"name":"cleanup","mutating":True,"supports_dry_run":True,"supports_json":True}, {"name":"validate-result","mutating":False,"supports_dry_run":False,"supports_json":True},
]
def parser() -> argparse.ArgumentParser:
 p=argparse.ArgumentParser(description="Deterministic, commit-based development phase orchestrator")
 p.add_argument("--repo", default=".", help="target Git repository (default: current directory)")
 p.add_argument("--json", action="store_true", help="emit stable JSON envelope")
 sub=p.add_subparsers(dest="command", required=True)
 for n in ("version","self-check","capabilities","doctor","init-config","validate-config"): sub.add_parser(n)
 pp=sub.add_parser("providers"); pp_sub=pp.add_subparsers(dest="providers_command", required=True); pp_sub.add_parser("list"); probe=pp_sub.add_parser("probe"); probe.add_argument("name", nargs="?")
 run=sub.add_parser("run"); run.add_argument("--spec", required=True); run.add_argument("--config"); run.add_argument("--base-branch"); run.add_argument("--run-id"); run.add_argument("--start-phase"); run.add_argument("--stop-after-phase"); run.add_argument("--provider"); run.add_argument("--model"); run.add_argument("--reasoning"); run.add_argument("--no-merge", action="store_true"); run.add_argument("--dry-run", action="store_true")
 for name in ("resume","retry","cancel","cleanup"):
  q=sub.add_parser(name); q.add_argument("run_id");
  if name=="cleanup": q.add_argument("--dry-run", action="store_true")
 status=sub.add_parser("status"); status.add_argument("run_id", nargs="?")
 vr=sub.add_parser("validate-result"); vr.add_argument("--role", required=True, choices=["coding-agent","completion-verifier","code-reviewer","fix-agent"]); vr.add_argument("--file", required=True)
 return p
def repo(args: argparse.Namespace) -> Path:
 path=Path(args.repo).resolve()
 if not path.is_dir(): raise ValidationError(f"repository directory does not exist: {path}")
 return path
def json_or_human(envelope: Envelope, as_json: bool) -> None:
 payload=envelope.payload()
 if as_json or not sys.stdout.isatty(): print(json.dumps(payload, indent=2, sort_keys=True))
 else:
  print(f"{payload['status']}: {payload['command']}"); print(json.dumps(payload['result'], indent=2))
def get_store(path: Path, run_id: str) -> RunStore: return RunStore(GitService(path).common_dir(), run_id)
def cmd_doctor(path: Path) -> Envelope:
 git=GitService(path); git.ensure_repo(); cp, config=load_config(path)
 schemas=Path(__file__).resolve().parents[2]/"schemas"; required=list(schemas.glob("*.schema.json"))
 health={name: provider(name, config).probe().__dict__ for name in config["providers"] if config["providers"][name].get("enabled",True)}
 configured_models={role: {"primary": value.get("primary",{}).get("model"), "fallbacks":[item.get("model") for item in value.get("fallbacks",[])]} for role,value in config.get("roles",{}).items()}
 runs=(git.common_dir()/"project-orchestrator"/"runs"); interrupted=[]; stale_locks=[]; collisions=[]
 if runs.exists():
  for state in runs.glob("*/run-state.json"):
   value=json.loads(state.read_text());
   if value.get("state") not in TERMINAL: interrupted.append(value.get("run_id"))
  for lock in runs.glob("*/.lock"):
   try:
    pid=json.loads(lock.read_text()).get("pid");
    if os.name != "nt" and not Path(f"/proc/{pid}").exists(): stale_locks.append(str(lock))
   except (OSError, json.JSONDecodeError): stale_locks.append(str(lock))
  managed=[str(Path(x.get("path")).resolve()) for f in runs.glob("*/run-state.json") for x in json.loads(f.read_text()).get("cleanup_ownership",[]) if x.get("kind")=="worktree"]
  collisions=sorted({p for p in managed if managed.count(p)>1})
 return Envelope("doctor", result={"python":sys.version.split()[0],"git":True,"repository":str(path),"base_branch":config["git"]["base_branch"],"base_exists":bool(git.head(config["git"]["base_branch"])),"clean":git.clean(),"config":str(cp),"schemas":len(required),"providers":health,"configured_models":configured_models,"interrupted_runs":interrupted,"stale_locks":stale_locks,"managed_worktree_collisions":collisions,"write_permissions":os.access(path,os.W_OK)}, warnings=["providers are probed without consuming model usage"])
def cmd_validate_result(args: argparse.Namespace) -> Envelope:
 file=Path(args.file).resolve()
 try: value=json.loads(file.read_text(encoding="utf-8"))
 except (OSError,json.JSONDecodeError) as exc: raise ValidationError(f"invalid result JSON: {exc}") from exc
 schema_name = {"coding-agent":"coding-result.schema.json", "completion-verifier":"completion-result.schema.json", "code-reviewer":"review-result.schema.json", "fix-agent":"fix-result.schema.json"}[args.role]
 schema = Path(__file__).resolve().parents[2] / "schemas" / schema_name
 validate_json_schema(value, schema)
 if value["role"] != args.role: raise ValidationError(f"result role {value['role']} does not match requested {args.role}")
 return Envelope("validate-result", result={"valid":True,"role":args.role,"status":value["status"],"schema":str(schema)})
def cmd_cleanup(path: Path, args: argparse.Namespace) -> Envelope:
 store=get_store(path,args.run_id); value=store.load(); owned=value.get("cleanup_ownership",[]); removed=[]
 if not args.dry_run:
  git=GitService(path)
  for item in owned:
   candidate=Path(item["path"]).resolve()
   if item.get("kind")!="worktree" or args.run_id not in candidate.parts: raise ValidationError("run contains unsafe cleanup ownership record")
   if candidate.exists(): git.remove_worktree(candidate); removed.append(str(candidate))
  value["cleanup_at"]=utcnow(); atomic_json(store.state_file,value)
 return Envelope("cleanup", changed=bool(removed), result={"owned_resources":owned,"removed":removed,"dry_run":args.dry_run})
def dispatch(args: argparse.Namespace) -> Envelope:
 path=repo(args); cmd=args.command
 if cmd=="version": return Envelope("version",result={"version":"1.0.0"})
 if cmd=="capabilities": return Envelope("capabilities",result={"version":"1.0.0","commands":COMMANDS})
 if cmd=="self-check": return cmd_doctor(path)
 if cmd=="doctor": return cmd_doctor(path)
 if cmd=="init-config":
  target=config_path(path)
  if target.exists(): return Envelope("init-config",result={"path":str(target),"created":False})
  atomic_json(target,DEFAULT_CONFIG); return Envelope("init-config",changed=True,result={"path":str(target),"created":True},artifacts=[{"path":str(target),"action":"created"}])
 if cmd=="validate-config":
  target,value=load_config(path); validate_config(value); return Envelope("validate-config",result={"valid":True,"path":str(target)})
 if cmd=="providers":
  _, config=load_config(path); names=[args.name] if args.providers_command=="probe" and args.name else list(config["providers"])
  items=[]
  for name in names:
   item=provider(name,config).probe(); items.append(item.__dict__)
  return Envelope(f"providers.{args.providers_command}",result={"providers":items})
 if cmd=="run":
  _, config=load_config(path,args.config); run_id=args.run_id or f"run-{uuid.uuid4().hex[:12]}"; value=prepare_run(path,Path(args.spec).resolve(),config,run_id,args.dry_run,args.base_branch)
  value.update({"dry_run":args.dry_run,"no_merge":args.no_merge,"requested_provider":args.provider,"requested_model":args.model,"requested_reasoning":args.reasoning,"start_phase":args.start_phase,"stop_after_phase":args.stop_after_phase})
  if not args.dry_run:
   store=get_store(path,run_id); persisted=store.load(); persisted.update({k:v for k,v in value.items() if k in {"no_merge","requested_provider","requested_model","requested_reasoning","start_phase","stop_after_phase"}}); atomic_json(store.state_file,persisted)
   # The implicit default configuration is used for planning; execution starts only
   # after a config is explicitly materialized (or a provider override is supplied).
   if (config_path(path).exists() or args.provider) and any(shutil.which(c.get("command",name)) for name,c in config.get("providers",{}).items() if c.get("enabled",True)):
    value=execute_run(path,run_id,config,no_merge=args.no_merge)
  return Envelope("run",changed=not args.dry_run,result=value,artifacts=[] if args.dry_run else [{"path":value["state_path"],"action":"created"}])
 if cmd=="status":
  git=GitService(path); runs=git.common_dir()/"project-orchestrator"/"runs"
  if args.run_id: return Envelope("status",result=get_store(path,args.run_id).load())
  values=[json.loads(f.read_text()) for f in sorted(runs.glob("*/run-state.json"))] if runs.exists() else []
  return Envelope("status",result={"runs":values})
 if cmd=="cancel":
  store=get_store(path,args.run_id); value=store.load()
  terminated=[]
  for pid_file in store.root.glob("phases/*/attempts/*/process.pid"):
   try:
    pid=int(pid_file.read_text().strip()); os.kill(pid, signal.SIGTERM); terminated.append(pid)
   except (OSError, ValueError): pass
  if value["state"] not in TERMINAL: value=store.transition("CANCELLED",{"reason":"explicit user cancellation"})
  return Envelope("cancel",changed=True,result={**value,"terminated_pids":terminated},warnings=["implementation worktrees, candidates, and reports are preserved"])
 if cmd=="resume" or cmd=="retry":
  store=get_store(path,args.run_id); value=store.load(); _, config=load_config(path)
  if value["state"] in TERMINAL: raise ValidationError(f"cannot {cmd} terminal run in state {value['state']}")
  if cmd == "resume": value["resume_requested"] = True; atomic_json(store.state_file, value)
  value=execute_run(path,args.run_id,config,no_merge=value.get("no_merge",False))
  return Envelope(cmd,changed=True,result=value)
 if cmd=="cleanup": return cmd_cleanup(path,args)
 if cmd=="validate-result": return cmd_validate_result(args)
 raise ValidationError(f"unknown command: {cmd}")
def main(argv: list[str] | None = None) -> int:
 raw = list(sys.argv[1:] if argv is None else argv)
 # Permit the documented --json flag before or after a subcommand.
 if "--json" in raw:
  raw.remove("--json"); raw.insert(0, "--json")
 args=parser().parse_args(raw)
 command=args.command if args.command!="providers" else f"providers.{args.providers_command}"
 try: env=dispatch(args); json_or_human(env,args.json); return 0
 except OrchestratorError as exc: json_or_human(failure(command,exc),True); return exc.code
 except Exception as exc: json_or_human(failure(command,exc),True); return 1
