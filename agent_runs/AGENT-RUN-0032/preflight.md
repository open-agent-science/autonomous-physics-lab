# Preflight

- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Loader policy: committed loader and quality-filter chain applied; no live NASA Exoplanet Archive fetch performed.
- Baseline policy: frozen Chen-Kipping 2017 piecewise relation; no segment was refit on the snapshot.
- Null baseline: per-CK17-class median log10(radius) on the same eligible rows.
- Promotion boundary: no canonical result, prediction registry entry, claim update, knowledge file edit, or habitability/biosignature/target-prioritization output is produced.

## Checks

| name | status | notes |
| --- | --- | --- |
| data_boundary | PASS | Only the committed snapshot is read; no live fetch. |
| baseline_freeze | PASS | CK17 segments are frozen from the published reference. |
| null_floor | PASS | Per-class median null baseline is computed and reported on both axes. |
| promotion_boundary | PASS | No canonical result, PRED, claim, knowledge, or habitability output is written. |
| task_scope | PASS | TASK-0361 requests a benchmark on the pinned snapshot, not reveal scoring. |
