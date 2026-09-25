import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "prompts"
VALIDATOR = ROOT / "_protocol" / "scripts" / "validate_prompt.py"


class PromptContractTests(unittest.TestCase):
    def run_resolve(self, expression: str, root: Path = ROOT) -> dict:
        result = subprocess.run(
            [
                sys.executable,
                str(root / "_protocol" / "scripts" / "validate_prompt.py"),
                "resolve",
                expression,
                "--root",
                str(root),
                "--json",
            ],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def test_registry_contract(self):
        registry = json.loads((PROMPTS / "registry.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["schema_version"], 1)
        ids = [item["id"] for item in registry["prompts"]]
        self.assertEqual(ids, ["chat-coder", "ci", "merge", "chat-release", "hotfix"])
        aliases = {alias: item["id"] for item in registry["prompts"] for alias in item["aliases"]}
        self.assertEqual(aliases["chat coder"], "chat-coder")
        self.assertEqual(aliases["chat dev"], "chat-coder")
        self.assertEqual(aliases["gh ci"], "ci")
        self.assertEqual(aliases["merge"], "merge")
        self.assertEqual(aliases["chat release"], "chat-release")
        self.assertEqual(aliases["hotfix"], "hotfix")
        external = {item["alias"]: item for item in registry["external_aliases"]}
        self.assertEqual(external["local ci"]["kind"], "skill")
        self.assertEqual(external["local ci"]["target"], "local-ci")
        self.assertEqual(external["local release"]["kind"], "skill")
        self.assertEqual(external["local release"]["target"], "local-release")
        composition = registry["composition"]
        self.assertEqual(composition["order"], "left-to-right")
        self.assertFalse(composition["implicit_stages"])
        self.assertFalse(composition["automatic_fallback"])
        self.assertEqual(
            composition["standalone_defaults"]["chat coder"],
            ["chat coder", "gh ci", "merge"],
        )
        self.assertEqual(
            composition["standalone_defaults"]["chat-coder"],
            ["chat-coder", "gh ci", "merge"],
        )

    def test_validator_and_alias_resolution(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "validate", "--root", str(ROOT), "--json"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

        standalone = self.run_resolve("chat coder")
        self.assertTrue(standalone["defaulted"])
        self.assertEqual(
            [item["target"] for item in standalone["sequence"]],
            ["chat-coder", "ci", "merge"],
        )

        normalized = self.run_resolve("  Chat   Coder  ")
        self.assertTrue(normalized["defaulted"])
        self.assertEqual(
            [item["target"] for item in normalized["sequence"]],
            ["chat-coder", "ci", "merge"],
        )

        hyphenated = self.run_resolve("chat-coder")
        self.assertTrue(hyphenated["defaulted"])
        self.assertEqual(
            [item["target"] for item in hyphenated["sequence"]],
            ["chat-coder", "ci", "merge"],
        )

        development_only = self.run_resolve("chat dev")
        self.assertFalse(development_only["defaulted"])
        self.assertEqual(
            [item["target"] for item in development_only["sequence"]],
            ["chat-coder"],
        )

        explicit = self.run_resolve("chat coder + gh ci + merge")
        self.assertFalse(explicit["defaulted"])
        self.assertEqual(
            [item["target"] for item in explicit["sequence"]],
            ["chat-coder", "ci", "merge"],
        )

        explicit_incomplete = self.run_resolve("chat coder + merge")
        self.assertFalse(explicit_incomplete["defaulted"])
        self.assertEqual(
            [item["target"] for item in explicit_incomplete["sequence"]],
            ["chat-coder", "merge"],
        )

        local = self.run_resolve("chat coder + local ci + merge")
        self.assertFalse(local["defaulted"])
        self.assertEqual(local["sequence"][1], {"alias": "local ci", "kind": "skill", "target": "local-ci"})
        self.assertEqual(
            [item["target"] for item in local["sequence"]],
            ["chat-coder", "local-ci", "merge"],
        )

        release = self.run_resolve("chat release")
        self.assertFalse(release["defaulted"])
        self.assertEqual(release["sequence"][0]["target"], "chat-release")

        hotfix = self.run_resolve("hotfix")
        self.assertFalse(hotfix["defaulted"])
        self.assertEqual(hotfix["sequence"][0]["target"], "hotfix")

    def test_standalone_default_schema_fails_closed(self):
        validator_text = VALIDATOR.read_text(encoding="utf-8")
        registry = json.loads((PROMPTS / "registry.json").read_text(encoding="utf-8"))
        cases = [
            ({"missing alias": ["chat coder", "gh ci", "merge"]}, "unknown alias"),
            ({"chat coder": []}, "non-empty list"),
            ({"chat coder": ["gh ci", "merge"]}, "must start with its source controller"),
            ({"chat coder": ["chat coder", "unknown stage"]}, "references unknown alias"),
        ]
        for defaults, expected in cases:
            with self.subTest(defaults=defaults), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "prompts").mkdir()
                (root / "_protocol" / "scripts").mkdir(parents=True)
                bad = json.loads(json.dumps(registry))
                bad["composition"]["standalone_defaults"] = defaults
                (root / "prompts" / "registry.json").write_text(
                    json.dumps(bad), encoding="utf-8"
                )
                (root / "_protocol" / "scripts" / "validate_prompt.py").write_text(
                    validator_text, encoding="utf-8"
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        str(root / "_protocol" / "scripts" / "validate_prompt.py"),
                        "resolve",
                        "chat coder",
                        "--root",
                        str(root),
                        "--json",
                    ],
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn(expected, result.stdout)

    def test_prompts_are_generic_and_separated(self):
        banned = [
            "SecretarIA",
            "secretaria-ci-delivery",
            "scripts/validate-all.sh",
            "fast-ci.yml",
            "coferlandia-ci, docker",
            "projects/1",
            "projects/2",
        ]
        texts = {}
        for name in ("chat-coder", "ci", "merge", "chat-release", "hotfix"):
            text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
            texts[name] = text
            for token in banned:
                self.assertNotIn(token, text, f"{name}.md hardcodes {token}")
        self.assertIn("READY_FOR_CI", texts["chat-coder"])
        self.assertIn("must not perform Qualification", texts["chat-coder"])
        self.assertIn("GITHUB_NATIVE", texts["ci"])
        self.assertIn("must not merge", texts["ci"])
        self.assertIn("REQUALIFICATION_REQUIRED", texts["merge"])
        self.assertIn("must not execute CI", texts["merge"])
        self.assertIn("authoritative target ref", texts["merge"])
        self.assertIn("not generically hardcoded to the repository default branch", texts["merge"])
        self.assertIn("does not generically assert", texts["merge"])
        self.assertIn("READY_FOR_RELEASE", texts["chat-release"])
        self.assertIn("coferlandia-release-publisher", texts["chat-release"])
        self.assertIn("TEMPORARY_MITIGATION", texts["hotfix"])
        self.assertIn("HOTFIX_BLOCKED", texts["hotfix"])

    def test_merge_explicitly_closes_work_item_after_authoritative_integration(self):
        text = (PROMPTS / "merge.md").read_text(encoding="utf-8")
        self.assertIn("Work-item closure is a required Integration closeout side effect", text)
        self.assertIn("explicitly close it through the available Issue/work-item mutation surface", text)
        self.assertIn("do **not** rely on `Closes`, `Fixes`, `Resolves`", text)
        self.assertIn("non-default integration target", text)
        self.assertIn("after the close operation, re-read the work item and verify it is closed", text)
        self.assertIn("CLOSEOUT_BLOCKED", text)
        self.assertIn("Do not report `COMPLETE` while required work-item closure is unverified", text)
        self.assertIn("Issue = <identity> / closed", text)

    def test_ci_is_resolved_explicitly_or_by_declared_chat_coder_default(self):
        text = (PROMPTS / "ci.md").read_text(encoding="utf-8")
        chat_coder = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        bootstrap = (PROMPTS / "BOOTSTRAP.md").read_text(encoding="utf-8")
        self.assertIn("## Invocation boundary", text)
        self.assertIn("This is a Chat prompt controller, not an Agent Skill", text)
        self.assertIn("registry-declared standalone `chat coder`", text)
        self.assertIn("does **not** by itself invoke this controller", text)
        self.assertIn("Standalone `chat dev` / `chat-dev` stops at `READY_FOR_CI`", text)
        self.assertIn("Qualification strategy is `GITHUB_NATIVE`", text)
        self.assertIn("standalone `chat coder` / `chat-coder` resolves", chat_coder)
        self.assertIn("standalone `chat dev` / `chat-dev` resolves only this Development stage", chat_coder)
        self.assertIn("explicit `+` composition", chat_coder)
        self.assertIn("internal durable handoff", chat_coder)
        self.assertIn("Next owner = <next resolved controller/surface or NONE>", chat_coder)
        self.assertIn("standalone `chat coder` / `chat-coder` resolves by default", bootstrap)
        self.assertIn("Explicit controller compositions execute left-to-right without applying standalone defaults", bootstrap)

    def test_standalone_chat_coder_has_unambiguous_top_level_status(self):
        bootstrap = (PROMPTS / "BOOTSTRAP.md").read_text(encoding="utf-8")
        self.assertIn("Chat Coder = COMPLETE", bootstrap)
        self.assertIn("Chat Coder = WAITING_CI", bootstrap)
        self.assertIn("Chat Coder = BLOCKED", bootstrap)
        self.assertIn("Stage = Development | Qualification | Integration", bootstrap)
        self.assertIn("Controller state = <exact underlying state>", bootstrap)
        self.assertIn("Next action = <specific action required>", bootstrap)
        self.assertIn("do not require a different controller command", bootstrap)

    def test_ci_reports_nonterminal_waiting_state_without_claiming_green(self):
        text = (PROMPTS / "ci.md").read_text(encoding="utf-8")
        self.assertIn("## Non-terminal GitHub Actions state", text)
        self.assertIn("Qualification workflow = WAITING_CI", text)
        self.assertIn("is a non-terminal Qualification state, not success", text)
        self.assertIn("continue observing the authoritative exact-SHA gate", text)
        self.assertIn("A stale or superseded run never becomes evidence", text)
        self.assertIn("yield immediately to `merge` without asking the user for confirmation", text)

    def test_ci_respects_profile_submission_mode_without_inventing_manual_dispatch(self):
        text = (PROMPTS / "ci.md").read_text(encoding="utf-8")
        self.assertIn("Trigger only the declared workflow/operation when explicit dispatch is required", text)
        self.assertIn("otherwise observe the repository's existing PR-event qualification", text)
        self.assertIn("Never introduce `workflow_dispatch` merely because this controller is GitHub-native", text)

    def test_chat_coder_claims_unassigned_issue_for_authenticated_user(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        self.assertIn("first state-changing action", text)
        self.assertIn("MUST assign it to the authenticated GitHub user", text)
        self.assertIn("verify that assignment succeeded", text)
        self.assertIn("preserve the existing ownership and stop", text)
        self.assertIn("Assignee = <authenticated GitHub user>", text)

    def test_chat_coder_accepts_only_explicit_repository_approved_delivery_context(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        self.assertIn("The default delivery context is ordinary repository development", text)
        self.assertIn("must never infer an exceptional lane", text)
        self.assertIn("An explicit controlling invocation may delegate", text)
        self.assertIn("current repository policy explicitly supports that context", text)
        self.assertIn("does not weaken Development requirements", text)
        self.assertIn("development-context blocker", text)
        self.assertIn("Do not silently fall back to ordinary development", text)
        self.assertIn("target/context mismatch blocks the handoff", text)
        self.assertIn("Delivery context = STANDARD | <explicit repository-approved context>", text)

    def test_chat_coder_reconciles_existing_tests_before_adding_coverage(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        self.assertIn("inspect the existing tests that cover the affected surface before adding or modifying tests", text)
        self.assertIn("update tests whose approved expected behavior intentionally changed", text)
        self.assertIn("remove tests only when the behavior or contract they verify was intentionally removed or superseded", text)
        self.assertIn("materially duplicate or overlapping tests", text)
        self.assertIn("parameterizing or consolidating existing tests", text)
        self.assertIn("test-only fixtures, helpers, mocks, snapshots or data", text)
        self.assertIn("do not leave obsolete tests skipped, disabled, commented out", text)
        self.assertIn("Test-count growth is not a goal", text)
        self.assertIn("smallest clear suite", text)
        self.assertIn("Never remove, weaken, bypass or broaden a test merely to make validation pass", text)
        self.assertIn("affected pre-existing tests were reviewed", text)
        self.assertIn("materially duplicate coverage without independent value", text)

    def test_chat_coder_ready_for_ci_requires_complete_cheap_validation(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        self.assertIn("every applicable cheap deterministic development check", text)
        self.assertIn("canonical complete frontend unit-test suite", text)
        self.assertIn("failing, skipped, unknown, stale", text)
        self.assertIn("effective or synthetic merge candidate", ready)
        self.assertIn("focused iteration tests are not used as a substitute", ready)
        self.assertIn("no applicable required development check is failing, skipped, unknown", ready)
        self.assertIn("Never weaken, delete, bypass, or broaden an assertion merely to make CI green", text)

    def test_chat_coder_ready_for_ci_distinguishes_versioned_contracts_from_reports(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        self.assertIn("explicitly declared as a versioned contract", text)
        self.assertIn("repository-owned generation or synchronization mechanism", text)
        self.assertIn("no unexpected diff", text)
        self.assertIn("missing, stale, manually approximated", text)
        self.assertIn("do not create, add to Git, or require snapshot freshness", text)
        self.assertIn("only when repository-owned policy explicitly declares that output to be a versioned contract", text)
        self.assertIn("repository-owned policy explicitly declares to be a versioned contract", ready)
        self.assertIn("freshness/idempotence/diff check", ready)
        self.assertIn("without unexpected diff", ready)
        self.assertIn("not synchronization prerequisites", ready)
        self.assertIn("not required to be committed or snapshot-fresh", ready)

    def test_ready_for_ci_currentizes_base_before_expensive_qualification(self):
        chat_coder = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ci = (PROMPTS / "ci.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        local_ci = (ROOT / "skills" / "engineering" / "local-ci" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Authoritative-base currentization before handoff", chat_coder)
        self.assertIn("Base SHA synchronized", chat_coder)
        self.assertIn("post-currentization validation", chat_coder)
        self.assertIn("DEVELOPMENT_CURRENTIZATION_BLOCKED", chat_coder)
        self.assertIn("Current-base qualification barrier", ci)
        self.assertIn("DEVELOPMENT_CURRENTIZATION_REQUIRED", ci)
        self.assertIn("do **not** currentize the branch inside Qualification", ci)
        self.assertIn("Base SHA synchronized:", ready)
        self.assertIn("base-sensitive selected Qualification profile", ready)
        self.assertIn("DEVELOPMENT_CURRENTIZATION_REQUIRED", local_ci)
        self.assertIn("must not currentize or mutate the candidate inside Qualification", local_ci)

    def test_chat_coder_ready_for_ci_requires_environment_classification(self):
        text = (PROMPTS / "chat-coder.md").read_text(encoding="utf-8")
        ready = (ROOT / "_protocol" / "delivery" / "READY_FOR_CI.md").read_text(encoding="utf-8")
        self.assertIn("### Environment / configuration impact", text)
        self.assertIn("Environment change: YES | NO", text)
        self.assertIn("Production required: YES | NO | CONDITIONAL", text)
        self.assertIn("Deployment action: <required action or NONE>", text)
        self.assertIn("Environment evidence:", text)
        self.assertIn("Environment change: YES | NO", ready)
        self.assertIn("Environment evidence:", ready)
        self.assertIn("when `Environment change: YES`", ready)
        self.assertIn("when `Environment change: NO`", ready)
        self.assertIn("secret values are never included", ready)

    def test_ci_rechecks_environment_declaration_before_qualification(self):
        text = (PROMPTS / "ci.md").read_text(encoding="utf-8")
        self.assertIn("## Environment / configuration qualification barrier", text)
        self.assertIn("re-evaluate the exact candidate against the authoritative base", text)
        self.assertIn("Environment change: YES", text)
        self.assertIn("Environment change: NO", text)
        self.assertIn("Fail closed when the declaration is missing, ambiguous or contradicted by the candidate", text)
        self.assertIn("Never expose or request secret values as qualification evidence", text)

    def test_bootstrap_is_small(self):
        bootstrap = (PROMPTS / "BOOTSTRAP.md").read_text(encoding="utf-8")
        full = sum(
            len((PROMPTS / f"{name}.md").read_text(encoding="utf-8"))
            for name in ("chat-coder", "ci", "merge", "chat-release", "hotfix")
        )
        self.assertLess(len(bootstrap), full // 3)


if __name__ == "__main__":
    unittest.main()
