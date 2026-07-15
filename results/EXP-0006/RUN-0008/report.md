# Dimensional Analysis Validator - Run Report

**Run:** RUN-0008  **Experiment:** EXP-0006  **Verdict:** VALID
**Scope:** `frozen_v2_calibration_80`

## Summary

| Metric | Value |
|---|---|
| Total items | 80 |
| Scoring contract | `label_blind_exact_v2` |
| Primary metric | `exact_agreement_fraction` |
| Primary agreement | 80/80 (100.0%) |
| Exact categorical agreement | 80/80 (100.0%) |
| Policy-adjusted agreement | 80/80 (100.0%) |
| VALID computed | 40 |
| INVALID computed | 40 |
| SUSPICIOUS computed | 0 |
| INCONCLUSIVE | 0 |
| Remaining primary disagreements | 0 |
| Agreement threshold | 90% |
| Calibration threshold outcome | **PASS** |
| Best verdict | **VALID** |

## Disagreements

| ID | Expected | Computed | Detail |
|---|---|---|---|
| none | - | - | No exact-label disagreements. |

The machine-readable `metrics.json` contains all 80 item
outcomes plus the complete disagreement ledger above.

## Class Breakdown

| Expected class | Support | Computed count | Exact correct | Recall |
|---|---:|---:|---:|---:|
| VALID | 40 | 40 | 40 | 100.0% |
| INVALID | 40 | 40 | 40 | 100.0% |
| INCONCLUSIVE | 0 | 0 | 0 | n/a |

## Domain Breakdown

| Domain | Total | Exact | Agreement | Expected | Computed | Disagreements |
|---|---:|---:|---:|---|---|---|
| astrophysics | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| electromagnetism | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| fluid_mechanics | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| nuclear_and_particle | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| quantum_and_atomic | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| rotational_mechanics | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| thermodynamics | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |
| waves_and_optics | 10 | 10 | 100.0% | INVALID:5, VALID:5 | INVALID:5, VALID:5 | none |

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
- This is same-owner, role-disjoint calibration evidence under `CALIBRATION_ONLY_ROLE_LIMIT`; it is not confirmatory evidence and cannot support Gate C or reopen CLAIM-0005.
- Expected labels were used only for the frozen digest preflight and the post-inference scoring phase; inference received only item id, formula, and declared variable dimensions.

## Claim Ceiling

The validator achieves 100.0% on its declared primary metric
(`exact_agreement_fraction`) for the frozen 80-item
`frozen_v2_calibration_80` benchmark scope. Exact and policy-adjusted metrics
are reported separately. This score is a bounded SI-focused validator
quality floor, not semantic or universal physical correctness. No claim
about unseen formulas, numerical correctness, empirical validity, or
physics domains outside the benchmark scope is made.
