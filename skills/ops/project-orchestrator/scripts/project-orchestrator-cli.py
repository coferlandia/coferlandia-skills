#!/usr/bin/env python3
"""Public entry point for the project-orchestrator skill."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from project_orchestrator_cli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
