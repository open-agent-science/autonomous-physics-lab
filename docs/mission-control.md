# Mission Control

## What APL Is Trying To Do

Autonomous Physics Lab (APL) is verification-first scientific infrastructure.
Its job is not to improvise grand theories on demand. Its job is to make
physics hypotheses testable, falsifiable, reproducible, and reviewable in a
shared public-memory repository.

APL currently operates in `v0.1-private-alpha`. The repository stays private
until the contributor pilot, validation discipline, and public-release gates
are satisfied.

## What APL Is Not Trying To Do

- It is not a chatbot for speculative physics claims.
- It is not a dashboard product yet.
- It is not a claim-promotion machine.
- It is not evidence of "new physics" just because a formula fits well.

## Current Scientific Posture

APL already has:

- two stabilized benchmark slices: `EXP-0001` pendulum formula discovery and
  `EXP-0002` damped oscillator regime verification;
- one strong public-style pendulum result package from `EXP-0001/RUN-0003`;
- a narrow particle-mass benchmark track with charged-lepton reproduction and
  tau holdout results;
- planning-only benchmark tracks for dimensional validation and thought
  experiment consistency.

The most important rule remains the same: when scope and verification quality
conflict, choose stronger verification.

## Campaign Map

APL's current contributor-facing campaigns are:

| Campaign | Status | Why it exists | Best starting point |
| --- | --- | --- | --- |
| [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md) | Active with canonical results | Stress-test approximation discovery against an exact reference | [pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md) |
| [Particle Mass Relations](./campaigns/particle-mass-relations.md) | Active with narrow results and strong guardrails | Test whether numerically impressive relations survive disciplined falsification | [koide-tau-holdout.md](./results/koide-tau-holdout.md) |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | Planning complete, implementation not started | Build a hard quality floor for future formula work | [dimensional-analysis-challenge-set.md](./notes/dimensional-analysis-challenge-set.md) |
| [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md) | Planning active, no canonical run yet | Extend APL beyond fit benchmarks into invariant-based consistency checks | [thought-experiment-consistency-suite.md](./notes/thought-experiment-consistency-suite.md) |

Use [docs/campaigns/README.md](./campaigns/README.md) for the full map.

## Current Results Worth Reading

Start with these if you want to understand what APL can already demonstrate:

1. [Pendulum Gauntlet 100 Summary](./results/pendulum-gauntlet-100-summary.md)
   for the strongest current measurable benchmark result.
2. [Historical Tau Holdout Prediction](./results/koide-tau-holdout.md) for the
   narrowest honest particle-mass benchmark result.
3. [Project Status](./status.md) for the current repository-wide readiness
   snapshot.
4. [Architecture](./architecture.md) for how hypotheses, experiments, results,
   claims, knowledge, and tasks fit together.

## Where Contributors Can Help

Humans and coding agents can contribute in four broad ways:

1. strengthen an existing benchmark with better validation, better wording, or
   tighter failure-mode reporting;
2. implement a planning-only campaign that already has a scoped benchmark
   design;
3. improve repository navigation, review discipline, or public-memory hygiene;
4. propose a new task when no `READY` task already fits.

Operational entry points:

- [tasks/ACTIVE.md](../tasks/ACTIVE.md) for the live task board;
- [docs/agent-task-protocol.md](./agent-task-protocol.md) for branch, task, PR,
  and validation rules;
- [tasks/proposals/README.md](../tasks/proposals/README.md) for proposal-first
  work;
- [docs/private-contributor-pilot.md](./private-contributor-pilot.md) for the
  invited contributor flow.

## Fast Contribution Paths

If you want a low-risk place to help next, prefer one of these patterns:

- documentation and public-wording tightening around existing results;
- planning tasks that sharpen future benchmark contracts without touching
  canonical result artifacts;
- validation and safety tasks that make overclaim or artifact drift harder.

If you want deeper implementation work, start from a campaign page and confirm
whether the next useful step is still planning, validation, or a real new
workflow.

## What Not To Claim Right Now

- Do not call pendulum approximations exact or globally valid.
- Do not treat the tau holdout benchmark as an explanation of particle masses.
- Do not claim the dimensional validator already works; that campaign is still
  pre-implementation.
- Do not describe the thought-experiment suite as a completed benchmark.
- Do not present the repository as public-launch ready.

## Read Order For New Contributors

1. [README.md](../README.md)
2. [docs/mission-control.md](./mission-control.md)
3. [docs/campaigns/README.md](./campaigns/README.md)
4. [docs/status.md](./status.md)
5. [tasks/ACTIVE.md](../tasks/ACTIVE.md)
6. [docs/agent-task-protocol.md](./agent-task-protocol.md)
