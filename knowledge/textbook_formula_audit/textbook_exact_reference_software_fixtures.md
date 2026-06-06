---
id: KNOW-0010
title: Textbook Exact-Reference Software Fixtures
domain: textbook_formula_audit
topic: deterministic software/convention validation over synthetic exact-reference fixtures
linked_objects:
  hypotheses:
    - HYP-0013
  experiments:
    - EXP-0013
  claims:
    - CLAIM-0011
  tasks:
    - TASK-0634
---

# Textbook Exact-Reference Software Fixtures

## Topic

Textbook Formula Audit, deterministic software/convention validation over
committed synthetic exact-reference fixtures (no empirical data).

## What Is Validated

The committed fixtures verify APL plumbing only:

- Stefan-Boltzmann SI arithmetic against synthetic spherical-emitter rows using
  the declared CODATA 2022 constant convention;
- Wien wavelength-domain arithmetic against synthetic Kelvin rows using the
  declared CODATA 2022 displacement constant convention;
- dimensional consistency, `T^4` and `R^2` scaling, monotonicity, and declared
  convention negative controls.

`RESULT-0019` records the Stefan-Boltzmann run with max exact-reference relative
error `0.0` under a `1e-12` tolerance and all gates passing; the Wien fixture is
test-backed supporting evidence.

## Why It Matters

This entry gives the Textbook Formula Audit campaign a reusable software/units
baseline before any empirical audit:

- the fixtures are synthetic and pinned, so the gates are reproducible;
- the constant conventions are frozen and explicit;
- the negative controls make convention regressions visible;
- a later empirical audit can reuse the same gate plumbing without inheriting an
  empirical claim from this entry.

## Boundary

This knowledge entry is about software and convention behavior only. It does not
assert empirical truth or falsification of Stefan-Boltzmann, Wien displacement,
blackbody physics, stellar observations, or any textbook formula, and it implies
no universal-law statement.

## Linked Objects

- Hypothesis: `HYP-0013`
- Experiment: `EXP-0013`
- Claim: `CLAIM-0011`
- Task: `TASK-0634`
- Canonical result: `RESULT-0019`
