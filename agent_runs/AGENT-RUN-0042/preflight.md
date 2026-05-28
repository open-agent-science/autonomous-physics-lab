# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Data boundary: only committed snapshot rows are read.
- Baseline freeze: CK17 segments unchanged; no refit.
- Primary axis: true-mass/transit-radius compact, sub-Neptune, combined slices.
- Pilot anchor: TASK-0390 / AGENT-RUN-0036; reproduction tolerance recorded in thresholds.
- Controls: 5 matched cohorts, 1 per-class residual shift, 3 deterministic negative controls.
- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only committed snapshot rows are read. |
| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |
| pilot_reproduction | PASS | Eligible + per-slice counts and RMSE compared to AGENT-RUN-0036. |
| control_floor | PASS | Matched and negative controls reported with counts and gates. |
| promotion_boundary | PASS | Sandbox-only output. |
