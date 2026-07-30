#!/usr/bin/env python3
"""Correct the review-fix test fixture, then apply the reviewed patch."""
from pathlib import Path
import runpy

root = Path(__file__).resolve().parents[1]
patcher = root / "scripts" / "epic-11-review-fixes.py"
text = patcher.read_text(encoding="utf-8")
old = '''        self.next_number += 1\n        self.issues.append(item)\n        return item\n\n    def try_add_sub_issue'''
new = '''        self.next_number += 1\n        return item\n\n    def try_add_sub_issue'''
if old not in text:
    raise SystemExit("review fixture patch target not found")
patcher.write_text(text.replace(old, new, 1), encoding="utf-8")
runpy.run_path(str(patcher), run_name="__main__")
