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
---

# Pendulum

## Topic

Classical mechanics, ideal mathematical pendulum.

## Known Baseline

The small-angle period is:

`T0 = 2*pi*sqrt(L/g)`

For finite amplitude, the exact period ratio is:

`T / T0 = (2 / pi) * K(k^2)` where `k = sin(theta / 2)`.

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
- Task: `TASK-0001`

## Open Questions

- Which low-order formula gives the best accuracy/complexity tradeoff?
- How quickly do polynomial amplitude corrections fail near large angles?
- Should the next benchmark include damping or forcing?
