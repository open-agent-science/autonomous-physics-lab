# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Data boundary: only committed snapshot is read; no live NASA Exoplanet Archive fetch.
- Baseline freeze: CK17 segments unchanged; no per-regime or per-row refit.
- Control floor: per-class median, shuffled-regime, and sample-size-matched neighbor controls evaluated on every executed regime.
- Minimum-slice gate: regimes below the minimum row count are flagged and excluded from the verdict.
- Promotion boundary: no canonical result, PRED, claim, knowledge, or habitability / biosignature / target-prioritization output.
- Task scope: TASK-0370 requests bounded regime hypotheses, not reveal scoring.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only the committed snapshot is read. |
| baseline_freeze | PASS | CK17 segments unchanged. |
| control_floor | PASS | Three controls per executed regime. |
| minimum_slice_gate | PASS | Regimes < min_row_count flagged and excluded from verdict. |
| promotion_boundary | PASS | No PRED, RESULT, claim, knowledge, or habitability output. |
| task_scope | PASS | TASK-0370 requests bounded regime hypotheses, not reveal scoring. |
