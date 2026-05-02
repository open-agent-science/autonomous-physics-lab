#!/usr/bin/env bash
# Produce a PR review bundle: branch info + git diff vs main in one Markdown file.
# Output: _snapshots/review_<safe-branch>_<timestamp>.md
# Usage: ./scripts/apl_review_bundle.sh [base-branch]
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

BASE="${1:-main}"
BRANCH="$(git branch --show-current)"
SAFE_BRANCH="$(echo "$BRANCH" | tr '/' '-')"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
OUT="_snapshots/review_${SAFE_BRANCH}_${TIMESTAMP}.md"

mkdir -p _snapshots

{
  echo "# PR Review Bundle"
  echo
  echo "- branch: \`$BRANCH\`"
  echo "- base: \`$BASE\`"
  echo "- generated_at_utc: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo

  echo "## Git status"
  echo '```'
  git status --short
  echo '```'
  echo

  echo "## Commits vs $BASE"
  echo '```'
  git log --oneline "$BASE..HEAD"
  echo '```'
  echo

  echo "## Changed files vs $BASE"
  echo '```'
  git diff --name-only "$BASE...HEAD"
  echo '```'
  echo

  echo "## Diff stat vs $BASE"
  echo '```'
  git diff --stat "$BASE...HEAD"
  echo '```'
  echo

  echo "## Full diff vs $BASE"
  echo '```diff'
  git diff "$BASE...HEAD"
  echo '```'

} > "$OUT"

echo "Review bundle written to: $OUT"
