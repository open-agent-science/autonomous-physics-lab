# Codex Task: Stabilize Multi-Benchmark Workflow Architecture

Read `AGENTS.md` and `docs/status.md` first.

## Goal

Stabilize the two-benchmark public-alpha state before adding any new physics
benchmark.

The current repository now has two runnable slices:

- `EXP-0001` — `Pendulum Formula Discovery`
- `EXP-0002` — `Damped Oscillator Regime Verification`

The next work should keep both workflows reproducible, non-dirty in CI, and
easy to hand off to future contributors.

## Priority Areas

Work in or around:

```text
physics_lab/workflows/artifacts.py
physics_lab/workflows/pendulum.py
physics_lab/workflows/damped_oscillator.py
physics_lab/workflows/runner.py
.github/workflows/ci.yml
tests/test_pendulum.py
tests/test_damped_oscillator.py
README.md
docs/status.md
```

## Required Outcomes

1. Keep `runner.py` thin and use workflow-specific modules.
2. Ensure example runs support `--output-dir` and do not dirty committed artifacts in CI.
3. Keep repository validation green with 2 hypotheses, 2 experiments, 2 claims,
   2 tasks, 2 knowledge notes, 2 examples, and 2 canonical results.
4. Keep docs honest about the current two-benchmark scope.

## Constraints

- Do not add a third benchmark.
- Do not add dashboard.
- Do not add web API.
- Do not add LLM calls.
- Do not add literature ingestion.
- Do not add multi-agent runtime.
- Keep tests fast.
- Keep scientific semantics unchanged.
- Do not promote claims directly from code execution.

## Before Finishing

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
git status --short
```
