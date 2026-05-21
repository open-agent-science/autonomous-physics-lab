#!/usr/bin/env bash
# auto_run_next_task.sh
#
# Check the local Claude Code token budget and, when headroom remains,
# pick the next highest-priority READY task that does NOT already have an
# open pull request and invoke the claude CLI.
#
# Usage:
#   ./scripts/auto_run_next_task.sh [--dry-run] [--max-turns N]
#
# Environment variables (all optional):
#   CLAUDE_WEEKLY_TOKEN_LIMIT    token limit passed to check_claude_budget.py
#   CLAUDE_MONTHLY_TOKEN_LIMIT   deprecated alias; honored with a stderr warning
#   CLAUDE_BUDGET_THRESHOLD_PCT  block above this % (default 50)
#   CLAUDE_MAX_TURNS             max agent turns (default 80)
#   REPO_ROOT                    path to repo (default: dir of this script/..)
#   APL_OPEN_PR_LIST_CMD         override the gh-based open-PR lookup
#                                (test hook; expected to print a JSON array
#                                in the same shape as `gh pr list --json`)

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
if [[ -n "${CLAUDE_WEEKLY_TOKEN_LIMIT:-}" ]]; then
  BUDGET_ARGS+=(--limit "$CLAUDE_WEEKLY_TOKEN_LIMIT")
elif [[ -n "${CLAUDE_MONTHLY_TOKEN_LIMIT:-}" ]]; then
  echo "warning: CLAUDE_MONTHLY_TOKEN_LIMIT is deprecated; set CLAUDE_WEEKLY_TOKEN_LIMIT instead." >&2
  BUDGET_ARGS+=(--limit "$CLAUDE_MONTHLY_TOKEN_LIMIT")
fi
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

# ── 2. Pick next task (skipping tasks with an open PR) ──────────────────────
echo "" >&2
echo "=== Selecting next task ===" >&2

MISSION_JSON=$(cd "$REPO_ROOT" && python3 scripts/apl_mission.py --json 2>/dev/null)

# Build the ranked READY list once. The shell loop below filters out any
# candidate whose TASK-XXXX id already has an open PR title match.
RANKED_READY=$(MISSION_JSON="$MISSION_JSON" python3 - <<'PYEOF'
import json
import os
import sys

try:
    data = json.loads(os.environ["MISSION_JSON"])
except (KeyError, json.JSONDecodeError) as exc:
    print(f"ERROR: could not parse apl_mission.py --json output: {exc}", file=sys.stderr)
    sys.exit(1)
candidates = data.get("live_task_candidates", [])

priority_weight = {"high": 0, "medium": 1, "low": 2}
difficulty_weight = {"low": 0, "medium": 1, "high": 2}

ready = [c for c in candidates if c.get("status", "").upper() == "READY"]
ready.sort(key=lambda c: (
    priority_weight.get(c.get("priority", "low"), 9),
    difficulty_weight.get(c.get("difficulty", "high"), 9),
))

print(json.dumps([
    {
        "task_id": c.get("task_id"),
        "title": c.get("title", ""),
        "priority": c.get("priority"),
        "difficulty": c.get("difficulty"),
    }
    for c in ready
]))
PYEOF
)

CANDIDATE_COUNT=$(echo "$RANKED_READY" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

if [[ "$CANDIDATE_COUNT" == "0" ]]; then
  echo "No READY tasks found. Nothing to do." >&2
  exit 0
fi

# Returns "1" when the given TASK id has at least one OPEN pull request whose
# title contains the task id. An override hook (APL_OPEN_PR_LIST_CMD) is
# honored so tests can mock the gh CLI without depending on network state.
has_open_pr() {
  local task_id="$1"
  local list_json=""
  if [[ -n "${APL_OPEN_PR_LIST_CMD:-}" ]]; then
    list_json=$(eval "$APL_OPEN_PR_LIST_CMD" 2>/dev/null || true)
  else
    list_json=$(gh pr list --state open --search "${task_id} in:title" --json number,title 2>/dev/null || true)
  fi
  if [[ -z "$list_json" ]]; then
    echo 0
    return
  fi
  TASK_ID="$task_id" LIST_JSON="$list_json" python3 - <<'PYEOF'
import json
import os
import sys

try:
    items = json.loads(os.environ.get("LIST_JSON", "") or "[]")
except json.JSONDecodeError:
    print(0)
    sys.exit(0)
task_id = os.environ.get("TASK_ID", "")
match = any(task_id and task_id in str(item.get("title", "")) for item in items)
print(1 if match else 0)
PYEOF
}

SELECTED_INDEX=-1
SELECTED_TASK_ID=""
SELECTED_TITLE=""
for ((i = 0; i < CANDIDATE_COUNT; i++)); do
  CANDIDATE_JSON=$(echo "$RANKED_READY" | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin)[$i]))")
  CAND_TASK_ID=$(echo "$CANDIDATE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['task_id'])")
  CAND_TITLE=$(echo "$CANDIDATE_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['title'])")

  OPEN_HIT=$(has_open_pr "$CAND_TASK_ID")
  if [[ "$OPEN_HIT" == "1" ]]; then
    echo "Skipping $CAND_TASK_ID — an open PR already targets this task." >&2
    continue
  fi

  SELECTED_INDEX=$i
  SELECTED_TASK_ID="$CAND_TASK_ID"
  SELECTED_TITLE="$CAND_TITLE"
  break
done

if [[ "$SELECTED_INDEX" == "-1" ]]; then
  echo "No READY task without an open PR is available. Nothing to do." >&2
  exit 0
fi

echo "Selected: $SELECTED_TASK_ID — $SELECTED_TITLE" >&2

# ── 3. Build task prompt ────────────────────────────────────────────────────
TASK_FILE=$(find "$REPO_ROOT/tasks" -name "${SELECTED_TASK_ID}-*.yaml" | head -1)
if [[ -z "$TASK_FILE" ]]; then
  echo "ERROR: task file for $SELECTED_TASK_ID not found in tasks/" >&2
  exit 1
fi

PROMPT=$(cat <<PROMPT
Execute task $SELECTED_TASK_ID from the Autonomous Physics Lab repository.
Task file: $TASK_FILE
Title: $SELECTED_TITLE

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
