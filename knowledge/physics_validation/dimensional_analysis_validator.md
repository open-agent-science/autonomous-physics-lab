---
id: KNOW-0004
title: Dimensional Analysis Validator
domain: physics_validation
topic: dimensional_analysis_validator
linked_objects:
  hypotheses:
    - HYP-0006
  experiments:
    - EXP-0006
  claims:
    - CLAIM-0005
  tasks:
    - TASK-0064
body: >
  Deterministic SI-dimension validator that classifies physics formulas as
  VALID, INVALID, SUSPICIOUS, or INCONCLUSIVE by computing dimension of LHS
  and RHS using a recursive AST evaluator and the SI base-unit symbol table.
---

# KNOW-0004: Dimensional Analysis Validator

> **Reference data warning:** This knowledge entry documents the APL
> dimensional-analysis validator engine. It describes the engine's capabilities
> and scope limits, not a scientific claim about any physical system.

---

## Summary

The dimensional-analysis validator (`physics_lab/engines/dimensions.py`) is a
deterministic quality-floor engine that checks whether a symbolic physics
formula is dimensionally consistent.

Given a formula like `F = m * a` and variable dimension declarations
`{F: "kg m s^-2", m: "kg", a: "m s^-2"}`, the validator:

1. Parses each dimension string into a SI base-dimension vector.
2. Evaluates the formula expression AST to compute the RHS dimension.
3. Compares LHS and RHS dimension vectors.
4. Returns: `VALID` (match), `INVALID` (mismatch), `SUSPICIOUS` (all
   variables dimensionless), or `INCONCLUSIVE` (unsupported syntax or unknown
   unit).

## MVP Benchmark Result

Benchmarked on DA-CHALLENGE-001 (50-item curated challenge set, TASK-0017):

- Agreement with curated labels: **49/50 (98%)**.
- Threshold target: 90%.
- Verdict: **VALID**.

## Scope Limits

- Cannot detect `KNOWN_LIMIT_FAIL` (numerical limit violations — physically
  valid dimension, wrong parameter range).
- Semantically-empty dimensionless formulas (DA-310 class: `r = (v/c)/(m/kg)`)
  pass as VALID; validator cannot infer lack of physical meaning from dimensions
  alone.
- Unit symbol table covers SI base units and common derived units; natural-unit
  and Gaussian-unit formulas are outside scope.
- Non-integer exponents require a dimensionless base; fractional exponents via
  `sqrt()` are supported.

## Re-verification Triggers

- When the challenge set (DA-CHALLENGE-001) is updated.
- When the unit symbol table is extended.
- When a new formula grammar feature is added to the engine.
