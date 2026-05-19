#!/usr/bin/env bash
# auto_run_next_task.sh
#
# Check the local Claude Code token budget and, when headroom remains,
# pick the next highest-priority READY task and invoke the claude CLI.
#
# Usage:
#   ./scripts/auto_run_next_task.sh [--dry-run] [--max-turns N]
#
# Environment variables (all optional):
#   CLAUDE_MONTHLY_TOKEN_LIMIT   token limit passed to check_claude_budget.py
#   CLAUDE_BUDGET_THRESHOLD_PCT  block above this % (default 50)
#   CLAUDE_MAX_TURNS             max agent turns (default 80)
#   REPO_ROOT                    path to repo (default: dir of this script/..)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${REPO_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

DRY_RUN=false
MAX_TURNS="${CLAUDE_MAX_TURNS:-80}"

# Parse CLI flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true; shift ;;
    --max-turns) MAX_TURNS="$2"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

# ── 1. Budget gate ──────────────────────────────────────────────────────────
echo "=== Claude Code budget check ===" >&2

BUDGET_ARGS=()
[[ -n "${CLAUDE_MONTHLY_TOKEN_LIMIT:-}" ]] && BUDGET_ARGS+=(--limit "$CLAUDE_MONTHLY_TOKEN_LIMIT")
[[ -n "${CLAUDE_BUDGET_THRESHOLD_PCT:-}" ]] && BUDGET_ARGS+=(--threshold "$CLAUDE_BUDGET_THRESHOLD_PCT")

BUDGET_JSON=$(python3 "$SCRIPT_DIR/check_claude_budget.py" --dry-run "${BUDGET_ARGS[@]}")
echo "$BUDGET_JSON" >&2

UNDER_THRESHOLD=$(echo "$BUDGET_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d['under_threshold']).lower())")
USED_PCT=$(echo "$BUDGET_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['used_pct'])")

if [[ "$UNDER_THRESHOLD" != "true" ]]; then
  echo "" >&2
  echo "Budget gate: BLOCKED — usage ${USED_PCT}% is at or above threshold." >&2
  echo "Set CLAUDE_BUDGET_THRESHOLD_PCT to a higher value to override." >&2
  exit 0
fi

echo "" >&2
echo "Budget gate: OK — usage ${USED_PCT}% is below threshold." >&2

# ── 2. Pick next task ───────────────────────────────────────────────────────
echo "" >&2
echo "=== Selecting next task ===" >&2

MISSION_JSON=$(cd "$REPO_ROOT" && python3 scripts/apl_mission.py --json 2>/dev/null)

NEXT_TASK=$(echo "$MISSION_JSON" | python3 - <<'PYEOF'
import sys, json

data = json.load(sys.stdin)
candidates = data.get("live_task_candidates", [])

# Filter to READY only, sort by priority weight then difficulty
priority_weight = {"high": 0, "medium": 1, "low": 2}
difficulty_weight = {"low": 0, "medium": 1, "high": 2}

ready = [c for c in candidates if c.get("status", "").upper() == "READY"]
ready.sort(key=lambda c: (
    priority_weight.get(c.get("priority", "low"), 9),
    difficulty_weight.get(c.get("difficulty", "high"), 9),
))

if ready:
    best = ready[0]
    print(json.dumps({
        "task_id": best.get("task_id"),
        "title": best.get("title", ""),
        "priority": best.get("priority"),
        "difficulty": best.get("difficulty"),
    }))
else:
    print(json.dumps(None))
PYEOF
)

if [[ "$NEXT_TASK" == "null" || -z "$NEXT_TASK" ]]; then
  echo "No READY tasks found. Nothing to do." >&2
  exit 0
fi

TASK_ID=$(echo "$NEXT_TASK" | python3 -c "import sys,json; print(json.load(sys.stdin)['task_id'])")
TASK_TITLE=$(echo "$NEXT_TASK" | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")

echo "Selected: $TASK_ID — $TASK_TITLE" >&2

# ── 3. Build task prompt ────────────────────────────────────────────────────
TASK_FILE=$(find "$REPO_ROOT/tasks" -name "${TASK_ID}-*.yaml" | head -1)
if [[ -z "$TASK_FILE" ]]; then
  echo "ERROR: task file for $TASK_ID not found in tasks/" >&2
  exit 1
fi

PROMPT=$(cat <<PROMPT
Execute task $TASK_ID from the Autonomous Physics Lab repository.
Task file: $TASK_FILE
Title: $TASK_TITLE

Follow all protocols in AGENTS.md and docs/agent-task-protocol.md exactly:
- Transition status READY → IN_PROGRESS before editing
- Work on a branch: agent/<contributor-id>/<agent-id>/task-<number>-<slug>
- Run full validation: ruff, pytest, validate-repo --strict, example runs, apl_review_bundle.sh
- Transition status → REVIEW_READY after validation passes
- Open a PR using apl_task_pr_helper.py with the full PR template body
- Do NOT push to main. Do NOT promote claims or write PRED-*.yaml files.
PROMPT
)

# ── 4. Invoke (or dry-run) ──────────────────────────────────────────────────
echo "" >&2
if [[ "$DRY_RUN" == "true" ]]; then
  echo "=== DRY RUN — would invoke ===" >&2
  echo "claude --max-turns $MAX_TURNS -p \"$(echo "$PROMPT" | head -1)...\"" >&2
  echo "" >&2
  echo "Full prompt:" >&2
  echo "$PROMPT" >&2
  exit 0
fi

echo "=== Invoking claude CLI ===" >&2
echo "" >&2

cd "$REPO_ROOT"
exec claude --max-turns "$MAX_TURNS" -p "$PROMPT"
