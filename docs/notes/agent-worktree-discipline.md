# Agent Worktree Discipline

**Status:** IMPLEMENTED UNDER TASK-0263
**Helpers:**
[`scripts/apl_new_worktree.sh`](../../scripts/apl_new_worktree.sh),
[`scripts/apl_branch_precondition.py`](../../scripts/apl_branch_precondition.py),
[`scripts/apl_setup_worktree.sh`](../../scripts/apl_setup_worktree.sh)

---

## 1. Why this exists

When two agent sessions (for example a Claude Code session and a Codex
session) share the same repository checkout, they share a single
working tree and a single `HEAD`. Any `git checkout`, `git add`, or
`git commit` from one session is silently visible to the other.

During TASK-0227 this caused a parallel Codex session to commit
TASK-0251 work onto the active Claude task branch and to move `HEAD`
afterwards. Recovery required `git reset --mixed`, a selective revert,
and a re-sync of generated views. The root cause is that one shared
working tree cannot safely serve two agents at once.

This note describes the discipline that prevents the failure mode.

## 2. When to use a separate worktree

Open a dedicated git worktree per task in any of these cases:

- a second agent session is (or might soon be) active in this
  repository;
- the same physical checkout is shared with another contributor for
  short bursts;
- the task is expected to take several hours and overlap with other
  agent work;
- the task creates many untracked files or large intermediate output
  that another session would otherwise see.

For a one-off short task on an otherwise idle checkout, a worktree is
not required. The precondition check (section 4) is still useful even
without a worktree.

## 3. Creating a worktree

Use the helper:

```bash
./scripts/apl_new_worktree.sh agent/<contributor-id>/<agent-id>/task-XXXX-<slug>
```

The script:

1. Refuses to overwrite an existing branch — name conflicts usually
   mean another agent already claimed the task.
2. Creates the worktree at `.worktrees/<branch-with-slashes-as-underscores>/`
   inside the project by default. `.worktrees/` is already gitignored so the
   new directory does not show up in `git status`. Keeping the worktree
   inside the project also avoids the permission prompts that Claude Code
   raises for paths outside the current working directory (see TASK-0271).
   Pass a second argument to override the path (it may point anywhere
   when the agent has a specific reason).
3. Bases the new branch on `origin/main` when the remote ref is
   present, otherwise on local `main`.
4. Runs [`scripts/apl_setup_worktree.sh`](../../scripts/apl_setup_worktree.sh)
   inside the new worktree to copy `.claude/settings.local.json` so the
   permission allowlist transfers.
5. Prints the next-step `cd`, status, and precondition commands.

After merge, clean up with:

```bash
git worktree remove <worktree-path>
```

## 4. The branch precondition check

`scripts/apl_branch_precondition.py` is a non-modifying check that
catches "wrong branch" and "surprise files" situations before they
become committed mistakes. Run it before any `git add` / `git commit`
/ `git push`:

```bash
python3 scripts/apl_branch_precondition.py \
    --expected-branch agent/<contributor-id>/<agent-id>/task-XXXX-<slug>
```

It exits with code `0` when both checks pass and code `1` when either
fails. Failure modes:

- **Branch mismatch.** `HEAD` is not on the expected branch. Usually
  the symptom of a parallel session having `git checkout`-ed somewhere
  else, or of the agent having dropped onto `main` between turns.
- **Unexpected working-tree changes.** Modified or untracked files
  that the agent did not produce. Harness state listed in
  `HARNESS_IGNORE_PATHS` (currently `.claude/scheduled_tasks.lock`) is
  filtered automatically. Anything else is reported.

Pass `--allow-untracked GLOB` (repeatable) or `--allow-modified GLOB`
to declare paths the agent is intentionally producing or editing
outside of the diff vs. main; the script removes those from the
surprise list before reporting.

Example for a task that generates a draft PR body in `/tmp`:

```bash
python3 scripts/apl_branch_precondition.py \
    --expected-branch agent/roman/claude/task-0263-foo \
    --allow-untracked "tasks/TASK-0263-*.yaml"
```

The check is opt-in and additive. It does not modify the working tree
and does not gate any existing tooling.

### Upstream tracking preflight (`--check-upstream`)

When several agents run one task per worktree, a task branch can end up
tracking `origin/main` (or have no upstream at all) instead of its own
remote branch. A bare `git push` then targets the wrong upstream. The
opt-in `--check-upstream` flag detects this for task-lifecycle branches
(canonical task, `propose-task`, `task-queue`, `closeout`, microtask) and
prints an exact, safe explicit-push command:

```bash
python3 scripts/apl_branch_precondition.py \
    --expected-branch agent/roman/claude/task-0624-foo \
    --check-upstream
```

If the branch tracks the wrong upstream or has none, the check fails and
prints `git push origin HEAD:<current-branch>`. It never force-pushes,
rewrites history, or mutates upstream tracking; it only reports and
suggests a safe command. Detached HEAD and non-task branches (such as
`main`) are skipped. Use `--remote` to target a remote other than
`origin`.

## 5. How it fits the canonical task protocol

Nothing in this note changes:

- branch naming;
- commit message format;
- task-state transitions;
- the maintainer review or closeout flow.

The new tooling is a thin safety layer above the existing protocol.
A follow-up task may consider whether to make the precondition check
mandatory before `apl_task_pr_helper.py create`; for now it is
opt-in so agents that do not need it can ignore it.

## 6. Files

- [`scripts/apl_new_worktree.sh`](../../scripts/apl_new_worktree.sh)
- [`scripts/apl_branch_precondition.py`](../../scripts/apl_branch_precondition.py)
- [`scripts/apl_setup_worktree.sh`](../../scripts/apl_setup_worktree.sh) (pre-existing,
  copies `.claude/settings.local.json` into a worktree)
- [`tests/test_apl_branch_precondition.py`](../../tests/test_apl_branch_precondition.py)
