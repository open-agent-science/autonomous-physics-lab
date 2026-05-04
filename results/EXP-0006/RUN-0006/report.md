# Dimensional Analysis Validator MVP — Run Report

**Run:** RUN-0006  **Experiment:** EXP-0006  **Verdict:** VALID

## Summary

| Metric | Value |
|---|---|
| Total items | 50 |
| Agreement | 49/50 (98.0%) |
| VALID computed | 21 |
| INVALID computed | 29 |
| INCONCLUSIVE | 0 |
| Agreement threshold | 90% |
| Best verdict | **VALID** |

## Disagreements

| ID | Expected | Computed | Detail |
|---|---|---|---|
| DA-310 | SUSPICIOUS | VALID | LHS = RHS = 1 |

## Limitations

- MVP scope: dimension-only check. Cannot detect KNOWN_LIMIT_FAIL
  (numerical limit violations) or semantically-empty dimensionless
  formulas (DA-310 class).
- SUSPICIOUS items with explicit dimensional mismatch are classified
  INVALID; this is stricter but operationally correct (formula is flagged).
- Unit symbol table is limited to SI base units and common derived units.
  Natural-unit or Gaussian-unit formulas are outside scope.

## Claim Ceiling

The validator achieves 98.0% agreement on the 50-item
DA-CHALLENGE-001 set. No claim about unseen formulas or physics
domains outside the challenge set is made.
