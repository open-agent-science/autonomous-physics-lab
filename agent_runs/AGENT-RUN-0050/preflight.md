# Preflight

- Snapshot: `data\exoplanets\exo-0001-pscomppars-snapshot.yaml`
- Data boundary: committed snapshot only; no live fetch.
- Baseline freeze: CK17 metadata reused without refit.
- Null family: four deterministic null baselines.
- Axis boundary: true-mass and minimum-mass rows reported separately.
- Promotion boundary: no RESULT, PRED, claim, knowledge, composition, habitability, biosignature, or target-priority output.

## Checks

| check | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only the committed snapshot is read. |
| baseline_freeze | PASS | CK17 segments are unchanged and not refit. |
| null_family | PASS | Per-class, nearest-mass, nearest-radius, and uncertainty-band controls are reported. |
| axis_separation | PASS | True-mass and minimum-mass rows remain separate. |
| slice_coverage | PASS | Compact, sub-Neptune, Jovian-radius, and hot-Jupiter slices are reported when rows are available. |
| promotion_boundary | PASS | No canonical scientific-memory promotion is written. |
