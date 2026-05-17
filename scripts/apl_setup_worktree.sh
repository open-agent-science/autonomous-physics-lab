#!/usr/bin/env bash
# Populate .claude/settings.local.json in the current worktree.
#
# Default (no flag):
#   Copy settings.local.json from the main repo root. Preserves any
#   per-contributor allowlist accumulated outside the committed baseline.
#
# --mode safe:
#   Write the safe profile (empty allow list). Relies entirely on the committed
#   baseline in .claude/settings.json. Anything outside the baseline triggers a
#   manual approval prompt. Recommended for onboarding and unfamiliar work.
#
# --mode autonomous:
#   Write the autonomous profile (Bash(*) plus broad /tmp/apl-* access).
#   No command confirmations during a session. Use only when you trust the
#   agent and the task scope is clear.
#
# All modes are idempotent: if .claude/settings.local.json already exists, the
# script exits without overwriting.
#
# See .claude/profiles/README.md for the full mode reference.

set -euo pipefail

MODE=""

usage() {
    cat <<'EOF'
Usage: apl_setup_worktree.sh [--mode safe|autonomous] [--help]

Without --mode, copies settings.local.json from the main repo root.
With --mode safe, writes the committed safe profile.
With --mode autonomous, writes the committed autonomous profile.

The script never overwrites an existing settings.local.json.
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        --mode)
            shift
            if [ $# -eq 0 ]; then
                echo "Error: --mode requires a value (safe|autonomous)" >&2
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
    ""|safe|autonomous) ;;
    *)
        echo "Error: --mode must be 'safe' or 'autonomous' (got: $MODE)" >&2
        exit 2
        ;;
esac

WORKTREE_ROOT="$(git rev-parse --show-toplevel)"
DEST="$WORKTREE_ROOT/.claude/settings.local.json"

if [ -f "$DEST" ]; then
    echo "Already present: $DEST"
    echo "Remove or rename it first if you want to switch modes."
    exit 0
fi

mkdir -p "$WORKTREE_ROOT/.claude"

if [ -n "$MODE" ]; then
    SRC="$WORKTREE_ROOT/.claude/profiles/$MODE.json"

    if [ ! -f "$SRC" ]; then
        echo "Error: profile not found: $SRC" >&2
        echo "This worktree may be on an older branch without committed profiles." >&2
        exit 1
    fi

    cp "$SRC" "$DEST"
    echo "Wrote ${MODE} profile to: $DEST"
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
    echo "No personal settings.local.json found at: $SRC"
    echo ""
    echo "Pick one of these modes instead:"
    echo "  ./scripts/apl_setup_worktree.sh --mode safe         # default for onboarding"
    echo "  ./scripts/apl_setup_worktree.sh --mode autonomous   # no command prompts"
    echo ""
    echo "See .claude/profiles/README.md for details."
    exit 1
fi

cp "$SRC" "$DEST"
echo "Copied: $SRC  ->  $DEST"
