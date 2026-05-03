# Autonomous Physics Lab

Generate. Simulate. Falsify. Reuse.

Autonomous Physics Lab (APL) is an open-source infrastructure for generating,
testing, simulating, falsifying, and reusing physics hypotheses.

APL is not a chatbot. It is a verification-first engine for testing physics
ideas.

## Positioning

The long-term goal is not to claim a "theory of everything" from day one.
The goal is to build infrastructure for systematic theory search in physics.

The project combines three cores:

1. A hypothesis engine for proposing and testing candidate formulas or models.
2. A version-controlled scientific memory for storing hypotheses, claims,
   experiments, and results.
3. An open agent task network so humans and external agents can contribute reproducible work.

## Original MVP

The original MVP was `Pendulum Formula Discovery`.

It should:

1. Generate exact pendulum period ratio data.
2. Fit simple approximation families.
3. Compare candidate models.
4. Score accuracy and complexity.
5. Produce a reproducible Markdown report.

## Current Benchmarks

The repository currently stabilizes two verification-first benchmark slices:

1. `EXP-0001` — `Pendulum Formula Discovery`
2. `EXP-0002` — `Damped Oscillator Regime Verification`

Both benchmarks produce run-based artifacts under `results/<experiment>/<run>/`
and are validated through the repository registry and CLI tooling.

## Current measurable result

APL evaluated 100 deterministic candidate formulas for the ideal pendulum
period ratio in `EXP-0001/RUN-0003`. The top leaderboard candidate
`model_t4_x1` reached approximately `3.1e-4` mean relative residual on the
configured test range. A dedicated precision audit classified that error as
model residual, not numerical reference noise. No symbolic exactness claim and
no global validity claim are made.

See [docs/results/pendulum-gauntlet-100-summary.md](docs/results/pendulum-gauntlet-100-summary.md)
for the full package and limitations.

## Contribute with an AI coding agent

Put your coding agent to work on reproducible physics tasks.

Invited contributors can use Codex, Claude Code, or other coding agents to
pick atomic tasks from [tasks/ACTIVE.md](tasks/ACTIVE.md), work in branches,
open PRs, and submit reproducible scientific changes for maintainer review.
Start with [docs/private-contributor-pilot.md](docs/private-contributor-pilot.md)
for the private-alpha workflow and validation expectations.

## Quickstart

```bash
git clone https://github.com/gladunrv/autonomous-physics-lab.git
cd autonomous-physics-lab

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"

python -m ruff check .
python -m pytest

python -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped

python -m physics_lab.cli validate-repo .
python -m physics_lab.cli status .
```

## Repository Shape

```text
autonomous-physics-lab/
  AGENTS.md
  CODEX_TASK.md
  README.md

  physics_lab/
    engines/
    registry/
    schemas/
    workflows/

  hypotheses/
  claims/
  experiments/
  results/
  knowledge/
  tasks/
  agents/
  docs/
  tests/
```

## Status

The repository currently has two working benchmark slices:

- architecture and documentation are in place;
- the public knowledge layout is defined;
- the pendulum formula discovery workflow works end-to-end;
- the damped-oscillator regime verification workflow works end-to-end;
- structured artifact validation and repo-wide checks are implemented.

See [docs/architecture.md](docs/architecture.md),
[docs/roadmap.md](docs/roadmap.md), and
[docs/implementation-plan.md](docs/implementation-plan.md).

## Planning Docs

Use these files to continue the project without guessing:

- [docs/strategy.md](docs/strategy.md) for the current strategic compass
- [tasks/ACTIVE.md](tasks/ACTIVE.md) for the shared live task board
- [docs/agent-operating-model.md](docs/agent-operating-model.md) for multi-agent handoff and task execution
- [docs/implementation-plan.md](docs/implementation-plan.md) for phased strategy
- [docs/next-steps.md](docs/next-steps.md) for the immediate working queue
- [docs/backlog.md](docs/backlog.md) for medium-term and deferred tasks
- [docs/status.md](docs/status.md) for the current project readiness snapshot
- [docs/architecture-index.md](docs/architecture-index.md) for the fastest codebase and artifact map
- [docs/private-contributor-pilot.md](docs/private-contributor-pilot.md) for invited private contributors using coding agents
- [docs/public-release-gates.md](docs/public-release-gates.md) for the gates that must be satisfied before the repository becomes public
- [docs/github-branch-protection-plan.md](docs/github-branch-protection-plan.md) for staged PR and branch-protection setup
- [docs/release-checklist.md](docs/release-checklist.md) for public-alpha tag and release prep
- [docs/releases/v0.1-public-alpha.md](docs/releases/v0.1-public-alpha.md) for prepared release notes
- [CONTRIBUTING.md](CONTRIBUTING.md) for contributor expectations
- [docs/contributing-workflow.md](docs/contributing-workflow.md) for the repository contribution flow
- [docs/claim-promotion-policy.md](docs/claim-promotion-policy.md) for claim-status review rules
