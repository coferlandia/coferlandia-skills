from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "test_skills.py"


def load_module():
    spec = importlib.util.spec_from_file_location("test_skills", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"No se pudo cargar {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillTestingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()
        temp_base = Path(os.environ.get("COFERLANDIA_TEST_TMP", Path.cwd() / ".test-tmp"))
        temp_base.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=temp_base)
        self.root = Path(self.tmp.name)
        (self.root / "skills" / "meta").mkdir(parents=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_skill(
        self,
        name: str,
        *,
        extra_frontmatter: str = "",
        body: str = "## Pasos\n\n1. Ejecutar la tarea.\n\n## Gotchas\n\n- Evitar entradas vacias.\n",
        status: str = "draft",
    ) -> Path:
        skill = self.root / "skills" / "meta" / name
        skill.mkdir(parents=True)
        tested = '\n  tested: "2026-06-12 - prueba"' if status == "active" else ""
        (skill / "SKILL.md").write_text(
            "---\n"
            f"name: {name}\n"
            "description: Valida Agent Skills. Usar cuando se auditan skills o su metadata.\n"
            f"{extra_frontmatter}"
            "metadata:\n"
            "  category: meta\n"
            f"  status: {status}"
            f"{tested}\n"
            "---\n\n"
            f"{body}",
            encoding="utf-8",
        )
        return skill

    def write_index(self, *names: str) -> None:
        rows = "\n".join(
            f"| [{name}](./meta/{name}/) | Test | draft |" for name in names
        )
        (self.root / "skills" / "INDEX.md").write_text(
            "| Skill | Descripcion | Status |\n"
            "|---|---|---|\n"
            f"{rows}\n",
            encoding="utf-8",
        )

    def test_rejects_noncanonical_when_to_use(self) -> None:
        skill = self.write_skill(
            "bad-frontmatter",
            extra_frontmatter="when_to_use: Usar siempre.\n",
        )

        result = self.module.audit_skill(skill, self.root)

        self.assertIn("frontmatter.unknown-field", self.issue_codes(result))

    def test_requires_active_skill_behavioral_evidence(self) -> None:
        skill = self.write_skill("active-without-cases", status="active")

        result = self.module.audit_skill(skill, self.root)

        self.assertIn("behavior.missing-cases", self.issue_codes(result))

    def test_behavior_cases_must_be_nonempty_lists(self) -> None:
        skill = self.write_skill("invalid-cases", status="active")
        tests = skill / "tests"
        tests.mkdir()
        (tests / "cases.json").write_text(
            json.dumps({"positive": "un prompt", "negative": ["otro prompt"]}),
            encoding="utf-8",
        )

        result = self.module.audit_skill(skill, self.root)

        self.assertIn("behavior.invalid-cases", self.issue_codes(result))

    def test_detects_index_drift(self) -> None:
        self.write_skill("indexed-skill")
        self.write_skill("missing-skill")
        self.write_index("indexed-skill", "stale-skill")

        result = self.module.audit_repository(self.root)

        codes = self.issue_codes(result)
        self.assertIn("index.missing-skill", codes)
        self.assertIn("index.stale-entry", codes)

    def test_detects_broken_local_markdown_link(self) -> None:
        skill = self.write_skill(
            "broken-link",
            body=(
                "## Pasos\n\n1. Leer [referencia](references/missing.md).\n\n"
                "## Gotchas\n\n- Verificar rutas.\n"
            ),
        )

        result = self.module.audit_skill(skill, self.root)

        self.assertIn("links.broken", self.issue_codes(result))

    def test_detects_broken_repository_document_link(self) -> None:
        self.write_skill("good-skill")
        self.write_index("good-skill")
        (self.root / "README.md").write_text(
            "Lee [la guía](docs/missing.md).\n",
            encoding="utf-8",
        )

        result = self.module.audit_repository(self.root)

        self.assertIn("links.broken", self.issue_codes(result))

    def test_checks_script_contract(self) -> None:
        skill = self.write_skill("script-contract")
        scripts = skill / "scripts"
        scripts.mkdir()
        (scripts / "bad.py").write_text("print('texto libre')\n", encoding="utf-8")

        result = self.module.audit_skill(skill, self.root)

        codes = self.issue_codes(result)
        self.assertIn("script.missing-pep723", codes)
        self.assertIn("script.missing-help", codes)

    def test_valid_skill_with_behavior_cases_passes(self) -> None:
        skill = self.write_skill("good-skill", status="active")
        tests = skill / "tests"
        tests.mkdir()
        (tests / "cases.json").write_text(
            json.dumps(
                {
                    "positive": ["Audita las skills de este repositorio"],
                    "negative": ["Calcula dos mas dos"],
                }
            ),
            encoding="utf-8",
        )
        self.write_index("good-skill")

        result = self.module.audit_repository(self.root)

        self.assertTrue(result["ok"], result)

    @staticmethod
    def issue_codes(result: dict) -> set[str]:
        return {issue["code"] for issue in result.get("issues", [])}


if __name__ == "__main__":
    unittest.main()
