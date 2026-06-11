# Task Closeout Checklist

Use this checklist after a task PR has already been merged.

## Closeout Rule

A task may move to `DONE` only after maintainer review and merge.

Agents must not mark their own task `DONE`.

The maintainer, or a maintainer-run review agent acting on explicit maintainer
instruction, may perform closeout after merge.

## Required Evidence For `DONE`

- The PR was merged into `main`.
- The task was `REVIEW_READY` before closeout.
- The accepted outputs are present in `main`.
- CI passed for the merged work.
- No unresolved blocker prevents the task outcome from being considered
  complete.
- No unresolved repository-safety concern remains open from maintainer review.

## Closeout Actions

- Set the task file status to `DONE`.
- Respect the optional task-level `closeout` policy. Omitted or
  `closeout: auto` means the task may be eligible for safe auto-closeout when
  all automation guards pass; `closeout: review` forces the manual review path
  even if the task otherwise looks safe.
- Do not confuse the task YAML `closeout` policy with `TASK-CLOSEOUT`, which is
  the closeout PR kind marker used in PR titles and metadata.
- Keep closeout PRs YAML-only. Do not regenerate
  [the task views](../task-views/research.md) or
  `docs/task-views/*.md` in the closeout branch; the post-merge
  `Sync Active Board` GitHub Action regenerates them on `main` after the
  closeout merges. Run
  `python3 -m physics_lab.cli sync-active-board .` by hand only for an
  explicit audit (set `APL_ENFORCE_BOARD_STALENESS=1`) or when the action
  is temporarily disabled.
- If the merged PR or a maintainer-side sync step touched files that feed
  `CONTEXT.md`, rerun `python3 scripts/generate_context_bundle.py` and stage
  `CONTEXT.md` in a later maintainer branch if it changed.
- If the merged work changes experiments, results, campaign profiles, agent
  runs, mission priorities, or release gates, compare
  [../../README.md](../../README.md), [../status.md](../status.md),
  [../mission-control.md](../mission-control.md), and
  [../next-steps.md](../next-steps.md) against authoritative structured state.
- Treat public docs sync as check-and-follow-up by default. Routine closeout may
  update task status, [the task views](../task-views/research.md), and
  `CONTEXT.md`; it should update public narrative docs only when the current
  task explicitly includes public-doc sync. Otherwise update an existing
  docs-sync task or create a follow-up task.
- If the merged work changes what a contributor should do next, review
  [../next-steps.md](../next-steps.md) and update it when its short-handoff
  queue has gone stale.
- In larger cleanup batches, sanity-check open `READY`, `REVIEW_READY`, and
  `BLOCKED` tasks so the board does not keep advertising already-merged or no
  longer relevant work.
- During closeout, unblock dependent tasks from `BLOCKED` to `READY` only when
  the blocker is deterministic and fully satisfied inside the repository, for
  example `Remain BLOCKED until TASK-XXXX and TASK-YYYY are DONE`. Keep tasks
  blocked when the unblock condition depends on source access, external data,
  maintainer waiver, artifact existence, or scientific judgment.
- After task status reaches `DONE`, run
  `python3 scripts/apl_close_task_claim_issues.py` to find stale GitHub
  task-claim issues. Close only the issues whose canonical task is already
  `DONE` (`--apply` after reviewing the printed list). Keep `REVIEW_READY`
  claim issues open until the task closeout PR merges.
- When opening a closeout PR, prefer
  `python3 scripts/apl_closeout_pr_helper.py scaffold ...` plus
  `python3 scripts/apl_closeout_pr_helper.py preflight ...` so the PR body
  follows [../../.github/pull_request_template.md](../../.github/pull_request_template.md)
  instead of a short ad hoc `--body`.
- Add a short closeout note if the maintainer wants a persistent explanation.
- Add an entry to [../multi-agent-dry-run.md](../multi-agent-dry-run.md) when
  the merged PR belongs to a dry run or contributor pilot.

## When Not To Force `DONE`

Do not force `DONE` when:

- accepted outputs are missing;
- the merged work is only partial;
- CI or validation evidence is incomplete;
- a follow-up blocker still defines whether the task really succeeded.

If the work is only partially complete, create a follow-up task instead of
stretching the finished task definition.
