# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Data boundary: only committed snapshot rows are read.
- Baseline freeze: CK17 segments unchanged; no refit.
- Partition predeclaration: quartile (primary) and half (fallback) rules declared before metrics.
- Source-slice anchor: CSN-001 from AGENT-RUN-0042; reproduction tolerance recorded in thresholds.
- Controls: per-class residual shift, nearest-radius and nearest-mass outside-compact cohorts, seeded random outside-compact.
- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only committed snapshot rows are read. |
| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |
| bins_predeclared | PASS | Partition rules declared before metrics. |
| compact_slice_reproduction | PASS | Compact-slice count and RMSE compared to CSN-001 anchor. |
| promotion_boundary | PASS | Sandbox-only output. |
