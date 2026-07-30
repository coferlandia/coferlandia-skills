#!/usr/bin/env python3
"""Apply the approved Epic #11 textual and controller wiring changes."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


# Epic Planner contract.
path = "skills/ops/coferlandia-project-manager/SKILL.md"
text = read(path)
text = replace_once(text, '  version: "0.6.0"', '  version: "0.7.0"', path)
text = replace_once(
    text,
    '  tested: "2026-07-27 - Phase 1 GitHub-native project-management protocol."',
    '  tested: "2026-07-30 - Single-store Epic planning with one-time orchestrator contract initialization."',
    path,
)
text = replace_once(
    text,
    "Do not require GitHub and local representations to be maintained manually at the same time.\n",
    """Epic Planner writes exactly one complete representation per invocation. It does not manually mirror or
continuously synchronize GitHub and `.agent/work-items/`.

When the resolved strategy is `Tracking: GitHub` but the active Planner lacks usable GitHub write
capability, it may emit the complete standard local Epic contract and hand it to
`project-orchestrator`. Before execution, the orchestrator performs one-time Initial Contract
Materialization to create the missing GitHub counterpart. When Planner writes the Epic directly to
GitHub, the orchestrator performs the inverse one-time materialization into local execution files.
After that boundary, the local files are the frozen contract snapshot for the run; later contract
changes are not propagated automatically in either direction.
""",
    path,
)
write(path, text)


# Analyst contract and pressure scenarios.
path = "skills/engineering/software-development/SKILL.md"
text = read(path)
text = replace_once(text, '  version: "4.4"', '  version: "4.5"', path)
text = replace_once(
    text,
    '  tested: "2026-07-27 - Retouch Mode retained; GitHub-native Coferlandia traceability replaces TODO/HISTORY dependencies while preserving non-GitHub repository compatibility."',
    '  tested: "2026-07-30 - Analyst single-store outputs and canonical analysis contract support one-time orchestrator initialization."',
    path,
)
text = replace_once(
    text,
    "tracking synchronization, and cleanup. Development roles never push.",
    "operational tracking, one-time contract-store initialization, and cleanup. Development roles never push.",
    path,
)
old = """### Analyst output modes

**GitHub mode:** when GitHub is available and selected by the workflow, the Epic/task Issues are the
authoritative active contracts. Record analysis in the Epic chronology/contract and create native
sub-issues when supported; otherwise use the repository's explicit parent-link convention. Do not
duplicate every task into local files merely for execution; the orchestrator materializes them.

**Local fallback:** when GitHub is unavailable or local tracking is explicitly selected, write the
equivalent contracts under:

```text
.agent/work-items/<epic>/
├── EPIC.md
├── ANALYSIS.md
├── manifest.json
├── tasks/
│   └── TASK-*.md
└── archive/
```

Analyst stops after the execution graph passes Atomic + Self-contained + Low-context and regression
gates. It never implements production code, creates implementation commits, or assigns itself as
reviewer.
"""
new = """### Analyst output modes

Analyst writes exactly one complete representation per invocation. It never manually mirrors or
continuously synchronizes GitHub and local work-item files.

**GitHub mode:** when GitHub is available and selected by the workflow, the Epic/task Issues are the
active contracts. Create native sub-issues when supported; otherwise use the repository's explicit
parent-link convention. Publish the complete canonical analysis as one marked Epic comment:

```html
<!-- coferlandia-analysis-contract -->
```

The current analysis follows that marker. Later decisions and execution evidence remain separate
chronological comments. Do not duplicate every task into local files merely for execution; the
orchestrator creates the standard local snapshot once before workers run.

**Local output:** when GitHub is unavailable, or when local tracking is selected, write the complete
representation under:

```text
.agent/work-items/<epic>/
├── EPIC.md
├── ANALYSIS.md
├── manifest.json
├── tasks/
│   └── TASK-*.md
└── archive/
```

If `Tracking: GitHub` is already resolved, this local output is not a change to local-fallback
tracking. It is a complete source contract for the orchestrator's one-time local-to-GitHub
initialization. Once initialization completes, the local files are the frozen execution snapshot;
Analyst does not maintain later cross-store synchronization.

Analyst stops after the execution graph passes Atomic + Self-contained + Low-context and regression
gates. It never implements production code, creates implementation commits, or assigns itself as
reviewer.
"""
text = replace_once(text, old, new, path)
text = replace_once(
    text,
    "Storage mode: {GitHub | local fallback}\nExecution strategy: {reference}",
    "Storage mode: {GitHub | local files}\nCanonical analysis: {marked Epic comment | ANALYSIS.md path}\nExecution strategy: {reference}",
    path,
)
text = replace_once(
    text,
    "Implementation performed: none\n",
    "Initial counterpart materialization performed: none\nImplementation performed: none\n",
    path,
)
write(path, text)

cases_path = ROOT / "skills/engineering/software-development/tests/cases.json"
cases = json.loads(cases_path.read_text(encoding="utf-8"))
new_cases = [
    {
        "id": "analyst-github-canonical-analysis",
        "prompt": "GitHub tracking is selected and available. Analyze this Epic and publish the execution graph.",
        "expect": "Writes only the GitHub representation, publishes the complete current analysis in one Epic comment marked <!-- coferlandia-analysis-contract -->, creates linked task Issues, and leaves local snapshot creation to project-orchestrator.",
    },
    {
        "id": "analyst-local-output-for-github-initialization",
        "prompt": "Tracking is already GitHub, but this Analyst has no GitHub tools. Produce the execution graph for the orchestrator.",
        "expect": "Writes one complete local EPIC.md/ANALYSIS.md/manifest.json/TASK-*.md representation without changing the selected tracking mode; project-orchestrator will publish the missing GitHub counterpart once before execution.",
    },
    {
        "id": "analyst-does-not-maintain-contract-sync",
        "prompt": "Keep the GitHub Issues and local task files continuously synchronized while implementation runs.",
        "expect": "Rejects continuous contract synchronization as outside the Analyst role; each invocation writes one representation and the orchestrator performs only one-time initial materialization before freezing the run snapshot.",
    },
]
existing = {item.get("id") for item in cases["evaluations"]}
for item in new_cases:
    if item["id"] not in existing:
        cases["evaluations"].insert(3, item)
for item in cases["evaluations"]:
    if item.get("id") == "project-orchestrator-retains-git-ownership":
        item["expect"] = item["expect"].replace("remote synchronization", "remote operational traceability")
cases_path.write_text(json.dumps(cases, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# Orchestrator public contract.
path = "skills/ops/project-orchestrator/SKILL.md"
text = read(path)
text = replace_once(text, '  version: "2.0"', '  version: "2.1"', path)
text = replace_once(
    text,
    '  tested: "2026-07-29 - Epic/task v2 lifecycle with direct-plan compatibility, low-context materialization, additive immutable review commits, and explicit final integration."',
    '  tested: "2026-07-30 - One-time bidirectional contract initialization with frozen local execution snapshots."',
    path,
)
text = replace_once(
    text,
    "worktrees, commits, durable run state, provider retries, GitHub synchronization, final integration,",
    "worktrees, commits, durable run state, provider retries, GitHub operational traceability, final integration,",
    path,
)
old = """GitHub mode is controller-facing. Coding/review/fix agents receive bounded local files and do not
need `gh`, GitHub API credentials, Project access, Issue browsing, or the original planning chat.

GitHub materialization lives under:

```text
.agent/work-items/epic-<issue>/
├── EPIC.md
├── manifest.json
├── tasks/
│   └── TASK-<issue>.md
└── archive/
```

Source metadata includes repository/Issue/Epic identity, update time, normalized source hash,
materialization time, and contract revision. Before assignment, stale GitHub contracts are refreshed;
an incompatible change to an in-progress task blocks rather than being overwritten.
"""
new = """GitHub mode is controller-facing. Coding/review/fix agents receive bounded local files and do not
need `gh`, GitHub API credentials, Project access, Issue browsing, or the original planning chat.

Before creating the Epic branch/worktree, the controller performs **Initial Contract
Materialization** exactly once:

- GitHub-only Epic/analysis/task contracts become the standard local execution tree;
- complete local contracts whose resolved strategy is `Tracking: GitHub` become marked, linked
  GitHub Epic/task Issues plus the canonical marked analysis comment;
- when both representations already exist, only repository/Epic/task identity and parent linkage
  are validated; bodies are not compared or merged;
- local-fallback tracking never publishes Issues merely because a remote exists.

The local tree is:

```text
.agent/work-items/epic-<issue>/
├── EPIC.md
├── ANALYSIS.md          # Analyst mode
├── manifest.json
├── tasks/
│   └── TASK-<issue>.md
└── archive/
```

Stable contract markers make interrupted local-to-GitHub initialization retry-safe and prevent
Issue duplication. Source hashes, timestamps, and revisions remain passive provenance. After
initialization, the local tree is the frozen contract snapshot for that run: the controller does not
re-fetch, compare, refresh, merge, or propagate later contract-body changes. Issue comments,
Project status, commit linkage, the final PR, closure, and archival remain active operational
traceability and are not contract synchronization.
"""
text = replace_once(text, old, new, path)
text = replace_once(
    text,
    "1. Resolve and validate the v2 manifest/Execution Strategy.",
    "1. Resolve and validate the v2 manifest/Execution Strategy, then complete one-time Initial Contract Materialization.",
    path,
)
text = replace_once(
    text,
    "Only the controller creates commits, branches/worktrees, remote synchronization, PRs, integration,",
    "Only the controller creates commits, branches/worktrees, remote operational traceability, PRs, integration,",
    path,
)
text = replace_once(
    text,
    "- Direct plans are not heuristically decomposed.\n",
    "- Direct plans are not heuristically decomposed.\n- Initial Contract Materialization occurs before the worktree is created and never becomes continuous synchronization.\n- Later GitHub/local contract-body drift does not mutate the frozen execution snapshot automatically.\n",
    path,
)
text = replace_once(
    text,
    "Use `run ... --dry-run` for local `--spec`/`--manifest` planning. GitHub `--epic` materialization is\nitself a local write; materialize first and preview its manifest when a mutation-free preview is\nrequired.",
    "Use `run ... --dry-run` for local `--spec`/`--manifest` planning. When their resolved tracking is GitHub, dry-run validates and reports that initialization is required without creating Issues or inventing Issue numbers. GitHub `--epic` materialization is itself a local write; materialize first and preview its manifest when a mutation-free preview is required.",
    path,
)
text = replace_once(
    text,
    "- `references/architecture.md` — controller/worker/source boundaries.\n",
    "- `references/architecture.md` — controller/worker/source boundaries.\n- `references/initial-contract-materialization.md` — one-time GitHub/filesystem initialization contract.\n",
    path,
)
write(path, text)


# Remove the runtime freshness lookup from the execution loop; initialization owns the boundary.
path = "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/engine.py"
text = read(path)
text = replace_once(
    text,
    "from .materialization import materialize_github_epic, verify_github_freshness",
    "from .materialization import materialize_github_epic",
    path,
)
block = """                    if state["manifest"].get("source", {}).get("kind") == "github":
                        try:
                            check = verify_github_freshness(repo, state["manifest"], in_progress_task=None)
                            if check.get("refreshed"):
                                state["manifest"] = _copy_contracts_to_worktree(repo, Path(state["resources"]["implementation_worktree"]), check["manifest"])
                                next_task = task_by_id(state["manifest"], next_task["id"])
                        except ValidationError as exc:
                            state = store.transition("BLOCKED_BY_STALE_CONTRACT", {"reason": str(exc)})
                            break
"""
text = replace_once(text, block, "", path)
write(path, text)

path = "skills/ops/project-orchestrator/scripts/project_orchestrator_cli/state.py"
text = read(path)
text = replace_once(text, '    "BLOCKED_BY_STALE_CONTRACT",\n', "", path)
text = replace_once(
    text,
    '    "TASK_SELECTED": {"CODING_RUNNING", "CANCELLED", "BLOCKED_BY_STALE_CONTRACT"},',
    '    "TASK_SELECTED": {"CODING_RUNNING", "CANCELLED"},',
    path,
)
write(path, text)


# References.
write(
    "skills/ops/project-orchestrator/references/architecture.md",
    """# Architecture

`project-orchestrator-cli.py` is the sole public interface. The deterministic controller owns
source resolution, one-time contract-store initialization, durable state transitions, Git,
worktrees, commits, provider retries, GitHub operational traceability, final integration, archival,
and cleanup. Models provide semantic coding/completion/review/fix results only; they never own
controller state or Git authority.

## Source boundary

The controller normalizes exactly one source into a v2 execution manifest:

- `--spec`: local direct plan -> one `DIRECT-PLAN` unit;
- `--epic`: GitHub Epic -> one frozen local Epic/analysis/task snapshot;
- `--manifest`: local v2 manifest/task DAG, optionally published once when Tracking is GitHub.

Before a run creates its Epic worktree, Initial Contract Materialization ensures the missing GitHub
or filesystem counterpart exists. GitHub-only contracts produce `EPIC.md`, canonical `ANALYSIS.md`
when applicable, `manifest.json`, and task files. Local GitHub-tracked contracts produce marked,
retry-safe Epic/task Issues and one marked canonical analysis comment. Existing dual
representations are checked only for identity and parent linkage.

After this boundary, workers use the frozen local snapshot. Contract bodies are not re-fetched,
compared, refreshed, merged, or propagated automatically. Operational Issue comments, Project
fields, commit references, PR creation, closure, and archival continue independently.

## Execution boundary

One Epic branch/worktree carries all execution units. Task dependencies are validated as a DAG and
executed serially. Candidate and review-fix commits are additive. Review always occurs from a
detached worktree at an immutable SHA. Passing a task marks it `ready_for_merge`; no task is merged
to `main` independently.

After all tasks pass, one holistic Epic review approves the final branch HEAD. GitHub mode then
opens one final PR; local fallback retains an equivalent explicit integration gate. `integrate`
is the only final delivery action.

## Components

- `work_items.py`: v2 manifest, tracking/origin metadata, Execution Strategy parsing, DAG validation/order.
- `contract_initialization.py`: one-time local-to-GitHub initialization, identity recovery, and dry-run preflight.
- `materialization.py`: one-time GitHub-to-local snapshots, canonical analysis extraction, passive provenance, archive paths.
- `github_service.py`: structured `gh` reads/writes for Issues, Projects, and PRs.
- `GitService`: argument-array Git operations and controlled staging.
- `RunStore`: atomic durable state/events and run locking.
- provider adapters: model/CLI execution boundary.
- `integration.py`: final traceability, PR/integration, archive, and cleanup.

Run state lives at `<git-common-dir>/project-orchestrator/runs/<run-id>/`; writes are atomic and
events are append-only. Execution adapters must use argument arrays, UTF-8, timeouts, redaction,
and never `shell=True`.
""",
)

path = "skills/ops/project-orchestrator/references/state-machine.md"
text = read(path)
text = replace_once(
    text,
    "  -> CONTRACT_RESOLVED\n  -> EPIC_WORKTREE_CREATING",
    "  -> CONTRACT_RESOLVED          # initial materialization already completed\n  -> EPIC_WORKTREE_CREATING",
    path,
)
text = replace_once(
    text,
    "specification/config/authentication, Git/base movement, merge conflicts, stale in-progress\ncontracts, and no semantic progress.",
    "specification/config/authentication, invalid contract identity/linkage during initialization,\nGit/base movement, merge conflicts, and no semantic progress. Later contract-body drift is not a\nruntime state transition because the local snapshot is frozen before the run begins.",
    path,
)
write(path, text)

path = "skills/ops/project-orchestrator/references/agent-protocol.md"
text = read(path)
text = replace_once(
    text,
    "Workers must not browse GitHub, perform Git lifecycle operations, or reconstruct the project plan.",
    "Workers must not browse GitHub, perform Git lifecycle operations, or reconstruct the project plan. The supplied local Epic/analysis/task files are the frozen contract snapshot for the run; workers never check remote freshness.",
    path,
)
write(path, text)


# Inventory and release notes.
path = "skills/INDEX.md"
text = read(path)
text = replace_once(
    text,
    "| [software-development](./engineering/software-development/) | Routes broad-context Analyst decomposition, developer/debugger work, executable coding-agent contracts, and independent review while keeping Git authority separate from semantic workers | active |",
    "| [software-development](./engineering/software-development/) | Routes broad-context Analyst decomposition with single-store outputs, developer/debugger work, executable coding-agent contracts, and independent review while keeping Git authority separate | active |",
    path,
)
text = replace_once(
    text,
    "| [coferlandia-project-manager](./ops/coferlandia-project-manager/) | Design Epics, resolve execution strategy, and manage GitHub Issues/Projects-backed portfolio state with a local planning fallback when GitHub is unavailable | active |",
    "| [coferlandia-project-manager](./ops/coferlandia-project-manager/) | Design Epics, resolve execution strategy, and emit one complete GitHub or local planning representation for orchestrator initialization | active |",
    path,
)
text = replace_once(
    text,
    "| [project-orchestrator](./ops/project-orchestrator/) | Explicitly execute direct plans or Analyst task DAGs through one Epic worktree, additive immutable reviews, GitHub/filesystem materialization, final PR traceability, and explicit integration | active |",
    "| [project-orchestrator](./ops/project-orchestrator/) | Execute direct plans or Analyst DAGs after one-time GitHub/filesystem initialization, using a frozen local snapshot, immutable reviews, final PR traceability, and explicit integration | active |",
    path,
)
text = replace_once(text, "*Last updated: 2026-07-29*", "*Last updated: 2026-07-30*", path)
write(path, text)

path = "RELEASE-NOTES.md"
text = read(path)
text = replace_once(text, "## Unreleased (2026-07-29)", "## Unreleased (2026-07-30)", path)
text = replace_once(
    text,
    "- **project-orchestrator** — v2.0 replaces phase-per-worktree/amend/per-phase-merge execution with a v2 manifest, `direct-plan` and `task-execution` modes, one Epic branch/worktree, GitHub-to-filesystem materialization with freshness checks, additive task/review-fix commits, detached immutable reviews, a mandatory holistic Epic review, bidirectional Issue/commit/PR traceability, one final PR, explicit `integrate`, and post-delivery task archival.",
    "- **project-orchestrator** — v2.1 keeps the Epic/task v2 lifecycle and replaces ongoing contract freshness refreshes with one-time bidirectional Initial Contract Materialization. GitHub-only plans become frozen local Epic/analysis/task snapshots; complete local GitHub-tracked plans are published with stable retry-safe markers before execution. Operational Issue/Project/commit/PR traceability remains active.",
    path,
)
text = replace_once(
    text,
    "- **coferlandia-project-manager** — adds Epic Planner as the initiative-level WHAT/WHY capability and records a normalized Execution Strategy.",
    "- **coferlandia-project-manager** — v0.7 adds Epic Planner as the initiative-level WHAT/WHY capability, records a normalized Execution Strategy, and emits exactly one complete planning representation for one-time orchestrator initialization.",
    path,
)
text = replace_once(
    text,
    "- **software-development** — adds the first-class, analysis-only `analyst` role.",
    "- **software-development** — v4.5 adds the first-class, analysis-only `analyst` role and formalizes single-store output plus the canonical marked GitHub analysis contract.",
    path,
)
write(path, text)

print("Epic #11 patch applied")
