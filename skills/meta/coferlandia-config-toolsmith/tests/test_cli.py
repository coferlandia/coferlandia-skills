from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))
from coferlandia_config_toolsmith_cli.model import load_data, validate_contract
from coferlandia_config_toolsmith_cli.operations import decide_candidate, generate_docs, generate_facade, check_drift

FIXTURES = SKILL / "tests" / "fixtures"

class TestContract(unittest.TestCase):
    def test_valid_contract(self):
        result=validate_contract(load_data(FIXTURES/"valid-contract.yaml")); self.assertTrue(result.valid, result.errors)
    def test_state_projection_rejected(self):
        result=validate_contract(load_data(FIXTURES/"invalid-state-contract.yaml")); self.assertFalse(result.valid); self.assertTrue(any("effective_value" in e for e in result.errors))

class TestCandidateLifecycle(unittest.TestCase):
    def test_approve_and_stale_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); contract=root/"contract.yaml"; candidates=root/"candidates.yaml"; decisions=root/"decisions.yaml"
            contract.write_text((FIXTURES/"valid-contract.yaml").read_text(),encoding="utf-8")
            candidates.write_text((FIXTURES/"candidates.yaml").read_text(),encoding="utf-8")
            result=decide_candidate(action="approve",candidate_id="CFG-CAND-001",candidates_path=candidates,contract_path=contract,decisions_path=decisions,expected_fingerprint="sha256:test-source",dry_run=False)
            self.assertTrue(result["contract_changed"])
            keys=[f["key"] for m in load_data(contract)["modules"] for f in m["fields"]]
            self.assertIn("notifications.sms.enabled",keys)
            self.assertEqual(load_data(candidates)["candidates"][0]["status"],"implemented")
            # reset candidate to prove stale protection
            data=load_data(candidates); data["candidates"][0]["status"]="pending"; candidates.write_text(json.dumps(data),encoding="utf-8")
            with self.assertRaises(Exception):
                decide_candidate(action="approve",candidate_id="CFG-CAND-001",candidates_path=candidates,contract_path=contract,decisions_path=decisions,expected_fingerprint="sha256:wrong",dry_run=False)
            self.assertEqual(load_data(candidates)["candidates"][0]["status"],"stale")

class TestGeneration(unittest.TestCase):
    def test_docs_are_deterministic_and_drift_detected(self):
        contract=load_data(FIXTURES/"valid-contract.yaml")
        with tempfile.TemporaryDirectory() as td:
            out=Path(td); generate_docs(contract,out,dry_run=False)
            first={p.name:p.read_text() for p in out.iterdir()}; generate_docs(contract,out,dry_run=False); second={p.name:p.read_text() for p in out.iterdir()}
            self.assertEqual(first,second); self.assertTrue(check_drift(contract,out)["clean"])
            (out/"CONFIG-SAFETY.md").write_text("drift",encoding="utf-8"); self.assertFalse(check_drift(contract,out)["clean"])
    def test_generated_python_facade_reads_and_writes_native_stores(self):
        contract=load_data(FIXTURES/"valid-contract.yaml")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"pyproject.toml").write_text("[project]\nname='sample'\n",encoding="utf-8")
            (root/".env").write_text("REMINDER_LEAD_MINUTES=60\nUNRELATED=keep\n",encoding="utf-8")
            (root/"config").mkdir(); (root/"config/native.json").write_text('{"notifications":{"email":{"enabled":true}}}\n',encoding="utf-8")
            result=generate_facade(contract,root,"python",dry_run=False); self.assertEqual(result["platform"],"python")
            cli=root/"scripts/sample-config-cli.py"
            get=subprocess.run([sys.executable,str(cli),"--root",str(root),"config","get","notifications.reminder_lead_minutes"],capture_output=True,text=True)
            self.assertEqual(get.returncode,0,get.stderr); self.assertEqual(json.loads(get.stdout)["result"]["value"],"60")
            dry=subprocess.run([sys.executable,str(cli),"--root",str(root),"config","set","notifications.reminder_lead_minutes","120","--dry-run"],capture_output=True,text=True)
            self.assertEqual(dry.returncode,0); self.assertIn("REMINDER_LEAD_MINUTES=60",(root/".env").read_text())
            applied=subprocess.run([sys.executable,str(cli),"--root",str(root),"config","set","notifications.reminder_lead_minutes","120","--confirm"],capture_output=True,text=True)
            self.assertEqual(applied.returncode,0,applied.stdout+applied.stderr); text=(root/".env").read_text(); self.assertIn("REMINDER_LEAD_MINUTES=120",text); self.assertIn("UNRELATED=keep",text)
            secret=subprocess.run([sys.executable,str(cli),"--root",str(root),"config","secret","set","notifications.telegram.token","--stdin","--confirm"],input="top-secret\n",capture_output=True,text=True)
            self.assertEqual(secret.returncode,0); self.assertNotIn("top-secret",secret.stdout); self.assertIn("TELEGRAM_TOKEN=top-secret",(root/".env").read_text())
    def test_stale_plan_rejected(self):
        contract=load_data(FIXTURES/"valid-contract.yaml")
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/"pyproject.toml").write_text("[project]\nname='sample'\n"); (root/".env").write_text("REMINDER_LEAD_MINUTES=60\n"); (root/"config").mkdir(); (root/"config/native.json").write_text('{}\n')
            generate_facade(contract,root,"python",dry_run=False); cli=root/"scripts/sample-config-cli.py"; plan=root/"plan.json"
            prep=subprocess.run([sys.executable,str(cli),"--root",str(root),"config","prepare-change","--set","notifications.reminder_lead_minutes=120","--output",str(plan)],capture_output=True,text=True); self.assertEqual(prep.returncode,0,prep.stdout)
            (root/".env").write_text("REMINDER_LEAD_MINUTES=90\n")
            apply=subprocess.run([sys.executable,str(cli),"--root",str(root),"config","apply-plan","--plan-file",str(plan),"--confirm"],capture_output=True,text=True)
            self.assertEqual(apply.returncode,3); self.assertIn("stale_plan",apply.stdout)

if __name__ == "__main__": unittest.main()
