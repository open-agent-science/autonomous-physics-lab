# AGENTS.md

## Project

This repository is `autonomous-physics-lab`.

Autonomous Physics Lab is an open-source scientific engine for generating,
testing, simulating, falsifying, scoring, and reusing physics hypotheses.

It is not a chatbot. It is a hypothesis-testing machine.

## Quick Orientation (single file)

If you prefer to read the full project context in one place, run:

```bash
python3 scripts/generate_context_bundle.py
```

This writes `CONTEXT.md` — a bundle of the core instructions, strategy, and
active task board. The file is also committed to the repo root for download.

## Agent First Default

New contributors and coding agents should start with the mission entrypoint:

```bash
python3 scripts/apl_mission.py
```

Default mode is `research`. The script recommends the highest-value current
scientific mission and provides guardrails for sandbox-only, reviewable work.
For machine-readable context or a copy-paste agent prompt, run:

```bash
python3 scripts/apl_mission.py --json
python3 scripts/apl_mission.py --agent-prompt
```

Use explicit modes when the maintainer asks for non-research work:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Agent First does not replace the task protocol, maintainer review agent, or
closeout flow. It only changes the default onboarding posture: research,
replay, audit, hypothesis testing, and sandbox result drafts come before
microtasks or docs-only support unless the maintainer says otherwise.

Executor agents should treat only `READY` tasks as available work. Do not offer
`REVIEW_READY` tasks as task choices unless the maintainer explicitly asks for
review, closeout, or queue triage.

## Agent Work Paths

Choose your path based on mission mode and available token or time budget:

```mermaid
flowchart LR
    classDef quick  fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,font-weight:bold
    classDef task   fill:#dcfce7,stroke:#16a34a,color:#14532d,font-weight:bold
    classDef sci    fill:#f3e8ff,stroke:#a855f7,color:#581c87,font-weight:bold
    classDef prop   fill:#fef3c7,stroke:#d97706,color:#78350f,font-weight:bold
    classDef finish fill:#f1f5f9,stroke:#64748b,color:#1e293b,font-weight:bold

    Start(["▶ Enter repo"]) --> Mission["🚀 apl_mission.py\nResearch Mode"]
    Mission --> Read["📋 AGENTS.md\n+ mission context"]

    Read -->|"default"| Sci["🔬 Research mission\nhypothesis · replay · audit"]:::sci
    Read -->|"support mode"| MT["⚡ Microtask"]:::quick
    Read -->|"task mode"| RT["🎯 READY task"]:::task
    Read -->|"new idea"| Prop["💡 Task proposal\ntasks/proposals/"]:::prop

    MT  --> PR["📬 branch → PR\n→ maintainer review"]:::finish
    RT  --> PR
    Sci --> PR
    Prop --> PropPR["📋 TASK-PROPOSAL PR\nwait for TASK-XXXX"]:::prop
```

All paths follow `docs/agent-task-protocol.md`. Never push directly to `main`.

## CRITICAL: Never push directly to main

Every change must go through the full task lifecycle:

1. `tasks/TASK-XXXX-*.yaml` — create or reference a task file
2. branch: `agent/<contributor-id>/<agent-id>/task-<number>-<slug>`
3. PR — open it, do not merge it yourself
4. maintainer review → merge

No exceptions for "small", "obvious", or "urgent" changes.
Documentation, scripts, config, and fixes all follow the same flow.
Pushing directly to `main` violates the repository protocol.

The only operations allowed directly on `main` are:
- post-merge task closeout (`status: DONE` + `sync-active-board`)
- `CONTEXT.md` regeneration after a batch merge

## Core Principle

LLMs may propose, explain, and organize hypotheses, but numerical and symbolic
claims must be verified by deterministic code.

Never trust an LLM-generated formula without validation.

## Public Scientific Memory

The project must maintain a public scientific memory.

New hypotheses, claims, experiments, results, tasks, and reusable knowledge
should be stored in version-controlled files.

The system must distinguish between:

- hypothesis: an unverified proposal;
- claim: a statement supported by evidence;
- result: output of a reproducible experiment;
- knowledge: reusable, reviewed information;
- theory: a structured collection of connected claims and hypotheses.

Do not promote a hypothesis to knowledge without validation.

## Open Agent Network

The project should support external agents and humans contributing work.

Tasks should be represented as structured YAML files and, later, GitHub issues
or API jobs.

Agents may propose hypotheses, run simulations, falsify models, improve
formulas, or review results.

Maintainer-run review agents may also review pull requests and perform task
closeout after merge, but they do not make final scientific or merge
decisions automatically.

Every agent output must include:

- task id;
- input references;
- method;
- code reference;
- metrics;
- limitations;
- verdict.

No anonymous unverifiable scientific claim should be accepted as a result.

## Shared Task Pool

Agents do not own permanent roles in this repository.

Instead:

- the task defines the contract;
- any compatible agent may pick a `READY` task;
- agents should prefer one atomic task at a time;
- tasks may be taken out of order only when they do not depend on each other or
  create artifact conflicts.

Use these files as the shared coordination layer:

- `docs/strategy.md`
- `docs/agent-task-protocol.md`
- `docs/task-proposal-protocol.md`
- `docs/agent-operating-model.md`
- `tasks/ACTIVE.md`
- `tasks/TASK-TEMPLATE.yaml`
- `tasks/proposals/TASK-PROPOSAL-TEMPLATE.yaml`

Do not treat `CODEX_TASK.md` as the single source of truth for active work.
Do not invent task branch, commit, PR, or task-state formats locally.
Use `docs/agent-task-protocol.md`.
Use `docs/task-proposal-protocol.md` when suggesting new task ideas that do
not yet have a maintainer-assigned canonical `TASK-XXXX` id.
Use `docs/maintainer-review-agent.md` when the maintainer wants structured PR
review or task closeout help.
Use `docs/agent-catalog.md` when you need the shortest map of which agent
paths, maintainer automation roles, and entrypoints already exist.

Before starting implementation, agents must create a working task branch using
the canonical branch format. Agents must not begin editing repository files,
staging changes, or otherwise performing task work on `main`.

## Task Proposal Rule

If no existing `READY` task fits and the maintainer did not explicitly assign a
canonical `TASK-XXXX` id, agents should create a proposal under
`tasks/proposals/` instead of guessing the next task number.

Normal agents should not assign canonical task ids during parallel work.

Maintainers may create canonical ids directly. Maintainer-directed review or
task-admin agents may do so only on explicit maintainer instruction.

## Original MVP

The first MVP was `Pendulum Formula Discovery`.

Goal:

1. Generate exact pendulum period data.
2. Fit correction formulas.
3. Compare models.
4. Score accuracy and complexity.
5. Produce a reproducible report.

## Current Benchmark Scope

The repository currently has eleven canonical experiment files:

- `EXP-0001` — `Pendulum Formula Discovery`
- `EXP-0002` — `Damped Oscillator Regime Verification`
- `EXP-0004` — `Charged-Lepton Koide Reproduction`
- `EXP-0005` — `Historical Tau Holdout Prediction`
- `EXP-0006` — `Dimensional Analysis Validator MVP`
- `EXP-0007` — `Neutrino Koide Consistency Test`
- `EXP-0008` — `Quark Koide Cascade — Brannen Phase Extension Test`
- `EXP-0009` — `Particle-Mass Relation Falsifier MVP`
- `EXP-0010` — `Muon g-2 Formula-Search Stress Test`
- `EXP-0011` — `Anharmonic Oscillator Period Benchmark`
- `EXP-0012` — `Nuclear Mass Baseline Residual Benchmark`

For public-facing summaries, keep the benchmark surface conservative:
completed benchmarks, falsifications, and sandbox pilots are reviewable
evidence, not automatic discovery claims. `EXP-0010` should be described only
as a guarded empirical formula-search stress test with explicit
multiple-testing and numerology limitations. `EXP-0012` is the current
research-first validation surface, but nuclear residual candidates remain
sandbox-only unless reviewed and promoted by a maintainer.

Use that broader benchmark scope when updating docs, status snapshots, and
contributor guidance during pre-public validation.

## Planning Files

To continue work consistently, use these project documents:

- `docs/strategy.md` for the strategic compass;
- `docs/agent-task-protocol.md` for the canonical execution protocol;
- `docs/agent-operating-model.md` for the shared agent workflow;
- `tasks/ACTIVE.md` for the live task board;
- `docs/implementation-plan.md` for the broader phased strategy;
- `docs/next-steps.md` for the current short-term execution queue;
- `docs/backlog.md` for deferred or medium-term work.

If you complete a meaningful block of work or if priorities change, update the
planning files so the next contributor can continue without reconstructing
project state from commits alone.

## Architecture

Use this package structure:

```text
physics_lab/
  cli.py
  engines/
    symbolic.py
    simulation.py
    formula_discovery.py
    scoring.py
    critic.py
  registry/
    hypotheses.py
    claims.py
    experiments.py
    tasks.py
  workflows/
    runner.py
```

## Scientific Rules

Every hypothesis test should try to produce:

- input hypothesis;
- assumptions;
- equations;
- generated or loaded data;
- fitted model;
- validation range;
- error metrics;
- failure cases;
- verdict.

Prefer this verdict vocabulary:

- VALID
- PARTIALLY_VALID
- INVALID
- OVERFITTED
- INCONCLUSIVE

For hypothesis lifecycle states, prefer:

- PROPOSED
- FORMALIZED
- TESTING
- VALID_IN_RANGE
- PARTIALLY_VALID
- FALSIFIED
- OVERFITTED
- INCONCLUSIVE
- INTEGRATED

## Pendulum MVP Requirements

Implement the first workflow for pendulum period approximation.

The exact pendulum period ratio is:

`T / T0 = (2 / pi) * K(k^2)`

`k = sin(theta / 2)`

where:

- `theta` is amplitude in radians;
- `K` is the complete elliptic integral of the first kind;
- `T0 = 2*pi*sqrt(L/g)`.

Compare at least these model families:

1. `1 + a*theta^2`
2. `1 + a*theta^2 + b*theta^4`
3. `1 + a*sin(theta/2)^2`
4. `1 + a*x + b*x^2` where `x = sin(theta/2)^2`

For each model, report:

- fitted coefficients;
- mean relative error;
- max relative error;
- train range;
- test range;
- complexity score;
- final verdict.

## Coding Rules

- Use Python 3.11+.
- Prefer small, pure functions.
- Keep scientific calculations in Python, not in LLM text.
- Use NumPy, SciPy, and SymPy for math.
- Avoid hidden global state.
- Avoid unnecessary abstractions in v0.1.
- Do not add web frameworks yet.
- Do not add dashboard yet.
- Do not integrate ScienceClaw, OpenClaw, or LabClaw yet.
- Prepare adapters later, but keep v0.1 standalone.

## Git Commit Rules for Agents

Agents may create git commits only when the maintainer explicitly asks for it.

Agents must create and switch to a task branch before doing any repository
work for a task.

Agents must not work on `main`.

Agents must commit only on a task branch, never directly on `main`.

Before committing, agents must run:

```bash
git status --short
git diff
```

Agents should stage only files relevant to the current task. Prefer explicit
file paths over broad staging.

Use commit messages in this format:

`<type>(task-XXXX): <short meaningful summary>`

Examples:

- `docs(task-0033): standardize contributor-agent identity format`
- `feat(task-0011): add numerical precision audit`
- `test(task-0017): add dimensional challenge validation`
- `fix(task-0018): support planning-only task inputs`

Allowed commit types:

- `docs`
- `feat`
- `fix`
- `test`
- `refactor`
- `chore`

Agents must not:

- commit directly to `main`
- merge branches
- rebase shared branches
- force-push
- create tags
- mark their own task as `DONE`
- use `Co-Authored-By` for AI agents

`git push` requires explicit maintainer approval.

AI assistance should be recorded in PR metadata, not in git co-author trailers.

Maintainer review and task closeout may be assisted by a maintainer-run review
agent, but that agent must not auto-merge PRs, promote claims, or mark tasks
`DONE` before maintainer review and merge.

After committing, agents should generate a review bundle:

```bash
./scripts/apl_review_bundle.sh
```

## Testing Rules

Add tests for:

- exact pendulum data generation;
- model fitting;
- scoring;
- CLI smoke run.

Tests must be fast.
Do not make tests depend on external APIs.

## Completion Expectations

Before marking work complete, run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --exit-code
```

If a change touches CLI behavior, include a smoke test.
If a change touches scientific formulas, include a numerical regression test.
For branch naming, commit messages, PR titles, task-state transitions, and the
standard execution flow, use `docs/agent-task-protocol.md`.
