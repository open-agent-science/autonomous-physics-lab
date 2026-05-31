#!/usr/bin/env bash
# Fast inner-loop validation: lint + the non-full_repo tests, in parallel.
#
# Use this during development for quick feedback. It excludes the slow
# full_repo smoke tests (run those — and the full suite — before opening a PR
# via `python3 -m pytest`, which is parallel by default; see TASK-0501).
#
# Requires the dev extras (which include pytest-xdist):
#   pip install -e ".[dev]"
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/validate_fast.py "$@"
