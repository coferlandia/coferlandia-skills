from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


SKILL = Path(__file__).parents[1]
SCRIPT = SKILL / "scripts" / "render_log.py"
EXAMPLE = SKILL / "references" / "example-log.ndjson"


class RenderLogTests(unittest.TestCase):
    def test_renders_utf8_when_parent_console_is_cp1252(self) -> None:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"

        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), str(EXAMPLE), "--view", "digest"],
            capture_output=True,
            env=env,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr.decode(errors="replace"))
        self.assertIn("✅".encode(), completed.stdout)


if __name__ == "__main__":
    unittest.main()
