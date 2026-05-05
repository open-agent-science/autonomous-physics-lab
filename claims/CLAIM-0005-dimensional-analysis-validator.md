---
id: CLAIM-0005
title: Dimensional Analysis Validator Correctly Classifies Physics Formulas
domain: physics_validation
status: DRAFT
hypothesis_id: HYP-0006
evidence:
  experiments:
    - EXP-0006
  results:
    - RESULT-0007
scope: >
  Restricted to the 50-item DA-CHALLENGE-001 curated challenge set
  (TASK-0017). No generalization to unseen formulas or physics domains is
  claimed.
---

# CLAIM-0005: Dimensional Analysis Validator Correctly Classifies Physics Formulas

## Statement

The APL dimensional-analysis validator achieves ≥90% agreement with curated
expected labels on the 50-item DA-CHALLENGE-001 challenge set. The achieved
agreement is 98% (49/50 items).

## Evidence Status

`EXP-0006` produced `RESULT-0007`. The validator is benchmarked at 98%
agreement against curated labels. This claim remains `DRAFT` until a human
reviewer explicitly accepts the scope and evidence chain.

## Review Recommendation

Keep `DRAFT`. The result is strong (98%), but:

- The challenge set is curated internally (TASK-0017); independent external
  validation has not been performed.
- One documented scope limit (DA-310 class: semantically-empty dimensionless
  formulas) means 100% agreement is not achievable by dimension-only check.
- A formal claim about "catching invalid physics formulas" requires broader
  domain coverage beyond the 50-item benchmark.

## Caution

This claim does not assert that the validator is complete or sound for arbitrary
physics formulas. It is a quality-floor engine scoped to the challenge set.
Do not cite this result as evidence of general formula-checking capability.
