# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Data boundary: only committed snapshot rows are read; no live fetch.
- Baseline freeze: CK17 segments unchanged; no refit.
- Primary axis: true-mass/transit-radius rows only.
- Diagnostic axis: minimum-mass rows are excluded from headline metrics.
- Controls: per-class median, shuffled-label, and matched-size controls.
- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only committed snapshot rows are read. |
| baseline_freeze | PASS | CK17 frozen segments are reused without refit. |
| true_mass_axis | PASS | True-mass/transit-radius rows are primary. |
| control_floor | PASS | Three controls per executed hypothesis. |
| promotion_boundary | PASS | Sandbox-only output. |
