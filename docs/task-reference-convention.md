# Task Reference Convention: id, not path

**Reference tasks by their immutable id (`TASK-XXXX`), not by file path.**

Write `TASK-0123` (optionally with a short description), not
`tasks/TASK-0123-some-slug.yaml`.

## Why

Task ids are immutable; file locations are not. Canonical task files move into
id-range buckets under `tasks/archive/<lo>-<hi>/` as they are archived
(see [task-archive-migration-plan.md](task-archive-migration-plan.md)). If prose
and docs reference tasks by **id**, archiving is a pure file move that never
breaks a reference. If they hardcode a **path**, every move would have to rewrite
every reference.

## How to find a task by id

- Deterministic path: a task's file is at
  `tasks/archive/<lo>-<hi>/TASK-<id>-<slug>.yaml` where `<lo> = id // 500 * 500`
  (active tasks are still flat under `tasks/`).
- Resolver CLI: `python3 scripts/apl_task_path.py TASK-0123`
- In code/tests: `physics_lab.registry.task_discovery.find_task_file(root, "TASK-0123")`.

## Rules

- Docs (`*.md`) and task proposals (`tasks/proposals/*.yaml`) must not contain
  literal `tasks/TASK-XXXX-*.yaml` paths; use the id. Enforced by
  `tests/test_task_reference_convention.py`.
- Code and tests must locate a task with `find_task_file`, never a hardcoded
  flat path.
- Generated output (a PR body, a report) may print the resolved path because it
  is computed at runtime from the file's actual location, not hardcoded.

## Allowed exceptions

- `docs/task-archive-migration-plan.md` and this file discuss paths as examples.
- Generated navigation under `docs/task-views/`.
</content>
