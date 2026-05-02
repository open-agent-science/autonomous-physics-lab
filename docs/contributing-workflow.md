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
5. Read [tasks/ACTIVE.md](../tasks/ACTIVE.md).
6. Read [docs/agent-operating-model.md](./agent-operating-model.md).
7. Pick one existing `READY` task, benchmark, or documentation gap.
8. Make the smallest reproducible change that advances the repository state.
9. Run validation before asking for review.
10. Use the GitHub issue and PR templates so the contribution stays linked to repository memory.
11. Use the branch, commit, PR title, and task-state protocol from
    [docs/agent-task-protocol.md](./agent-task-protocol.md).

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

- one `HYP-*` or `TASK-*`
- optional `EXP-*` scaffold

Rules:

- keep the proposal narrow;
- define assumptions clearly;
- avoid speculative universal claims.

## Validation Checklist

Run before asking for review:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
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
- Fill in the **Agent assistance** section in the PR description.
- The human opening or approving the PR is responsible for the change.

This keeps git history clean and human accountability explicit. The full
policy is in [docs/agent-task-protocol.md](./agent-task-protocol.md).

## Review Expectations

Review should confirm:

- the change is linked to repository memory;
- scientific claims remain cautious;
- validation is green;
- claim and knowledge wording matches the actual evidence strength;
- claim promotions follow the maintainer review policy;
- no unrelated artifact churn was introduced.
