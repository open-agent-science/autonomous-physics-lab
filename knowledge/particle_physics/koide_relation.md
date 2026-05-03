---
id: KNOW-0003
title: Koide Relation
domain: particle_physics
topic: charged-lepton Koide reproduction benchmark
linked_objects:
  hypotheses:
    - HYP-0004
  experiments:
    - EXP-0004
  claims:
    - CLAIM-0003
  tasks:
    - TASK-0037
---

# Koide Relation

## Topic

Particle physics, charged-lepton Koide reproduction benchmark.

## Known Baseline

The charged-lepton Koide quantity is:

`Q = (m_e + m_mu + m_tau) / (sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau))^2`

The current canonical benchmark result is:

- `RESULT-0005` / `RUN-0004`

This repository treats that result as:

- charged-lepton scoped;
- dataset-backed and uncertainty-aware;
- reproduction evidence only, not explanation.

## Why It Matters

This is the first particle-mass benchmark slice in APL because:

- it uses explicit source-aware input data;
- it is numerically precise enough for an uncertainty-aware comparison;
- it is scientifically interesting while still requiring strong anti-numerology discipline.

## Linked Objects

- Hypothesis: `HYP-0004`
- Experiment: `EXP-0004`
- Claim: `CLAIM-0003`
- Task: `TASK-0037`
- Canonical result: `RESULT-0005`

## Open Questions

- How far does the charged-lepton benchmark remain meaningful under different uncertainty treatments?
- What is the right holdout framing for the historical tau benchmark?
- Which later particle-family comparisons remain scientifically disciplined rather than numerological?
