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
- Move the task from `REVIEW_READY` to `DONE RECENTLY` in
  [../../tasks/ACTIVE.md](../../tasks/ACTIVE.md).
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
