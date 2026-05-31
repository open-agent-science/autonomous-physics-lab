# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Data boundary: only committed snapshot fields are read.
- Model boundary: no correction model and no CK17 baseline refit.
- Scope: true-mass rows with transit radii; compact radius R/Re < 1.5.
- Promotion boundary: sandbox-only; no canonical result, prediction, claim, or knowledge output.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only committed snapshot fields are read. |
| no_live_fetch | PASS | No external source refresh is performed. |
| no_correction_model | PASS | The runner reports coverage only. |
| compact_slice_present | PASS | 92 compact rows are available. |
| promotion_boundary | PASS | Sandbox-only output. |
