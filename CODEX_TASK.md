# Codex Task: Build v0.1 Pendulum Formula Discovery MVP

Read `AGENTS.md` first and follow it.

## Goal

Create a standalone Python package that can run a pendulum formula discovery
experiment and store its artifacts in the public repository structure.

The experiment should:

1. generate exact pendulum period ratio data;
2. fit simple correction formulas;
3. compute errors;
4. score models;
5. write a Markdown report.

## Required Files

Create or update:

```text
physics_lab/cli.py
physics_lab/engines/simulation.py
physics_lab/engines/formula_discovery.py
physics_lab/engines/scoring.py
physics_lab/engines/critic.py
physics_lab/workflows/runner.py
examples/pendulum.yaml
tests/test_pendulum.py
```

## CLI

This command should work:

```bash
physics-lab run examples/pendulum.yaml
```

## Expected Output

Generate:

```text
examples/reports/pendulum_formula_discovery.md
results/EXP-0001/
```

The report should include:

- experiment title;
- data range;
- candidate formulas;
- fitted coefficients;
- mean relative error;
- max relative error;
- verdict;
- short conclusion.

## Constraints

- Do not add dashboard.
- Do not add LLM calls.
- Do not add ScienceClaw, OpenClaw, or LabClaw integration yet.
- Keep it deterministic and testable.
- Use SciPy for elliptic integral.
- Use NumPy for fitting.
- Keep tests fast.

## Before Finishing

Run:

```bash
ruff check .
pytest
```
