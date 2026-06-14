#!/usr/bin/env bash
# Create a fresh git worktree for a task branch and initialize it for
# agent work.
#
# Usage:
#   ./scripts/apl_new_worktree.sh <branch-name>
#   ./scripts/apl_new_worktree.sh <branch-name> <worktree-path>
#
# The default worktree path is .worktrees/<branch-slug>/ inside the
# project, where <branch-slug> replaces "/" with "_" in the branch
# name so the directory name is filesystem-safe. .worktrees/ is
# already gitignored so the new directory does not appear in
# git status. Keeping the worktree inside the project also avoids
# the Claude Code permission prompts that fire when a worktree
# lives outside the current working directory (see TASK-0271).
#
# An explicit second-argument path always overrides the default and
# may point anywhere (including outside the project) when the agent
# has a specific reason to do so.
#
# The script:
#
# 1. Refuses to run if the branch already exists locally — name conflicts
#    are usually the symptom of a duplicate task being set up by another
#    agent, and we want the human to resolve them rather than overwrite.
# 2. Creates the worktree from the current main branch tip (origin/main
#    when available, falls back to main).
# 3. Runs apl_setup_worktree.sh inside the new worktree to copy local
#    settings.
# 4. Prints next-step commands so the agent can switch into the new
#    worktree.
#
# Why this exists: parallel agent sessions sharing a single checkout can
# step on each other's branches and untracked files (see TASK-0263). A
# dedicated worktree per task is the safest isolation level short of a
# separate clone.

set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
    cat <<'USAGE' >&2
Usage: apl_new_worktree.sh <branch-name> [<worktree-path>]

Example:
  ./scripts/apl_new_worktree.sh agent/gladunrv/claude/task-0263-foo
  ./scripts/apl_new_worktree.sh agent/gladunrv/claude/task-0263-foo .worktrees/task-0263-foo
USAGE
    exit 2
fi

BRANCH="$1"
DEFAULT_PATH=".worktrees/$(echo "$BRANCH" | tr '/' '_')"
WORKTREE_PATH="${2:-$DEFAULT_PATH}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "Branch already exists locally: $BRANCH" >&2
    echo "Use 'git worktree add $WORKTREE_PATH $BRANCH' to attach to it, or pick a different branch name." >&2
    exit 1
fi

if [ -e "$WORKTREE_PATH" ]; then
    echo "Worktree path already exists: $WORKTREE_PATH" >&2
    echo "Remove it or choose a different path." >&2
    exit 1
fi

if git show-ref --verify --quiet "refs/remotes/origin/main"; then
    BASE_REF="origin/main"
else
    BASE_REF="main"
fi

echo "Creating worktree:"
echo "  branch: $BRANCH"
echo "  path:   $WORKTREE_PATH"
echo "  base:   $BASE_REF"
git worktree add "$WORKTREE_PATH" -b "$BRANCH" "$BASE_REF"

if [ -x "$REPO_ROOT/scripts/apl_setup_worktree.sh" ]; then
    (
        cd "$WORKTREE_PATH"
        "$REPO_ROOT/scripts/apl_setup_worktree.sh" || true
    )
fi

cat <<EOF

Worktree ready.

Next steps:
  cd "$WORKTREE_PATH"
  git status
  # ... do task work ...
  python3 "$REPO_ROOT/scripts/apl_branch_precondition.py" --expected-branch "$BRANCH"

When the task is merged, clean up with:
  git worktree remove "$WORKTREE_PATH"
EOF
