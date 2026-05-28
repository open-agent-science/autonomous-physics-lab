# Autonomous Task Runner

The canonical cross-platform entrypoint is:

```bash
python3 scripts/auto_run_next_task.py --dry-run
python3 scripts/auto_run_next_task.py --max-turns 200
```

The runner:

- checks the local Claude Code budget using `scripts/check_claude_budget.py`;
- reads `scripts/apl_mission.py --output json`;
- selects the highest-ranked `READY` task;
- skips tasks that already have an open PR;
- builds a task-execution prompt for Claude Code;
- detects `Reached max turns` exits and prints a clear work-in-progress summary.

There is intentionally no shell-wrapper entrypoint. Keeping a single Python
path prevents agents from splitting between platform-specific launch paths and
keeps Windows, macOS, and Linux validation aligned.

## Test Hooks

Use `APL_OPEN_PR_LIST_JSON` in tests and local dry-runs when you need to mock
open PRs without invoking GitHub:

```bash
APL_OPEN_PR_LIST_JSON='[{"number": 1, "title": "TASK-0001: example"}]' \
  python3 scripts/auto_run_next_task.py --dry-run
```

`APL_OPEN_PR_LIST_CMD` remains available as an escape hatch for local operator
experiments, but `APL_OPEN_PR_LIST_JSON` is preferred because it avoids shell
quoting differences between Windows, macOS, and Linux.
