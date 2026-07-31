#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def insert_before(relative: str, anchor: str, block: str, sentinel: str) -> None:
    text = read(relative)
    if sentinel in text:
        return
    if text.count(anchor) != 1:
        raise RuntimeError(f"{relative}: expected one anchor {anchor!r}, found {text.count(anchor)}")
    write(relative, text.replace(anchor, block.rstrip() + "\n\n" + anchor, 1))


def patch_metadata(relative: str, version: str, tested: str) -> None:
    text = read(relative)
    text, version_count = re.subn(
        r'(?m)^  version: "[^"]+"$',
        f'  version: "{version}"',
        text,
        count=1,
    )
    text, tested_count = re.subn(
        r'(?m)^  tested: "[^"]*"$',
        f'  tested: "{tested}"',
        text,
        count=1,
    )
    if version_count != 1 or tested_count != 1:
        raise RuntimeError(f"{relative}: failed to update frontmatter metadata")
    write(relative, text)


pm_block = '''### Architecture Gate

Before publishing an initiative, decide whether it materially needs `the-architect` Architecture
Preflight. Select the gate for new or cross-cutting subsystems, shared/public contracts,
persistence or migrations, security/trust boundaries, reliability/concurrency/transactions/eventing,
deployment topology, reusable-component selection or extraction, major modernization, or material
performance/scalability constraints.

Do not require the gate for Retouch Mode or ordinary localized work. Epic Planner records the gate
but does not perform the assessment. When selected, use:

```md
## Architecture Gate

Mode: the-architect
Status: required
Assessment reference: none
Addendum updated: none
Blocker: Architecture Preflight pending
```

Read `references/architecture-gate.md` whenever gate selection may apply. The Architect updates the
managed addendum and changes the status to `passed` or `blocked` before Analyst or direct execution.'''

sd_block = '''## Architecture Gate

Retouch Mode remains the first routing check. For every standard Analyst, developer, debugger, or
coding-agent workflow, inspect the supplied work contract for an optional `## Architecture Gate`.
An absent gate or `Mode: none` with `Status: not-required` is backward compatible. When
`Mode: the-architect`, only `Status: passed` permits analysis decomposition or implementation.

Stop before production changes when a required gate is unresolved or blocked. Consume and preserve
the managed Architect Addendum without repeating portfolio/component-history research already
settled there. If current repository evidence, scope, or safety contradicts the addendum, return the
conflict to the control authority and `the-architect`; do not silently rewrite it.

Read `references/architecture-gate.md` before acting on a contract that contains an Architecture Gate.'''

orchestrator_block = '''## Architecture Gate

During source/contract validation, before creating the Epic branch or worktree, validate the optional
`## Architecture Gate`. Absent gates and `Mode: none` / `Status: not-required` remain compatible.
When `Mode: the-architect`, only `Status: passed` may continue; `required` or `blocked` returns a
deterministic contract-validation blocker before materialization or Git side effects.

The controller never invokes `the-architect` automatically. The complete Epic body, including the
managed Architect Addendum, remains inside `EPIC.md` through one-time Initial Contract
Materialization. Do not create `ARCHITECTURE.md` or add contract synchronization.

Read `references/architecture-gate.md` when resolving any source contract that contains the gate.'''

archivist_block = '''## The Architect boundary

`the-architect` owns cross-project architecture memory, reusable-component definitions, component
application results, and architectural engagement history in its dedicated architecture home.
Archivist continues to own durable documentation inside the target repository: README, AGENTS,
DECISIONS, RUNBOOK, and catalog traceability.

Architect findings may be consumed as evidence, but neither role mirrors the other's knowledge base.
GitHub Issues and Projects remain operational work state. Read
`references/the-architect-boundary.md` when processing Architect-produced evidence or deciding where
architecture knowledge belongs.'''

insert_before(
    "skills/ops/coferlandia-project-manager/SKILL.md",
    "### Planning storage policy",
    pm_block,
    "### Architecture Gate\n",
)
insert_before(
    "skills/engineering/software-development/SKILL.md",
    "## Retouch Mode",
    sd_block,
    "## Architecture Gate\n",
)
insert_before(
    "skills/ops/project-orchestrator/SKILL.md",
    "## Contract sources",
    orchestrator_block,
    "## Architecture Gate\n",
)
insert_before(
    "skills/content/project-documentation-archivist/SKILL.md",
    "## Source-of-truth boundaries",
    archivist_block,
    "## The Architect boundary\n",
)

patch_metadata(
    "skills/ops/coferlandia-project-manager/SKILL.md",
    "0.8.0",
    "2026-07-31 - Architecture Gate selection and the-architect handoff contract covered by cross-skill tests.",
)
patch_metadata(
    "skills/engineering/software-development/SKILL.md",
    "4.6",
    "2026-07-31 - Architecture Gate blocking, passed, absent, not-required, and Retouch compatibility covered by cross-skill tests.",
)
patch_metadata(
    "skills/ops/project-orchestrator/SKILL.md",
    "2.2",
    "2026-07-31 - Optional Architecture Gate enforcement validated before materialization/worktree creation on local and GitHub inputs.",
)
patch_metadata(
    "skills/content/project-documentation-archivist/SKILL.md",
    "3.1.0",
    "2026-07-31 - The Architect cross-project memory boundary covered by cross-skill ownership tests.",
)

cases_path = "skills/engineering/software-development/tests/cases.json"
cases = json.loads(read(cases_path))
new_cases = [
    {
        "id": "architecture-gate-required-blocks-analyst",
        "prompt": "Analyze and decompose this Epic. Its Architecture Gate says Mode: the-architect and Status: required.",
        "expect": "Stops before Analyst decomposition and returns the unresolved Architecture Gate to the control authority/the-architect; it does not publish executable tasks.",
    },
    {
        "id": "architecture-gate-passed-allows-analyst",
        "prompt": "Analyze this Epic. Its Architecture Gate says Mode: the-architect and Status: passed with a managed Architect Addendum.",
        "expect": "Analyst consumes and preserves the addendum, avoids duplicating settled portfolio/component research, and continues normal low-context decomposition.",
    },
    {
        "id": "architecture-gate-required-blocks-direct-coding",
        "prompt": "Execute this detailed plan directly; its Architecture Gate is required and not yet passed.",
        "expect": "Coding-agent stops before implementation despite the otherwise executable plan and reports the pending Architecture Preflight.",
    },
    {
        "id": "architecture-gate-absent-or-not-required-compatible",
        "prompt": "Execute a standard work contract with no Architecture Gate, or with Mode: none and Status: not-required.",
        "expect": "Preserves existing routing and execution behavior; no Architect invocation or extra gate is invented.",
    },
    {
        "id": "retouch-does-not-require-architecture-gate",
        "prompt": "Tiny retouch: correct one local CSS color; no Architecture Gate is present.",
        "expect": "Retouch Mode remains first, uses its existing eligibility/current-branch flow, and does not invent an Architecture Gate.",
    },
]
existing_ids = {item.get("id") for item in cases.get("evaluations", [])}
for item in new_cases:
    if item["id"] not in existing_ids:
        cases["evaluations"].append(item)
write(cases_path, json.dumps(cases, indent=2, ensure_ascii=False) + "\n")

release_path = "RELEASE-NOTES.md"
release = read(release_path)
release, count = re.subn(r"## Unreleased \(\d{4}-\d{2}-\d{2}\)", "## Unreleased (2026-07-31)", release, count=1)
if count != 1:
    raise RuntimeError("RELEASE-NOTES.md: Unreleased heading not found")
release_block = '''### The Architect

- **the-architect** — v1.0.0 adds cross-project architecture memory, evidence-based preflight and assessment, reusable-component lifecycle/application history, explicit extraction contracts, concise delta-first reports, and a portable Markdown/Obsidian architecture home managed through one deterministic Python CLI.
- **Architecture Gate integration** — `coferlandia-project-manager` v0.8.0 may select the gate for material architecture work; `software-development` v4.6 consumes/blocks it before Analyst or direct execution; `project-orchestrator` v2.2 enforces it before materialization/worktree creation; `project-documentation-archivist` v3.1.0 retains in-project documentation ownership while the Architect owns cross-project evidence.
- **Validation** — cross-skill ownership and gate behavior are regression-tested alongside the Architect CLI and the full Project Orchestrator suite on Linux and Windows.

'''
if "### The Architect\n" not in release:
    anchor = "### Epic-based development workflow\n"
    if release.count(anchor) != 1:
        raise RuntimeError("RELEASE-NOTES.md: Epic workflow anchor not found")
    release = release.replace(anchor, release_block + anchor, 1)
write(release_path, release)

cross_skill_test = '''from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


class CrossSkillIntegrationTests(unittest.TestCase):
    def text(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_owning_skills_load_their_architecture_references(self) -> None:
        expectations = {
            "skills/ops/coferlandia-project-manager/SKILL.md": ("### Architecture Gate", "references/architecture-gate.md"),
            "skills/engineering/software-development/SKILL.md": ("## Architecture Gate", "references/architecture-gate.md"),
            "skills/ops/project-orchestrator/SKILL.md": ("## Architecture Gate", "references/architecture-gate.md"),
            "skills/content/project-documentation-archivist/SKILL.md": ("## The Architect boundary", "references/the-architect-boundary.md"),
        }
        for path, phrases in expectations.items():
            text = self.text(path)
            for phrase in phrases:
                self.assertIn(phrase, text, path)

    def test_development_pressure_cases_cover_gate_matrix(self) -> None:
        cases = json.loads(self.text("skills/engineering/software-development/tests/cases.json"))
        ids = {item["id"] for item in cases["evaluations"]}
        self.assertTrue({
            "architecture-gate-required-blocks-analyst",
            "architecture-gate-passed-allows-analyst",
            "architecture-gate-required-blocks-direct-coding",
            "architecture-gate-absent-or-not-required-compatible",
            "retouch-does-not-require-architecture-gate",
        }.issubset(ids))

    def test_release_notes_and_versions_are_reconciled(self) -> None:
        notes = self.text("RELEASE-NOTES.md")
        self.assertIn("### The Architect", notes)
        self.assertIn("the-architect", notes)
        versions = {
            "skills/ops/coferlandia-project-manager/SKILL.md": 'version: "0.8.0"',
            "skills/engineering/software-development/SKILL.md": 'version: "4.6"',
            "skills/ops/project-orchestrator/SKILL.md": 'version: "2.2"',
            "skills/content/project-documentation-archivist/SKILL.md": 'version: "3.1.0"',
        }
        for path, version in versions.items():
            self.assertIn(version, self.text(path), path)


if __name__ == "__main__":
    unittest.main()
'''
write("skills/engineering/the-architect/tests/test_cross_skill_integration.py", cross_skill_test)

# Remove the one-shot patch mechanism from the resulting branch.
(ROOT / ".github/workflows/apply-the-architect-integration.yml").unlink()
Path(__file__).unlink()
