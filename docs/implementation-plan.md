# Implementation Plan

## Current Decision

Start with a narrow but complete vertical slice:

`Hypothesis -> Experiment -> Result -> Claim -> Knowledge -> Next Task`

The first slice is `Pendulum Formula Discovery`.
The second slice is `Damped Oscillator Regime Verification`.

## Status Snapshot

Completed so far:

- Phase 0 foundation work;
- Phase 1 pendulum MVP;
- a substantial part of Phase 2 public-memory integration:
  - versioned hypothesis, experiment, task, claim, agent, and result artifacts;
  - schema validation;
  - repo-wide validation;
  - referential integrity checks.
  - richer result semantics and traceability metadata
  - schema coverage for knowledge notes and example configs
  - generated claim and knowledge update helper artifacts
  - run-based evidence artifacts under `results/<experiment>/<run>/`
  - first verification gate for pendulum evidence
  - structure-aware dimensional consistency validation for pendulum candidates
  - small-angle exact-window verification against the elliptic-integral reference
  - derivative-based small-angle curvature verification
  - upper-range exact-window verification on the configured amplitude interval
  - non-gating near-separatrix extrapolation diagnostic
  - theory-aware separatrix asymptotic diagnostic
  - theory-aware pendulum candidate family with committed `RESULT-0003` under `results/EXP-0001/RUN-0002/`
  - immutable run-input snapshots so historical canonical results remain validation-stable as repository inputs evolve
  - second runnable benchmark for exact damped-oscillator regime verification
  - committed `RESULT-0002` artifact set under `results/EXP-0002/RUN-0001/`
  - maintainer-facing claim promotion policy linked to generated claim suggestions
  - result input-hash drift detection for committed canonical artifacts

Use [next-steps.md](./next-steps.md)
for the active short-term queue.

Use [backlog.md](./backlog.md)
for medium-term and deferred work.

## Phase 0: Foundation

Goal: create the repository contract before writing scientific code.

Done in this phase:

- define positioning;
- define architecture;
- define public knowledge layout;
- define agent/task model;
- define roadmap and MVP boundaries.

Outputs:

- `README.md`
- `AGENTS.md`
- `CODEX_TASK.md`
- `docs/*.md`
- starter registry files

## Phase 1: Scientific Core MVP

Goal: make one deterministic experiment run end-to-end.

Implementation targets:

1. minimal Python package scaffold;
2. exact pendulum simulator using elliptic integral;
3. candidate formula fitting;
4. scoring and verdict engine;
5. Markdown report writer;
6. CLI command for running an example experiment;
7. fast tests;
8. minimal CI.

Definition of done:

- `physics-lab run examples/pendulum.yaml` works;
- report file is produced;
- metrics artifact is stored;
- tests pass quickly;
- lint passes.

Status:

- implemented

## Phase 2: Public Memory Integration

Goal: connect the code workflow to repository knowledge objects.

Implementation targets:

1. load hypothesis and experiment definitions from files;
2. write result artifacts into `results/`;
3. link results to claim and knowledge references;
4. validate structured object shape with schemas.

Definition of done:

- experiment inputs come from versioned files;
- outputs can be traced back to ids;
- artifact naming is stable and reviewable.

Status:

- implemented for the pendulum slice
- implemented for the damped-oscillator slice
- remaining work includes deeper evidence semantics and more automated public-memory updates

## Phase 3: Verification Stack Expansion

Goal: move from one simulator into a real verification platform.

Implementation targets:

1. dimensional analysis hooks;
2. symbolic validation helpers;
3. stronger known-limit and structure-aware tests;
4. more benchmark physics problems.

Candidate next domains:

- orbital perturbation;
- diffusion scaling;
- driven oscillator or nonlinear oscillator extensions.

## Phase 4: Open Agent Workflow

Goal: allow others to contribute in a controlled way.

Implementation targets:

1. task schema;
2. agent manifest schema;
3. contribution guide;
4. CI checks for structured files;
5. result review flow.

## Near-Term Execution Order

This is the practical order I recommend next:

1. deepen known-limit and structural verification checks for pendulum and damped oscillator;
2. deepen claim and knowledge evidence semantics;
3. improve contributor docs and project status tooling;
4. decide the third benchmark physics workflow after the two current slices are fully release-ready.

Current stabilization rule:

- keep workflow-specific implementation in dedicated modules;
- keep `runner.py` as dispatch only;
- keep CI example runs non-dirty by using temp output roots.
- keep claim promotion as a human review gate even when automated suggestions exist.

## Risks to Avoid

- adding too much infra before one workflow works;
- mixing scientific claims with unverified prose;
- adding LLM logic before deterministic validation exists;
- building dashboard or agent orchestration too early;
- over-promising with "new physics" language before verification is mature.

## Working Principle

At each step, prefer a smaller reproducible system over a broader speculative
one.
