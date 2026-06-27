Delete unused sections before requesting review. Do not leave placeholder
examples such as `TASK-XXXX`, fake file paths, or generic branch strings in the
final PR body.

Maintainer review checks for the required section headings below. If creating
the PR from an agent or CLI, prepare a filled body file from this template and
use `gh pr create --body-file <path>` rather than a short ad hoc `--body`.

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

## PR Lifecycle

- [ ] Branch pushed
- [ ] Draft PR opened by agent or manual PR creation commands provided
- [ ] Post-PR review command run or manual review command provided if no PR number is available
- [ ] Marked ready for review after CI passes and review agent returns `MERGE_OK`, or manual ready command provided

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
- [ ] `./scripts/apl_review_bundle.sh`

Note: agents no longer commit regenerated `docs/task-views/*.md` from task
PRs. The `Sync Active Board` post-merge GitHub Action regenerates them on
`main` after every merge that touches `tasks/**` or `missions/current.yaml`.

Broader code/science path when applicable:

- [ ] `python3 -m ruff check .`
- [ ] `python3 -m pytest`
- [ ] `python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum`
- [ ] `python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped`
- [ ] `git diff --exit-code`

## Scientific Claim Impact

- Claim files changed: yes/no
- Novelty Classification: `frontier_novel` / `reusable_dataset` / `valuable_negative` / `calibration_known_physics` / `n/a`
- Claim status impact:

`Novelty Classification` is required when creating or editing `claims/*.md`.
Use `n/a` only when no claim file changes. A
`calibration_known_physics` result must stay a validated `RESULT-*` or dataset
artifact rather than being promoted as a scientific claim.

## Result Artifact Impact

- [ ] I used `--output-dir` for routine validation runs, or no workflow runs were needed.
- [ ] I intentionally updated committed `results/` artifacts, or I left them untouched.
- [ ] If canonical artifacts changed, the change is scientifically meaningful and explained in this PR.

## Output Routing

Use this section for research, validation, benchmark, source-curation,
prediction, result, claim, or knowledge-facing PRs. Delete only when the PR is
pure docs/task-admin and no scientific output class is involved.

- Task verdict:
- Canonical destination:
- Review tier: `none`, `AGENT_PUBLISHED`, `AGENT_VALIDATED`, `MAINTAINER_REVIEWED`, `EXTERNAL_REPLICATED`, or `LEGACY_UNTIERED`
- Gate A status:
- Gate B status:
- Claim impact:
- Knowledge impact:
- Limitations / blockers:

If this PR contains `AGENT_PUBLISHED` or `AGENT_VALIDATED` artifacts, keep the
qualifier explicit in the summary and changed-file notes. Claim status
transitions are maintainer-only in Phase 1, and missing publication tooling
must be reported as blocked rather than replaced by prose claims.

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
