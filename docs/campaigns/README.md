# Campaign Map

This directory is the campaign-level map for APL.

Use it when you need to answer four questions quickly:

1. What scientific direction is this repository pursuing?
2. Which directions already have reproducible evidence?
3. Which directions are still planning-only?
4. Where can a human or agent contribute next without overclaiming?

## Current Campaigns

| Campaign | Maturity | Current evidence | Best next contribution |
| --- | --- | --- | --- |
| [Pendulum Formula Falsification](./pendulum-formula-falsification.md) | Active benchmark with multiple canonical runs | `EXP-0001/RUN-0001`, `RUN-0002`, `RUN-0003` and the gauntlet result package | stronger falsification probes, clearer diagnostics, safer wording |
| [Particle Mass Relations](./particle-mass-relations.md) | Active benchmark track with narrow charged-lepton results | `EXP-0004/RUN-0004` and `EXP-0005/RUN-0005` | guardrail-preserving follow-up tasks before broader search |
| [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | Planning complete, implementation pending | challenge-set design plus 50-item dataset scaffold | symbolic checker implementation and benchmark wiring |
| [Thought-Experiment Consistency](./thought-experiment-consistency.md) | Planning active, no canonical run yet | suite design plus light-clock micro-planning task | scoped scenario planning, then deterministic validator design |

## How To Use This Map

- If you want the strongest existing evidence, start with pendulum.
- If you want the highest scientific-overclaim risk with useful guardrails,
  start with particle-mass relations.
- If you want a clean validator-style benchmark with no discovery language,
  start with dimensional analysis.
- If you want analytical consistency work instead of fitting work, start with
  thought experiments.

## Repository-Wide Orientation

Pair these campaign pages with:

- [Mission Control](../mission-control.md)
- [Project Status](../status.md)
- [Architecture](../architecture.md)
- [Active Task Board](../../tasks/ACTIVE.md)
