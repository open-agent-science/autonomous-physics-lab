# Maintainer Routine Mode

Use this file for periodic maintainer automation sweeps.

This file is intended to be readable by a human, a coding agent, or a future
automation runner.

## Purpose

Reduce maintainer backlog by periodically scanning:

- open pull requests;
- open proposal PRs;
- merged tasks that still need closeout.

## Trigger Style

Use this mode when the run is periodic rather than targeted.

Good examples:

- morning repository sweep;
- after several merges;
- before a review session;
- before release-readiness planning.

## Routine Inputs

- current `main`
- open PR list
- canonical task YAML files
- `tasks/ACTIVE.md`
- `docs/strategy.md`
- `docs/roadmap.md`
- `docs/status.md`

## Routine Steps

1. Review the open PR queue.
   Classify each open PR as:
   - `merge candidate`
   - `needs follow-up`
   - `stale / superseded`
   - `unknown, inspect deeper`

2. For proposal PRs, check strategic fit.
   Favor proposals that:
   - align with the current roadmap;
   - unblock existing tasks;
   - improve release readiness;
   - reduce maintainer friction or review load.

3. For ordinary task PRs, run the maintainer review agent when needed.
   First choose a lane:
   - `fast review` for low-risk docs, planning, proposal-only, task-admin, and
     closeout PRs
   - `deep review` for engines, workflows, schemas, claims, results,
     maintainer scripts, CI, and public scientific wording
   Return:
   - `MERGE_OK`
   - `NEEDS_CHANGES`
   - `BLOCKED`

   Prefer `fast review` by default when the PR clearly stays in low-risk
   surfaces. Escalate to `deep review` only when the changed files or wording
   justify it.

4. Scan for merged tasks that still are not `DONE`.
   Verify before recommending closeout:
   - merged PR exists
   - GitHub PR metadata still binds that PR to the same canonical task id
   - accepted outputs exist in `main`
   - no unresolved blocker remains

5. Return a prioritized action list.
   Recommended sections:
   - `merge now`
   - `review next`
   - `closeout now`
   - `hold`
   - `superseded or stale`

6. If the calling automation explicitly enables action mode, hand off only the
   verified closeout subset first to
   [./maintainer-action-mode.md](./maintainer-action-mode.md).

## Default Safety Rules

- Do not merge PRs automatically.
- Do not comment on PRs automatically.
- Do not close PRs automatically.
- Do not push branches automatically.
- Do not mark tasks `DONE` without verification.
- Do not promote claims.
- Do not rewrite scientific verdicts.

The one recommended exception for an enabled action policy is:

- opening a closeout PR for verified merged tasks and then running the review
  agent on that PR; once closeout edits are applied, the action should continue
  through PR creation, review, and authorized merge, or report a concrete
  blocker with exact next commands instead of leaving local closeout changes
  uncommitted

## Optional Follow-Up Actions

Only if the maintainer explicitly asks, or if a higher-level automation
explicitly delegates to action mode:

- post an English PR comment draft;
- prepare a clean replacement PR for a stale or contaminated branch;
- prepare a closeout batch;
- accept a proposal into a canonical task.

For the first automation rollout, prefer only:

- prepare a closeout batch or per-task closeout PR
- run the review agent on the newly opened closeout PR

## Output Template

Use this structure:

### Merge now

- PR #

### Review next

- PR #

### Closeout now

- TASK-XXXX

### Hold

- PR #

### Superseded / stale

- PR #

## Escalation Rules

Stop and ask for maintainer direction when:

- a proposal has strategic value but changes roadmap direction;
- a PR changes protected scientific artifacts outside its task contract;
- a merged-task candidate cannot be rebound to the same `TASK-XXXX` through
  GitHub PR metadata;
- a closeout candidate looks merged but accepted outputs are ambiguous;
- multiple open PRs conflict over the same task or artifact surface.
