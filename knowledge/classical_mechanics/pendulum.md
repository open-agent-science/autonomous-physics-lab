---
id: KNOW-0001
title: Pendulum
domain: classical_mechanics
topic: ideal mathematical pendulum
linked_objects:
  hypotheses:
    - HYP-0001
  experiments:
    - EXP-0001
  claims:
    - CLAIM-0001
  tasks:
    - TASK-0001
    - TASK-0003
    - TASK-0010
    - TASK-0086
    - TASK-0110
---

# Pendulum

## Topic

Classical mechanics, ideal mathematical pendulum.

## Known Baseline

The small-angle period is:

`T0 = 2*pi*sqrt(L/g)`

For finite amplitude, the exact period ratio is:

`T / T0 = (2 / pi) * K(k^2)` where `k = sin(theta / 2)`.

The current public-alpha benchmark has several canonical pendulum runs:

- `RESULT-0001` / `RUN-0001` for the original low-order candidate comparison;
- `RESULT-0003` / `RUN-0002` for the theory-aware near-separatrix follow-up;
- `RESULT-0004` / `RUN-0003` for the 100-candidate gauntlet;
- `RESULT-0008` / `RUN-0004` for the physics-constrained gauntlet;
- `RESULT-0013` / `RUN-0005` for the asymptotic-refined 102-candidate
  follow-up.

The latest asymptotic-refined follow-up identifies:

- `model_asymptotic_refined`
- verdict: `VALID_IN_RANGE`

This does not turn the benchmark into an exact or globally valid formula. The
pendulum evidence remains range-limited and candidate-family-limited.

## Why It Matters

This is a good first benchmark because:

- the exact reference solution is known;
- the approximation problem is meaningful but bounded;
- candidate formulas can be compared quantitatively;
- the workflow exercises simulation, fitting, scoring, and reporting.

## Linked Objects

- Hypothesis: `HYP-0001`
- Experiment: `EXP-0001`
- Claim: `CLAIM-0001`
- Tasks:
  - `TASK-0001`
  - `TASK-0003`
  - `TASK-0010`
  - `TASK-0086`
  - `TASK-0110`
- Canonical results:
  - `RESULT-0001`
  - `RESULT-0003`
  - `RESULT-0004`
  - `RESULT-0008`
  - `RESULT-0013`

## Open Questions

- Which low-order formula gives the best accuracy/complexity tradeoff?
- How quickly do polynomial amplitude corrections fail near large angles?
- Can a theory-aware approximation improve separatrix behavior further without
  losing in-range clarity or increasing complexity too much?
- Should the next benchmark include damping or forcing?
