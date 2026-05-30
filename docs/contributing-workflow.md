# Contributing Workflow

## Goal

This repository accepts contributions only when they are reviewable,
reproducible, and linked to public scientific memory.

Every meaningful change should connect back to one or more of:

- `HYP-*`
- `EXP-*`
- `TASK-*`
- `RESULT-*`
- `CLAIM-*`
- `KNOW-*`

## Recommended Flow

1. Read [AGENTS.md](../AGENTS.md).
2. Read [docs/agent-task-protocol.md](./agent-task-protocol.md).
3. Read [docs/status.md](./status.md).
4. Read [docs/strategy.md](./strategy.md).
5. Read the [task views](task-views/research.md).
6. Read [docs/agent-operating-model.md](./agent-operating-model.md).
7. Pick one existing `READY` task, benchmark, or documentation gap.
8. If no existing `READY` task fits, create a task proposal using
   [task-proposal-protocol.md](./task-proposal-protocol.md).
9. Create and switch to the canonical task branch or proposal branch before changing repository files.
10. Make the smallest reproducible change that advances the repository state.
11. Run validation before asking for review.
12. Use the GitHub issue and PR templates so the contribution stays linked to repository memory.
13. Use the branch, commit, PR title, and task-state protocol from
    [docs/agent-task-protocol.md](./agent-task-protocol.md).
14. When an AI tool is used, record both the human contributor and the agent
    tool in the PR metadata block.

Do not start task implementation on `main`.

For routine canonical task work, treat the `TASK-*.yaml` file as the source of
truth for task status. Do not hand-edit `docs/task-views/*.md` just to move a task
between `READY`, `IN_PROGRESS`, `REVIEW_READY`, or `DONE`. The
`Sync Active Board` GitHub Action regenerates the board snapshot on `main`
after every push that touches `tasks/**` or `missions/current.yaml`, so
contributors do not commit the regenerated
`docs/task-views/*.md` from a PR branch.

## Typical Contribution Types

### Benchmark Improvement

Use this when improving:

- pendulum verification;
- damped-oscillator verification;
- result semantics;
- workflow implementation.

Expected links:

- one `EXP-*`
- one `TASK-*`
- one or more `RESULT-*`

Expected updates:

- code under `physics_lab/`
- tests under `tests/`
- result artifacts under `results/<experiment>/<run>/` only when the canonical benchmark is intentionally regenerated
- docs if semantics or contributor expectations changed

### Claim / Knowledge Update

Use this when turning validated output into better repository memory.

Expected links:

- one `CLAIM-*` or `KNOW-*`
- at least one `RESULT-*`

Rules:

- do not promote a claim without evidence;
- keep scope language explicit;
- prefer `PARTIALLY_SUPPORTED` when evidence is range-limited;
- use `SUPPORTED` only when the referenced evidence really matches the claim scope.
- follow [claim-promotion-policy.md](./claim-promotion-policy.md) before changing a claim status.

### New Task / Hypothesis

Use this when proposing new work without fully implementing it yet.

Expected links:

- one `HYP-*` or task proposal
- optional `EXP-*` scaffold

Rules:

- keep the proposal narrow;
- define assumptions clearly;
- avoid speculative universal claims.
- use `tasks/proposals/` unless the maintainer explicitly assigned a canonical
  `TASK-XXXX` id.

## Validation Checklist

Run before asking for review on a canonical task PR:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

For task proposal PRs, use the lighter validation path:

```bash
./scripts/validate_quick.sh
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
./scripts/apl_review_bundle.sh
```

Optional but recommended for larger work:

```bash
RUN_EXPERIMENT=1 ./scripts/apl_snapshot.sh
```

## GitHub Templates

Use the built-in repository templates when contributing through GitHub:

- `Benchmark Improvement` for work on an existing benchmark or verifier;
- `Hypothesis Proposal` for a new narrow claim, task, or experiment scaffold;
- the PR template for linked artifacts, validation, claim-scope review, and
  task protocol metadata.

## Artifact Policy

- Use `--output-dir` for routine validation runs.
- Do not update committed canonical artifacts accidentally.
- Only regenerate committed `results/` artifacts when the benchmark itself has meaningfully changed.
- If canonical artifacts change, include a short explanation in the PR.

## AI Agent Attribution

If an AI agent assisted with any part of the contribution:

- Do **not** add `Co-Authored-By` for AI tools in commit messages.
- Fill in the **Agent / Contributor Metadata** section in the PR description.
- Record both the human contributor id and the execution tool.
- The human opening or approving the PR is responsible for the change.

This keeps git history clean and human accountability explicit. The full
policy is in [docs/agent-task-protocol.md](./agent-task-protocol.md).

## Review Expectations

Review should confirm:

- the change is linked to repository memory;
- scientific claims remain cautious;
- validation is green;
- task status remains `REVIEW_READY` until maintainer review and merge;
- claim and knowledge wording matches the actual evidence strength;
- claim promotions follow the maintainer review policy;
- no unrelated artifact churn was introduced.

Maintainers may use
[maintainer-review-agent.md](./maintainer-review-agent.md) and the review
checklists under `docs/review-checklists/` to standardize PR review and
post-merge closeout. The review agent returns recommendations only; it does not
merge PRs or make automatic scientific decisions.
