"""All orchestrator-owned git actions use argument arrays through this service."""
from __future__ import annotations

import subprocess
import hashlib
from pathlib import Path

from .contracts import DependencyError, OrchestratorError, UnsafeOperation, ValidationError

class GitService:
    def __init__(self, repo: Path): self.repo = repo.resolve()
    def run(self, *args: str, cwd: Path | None = None) -> str:
        try:
            env = {**__import__("os").environ, "GIT_EDITOR":"true", "GIT_SEQUENCE_EDITOR":"true", "GIT_TERMINAL_PROMPT":"0", "GIT_CONFIG_NOSYSTEM":"1", "GIT_CONFIG_GLOBAL":"/dev/null", "GIT_OPTIONAL_LOCKS":"0"}
            result = subprocess.run(["git", "-c", "maintenance.auto=false", *args], cwd=cwd or self.repo, env=env, text=True, capture_output=True, check=False)
        except FileNotFoundError as exc: raise DependencyError("git is required but was not found on PATH") from exc
        if result.returncode: raise OrchestratorError((result.stderr or result.stdout).strip() or f"git {' '.join(args)} failed")
        return result.stdout.strip()
    def common_dir(self) -> Path:
        value = Path(self.run("rev-parse", "--git-common-dir"))
        return (self.repo / value).resolve() if not value.is_absolute() else value.resolve()
    def head(self, ref: str = "HEAD") -> str: return self.run("rev-parse", ref)
    def branch_exists(self, branch: str) -> bool:
        return subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"], cwd=self.repo).returncode == 0
    def clean(self) -> bool: return not self.run("status", "--porcelain")
    def ensure_repo(self) -> None:
        if self.run("rev-parse", "--is-inside-work-tree") != "true": raise ValidationError("current directory is not a Git worktree")
    def ensure_branch(self, branch: str, base: str) -> None:
        if not branch.startswith("orchestrator/") or ".." in branch: raise UnsafeOperation("unsafe orchestrator branch")
        if not self.branch_exists(branch): self.run("branch", branch, base)
    def add_worktree(self, path: Path, branch: str) -> None:
        if path.exists(): raise UnsafeOperation(f"managed worktree path already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True); self.run("worktree", "add", str(path), branch)
    def add_review_worktree(self, path: Path, commit: str) -> None:
        if path.exists(): raise UnsafeOperation(f"review worktree path already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True); self.run("worktree", "add", "--detach", str(path), commit)
    def remove_worktree(self, path: Path) -> None: self.run("worktree", "remove", str(path))
    def status(self, cwd: Path | None = None) -> str: return self.run("status", "--porcelain", cwd=cwd)
    def diff_hash(self, base: str, cwd: Path | None = None) -> str:
        diff = self.run("diff", "--binary", base, cwd=cwd)
        return hashlib.sha256(diff.encode()).hexdigest()
    def add_all(self, cwd: Path) -> None: self.run("add", "--all", cwd=cwd)
    def commit(self, message: str, cwd: Path) -> str: self.run("commit", "--allow-empty", "-m", message, cwd=cwd); return self.head("HEAD")
    def amend(self, message: str, cwd: Path) -> str: self.run("commit", "--amend", "-m", message, cwd=cwd); return self.head("HEAD")
    def merge_ff_only(self, commit: str) -> str: return self.run("merge", "--ff-only", commit)
    def rebase(self, base: str, cwd: Path) -> None: self.run("rebase", base, cwd=cwd)
    def remove_branch(self, branch: str) -> None:
        if self.branch_exists(branch): self.run("branch", "-D", branch)
