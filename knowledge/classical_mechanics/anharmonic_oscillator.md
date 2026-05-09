---
id: KNOW-0008
title: Anharmonic Oscillator
domain: classical_mechanics
topic: quartic anharmonic oscillator period benchmark
linked_objects:
  hypotheses:
    - HYP-0011
  experiments:
    - EXP-0011
  claims:
    - CLAIM-0009
  tasks:
    - TASK-0159
---

# Anharmonic Oscillator

## Topic

Classical mechanics, conservative quartic anharmonic oscillator period
benchmark.

## Known Baseline

The current benchmark studies the potential:

`V(x) = 1/2 k x^2 + lambda x^4`

using:

- a harmonic baseline `T0 = 2*pi*sqrt(m/k)`;
- a leading-order perturbative correction in
  `epsilon = lambda*A^2/k`;
- a train-fitted empirical quadratic model for holdout comparison;
- a deterministic period-integral reference.

The benchmark compares the harmonic baseline, the leading-order perturbative
correction, and a train-fitted empirical quadratic model.

## Why It Matters

This benchmark adds a stronger nonlinear mechanics surface than pure replay or
numerology-style searches:

- the reference path is deterministic;
- the weak-regime claim ceiling is explicit;
- the holdout slice is predeclared;
- breakdown outside the weak regime is measurable.

## Linked Objects

- Hypothesis: `HYP-0011`
- Experiment: `EXP-0011`
- Claim: `CLAIM-0009`
- Task: `TASK-0159`
- Canonical result: `RESULT-0014`

## Open Questions

- How far can the leading-order perturbative approximation stretch before it
  becomes misleading?
- Which higher-order or structure-aware models improve holdout accuracy without
  becoming opaque?
- Should the next benchmark extend to softening or double-well regimes in a
  separate task?
