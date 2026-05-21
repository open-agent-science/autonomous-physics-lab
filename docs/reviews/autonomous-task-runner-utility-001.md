# Autonomous Task Runner Utility 001

**Task:** TASK-0318  
**Scripts:** `scripts/check_claude_budget.py`, `scripts/auto_run_next_task.sh`  
**Tests:** `tests/test_check_claude_budget.py`

## Purpose

Enable a local autonomous loop that reads Claude Code session logs, checks
monthly token budget, and invokes the next READY scientific task when sufficient
headroom remains.

## Design

### Budget gate (`check_claude_budget.py`)

Reads `~/.claude/projects/` JSONL session files, sums `input_tokens`,
`output_tokens`, and `cache_creation_input_tokens` for the current calendar
month, and compares the total against a configurable limit. Cache-read tokens
are reported separately because they are useful telemetry but should not block
repeated local-agent runs by default.

```
CLAUDE_MONTHLY_TOKEN_LIMIT   default 6 000 000   (~Claude Max 5x monthly estimate)
CLAUDE_BUDGET_THRESHOLD_PCT  default 50          block when usage ≥ threshold
```

The script exits 0 when usage is below the threshold and 1 when at or above it.
`--dry-run` always exits 0 (safe for inspection).

Output example:

```json
{
  "input_tokens": 18754,
  "output_tokens": 1085079,
  "cache_creation_tokens": 0,
  "cache_read_tokens": 0,
  "total_tokens": 1103833,
  "used_tokens": 1103833,
  "limit_tokens": 6000000,
  "sessions_scanned": 2270,
  "files_read": 10,
  "period_start": "2026-05-01T00:00:00+00:00",
  "monthly_limit": 6000000,
  "threshold_pct": 50,
  "used_pct": 18.4,
  "remaining_pct": 81.6,
  "under_threshold": true
}
```

### Autonomous runner (`auto_run_next_task.sh`)

1. Calls `check_claude_budget.py`; exits cleanly if budget gate blocks.
2. Reads `scripts/apl_mission.py --json` to find READY tasks sorted by
   priority (high → medium → low) then difficulty (low → medium → high).
3. Builds a task prompt instructing Claude Code to follow all APL protocols.
4. Invokes `claude --max-turns N -p "<prompt>"`.

`--dry-run` prints what it would do without calling the claude CLI.

## Usage

```bash
# Check budget only (dry-run safe)
python3 scripts/check_claude_budget.py

# Set a custom limit (e.g. Claude Pro ~ 1.3 M output tokens/month)
CLAUDE_MONTHLY_TOKEN_LIMIT=1300000 python3 scripts/check_claude_budget.py

# Autonomous runner, dry-run to preview
./scripts/auto_run_next_task.sh --dry-run

# Autonomous runner, real execution with 60-turn cap
./scripts/auto_run_next_task.sh --max-turns 60

# Recurring: run every 30 minutes if budget allows
watch -n 1800 ./scripts/auto_run_next_task.sh --dry-run
```

## Calibrating the monthly limit

| Plan | Approx monthly tokens (output) | Suggested `CLAUDE_MONTHLY_TOKEN_LIMIT` |
|------|-------------------------------|----------------------------------------|
| Claude Pro (~$20) | 1 300 000 | `1300000` |
| Claude Max 5x (~$100) | 6 500 000 | `6500000` |
| Claude Max 20x (~$200) | 13 000 000 | `13000000` |

These are rough estimates based on Sonnet output pricing ($15/M tokens).
Adjust to match your observed billing cycle.

## Limitations

- Token counts are read from local JSONL logs written by the Claude Code CLI.
  If logs are cleared or relocated, the count resets.
- The monthly limit must be set manually; no live Anthropic API call is made.
- The runner picks the next READY task but does not validate that a previous
  agent is not already working on the same task. Use separate worktrees for
  parallel agents.
- `auto_run_next_task.sh` requires the `claude` CLI to be on `PATH`.
- `auto_run_next_task.sh` has a dry-run smoke test that verifies READY-task
  selection without invoking Claude.

## Tests

21 unit tests covering: missing dir, month filtering, multi-message summation,
cache token accounting, malformed line skipping, threshold boundary conditions,
CLI exit codes, env-var configuration, JSON output validity, and
`auto_run_next_task.sh --dry-run` READY-task selection.
