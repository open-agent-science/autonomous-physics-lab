# Science-Output Conveyor Sample

**Task:** TASK-0382
**Status:** sample report; advisory only; no tasks created; no claims promoted

## Sample Command

```bash
python3 scripts/science_output_conveyor.py --recent-limit 5
```

## Expected Shape

The report should include:

- a `task_queue_needed` boolean;
- READY science task counts and active surfaces;
- recent task transitions;
- recent canonical result artifacts;
- sandbox result candidates;
- blocker reviews;
- campaign decisions;
- BLOCKED lane summaries;
- overclaim-risk notes;
- guardrails stating that the report is advisory only.

## Example Excerpt

```text
# Science-Output Conveyor Health Report

- Advisory only: `true`
- Task queue needed: `false`
- READY science tasks: `5`

## Possible Result Candidates
- RESULT-0015 / TASK-0168: Nuclear Mass Baseline Residual Benchmark (PARTIALLY_VALID)

## Overclaim Risk
- Claim promotion remains blocked unless a separate maintainer review explicitly allows it.
```

## Scope Notes

This sample does not freeze a canonical report snapshot because the task board
continues to change after every merge. Reviewers should run the command above
against the PR branch and inspect the live output.

The helper reads repository state and prints Markdown or JSON. It does not
create task files, merge PRs, promote claims, rewrite generated task views, or
change result artifacts.
