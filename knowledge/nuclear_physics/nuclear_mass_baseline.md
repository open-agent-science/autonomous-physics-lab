---
id: KNOW-0009
title: Nuclear Mass Baseline
domain: nuclear_physics
topic: semi-empirical nuclear-mass baseline residual benchmark
linked_objects:
  hypotheses:
    - HYP-0012
  experiments:
    - EXP-0012
  claims:
    - CLAIM-0010
  tasks:
    - TASK-0168
---

# Nuclear Mass Baseline

## Topic

Nuclear physics, pinned measured slice baseline residual benchmark.

## Known Baseline

The current benchmark studies a small measured nuclear-mass slice using:

- a reference liquid-drop baseline without pairing;
- a reference semi-empirical baseline with pairing;
- a slice-fitted semi-empirical baseline;
- deterministic conversion from atomic mass to binding energy.

The benchmark compares reference-coefficient and fitted semi-empirical
baselines against a small pinned measured slice.

## Why It Matters

This benchmark makes the nuclear-mass campaign executable without pretending
we already have a full discovery-ready dataset:

- the dataset slice is pinned and measured-only;
- shell-closure and pairing-sensitive subsets are explicit diagnostics;
- uncertainty-normalized residuals are reviewable;
- the next holdout task has a concrete residual surface to formalize.

## Linked Objects

- Hypothesis: `HYP-0012`
- Experiment: `EXP-0012`
- Claim: `CLAIM-0010`
- Task: `TASK-0168`
- Canonical result: `RESULT-0015`

## Open Questions

- How much of the current residual map survives once the full AME-style dataset is pinned?
- Which shell-neighborhood definitions should become mandatory in the holdout protocol?
- Does a compact correction family improve magic-subset behavior without collapsing on future holdout slices?

