# Maintainer Manual Mode

Use this file for targeted maintainer automation runs.

This mode is for direct requests such as:

- review PR `#63`
- check whether `TASK-0024` can be closed
- inspect all open PRs right now
- prepare a closeout PR
- execute a bounded maintainer action on a verified target

## Purpose

Run one well-scoped maintainer operation deeply and return an actionable
result.

## Inputs

The maintainer should provide one of:

- PR number
- task id
- explicit queue request such as "review all open PRs"
- explicit closeout request

## Manual Run Types

### 1. Selected PR Review

Use the maintainer review agent.

Select the review lane first:
- `fast review` for low-risk docs, planning, proposal-only, task-admin, and
  closeout PRs
- `deep review` for engines, workflows, schemas, claims, results, maintainer
  scripts, CI, and public scientific wording

Return:
- `MERGE_OK`
- `NEEDS_CHANGES`
- `BLOCKED`

Also return:
- blockers
- required fixes
- recommended next action

If useful, offer an English PR comment draft, but do not post it unless the
maintainer asks.

Prefer the fast lane when the PR obviously fits it. Do not default to deep
review just because a deterministic helper exists.

### 2. Proposal Acceptance Review

Use when the maintainer asks whether a proposal PR should be accepted.

Check:
- strategy alignment
- roadmap fit
- blocker relevance
- duplication with existing canonical tasks

Return:
- `accept now`
- `hold`
- `reject`

### 3. Merged Task Closeout

Use when the maintainer asks whether a merged task can be closed.

Required checks:
- PR was merged
- accepted outputs exist in `main`
- no unresolved blocker remains

If valid, prepare or apply closeout changes according to maintainer approval.
After opening a closeout PR, run the maintainer review agent. If the review
verdict is `MERGE_OK`, CI is green, and the maintainer already authorized
closeout/merge in the current request chain, the agent may merge a pure
closeout PR without asking again. If that authorization is absent or the PR is
not pure closeout bookkeeping, ask the maintainer an explicit yes/no question:
`Merge closeout PR #<number>?` Do not silently stop with only a status report.
Once closeout edits are applied locally, the agent should continue through PR
creation, review, and merge when authorized; if it cannot, it must name the
specific blocker and provide exact next commands instead of leaving an
uncommitted closeout diff in the repo.

Pure closeout bookkeeping may include directly dependent task unblocks from
`BLOCKED` to `READY` when the merged task wave satisfied explicit prerequisites.
The closeout PR title or body must say it is unblocking the dependent task; this
does not authorize claim promotion, result edits, or new experiment execution.
It may also include maintainer-approved stale/superseded task closures to
`REJECTED` or `SUPERSEDED`; this is optional queue hygiene, and the closeout agent should use
context instead of forcing stale-task cleanup through extra script-level
blockers.

### 4. Queue Triage

Use when the maintainer asks for a fresh prioritized queue.

Return:
- best next merge candidates
- blocked PRs
- stale/superseded PRs
- tasks needing closeout

### 5. Action Delegation

Use when the maintainer explicitly wants the automation to do something, not
just report.

Examples:

- post the prepared PR comment
- close the superseded PR
- open the closeout PR
- open the clean replacement PR

When this happens, delegate the actual action rules to
[./maintainer-action-mode.md](./maintainer-action-mode.md).

## Default Safety Rules

- Do not merge automatically.
- Do not close PRs automatically.
- Do not post comments automatically.
- Do not push branches automatically.
- Do not promote claims.
- Do not rewrite scientific verdicts.

If the maintainer explicitly asks for one of those actions, switch to action
mode instead of improvising within manual mode.

## Recommended Prompt Shape

```text
Run the maintainer automation agent in manual mode.
Target: <PR number | TASK-XXXX | open PR queue>.
Use repository docs and deterministic helpers.
Return only actionable maintainer guidance.
Do not merge, comment, or push unless I explicitly ask.
```

## Suggested Output Shapes

For PR review:

- verdict
- risk
- blockers
- required fixes
- recommended next action

For closeout:

- merged status
- accepted-output verification
- closeout recommendation
- whether a batch closeout is cleaner than per-task closeout

For queue triage:

- `merge now`
- `review next`
- `closeout now`
- `hold`
- `superseded`
