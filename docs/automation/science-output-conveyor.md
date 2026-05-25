# Science-Output Conveyor

## Purpose

The science-output conveyor report is a maintainer-facing health pulse for
recent APL work. It asks whether the latest merged work produced a result,
blocker review, campaign decision, result candidate, or need for a bounded
task-queue PR.

It is advisory only. It must not create task files, merge PRs, promote claims,
rewrite generated task navigation, or change result artifacts by itself.

## Command

Markdown output for maintainer review:

```bash
python3 scripts/science_output_conveyor.py
```

JSON output for automation:

```bash
python3 scripts/science_output_conveyor.py --json
```

Limit each section for shorter reports:

```bash
python3 scripts/science_output_conveyor.py --recent-limit 5
```

## Report Sections

The report summarizes:

- recent task transitions from canonical `tasks/TASK-*.yaml`;
- canonical result artifacts under `results/*/*/result.yaml`;
- sandbox result candidates under `agent_runs/AGENT-RUN-*/agent_run.yaml`;
- blocker reviews and campaign-decision notes under `docs/reviews/`;
- READY science task pool health and `task_queue_needed`;
- high-priority BLOCKED lanes;
- explicit overclaim-risk notes.

## Interpretation

`task_queue_needed: true` is a warning to the maintainer that a bounded
TASK-QUEUE PR may be useful. It is not a CI failure and does not authorize an
agent to create canonical tasks without maintainer direction.

Result candidates listed by the report still need maintainer review and any
campaign-specific result-promotion gates. Sandbox runs are never public claims
by themselves.
