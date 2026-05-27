# READY Science Task Pool Health Policy

Status: maintainer workflow policy. This policy is advisory and must not fail
normal PR validation by itself.

## Purpose

APL should keep enough independent READY scientific work available for parallel
agents without letting agents drift into blocked lanes or invent unreviewed
task ids.

The target pool is:

- minimum: 5 independent READY science tasks;
- preferred during public/open-agent onboarding: 6-10 READY science tasks;
- campaign/surface coverage: at least 3 active scientific surfaces when
  possible.

## What Counts

A READY science task counts when:

- its canonical `tasks/TASK-*.yaml` status is `READY`;
- its task type is research/science oriented, such as scientific validation,
  scientific dataset work, benchmark protocol, autonomous research pilot,
  replay, audit, or result packaging;
- it has a bounded accepted-output contract;
- it does not require hidden external access, live data fetches, or claim
  promotion unless the task explicitly scopes that work.

Independence can come from any of:

- a distinct campaign or related domain;
- a distinct artifact surface;
- a distinct dataset/source package;
- a distinct hypothesis family;
- a source/review task in a source-gated campaign while another campaign runs
  validation or hypothesis work.

## Warning-Only Health Check

Mission control exposes a warning-only health summary:

```bash
python3 scripts/apl_mission.py --json
```

The JSON includes `ready_science_pool_health` with:

- `ready_science_count`;
- `ready_science_task_ids`;
- `active_surfaces`;
- minimum/preferred/target thresholds;
- `task_queue_needed`;
- advisory notes.

`task_queue_needed: true` means a maintainer should consider a bounded
TASK-QUEUE PR. It does not mean CI should fail, tasks should be auto-created,
or agents should bypass maintainer review.

## Maintainer Response

When the pool is below target, prefer adding a small task queue with:

- 1-2 hard scientific validation tasks;
- 1-2 medium source/readiness tasks;
- 1 packaging or blocker-review task;
- at most one infrastructure task unless it directly unblocks a campaign.

Do not add broad formula-search tasks only to inflate the READY count. Source
gates, negative results, and blocker reviews are valid scientific work when
they move a campaign toward reviewable outputs.

## Guardrails

- Do not offer `REVIEW_READY`, `BLOCKED`, `DONE`, `SUPERSEDED`, or `REJECTED`
  tasks as executor choices.
- Do not auto-create canonical task files from the health warning.
- Do not treat READY pool size as scientific success.
- Do not let a low READY pool justify claim promotion or discovery wording.
