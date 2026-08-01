#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Deterministic release maintenance for the coferlandia-skills repository."""

from release_maintainer.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
