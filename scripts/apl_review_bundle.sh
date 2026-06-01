#!/usr/bin/env bash
# Linux/macOS convenience wrapper for the portable Python implementation.
# Usage: ./scripts/apl_review_bundle.sh [base-branch]
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
exec python3 "$REPO_ROOT/scripts/apl_review_bundle.py" "${1:-main}" --root "$REPO_ROOT"
