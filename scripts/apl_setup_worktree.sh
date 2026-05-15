#!/usr/bin/env bash
# Copy .claude/settings.local.json from the main project root to this worktree.
# Run once at the start of any new worktree session where the file is missing.
# Safe to re-run: exits 0 without overwriting if the file already exists.

set -euo pipefail

WORKTREE_ROOT="$(git rev-parse --show-toplevel)"
DEST="$WORKTREE_ROOT/.claude/settings.local.json"

if [ -f "$DEST" ]; then
    echo "Already present: $DEST"
    exit 0
fi

# git --git-common-dir returns the main repo's .git directory.
# For a worktree it is an absolute path; for the main checkout it is ".git".
GIT_COMMON_RAW="$(git rev-parse --git-common-dir)"
GIT_COMMON="$(cd "$GIT_COMMON_RAW" && pwd)"
MAIN_REPO_ROOT="$(dirname "$GIT_COMMON")"

SRC="$MAIN_REPO_ROOT/.claude/settings.local.json"

if [ ! -f "$SRC" ]; then
    echo "Source not found: $SRC"
    echo "Run this script from a worktree of the Autonomous Physics Lab repository."
    exit 1
fi

mkdir -p "$WORKTREE_ROOT/.claude"
cp "$SRC" "$DEST"
echo "Copied: $SRC  ->  $DEST"
