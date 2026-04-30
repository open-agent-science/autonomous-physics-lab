---
id: KNOW-0002
title: Damped Oscillator
domain: classical_mechanics
topic: linear damped harmonic oscillator
linked_objects:
  hypotheses:
    - HYP-0002
  experiments:
    - EXP-0002
  claims:
    - CLAIM-0002
  tasks:
    - TASK-0002
---

# Damped Oscillator

## Topic

Classical mechanics, linear damped harmonic oscillator.

## Known Baseline

The governing equation is:

`m*x'' + c*x' + k*x = 0`

The solution structure depends on the damping ratio:

- underdamped;
- critically damped;
- overdamped.

The current canonical benchmark result is:

- `RESULT-0002` / `RUN-0001`

Its verification summary passes all current checks, including:

- regime classification;
- initial-condition recovery;
- underdamped energy decay;
- oscillatory vs non-oscillatory behavior;
- dimensional consistency;
- `c -> 0` undamped-limit behavior;
- underdamped envelope decay-rate behavior;
- critical damping boundary behavior;
- overdamped asymptotic tail behavior.

## Why It Matters

This is a strong second benchmark because:

- exact analytic solutions are known;
- regime transitions are physically meaningful;
- verification can include limits, dimensional checks, and decay behavior;
- it extends the project beyond pendulum-specific approximation workflows.

## Linked Objects

- Hypothesis: `HYP-0002`
- Experiment: `EXP-0002`
- Claim: `CLAIM-0002`
- Task: `TASK-0002`
- Canonical result: `RESULT-0002`

## Open Questions

- Which deterministic checks best separate the three damping regimes?
- How should energy decay be reported across regimes?
- Should the next step benchmark driven or nonlinear oscillators?
