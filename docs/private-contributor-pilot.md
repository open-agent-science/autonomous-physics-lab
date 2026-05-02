# Private Contributor Pilot

This document explains how invited contributors should work during
`v0.1-private-alpha`.

The repository is still private. Contributions should optimize for reproducible
scientific work, task clarity, and review discipline rather than speed or broad
visibility.

## Clone the Private Repository

After the maintainer grants access, clone the repository with SSH or HTTPS:

```bash
git clone git@github.com:gladunrv/autonomous-physics-lab.git
cd autonomous-physics-lab
```

Then create and activate a local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Pick a Task

Choose one `READY` task from [../tasks/ACTIVE.md](../tasks/ACTIVE.md).

Before starting:

1. Read [../AGENTS.md](../AGENTS.md).
2. Read [agent-task-protocol.md](./agent-task-protocol.md).
3. Read [status.md](./status.md), [strategy.md](./strategy.md), and
   [agent-operating-model.md](./agent-operating-model.md).
4. Confirm that the task is atomic and does not silently expand scope.

If a task is unclear, narrow it first. Do not combine several unrelated tasks in
one PR.

Not every task points to a concrete benchmark.

- science execution tasks should reference a real `hypothesis_id` and `experiment_id`
- planning tasks may use `mode: planning_only`
- contributor or workflow tasks may use `mode: workflow`

Do not add fake pendulum references to unrelated planning tasks just to match an
older task shape.

## Branch Naming Convention

Use the canonical format from
[agent-task-protocol.md](./agent-task-protocol.md):

`agent/<agent-id>/task-<task-number>-<short-slug>`

Example:

```bash
git checkout -b agent/roman/task-0011-numerical-audit
```

Rules:

- lowercase only
- no spaces
- no underscores
- include the task number
- keep the slug short

Do not work directly on `main`. Do not invent alternate branch formats.

## Commit and Pull Request Format

Use the canonical commit and PR title formats from
[agent-task-protocol.md](./agent-task-protocol.md).

Examples:

```text
docs(task-0019): standardize agent task protocol
TASK-0019: Standardize agent branch, commit, and pull request protocol
```

## Pull Request Requirements

Every PR must:

- link to a `TASK-*` id
- use the standard PR title format
- stay within one atomic task scope
- explain what changed and why
- state any scientific limitations clearly
- include validation results
- wait for maintainer review before merge

## Required Validation Before PR

Run all of the following:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

Use `--output-dir` for routine example runs so committed canonical artifacts do
not change accidentally.

## What Not to Do

- do not work directly on `main`
- do not rewrite canonical `results/` artifacts casually
- do not expand a task into dashboard, web API, database, ingestion, or runtime work
- do not promote claims without maintainer review
- do not present a numerical fit as a scientific discovery
- do not use marketing language such as "AI solved physics"

## Overclaiming Guardrails

Keep scientific wording conservative:

- say "validated to tolerance" for numerical agreement
- do not say "100% exact" unless symbolic equality is proven
- keep range limits, assumptions, and failure modes visible
- treat generated claim updates as review suggestions, not automatic truth

Claims must not be promoted without maintainer review. Follow
[claim-promotion-policy.md](./claim-promotion-policy.md) before changing any
claim status.
