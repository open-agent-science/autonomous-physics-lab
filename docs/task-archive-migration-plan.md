# Task Archive Migration Plan (Preflight)

**Task:** `TASK-0559` (preflight; **no task files are moved in this PR**)
**Related:** `TASK-0557` (repository map / artifact lifecycle)
**Status:** design + test plan for a later migration PR

## Problem

`tasks/` holds **~560 canonical task files, ~507 of them terminal**
(`DONE`/`SUPERSEDED`/`REJECTED`). Active work is ~5 `READY` plus a handful of
`BLOCKED`/`REVIEW_READY`. The flat directory is noisy for humans and agents, but
**it is not a correctness bug today** — `validate-repo` is green and the files
are the canonical historical record.

The risk is in *how* we declutter. A naive `mv` of terminal tasks into
`tasks/archive/` would silently break invariants, because the loader reads
`tasks/` **flat**:

```python
# physics_lab/registry/repository.py
recursive_directories = {"knowledge", "results"}   # "tasks" is NOT here
iterator = base_path.glob("*.yaml")                # tasks/*.yaml only
```

## What we must preserve (invariants)

Archiving must keep these guarantees, or it is unsafe:

1. **Global task-id uniqueness.** `_validate_unique_task_ids` must still see
   archived ids so a new `TASK-0123` cannot reuse an archived one.
2. **Find-task-by-id.** Closeout, artifact back-links, snapshot, review, and
   claim/conveyor lookups locate a task with
   `(root/"tasks").glob(f"{task_id}-*.yaml")`. These must resolve archived ids.
3. **Cross-reference resolution.** `linked_objects.tasks` and "depends on
   TASK-XXXX" references that point at archived tasks must still resolve.
4. **Active surfaces stay active-only.** Mission, task-views, and the active
   board must continue to list only non-terminal tasks and must not surface
   archived history as current work.

## What we should deliberately NOT do

- **Do not full-strict-schema-validate the entire archive forever.** The `task`
  schema evolves. Re-validating hundreds of historical files against a stricter
  future schema would cause mass failures and force edits to history nobody is
  executing. Archive gets a **minimal** check (parse + required id fields +
  uniqueness + link resolution), not the full evolving schema.
- **Do not add a committed static task index for agents.** Keep dynamic scripts
  and the generated human task views (see the static-index postmortem).
- **Do not move task files in the preflight PR.**

## Inventory: code paths that assume flat `tasks/`

Two idioms dominate (~15 modules). All must route through a shared,
archive-aware discovery helper before any move.

**Enumerate-all** `glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")`:
- `physics_lab/registry/active_board.py`
- `physics_lab/registry/task_views.py`
- `physics_lab/registry/mission_control.py`
- `physics_lab/registry/mission_freshness.py`
- `physics_lab/registry/task_campaign_index.py`
- `physics_lab/registry/proposal_triage.py`

**Find-one-by-id** `glob(f"{task_id}-*.yaml")`:
- `physics_lab/registry/task_closeout.py`
- `physics_lab/registry/maintainer_review.py`
- `physics_lab/registry/task_claim_issues.py`
- `physics_lab/registry/task_validation_plan.py`
- `physics_lab/registry/science_output_conveyor.py`
- `physics_lab/registry/snapshot.py`
- `physics_lab/workflows/artifacts.py`
- `scripts/auto_run_next_task.py`

**Broad/other**:
- `physics_lab/registry/repository.py` (`PATTERNS["tasks"] = "*.yaml"`, flat loader; `TASK-TEMPLATE.yaml` skip)
- `physics_lab/registry/task_unblock.py`, `closeout_sweep.py` (`glob("TASK-*.yaml")`)
- `scripts/apl_closeout_task.py`, `scripts/apl_closeout_sweep.py`, `scripts/apl_mission.py` (consume the above)

Note: `tasks/` already contains `tasks/proposals/` (33) and `tasks/microtasks/`
(8). These use non-`TASK-NNNN` filenames, so a recursive
`rglob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")` naturally excludes them — confirmed
by the preflight test.

## Recommended discovery model (hybrid, not pure A/B)

- **Invariant-bearing reads → recursive** via one shared helper
  (`iter_canonical_task_files(root)` and `find_task_file(root, task_id)`), so
  id-uniqueness, by-id lookup, links, board/mission all see the archive.
- **Heavy schema validation → scoped to active** `tasks/*.yaml`; archive gets a
  minimal parse + id-field + uniqueness check only.

Concrete discovery rule (proved by the preflight test):

```python
def iter_canonical_task_files(tasks_root):
    # recursive; matches canonical ids anywhere under tasks/, including archive
    for p in sorted(tasks_root.rglob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
        if p.name == "TASK-TEMPLATE.yaml":
            continue
        yield p
```

This is a drop-in for every enumerate-all and find-one-by-id call site (the
by-id case filters by prefix), and it is layout-agnostic — flat today, archived
later, with zero further call-site churn.

## Recommended archive layout: id-range buckets

`tasks/archive/<lo>-<hi>/TASK-<id>-<slug>.yaml`, buckets of **500 ids**:

```
tasks/archive/0000-0499/
tasks/archive/0500-0999/
tasks/archive/1000-1499/
```

Rationale (vs alternatives):

| Layout | Stable path? | Even size | Needs close-date? | Verdict |
| --- | --- | --- | --- | --- |
| **id-range buckets (500)** | ✅ pure function of immutable id | ✅ ~even | ❌ no | **recommended** |
| `archive/YYYY/` (by year) | ❌ depends on close date | ❌ ~6000/yr at current rate | ✅ | too coarse |
| `archive/YYYY-MM/` | ❌ depends on close date | ⚠️ ~500/mo | ✅ | viable fallback |
| `archive/done/` flat | ✅ | ❌ grows unbounded | ❌ | just moves the noise |

Why id-range wins: a task's archive location is a **pure function of its
immutable id** (`bucket = id // 500`), so no module needs to know *when* a task
closed, no dependence on closeout-date metadata (which some old files lack), and
the target is trivially computable for both writing and lookup. At the observed
~500 tasks/month, a 500-id bucket is also roughly one month — time-readable
without coupling to dates. (Year-only is rejected: ~6000 tasks/year would refill
the same noise.)

## Cadence: deferred periodic sweep (never per-close)

- **Closeout stays simple:** `apl_closeout_task.py` marks `DONE` in place; it
  does **not** move files.
- **A separate `apl_archive_sweep.py`** moves terminal tasks
  (`DONE`/`SUPERSEDED`/`REJECTED`) into their id-range bucket, run:
  - on a **threshold** (e.g., > 150 terminal tasks sitting in flat `tasks/`), and/or
  - **monthly** by the maintainer.
- The sweep is one reviewable PR per run (git history preserves moves; use
  `git mv`).

This avoids churn on every task close and keeps each archival batch auditable.

## Migration sequence (future PRs, after this preflight)

1. **PR-1 (enabler):** add the shared `iter_canonical_task_files` /
   `find_task_file` helper; route all ~15 call sites through it; keep files flat.
   No behavior change (helper returns the same set on a flat tree). Ship the
   preflight test from this task as the regression guard.
2. **PR-2 (validation scoping):** make `validate-repo` apply full schema to
   active `tasks/*.yaml` and a minimal check to `tasks/archive/**`.
3. **PR-3 (the move):** add `apl_archive_sweep.py`; run the first batch
   (`git mv` terminal tasks into buckets); confirm id-uniqueness, by-id lookup,
   links, mission/views, snapshot all still pass.
4. **PR-4 (cadence):** document the threshold/monthly sweep in the closeout and
   maintainer-automation docs.

## Blocker list for the eventual move

- [ ] No shared discovery helper yet — ~15 flat-glob call sites must be migrated first (PR-1).
- [ ] `find_task_file(task_id)` by-id lookups (closeout, artifacts, snapshot, review, conveyor) will not find archived ids until they use the recursive helper.
- [ ] `validate-repo` schema scope must be split (active vs archive) to avoid schema-drift mass failures (PR-2).
- [ ] `repository.py` would need `tasks` made archive-aware without sweeping in `tasks/proposals/` and `tasks/microtasks/` (the `TASK-NNNN` pattern handles this; add a test).
- [ ] Snapshot / context-bundle path strings (`tasks/TASK-*.yaml`) are descriptive but should be checked for any existence assertions.
- [ ] Decide whether `git mv` batches should be split per bucket to keep PR diffs reviewable.

## Test plan / coverage

`tests/test_task_archive_discovery_preflight.py` (added by this task, no files
moved) proves on a temporary fixture that the recommended discovery rule:

- finds canonical tasks in **both** flat `tasks/*.yaml` and archived
  `tasks/archive/<bucket>/*.yaml`;
- **excludes** `tasks/proposals/`, `tasks/microtasks/`, and `TASK-TEMPLATE.yaml`;
- supports **find-one-by-id** across flat + archive;
- a uniqueness scan across flat + archive **catches a duplicate id** (the
  primary safety invariant).

This locks the discovery contract before any real migration PR.
