# Mission Drift Checker

`scripts/apl_check_mission_drift.py` is an advisory check that detects when
`missions/current.yaml` routes agents into work the canonical state no longer
supports. It reads canonical task YAML, `campaign_profiles/_catalog.yaml`, and
`missions/current.yaml` and reports:

- **stale_task_reference** — a current/recommended mission action (or any
  support/maintainer action) points at a task that is `DONE`, `BLOCKED`,
  `REJECTED`, `SUPERSEDED`, or `PROPOSED`;
- **missing_task_reference** — the referenced canonical task does not exist;
- **transient_task_reference** — the referenced task is `REVIEW_READY`
  (advisory only; expected right after handoff, refreshed at closeout);
- **campaign_conflict** — a mission still lists a campaign the catalog marks
  non-actionable (`blocked`, `superseded`, `retired`, `archived`, `deprecated`);
- **dangling_campaign** — a mission references a campaign id absent from
  `campaign_profiles/_catalog.yaml`.

## Relationship to mission_freshness / validate-repo

`physics_lab/registry/mission_freshness.py` already flags non-actionable task
references during `validate-repo --strict` (`mission_stale_task_reference` as
`ERROR`, `mission_review_ready_task_reference` as `INFO`). This checker
**reuses** that module's status sets and task loader rather than duplicating
them, and adds the campaign-conflict dimension plus a standalone report. It is
deliberately **not** wired into strict validation as a second gate, to avoid
double-reporting and noisy false positives.

## When to run

- After a large merge wave, before recommending the next agent lane, to catch
  mission actions left pointing at just-completed or just-blocked tasks.
- During a Scientific Campaign Director or Architect pool review.
- Optionally in maintainer automation as an advisory signal.

```bash
# Advisory report (exit 0)
python3 scripts/apl_check_mission_drift.py

# Machine-readable
python3 scripts/apl_check_mission_drift.py --json

# Fail (exit 1) on drift, e.g. for an opt-in maintainer audit
python3 scripts/apl_check_mission_drift.py --strict
```

The checker never rewrites `missions/current.yaml`; resolving drift (refreshing
mission recommendations) stays a maintainer/curator action.
