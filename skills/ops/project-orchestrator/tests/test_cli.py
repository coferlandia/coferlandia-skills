"""Black-box tests for the deterministic project-orchestrator CLI."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
CLI = SKILL / "scripts" / "project-orchestrator-cli.py"
sys.path.insert(0, str(SKILL / "scripts"))


def run_cli(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=repo, text=True, capture_output=True
    )


class CliTests(unittest.TestCase):
    def make_repo(self) -> Path:
        directory = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-b", "main", str(directory)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(directory), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(directory), "config", "user.name", "Test"], check=True)
        subprocess.run(["git", "-C", str(directory), "config", "core.autocrlf", "false"], check=True)
        (directory / "README.md").write_text("test\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(directory), "add", "README.md"], check=True)
        subprocess.run(["git", "-C", str(directory), "commit", "-m", "initial"], check=True, capture_output=True)
        return directory

    def test_capabilities_is_a_json_envelope(self) -> None:
        result = run_cli(self.make_repo(), "capabilities", "--json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "success")
        self.assertIn("run", [item["name"] for item in payload["result"]["commands"]])

    def test_dry_run_creates_no_branch_or_worktree(self) -> None:
        repo = self.make_repo()
        spec = Path(tempfile.mkdtemp()) / "plan.md"
        spec.write_text("# Phase 1: add a thing\n\nAcceptance criteria: tests pass.\n", encoding="utf-8")
        result = run_cli(repo, "run", "--spec", str(spec), "--dry-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["changed"])
        branches = subprocess.run(["git", "-C", str(repo), "branch", "--list", "orchestrator/*"], text=True, capture_output=True).stdout
        self.assertEqual(branches.strip(), "")

    def test_validate_result_rejects_wrong_role(self) -> None:
        repo = self.make_repo()
        result_file = repo / "result.json"
        result_file.write_text(json.dumps({"protocol_version": "1.0", "role": "code-reviewer", "status": "approved"}), encoding="utf-8")
        result = run_cli(repo, "validate-result", "--role", "coding-agent", "--file", str(result_file), "--json")
        self.assertEqual(result.returncode, 3)
        self.assertEqual(json.loads(result.stdout)["status"], "failure")

    def test_init_config_is_idempotent(self) -> None:
        repo = self.make_repo()
        first = run_cli(repo, "init-config", "--json")
        second = run_cli(repo, "init-config", "--json")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertFalse(json.loads(second.stdout)["changed"])

    def test_run_assigns_one_owned_implementation_worktree(self) -> None:
        repo = self.make_repo()
        spec = Path(tempfile.mkdtemp()) / "plan.md"
        spec.write_text("# Phase 1: add a thing\n", encoding="utf-8")
        result = run_cli(repo, "run", "--spec", str(spec), "--run-id", "run-test", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        state = run_cli(repo, "status", "run-test", "--json")
        value = json.loads(state.stdout)["result"]
        self.assertEqual(value["state"], "IMPLEMENTATION_WORKTREE_CREATED")
        self.assertTrue(Path(value["resources"]["implementation_worktree"]).is_dir())
        cleanup = run_cli(repo, "cleanup", "run-test", "--json")
        self.assertEqual(cleanup.returncode, 0, cleanup.stderr)

    def test_validate_result_checks_complete_schema(self) -> None:
        repo = self.make_repo()
        result_file = repo / "result.json"
        result_file.write_text(json.dumps({
            "protocol_version": "1.0", "role": "coding-agent", "status": "completed",
            "remaining_work": "not-an-array"
        }), encoding="utf-8")
        result = run_cli(repo, "validate-result", "--role", "coding-agent", "--file", str(result_file), "--json")
        self.assertEqual(result.returncode, 3)
        self.assertIn("schema", json.loads(result.stdout)["errors"][0].lower())

    def test_provider_runner_captures_jsonl_and_final_response(self) -> None:
        from project_orchestrator_cli.providers import ProcessRunner, ProcessRequest
        repo_path = self.make_repo()
        request = ProcessRequest(command=[sys.executable, "-c", "import sys; print('{\\\"session_id\\\":\\\"s1\\\"}'); print('{\\\"status\\\":\\\"completed\\\"}')"], cwd=repo_path, timeout=5)
        result = ProcessRunner().execute(request)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.session_id, "s1")
        self.assertEqual(result.events[-1]["status"], "completed")

    def test_extract_agent_result_from_codex_agent_message_event(self) -> None:
        from project_orchestrator_cli.providers import extract_agent_result
        payload = {"status": "completed", "role": "coding-agent"}
        events = [
            {"type": "thread.started", "thread_id": "t1"},
            {"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(payload)}},
            {"type": "tool.completed", "status": "completed"},
        ]
        self.assertEqual(extract_agent_result(events), payload)

    def test_extract_agent_result_from_nested_opencode_text_event(self) -> None:
        from project_orchestrator_cli.providers import extract_agent_result
        payload = {"status": "completed", "role": "coding-agent"}
        events = [{"type": "text", "part": {"type": "text", "text": json.dumps(payload)}}]
        self.assertEqual(extract_agent_result(events), payload)

    def test_normalize_provider_result_to_completion_contract(self) -> None:
        from project_orchestrator_cli.engine import normalize_provider_result
        result = normalize_provider_result("completion-verifier", {
            "status": "pass", "acceptance": {"hello.txt exists": "pass"},
            "findings": [], "summary": "ok", "worktree": "/tmp/work"
        })
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["requirement_completion"][0]["criterion"], "hello.txt exists")
        self.assertNotIn("summary", result)

    def test_run_lock_rejects_second_owner(self) -> None:
        from project_orchestrator_cli.state import RunLock
        common = Path(tempfile.mkdtemp())
        first = RunLock(common, "run-lock")
        second = RunLock(common, "run-lock")
        first.acquire()
        try:
            with self.assertRaises(Exception):
                second.acquire()
        finally:
            first.release()

    def test_simulated_clock_advances_retry_without_waiting(self) -> None:
        from project_orchestrator_cli.state import SimulatedClock, retry_due
        clock = SimulatedClock()
        retry_at = (clock.now() + __import__("datetime").timedelta(seconds=300)).isoformat()
        self.assertFalse(retry_due(retry_at, clock.now()))
        clock.sleep(300)
        self.assertTrue(retry_due(retry_at, clock.now()))

    def test_default_model_ids_match_provider_syntax(self) -> None:
        from project_orchestrator_cli.engine import DEFAULT_CONFIG
        from project_orchestrator_cli.providers import OpenCodeProvider
        self.assertEqual(DEFAULT_CONFIG["roles"]["code_reviewer"]["primary"]["model"], "gpt-5.6-luna")
        self.assertEqual(DEFAULT_CONFIG["roles"]["coding_agent"]["primary"]["model"], "gpt-5.4-mini")
        self.assertEqual(OpenCodeProvider("opencode").resolve_model("bigpickle"), "opencode/big-pickle")
        command = OpenCodeProvider("opencode").build_command(worktree=Path("/tmp"), model="opencode/big-pickle", prompt_file=Path("/tmp/prompt.md"), role="coding-agent")
        self.assertIn("--auto", command)

    def test_fake_provider_completes_candidate_review_and_merge(self) -> None:
        repo = self.make_repo()
        fake = repo / "fake-provider.py"
        fake.write_text("""#!/usr/bin/env python3
import json, pathlib, re, sys
prompt = sys.stdin.read()
role = 'code-reviewer' if 'code-reviewer' in prompt else ('completion-verifier' if 'completion-verifier' in prompt else ('fix-agent' if 'fix-agent' in prompt else 'coding-agent'))
candidate = re.search(r'Candidate: ([0-9a-f]+)', prompt)
result = {'protocol_version':'1.0','role':role,'status':'approved' if role == 'code-reviewer' else 'completed','remaining_work':[],'requirement_completion':[],'findings':[],'candidate_commit':candidate.group(1) if candidate else '','base_commit':'base','changed_files':[],'tests':[],'blockers':[],'scope_deviations':[]}
if role == 'coding-agent':
    result = {k: result[k] for k in ('protocol_version','role','status','remaining_work','changed_files','tests','blockers','scope_deviations')}
elif role == 'completion-verifier':
    result = {k: result[k] for k in ('protocol_version','role','status','requirement_completion','remaining_work','blockers','scope_deviations','tests')}
elif role == 'fix-agent':
    result = {k: result[k] for k in ('protocol_version','role','status','findings','changed_files','tests','blockers')}
elif role == 'code-reviewer':
    result = {k: result[k] for k in ('protocol_version','role','status','candidate_commit','base_commit','findings','tests','scope_deviations')}
if role == 'coding-agent' and '--version' not in sys.argv and 'login' not in sys.argv: pathlib.Path('README.md').write_text('done\\n')
print(json.dumps(result))
""", encoding="utf-8")
        fake.chmod(0o755)
        config = json.loads(json.dumps({
            "version": 1, "git": {"base_branch":"main", "branch_prefix":"orchestrator", "worktree_root":"../.worktrees", "require_clean_base_worktree":True, "merge_strategy":"ff-only"},
            "roles": {role:{"primary":{"client":"codex","model":"fake"}} for role in ("orchestrator","coding_agent","completion_verifier","code_reviewer","fix_agent")},
            "providers": {"codex":{"command":str(fake),"enabled":True},"opencode":{"enabled":False}},
            "retry":{"provider_wait_seconds":1}, "timeouts":{"coding_seconds":5,"completion_verification_seconds":5,"review_seconds":5,"fix_seconds":5,"process_termination_grace_seconds":1}, "loops":{}, "protocol":{}
        }))
        config_dir = repo / ".project-orchestrator"; config_dir.mkdir()
        (config_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
        spec = repo / "plan.md"; spec.write_text("# Phase 1: fake execution\n\n# Phase 2: second execution\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-m", "fixture"], check=True, capture_output=True)
        result = run_cli(repo, "run", "--spec", str(spec), "--run-id", "fake-run", "--json")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        state = json.loads(result.stdout)["result"]
        self.assertEqual(state["state"], "PROJECT_COMPLETED", result.stdout)
        self.assertTrue((Path(state["state_path"]) / "FINAL-REPORT.md").exists())
        cleaned_worktrees = state.get("cleaned_worktrees", [])
        self.assertEqual(len(cleaned_worktrees), 2)
        self.assertTrue(
            all(not Path(item["path"]).exists() for item in cleaned_worktrees),
            "a successful merge must remove every run-owned worktree",
        )

    def test_real_git_rebase_conflict_is_detectable_without_guessing(self) -> None:
        from project_orchestrator_cli.git_service import GitService
        repo = self.make_repo()
        branch = "orchestrator/conflict/phase-001"
        worktree = Path(tempfile.mkdtemp()) / "conflict-worktree"
        subprocess.run(["git", "-C", str(repo), "branch", branch], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "worktree", "add", str(worktree), branch], check=True, capture_output=True)
        try:
            (worktree / "README.md").write_text("implementation\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(worktree), "add", "README.md"], check=True)
            subprocess.run(["git", "-C", str(worktree), "commit", "-m", "implementation"], check=True, capture_output=True)
            (repo / "README.md").write_text("base change\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
            env = {**os.environ, "GIT_EDITOR":"true", "GIT_TERMINAL_PROMPT":"0", "GIT_CONFIG_GLOBAL":"/dev/null"}
            subprocess.run(["git", "-C", str(repo), "-c", "core.hooksPath=/dev/null", "-c", "maintenance.auto=false", "commit", "-m", "base change"], check=True, capture_output=True, env=env)
            with self.assertRaises(Exception):
                GitService(repo).run("merge", "--no-commit", "main", cwd=worktree)
            merge_head = subprocess.run(
                ["git", "-C", str(worktree), "rev-parse", "--quiet", "--verify", "MERGE_HEAD"],
                text=True,
                capture_output=True,
            )
            if merge_head.returncode == 0:
                GitService(repo).run("merge", "--abort", cwd=worktree)
            self.assertEqual(subprocess.run(["git", "-C", str(worktree), "status", "--porcelain"], text=True, capture_output=True).stdout, "")
        finally:
            subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)], check=False, capture_output=True)
