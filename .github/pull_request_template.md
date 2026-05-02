# Task ID

- `TASK-XXXX`

## Task File

- `tasks/TASK-XXXX-short-slug.yaml`

## Branch Name

- `agent/<agent-id>/task-<task-number>-<short-slug>`

## Summary

Describe the change in narrow, verification-first terms.

## Changed Files

- 

## Linked Repository Memory

- Hypothesis:
- Experiment:
- Task:
- Result:
- Claim / Knowledge:

## Validation Commands

- [ ] `python3 -m ruff check .`
- [ ] `python3 -m pytest`
- [ ] `python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum`
- [ ] `python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped`
- [ ] `python3 -m physics_lab.cli validate-repo .`
- [ ] `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`
- [ ] `git diff --exit-code`

## Scientific Claim Impact

- 

## Result Artifact Impact

- [ ] I used `--output-dir` for routine validation runs.
- [ ] I intentionally updated committed `results/` artifacts, or I left them untouched.
- [ ] If canonical artifacts changed, the change is scientifically meaningful and explained in this PR.

## Maintainer Review Notes

- 
