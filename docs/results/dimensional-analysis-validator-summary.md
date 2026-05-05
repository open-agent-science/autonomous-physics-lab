# Dimensional Analysis Validator MVP — Result Summary

**Experiment:** EXP-0006
**Run:** RUN-0006
**Result:** RESULT-0007
**Task:** TASK-0064
**Verdict:** VALID

---

## What Was Done

We implemented and benchmarked a deterministic SI-dimension validator
(`physics_lab/engines/dimensions.py`) against the 50-item curated challenge
set DA-CHALLENGE-001 (TASK-0017).

The validator:

1. Parses variable dimension annotations (e.g. `"kg m s^-2"`) into base-SI
   dimension vectors.
2. Walks the formula AST (e.g. `F = m * a`) recursively, computing the
   dimension of the right-hand side.
3. Compares LHS and RHS dimensions and assigns a verdict: `VALID`, `INVALID`,
   `SUSPICIOUS`, or `INCONCLUSIVE`.

No external API calls, no symbolic algebra system, no fitting — just
deterministic dimension arithmetic.

## Result

| Metric | Value |
|---|---|
| Challenge set items | 50 |
| Agreement with curated labels | **49/50 (98%)** |
| Target threshold | 90% |
| VALID computed | 21 |
| INVALID computed | 29 |
| INCONCLUSIVE | 0 |
| Verdict | **VALID** |

## One Documented Scope Limit

**DA-310 class** — semantically-empty dimensionless formulas such as
`r = (v/c)/(m/kg)` where `kg` is used as a free variable. This formula is
dimensionally consistent (both sides are dimensionless) but physically
meaningless. The dimension-only validator correctly says `VALID` and cannot
detect the semantic issue. This class of formulas is documented as outside
MVP scope.

All other items — including all 10 VALID formulas, all 15 invalid-unit
formulas, all 10 missing-constants formulas, and all 5 known-limit formulas
— are classified correctly.

## What This Does Not Claim

- The validator is not proven correct on formulas outside the challenge set.
- A 98% agreement does not mean the engine will catch every invalid formula
  in the wild.
- No claim about any physical system is made; this is a software benchmark
  against a curated dataset.

## Claim Status

CLAIM-0005 is drafted `DRAFT`. It will not be promoted automatically.
A human reviewer must explicitly accept the scope and evidence chain before
any status change.

## Full Artifacts

- Result: `results/EXP-0006/RUN-0006/result.yaml`
- Report: `results/EXP-0006/RUN-0006/report.md`
- Metrics: `results/EXP-0006/RUN-0006/metrics.json`
- Knowledge: `knowledge/physics_validation/dimensional_analysis_validator.md`
- Claim: `claims/CLAIM-0005-dimensional-analysis-validator.md`
