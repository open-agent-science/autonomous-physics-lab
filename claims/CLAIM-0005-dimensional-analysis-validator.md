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
    - RESULT-0020
scope: >
  Restricted to two curated challenge sets: the 50-item DA-CHALLENGE-001
  set (TASK-0017) and the frozen 74-item frozen_live_74 snapshot
  (RESULT-0020). No generalization to unseen formulas or physics domains
  is claimed.
---

# CLAIM-0005: Dimensional Analysis Validator Correctly Classifies Physics Formulas

## Statement

The APL dimensional-analysis validator achieves ≥90% agreement with curated
expected labels on the 50-item DA-CHALLENGE-001 challenge set. The achieved
agreement is 98% (49/50 items).

On the larger frozen 74-item `frozen_live_74` challenge set the validator
achieves 100% agreement (74/74 items, threshold 90%, zero-disagreement
ledger) — `RESULT-0020`, deterministic replay of
`examples/dimensional_analysis_live_74.yaml`.

## Evidence Status

`EXP-0006` produced `RESULT-0007` (50 items, 98%) and `RESULT-0020`
(74 items, 100%). `RESULT-0020` is `AGENT_VALIDATED` with
`validation_independence: independent`: the Gate B replay was performed by
akutenyov (Codex, 2026-07-07) — a different human from both the original
publisher (romanhladun24-dot) and the packaging-fix author (gladunrv) —
with zero drift across 17 metrics at tolerance 1e-9. This claim remains
`DRAFT` until the maintainer explicitly accepts the scope and evidence
chain at Gate C.

## Review Recommendation

Keep `DRAFT` until Gate C. The evidence is strong (98% on 50 items, 100%
on 74 items), and the promotion protocol's independence requirement is now
satisfied: `RESULT-0020` carries an independently validated Gate B replay
(different human, zero drift), so Gate C promotion has the required basis
available. Honest residual limits:

- Both challenge sets are curated internally; the labels themselves have no
  external validation (the independent replay validates reproduction, not
  label ground truth).
- One documented scope limit (DA-310 class: semantically-empty dimensionless
  formulas) means dimension-only checking has a known ceiling on the 50-item
  set.
- A formal claim about "catching invalid physics formulas" in general would
  require broader domain coverage beyond these two benchmarks.

## Caution

This claim does not assert that the validator is complete or sound for arbitrary
physics formulas. It is a quality-floor engine scoped to the challenge set.
Do not cite this result as evidence of general formula-checking capability.
