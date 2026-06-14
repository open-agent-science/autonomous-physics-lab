# Agent Task Claiming

This document defines the lightweight GitHub-native claiming ledger for APL
canonical tasks. It prevents duplicate task PRs, overlapping write surfaces, and
accidental reuse of the same sandbox or result artifact path without adding a
custom server, database, dashboard, or scheduler.

## Purpose

A task claim answers four questions before substantial work starts:

1. Which `TASK-XXXX` is being worked?
2. Who is responsible for the implementation branch and review loop?
3. Which repository paths or artifact surfaces will be edited?
4. Is there already an open PR or active claim for the same task or surface?

The claim is coordination metadata only. It does not reserve scientific truth,
promote evidence, approve results, or replace maintainer review.

## When A Claim Is Required

Create or declare a task claim before substantial work on any canonical
`TASK-XXXX` that will open a PR.

A claim is especially required when the task may touch one of these surfaces:

- `agent_runs/AGENT-RUN-*`
- `results/`
- `prediction_registry/`
- `claims/`
- `knowledge/`
- `docs/reviews/`
- `docs/task-views/`
- `missions/current.yaml`
- shared scripts, schemas, or validators

For local exploration with no repository edits, a claim is not required. Before
committing or opening a PR, the agent must still check for open PRs and surface
conflicts.

## Claim Channels

Use the first available channel:

1. **Canonical PR body** — preferred when the agent opens a PR quickly.
2. **GitHub issue from `.github/ISSUE_TEMPLATE/task-claim.yml`** — preferred for
   longer-running or manually assigned work.
3. **Maintainer comment in the existing task or PR discussion** — acceptable for
   agents without issue-creation permission.
4. **Chat handoff text** — fallback only; the next agent must mirror the claim in
   GitHub before continuing.

## Required Claim Fields

Every claim must include:

- Task ID, for example `TASK-0483`.
- Task file path, for example `tasks/TASK-0483-...yaml`.
- Contributor ID and agent/tool ID. Contributor ID SHOULD be the lowercased
  GitHub username when available; otherwise use a stable maintainer-approved
  short id.
- GitHub username when available, kept as separate PR metadata even when it
  matches Contributor ID.
- Planned branch name.
- Claim channel and URL once available.
- Expected write surfaces.
- Artifact IDs or reserved paths, if any.
- Intended artifact tier: `sandbox-only`, `AGENT_PUBLISHED`,
  `AGENT_VALIDATED`, `maintainer-reviewed`, or `not-applicable`.
- Existing-PR search result.
- Claim expiry timestamp or expiry rule.

## Required Pre-Claim Search

Before creating a branch or claim, search GitHub for:

```text
is:pr is:open TASK-XXXX
is:issue is:open TASK-XXXX claim
AGENT-RUN-XXXX
<review-doc-or-result-path>
```

For task-id PR occupancy, agents can use the advisory helper before claiming
or opening a branch:

```bash
python3 scripts/apl_task_occupancy.py --task TASK-XXXX
```

Pass `--task` more than once for a batch of candidate tasks. The helper reads
live GitHub PR metadata when available, scans PR title, body, and branch name
for task ids, and classifies each requested task as `occupied`,
`merged_pending_closeout`, or `apparently_free`. If GitHub CLI, network, or
known local proxy blockers prevent the live lookup, the helper exits
successfully with an advisory fallback instead of becoming a hard offline
blocker.

If an open PR already implements the same task, do not open a duplicate
implementation PR. Instead:

- review the existing PR;
- add validation results as a comment;
- ask the maintainer whether a competing implementation is wanted; or
- propose a follow-up task if the work is materially different.

## Write Surface Declaration

A write surface is any path or artifact namespace that concurrent work could
conflict on.

Examples:

```text
agent_runs/AGENT-RUN-0050/
docs/reviews/exoplanet-null-baseline-family-audit.md
scripts/run_exoplanet_null_baseline_family_audit.py
tests/test_exoplanet_null_baseline_family_audit.py
```

Agents must declare concrete paths when known. If a path is not yet known, use a
specific namespace plus the reservation rule, for example:

```text
agent_runs/AGENT-RUN-next-unused-for-TASK-0483/
```

Before committing generated artifacts, replace placeholder reservations with the
exact committed paths.

## Active Claim Rule

One canonical task should have at most one active implementation claim at a
time.

A second claim is allowed only when one of these is true:

- the maintainer explicitly asks for an alternative implementation;
- the second claim is a review-only or validation-only lane;
- the second claim is a follow-up proposal and does not edit the same outputs;
- the tasks are independent and their write surfaces are disjoint.

If two agents claim the same task, the maintainer should keep one canonical PR
and close or retarget the duplicate.

## Claim Expiry

Default expiry:

- a claim with no branch or PR activity expires after 24 hours;
- a claim with a branch but no commits or comments expires after 48 hours;
- a draft PR claim remains active while the PR has activity within the last 7
  days;
- a maintainer may release, transfer, or extend any claim.

Expired claims should not be treated as abandoned scientific work. They only
release coordination priority so another agent may continue safely.

## Duplicate PR Resolution

When duplicate PRs already exist for the same `TASK-XXXX`:

1. Prefer the PR opened or explicitly designated by the maintainer.
2. If neither is maintainer-designated, prefer the earlier PR with passing CI and
   smaller scope.
3. Prefer the PR that preserves canonical artifact IDs and avoids overwriting
   existing `agent_runs/`, `results/`, `claims/`, or `knowledge/` paths.
4. Close the duplicate PR with a comment linking the kept PR.
5. Salvage useful changes only through a follow-up PR or maintainer-requested
   cherry-pick.

Recommended duplicate-close comment:

```text
Closing as duplicate of #<kept-pr>. This task already has a canonical review
target and both PRs touch the same TASK/output surface. Please move any useful
additional ideas into a review comment or follow-up task.
```

## Manual Fallback For Agents Without GitHub Write Permission

If an agent cannot create issues, labels, or PRs, it must provide a maintainer
handoff block:

```text
Task claim request
- Task ID:
- Task file:
- Contributor / agent:
- Proposed branch:
- Expected write surfaces:
- Existing PR search performed:
- Artifact tier:
- Expiry:
```

The maintainer can paste this into an issue, PR, or task discussion before work
continues.

## Claim Labels

When GitHub labels are available, use lightweight labels:

- `task-claim`
- `claimed`
- `duplicate`
- `needs-maintainer-routing`
- `review-only`

Labels are advisory. The task YAML status and PR state remain the authoritative
lifecycle signals.

## Relationship To Task Status

A claim does not replace task status.

- `READY` means the task is executable.
- `IN_PROGRESS` means one contributor or agent is actively implementing it.
- `REVIEW_READY` means implementation is complete and maintainer review is
  required.

The claim ledger explains who is working and where, while the task YAML explains
the lifecycle status.

## Examples

### Implementation Claim

```text
Task ID: TASK-0483
Task file: TASK-0483
Contributor / agent: gladunrv / codex
Branch: agent/gladunrv/codex/task-0483-exoplanet-null-baselines
Write surfaces:
- scripts/run_exoplanet_null_baseline_family_audit.py
- tests/test_exoplanet_null_baseline_family_audit.py
- agent_runs/AGENT-RUN-0050/
- docs/reviews/exoplanet-null-baseline-family-audit.md
Artifact tier: sandbox-only
Existing PR search: no open canonical implementation PR found at claim time
Expiry: active while PR has activity within 7 days
```

### Duplicate Detection

If another PR already touches the same task and `AGENT-RUN-0050`, the new agent
must not create a second implementation PR. It should review the existing PR or
ask the maintainer whether an alternative implementation is explicitly desired.
