# Strategy

## Current Phase

Post-`v0.1-public-alpha` stabilization with shared agent handoff and tighter
scientific execution discipline.

## Mission

Build open scientific infrastructure for testing, falsifying, scoring, and
reusing physics hypotheses.

The repository is not trying to produce speculative "AI discoveries" on demand.
It is trying to make verification-first scientific work reproducible, reviewable,
and reusable.

## Current Priorities

1. Maintain verification-first discipline across all benchmarks.
2. Keep public scientific memory internally consistent and reviewable.
3. Improve agent handoff so different developers and coding agents can continue
   work without losing context.
4. Prefer atomic tasks with deterministic outputs and clear validation.
5. Avoid feature expansion that outruns current verification quality.

## Current North-Star Result

Produce benchmark slices where many candidate physics formulations can be:

- generated or proposed;
- tested deterministically;
- classified by failure mode and validity range;
- stored as public scientific memory.

The current visible examples are:

- `EXP-0001` — pendulum formula discovery with range-aware and
  separatrix-aware review artifacts;
- `EXP-0002` — damped oscillator regime verification with exact linear checks.

## Current Execution Model

The repository uses a shared task pool.

Agents are not assigned permanent roles. Instead:

- a task defines the contract;
- an agent picks one atomic task;
- the agent runs validation;
- the agent updates task state and docs if the task changes project reality;
- the next agent continues from the same repository state.

Sequential local work is preferred by default, but independent `READY` tasks may
be taken out of order when they do not create hidden coupling or artifact churn.

## Task Selection Rules

- Use [tasks/ACTIVE.md](../tasks/ACTIVE.md) as the live task board.
- Use [docs/agent-operating-model.md](./agent-operating-model.md) for the shared
  execution protocol.
- Use [tasks/TASK-TEMPLATE.yaml](../tasks/TASK-TEMPLATE.yaml) when proposing a
  new task.

## Non-Goals

- Do not auto-promote claims.
- Do not claim global validity from range-limited evidence.
- Do not add dashboard, web API, literature ingestion, or multi-agent runtime
  before current verification goals are met.
- Do not use LLM output as a substitute for deterministic validation.
- Do not frame the project as "solving physics" or "finding a theory of
  everything."

## Decision Rule

When choosing between broader scope and stronger verification, choose stronger
verification.
