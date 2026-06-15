# Dimensional Analysis Validator - Run Report

**Run:** RUN-0007  **Experiment:** EXP-0006  **Verdict:** VALID
**Scope:** `frozen_live_74`
**Result:** `RESULT-0020`  **Review tier:** `AGENT_PUBLISHED`

## Summary

| Metric | Value |
|---|---|
| Total items | 74 |
| Agreement | 74/74 (100.0%) |
| VALID computed | 37 |
| INVALID computed | 35 |
| SUSPICIOUS computed | 2 |
| INCONCLUSIVE | 0 |
| Remaining disagreements | 0 |
| Agreement threshold | 90% |
| Best verdict | **VALID** |

## Disagreements

| ID | Expected | Computed | Detail |
|---|---|---|---|
_None_

## Limitations

- Dimension-only checks do not establish numerical correctness,
  empirical validity, or physical truth.
- KNOWN_LIMIT_FAIL rows are expected to be dimensionally balanced;
  their numerical or regime failures remain outside validator scope.
- Curated dimensionally balanced SUSPICIOUS rows require explicit
  metadata because dimensions alone cannot infer missing dimensionless
  factors or semantic emptiness.
- SUSPICIOUS items with explicit dimensional mismatch are classified
  INVALID; this is stricter but operationally correct (formula is flagged).
- Unit symbol table is limited to SI base units and common derived units.
  Natural-unit or Gaussian-unit formulas are outside scope.

## Claim Ceiling

The validator achieves 100.0% agreement on the frozen
74-item `frozen_live_74` benchmark scope. No claim
about unseen formulas, numerical correctness, empirical validity,
or physics domains outside the benchmark scope is made.

## Output Routing

- Task verdict: `VALID` for deterministic agreement with the curated benchmark.
- Canonical destination: `results/EXP-0006/RUN-0007/result.yaml`.
- Review tier: `AGENT_PUBLISHED`; not independently validated or maintainer-reviewed.
- Gate A: pass after the repository publication checker.
- Gate B: not attempted.
- Hypothesis impact: evidence reference added to `HYP-0006`; its status and
  verdict remain unchanged.
- Claim impact: no change to `CLAIM-0005`.
- Knowledge impact: no knowledge entry or endorsement.
- Publication blocker: none for agent-published evidence; higher trust tiers still
  require independent replay or maintainer review.
