Delete unused sections before requesting review. Do not leave placeholder
examples such as `TASK-XXXX`, fake file paths, or generic branch strings in the
final PR body.

## PR Kind

Choose one:

- [ ] Canonical task PR
- [ ] Task proposal PR
- [ ] Microtask PR
- [ ] Task closeout PR

## Primary Reference

Canonical task PR:

- Task ID: `TASK-XXXX`
- Task File: `tasks/TASK-XXXX-short-slug.yaml`

Task proposal PR:

- Task ID: `TASK-PROPOSAL`
- Proposal File: `tasks/proposals/YYYYMMDD-contributor-short-slug.yaml`

Microtask PR:

- Queue ID: `queue-id`
- Queue File: `tasks/microtasks/queue-id.yaml`
- Microtask IDs: `ABC-001` or a small same-queue batch such as `ABC-001, ABC-002`

Task closeout PR:

- Task ID: `TASK-CLOSEOUT`
- Closed Task Files: `tasks/TASK-XXXX-short-slug.yaml`

## Branch Name

- Canonical task: `agent/<contributor-id>/<agent-id>/task-<task-number>-<short-slug>`
- Task proposal: `agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`
- Single microtask: `agent/<contributor-id>/<agent-id>/microtask-<microtask-id>-<short-slug>`
- Batch microtask: `agent/<contributor-id>/<agent-id>/microtask-batch-<queue-id>--<short-slug>`
- Closeout: `agent/<contributor-id>/<agent-id>/closeout-<short-slug>`

## PR Title

- Canonical task: `TASK-XXXX: <short title>`
- Task proposal: `TASK-PROPOSAL: <short title>`
- Microtask: `microtask(<queue-id>): <short description>`
- Closeout: `TASK-CLOSEOUT: <short title>`

## Summary

Describe the change in narrow, verification-first terms.

## Changed Files

- 

## Linked Repository Memory

- Hypothesis:
- Experiment:
- Task / Proposal / Queue:
- Result:
- Claim / Knowledge:

## Validation Commands

List only the commands you actually ran. Delete anything not applicable.

Common narrow microtask/docs path:

- [ ] `./scripts/validate_quick.sh`
- [ ] `python3 -m physics_lab.cli validate-repo .`
- [ ] `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`
- [ ] `python3 -m physics_lab.cli sync-active-board .`
- [ ] `./scripts/apl_review_bundle.sh`

Broader code/science path when applicable:

- [ ] `python3 -m ruff check .`
- [ ] `python3 -m pytest`
- [ ] `python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum`
- [ ] `python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped`
- [ ] `git diff --exit-code`

## Scientific Claim Impact

- 

## Result Artifact Impact

- [ ] I used `--output-dir` for routine validation runs, or no workflow runs were needed.
- [ ] I intentionally updated committed `results/` artifacts, or I left them untouched.
- [ ] If canonical artifacts changed, the change is scientifically meaningful and explained in this PR.

## Agent / Contributor Metadata

Record both the human owner and the execution tool here. Do not add
Co-Authored-By to commits. AI agents are tools, not git co-authors.

- Contributor ID:
- GitHub username:
- Agent tool:
- Model/version if known:
- Task ID / Proposal / Queue:
- Branch:
- Human reviewer:

## Maintainer Review Notes

- 
