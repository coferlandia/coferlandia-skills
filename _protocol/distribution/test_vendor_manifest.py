from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "_protocol" / "distribution" / "vendor_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("vendor_manifest", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VendorManifestTests(unittest.TestCase):
    def test_manifest_is_reproducible_and_detects_byte_drift(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            (root / "prompts").mkdir(parents=True)
            (root / "prompts" / "chat-coder.md").write_text("hello\n", encoding="utf-8")
            (root / "_protocol" / "delivery").mkdir(parents=True)
            (root / "_protocol" / "delivery" / "READY_FOR_CI.md").write_text("ready\n", encoding="utf-8")
            (root / "skills" / "meta" / "demo").mkdir(parents=True)
            (root / "skills" / "meta" / "demo" / "SKILL.md").write_text("skill\n", encoding="utf-8")

            first = module.build_manifest(root, release_version="1.2.3", source_revision="a" * 40)
            second = module.build_manifest(root, release_version="1.2.3", source_revision="a" * 40)
            self.assertEqual(first, second)

            consumer = Path(tmp) / "consumer"
            for entry in first["entries"]:
                target = consumer / entry["consumer_path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                source = root / entry["source_path"]
                target.write_bytes(source.read_bytes())

            provenance = {
                "schema_version": 1,
                "source_repository": "coferlandia/coferlandia-skills",
                "source_release_version": "1.2.3",
                "source_revision": "a" * 40,
                "families": ["prompts", "delivery", "skill:demo"],
            }
            ok = module.check_consumer(consumer, first, provenance)
            self.assertEqual(ok["status"], "ok")

            target = consumer / ".agents" / "prompts" / "chat-coder.md"
            target.write_text("changed\n", encoding="utf-8")
            drift = module.check_consumer(consumer, first, provenance)
            self.assertEqual(drift["status"], "error")
            self.assertIn(".agents/prompts/chat-coder.md", drift["modified"])

    def test_missing_artifact_and_revision_mismatch_fail_closed(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            (root / "prompts").mkdir(parents=True)
            (root / "prompts" / "ci.md").write_text("ci\n", encoding="utf-8")
            manifest = module.build_manifest(root, release_version="2.0.0", source_revision="b" * 40)
            consumer = Path(tmp) / "consumer"
            provenance = {
                "schema_version": 1,
                "source_repository": "coferlandia/coferlandia-skills",
                "source_release_version": "2.0.0",
                "source_revision": "c" * 40,
                "families": ["prompts"],
            }
            result = module.check_consumer(consumer, manifest, provenance)
            self.assertEqual(result["status"], "error")
            self.assertTrue(result["missing"])
            self.assertIn("source_revision", result["provenance_errors"])

    def test_selected_artifacts_and_declared_overlays_are_supported(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            (root / "prompts").mkdir(parents=True)
            (root / "prompts" / "chat-coder.md").write_text("chat\n", encoding="utf-8")
            (root / "prompts" / "registry.json").write_text("{}\n", encoding="utf-8")
            manifest = module.build_manifest(root, release_version="2.1.0", source_revision="e" * 40)

            consumer = Path(tmp) / "consumer"
            exact = consumer / ".agents" / "prompts" / "chat-coder.md"
            exact.parent.mkdir(parents=True, exist_ok=True)
            exact.write_text("chat\n", encoding="utf-8")
            overlay = consumer / ".agents" / "prompts" / "registry.json"
            overlay.write_text('{"local": true}\n', encoding="utf-8")

            provenance = {
                "schema_version": 1,
                "source_repository": "coferlandia/coferlandia-skills",
                "source_release_version": "2.1.0",
                "source_revision": "e" * 40,
                "families": ["prompts"],
                "artifacts": [".agents/prompts/chat-coder.md"],
                "overlays": [
                    {
                        "consumer_path": ".agents/prompts/registry.json",
                        "reason": "repository-local registry extension",
                    }
                ],
            }
            result = module.check_consumer(consumer, manifest, provenance)
            self.assertEqual(result["status"], "ok")
            self.assertEqual(result["checked"], 1)
            self.assertEqual(result["overlays"], [".agents/prompts/registry.json"])

    def test_unknown_or_conflicting_selection_fails_closed(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            (root / "prompts").mkdir(parents=True)
            (root / "prompts" / "ci.md").write_text("ci\n", encoding="utf-8")
            manifest = module.build_manifest(root, release_version="2.2.0", source_revision="f" * 40)
            consumer = Path(tmp) / "consumer"
            target = consumer / ".agents" / "prompts" / "ci.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("ci\n", encoding="utf-8")
            provenance = {
                "schema_version": 1,
                "source_repository": "coferlandia/coferlandia-skills",
                "source_release_version": "2.2.0",
                "source_revision": "f" * 40,
                "families": ["prompts"],
                "artifacts": [".agents/prompts/ci.md", ".agents/prompts/missing.md"],
                "overlays": [
                    {"consumer_path": ".agents/prompts/ci.md", "reason": "invalid overlap"},
                    {"consumer_path": ".agents/prompts/unknown.md", "reason": "unknown"},
                ],
            }
            result = module.check_consumer(consumer, manifest, provenance)
            self.assertEqual(result["status"], "error")
            self.assertIn("artifact:.agents/prompts/missing.md", result["provenance_errors"])
            self.assertIn("overlay:.agents/prompts/unknown.md", result["provenance_errors"])
            self.assertIn(
                "artifact-overlay-conflict:.agents/prompts/ci.md",
                result["provenance_errors"],
            )

    def test_unmanaged_extra_files_do_not_break_exact_selected_families(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            (root / "skills" / "content" / "demo").mkdir(parents=True)
            (root / "skills" / "content" / "demo" / "SKILL.md").write_text("demo\n", encoding="utf-8")
            manifest = module.build_manifest(root, release_version="3.0.0", source_revision="d" * 40)
            consumer = Path(tmp) / "consumer"
            expected = consumer / ".agents" / "skills" / "demo" / "SKILL.md"
            expected.parent.mkdir(parents=True, exist_ok=True)
            expected.write_text("demo\n", encoding="utf-8")
            extra = consumer / ".agents" / "skills" / "local-only" / "SKILL.md"
            extra.parent.mkdir(parents=True, exist_ok=True)
            extra.write_text("local\n", encoding="utf-8")
            provenance = {
                "schema_version": 1,
                "source_repository": "coferlandia/coferlandia-skills",
                "source_release_version": "3.0.0",
                "source_revision": "d" * 40,
                "families": ["skill:demo"],
            }
            result = module.check_consumer(consumer, manifest, provenance)
            self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
