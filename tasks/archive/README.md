# Task Archive

Terminal canonical tasks (`DONE` / `SUPERSEDED` / `REJECTED`) live here, grouped
into **id-range buckets** so the active `tasks/` directory stays small. Active
tasks (`READY` / `BLOCKED` / `REVIEW_READY` / `IN_PROGRESS` / `PROPOSED`) remain
flat directly under `tasks/`.

## Layout

```
tasks/archive/0000-0499/TASK-0001-....yaml
tasks/archive/0500-0999/TASK-0500-....yaml
tasks/archive/1000-1499/TASK-1000-....yaml
```

The bucket is a pure function of the task's immutable id:
`bucket = (id // 500)`, i.e. `0000-0499`, `0500-0999`, `1000-1499`, …

## Finding a task

A task's location is computable from its id, so you never scan:

- Resolver CLI: `python3 scripts/apl_task_path.py TASK-0123`
- Deterministic path: `tasks/archive/<lo>-<hi>/TASK-0123-<slug>.yaml`
- `git grep TASK-0123 -- tasks/`
- In code/tests: `physics_lab.registry.task_discovery.find_task_file(root, "TASK-0123")`

Reference tasks by **id** (`TASK-0123`), never by path — see
[../../docs/task-reference-convention.md](../../docs/task-reference-convention.md).

## How tasks get here

The reusable, idempotent sweep moves newly-terminal tasks into their buckets:

```bash
python3 scripts/apl_archive_sweep.py --dry-run   # preview
python3 scripts/apl_archive_sweep.py             # perform (git mv only)
```

Run it periodically (monthly, or when too many terminal tasks accumulate flat),
not per task close. It is a pure `git mv`; it rewrites no references. See
[../../docs/task-archive-migration-plan.md](../../docs/task-archive-migration-plan.md).
</content>
