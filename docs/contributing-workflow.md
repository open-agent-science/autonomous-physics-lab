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
2. Read [docs/status.md](./status.md).
3. Read [docs/next-steps.md](./next-steps.md).
4. Pick an existing task, benchmark, or documentation gap.
5. Make the smallest reproducible change that advances the repository state.
6. Run validation before asking for review.
7. Use the GitHub issue and PR templates so the contribution stays linked to repository memory.

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
```

Optional but recommended for larger work:

```bash
RUN_EXPERIMENT=1 ./scripts/apl_snapshot.sh
```

## GitHub Templates

Use the built-in repository templates when contributing through GitHub:

- `Benchmark Improvement` for work on an existing benchmark or verifier;
- `Hypothesis Proposal` for a new narrow claim, task, or experiment scaffold;
- the PR template for linked artifacts, validation, and claim-scope review.

## Artifact Policy

- Use `--output-dir` for routine validation runs.
- Do not update committed canonical artifacts accidentally.
- Only regenerate committed `results/` artifacts when the benchmark itself has meaningfully changed.
- If canonical artifacts change, include a short explanation in the PR.

## Review Expectations

Review should confirm:

- the change is linked to repository memory;
- scientific claims remain cautious;
- validation is green;
- claim and knowledge wording matches the actual evidence strength;
- no unrelated artifact churn was introduced.
