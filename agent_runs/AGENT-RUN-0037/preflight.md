# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Data boundary: only committed snapshot rows are read.
- Baseline freeze: CK17 segments unchanged; no refit.
- Primary axis: true-mass/transit-radius neptunian rows.
- Controls: per-class median, nearest-radius, host-temperature, and uncertainty-band controls.
- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only committed snapshot rows are read. |
| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |
| control_floor | PASS | Required controls are reported with counts and gates. |
| promotion_boundary | PASS | Sandbox-only output. |
