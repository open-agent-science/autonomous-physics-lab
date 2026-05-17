#!/usr/bin/env bash
# Populate .claude/settings.local.json in the current worktree.
#
# Default (no flag):
#   Copy settings.local.json from the main repo root. Preserves any
#   per-contributor allowlist accumulated outside the committed baseline.
#   This is the safe onboarding path.
#
# --mode autonomous:
#   Write the autonomous profile (Bash(*) plus broad /tmp/apl-* access).
#   No command confirmations during a session. Use only when you trust the
#   agent and the task scope is clear, e.g. supervised agent loops.
#
# Both invocations are idempotent: if .claude/settings.local.json already
# exists, the script exits without overwriting.
#
# See .claude/profiles/README.md for the full mode reference.

set -euo pipefail

MODE=""

usage() {
    cat <<'EOF'
Usage: apl_setup_worktree.sh [--mode autonomous] [--help]

Without --mode, copies settings.local.json from the main repo root
(safe onboarding default).

With --mode autonomous, writes the committed autonomous profile that allows
all bash commands without confirmation prompts.

The script never overwrites an existing settings.local.json.
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --mode)
            shift
            if [ $# -eq 0 ]; then
                echo "Error: --mode requires a value (autonomous)" >&2
                usage >&2
                exit 2
            fi
            MODE="$1"
            ;;
        --mode=*)
            MODE="${1#--mode=}"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Error: unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

case "$MODE" in
    ""|autonomous) ;;
    *)
        echo "Error: --mode must be 'autonomous' (got: $MODE)" >&2
        exit 2
        ;;
esac

WORKTREE_ROOT="$(git rev-parse --show-toplevel)"
DEST="$WORKTREE_ROOT/.claude/settings.local.json"

if [ -f "$DEST" ]; then
    echo "Already present: $DEST"
    echo "Remove it first if you want to switch modes."
    exit 0
fi

mkdir -p "$WORKTREE_ROOT/.claude"

if [ "$MODE" = "autonomous" ]; then
    SRC="$WORKTREE_ROOT/.claude/profiles/autonomous.json"

    if [ ! -f "$SRC" ]; then
        echo "Error: profile not found: $SRC" >&2
        echo "This worktree may be on an older branch without committed profiles." >&2
        exit 1
    fi

    cp "$SRC" "$DEST"
    echo "Wrote autonomous profile to: $DEST"
    echo "See .claude/profiles/README.md for what this mode allows."
    exit 0
fi

# Default behavior: copy personal settings.local.json from the main repo.
# git --git-common-dir returns the main repo's .git directory.
# For a worktree it is an absolute path; for the main checkout it is ".git".
GIT_COMMON_RAW="$(git rev-parse --git-common-dir)"
GIT_COMMON="$(cd "$GIT_COMMON_RAW" && pwd)"
MAIN_REPO_ROOT="$(dirname "$GIT_COMMON")"

SRC="$MAIN_REPO_ROOT/.claude/settings.local.json"

if [ ! -f "$SRC" ]; then
    echo "Source not found: $SRC"
    echo "Run this script from a worktree of the Autonomous Physics Lab repository."
    echo ""
    echo "If you want a fully autonomous setup instead, run:"
    echo "  ./scripts/apl_setup_worktree.sh --mode autonomous"
    exit 1
fi

cp "$SRC" "$DEST"
echo "Copied: $SRC  ->  $DEST"
