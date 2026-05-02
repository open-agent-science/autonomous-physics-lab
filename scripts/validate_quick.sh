#!/usr/bin/env bash
# Quick local validation: lint + tests only. No example runs, no repo scan.
# Use this for fast iteration feedback during development.
# Run full validation (AGENTS.md) before opening a PR.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m ruff check .
python3 -m pytest -q
