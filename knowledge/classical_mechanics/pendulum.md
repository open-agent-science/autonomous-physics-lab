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
---

# Pendulum

## Topic

Classical mechanics, ideal mathematical pendulum.

## Known Baseline

The small-angle period is:

`T0 = 2*pi*sqrt(L/g)`

For finite amplitude, the exact period ratio is:

`T / T0 = (2 / pi) * K(k^2)` where `k = sin(theta / 2)`.

The current public-alpha benchmark has two canonical pendulum runs:

- `RESULT-0001` / `RUN-0001` for the original low-order candidate comparison;
- `RESULT-0003` / `RUN-0002` for the theory-aware near-separatrix follow-up.

The current best overall candidate remains:

- `model_theta2_theta4`
- verdict: `VALID_IN_RANGE`

`RUN-0002` also shows that theory-aware candidate `model_x_x2_log` improves
near-separatrix behavior relative to `RUN-0001`, but it does not turn the
benchmark into an exact or globally valid formula.

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
- Canonical results:
  - `RESULT-0001`
  - `RESULT-0003`

## Open Questions

- Which low-order formula gives the best accuracy/complexity tradeoff?
- How quickly do polynomial amplitude corrections fail near large angles?
- Can a theory-aware approximation improve separatrix behavior further without
  losing in-range clarity or increasing complexity too much?
- Should the next benchmark include damping or forcing?
