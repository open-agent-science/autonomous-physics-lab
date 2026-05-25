# Exoplanet Mass-Radius Baseline Summary

**Status:** public-alpha summary draft  
**Evidence class:** sandbox-only benchmark summary  
**Input review:** `docs/reviews/exoplanet-mass-radius-baseline-benchmark.md`  
**Failure map:** `docs/reviews/exoplanet-mass-radius-residual-failure-map.md`  
**Verdict:** `INCONCLUSIVE`

The first Exoplanet Mass-Radius benchmark compares a frozen Chen-Kipping
2017-style mass-radius baseline with a per-class median null baseline on the
committed NASA Exoplanet Archive PSCompPars snapshot. It is a benchmark and
failure-map surface, not a claim that APL found a new planet law.

## Snapshot Boundary

| item | value |
| --- | ---: |
| Snapshot rows | 6291 |
| Post-filter included rows | 4301 |
| True-mass/transit-radius benchmark rows | 1207 |
| Minimum-mass/transit-radius benchmark rows | 2 |

Rows with true mass and transit radius are evaluated separately from `M sin i`
minimum-mass rows. Radius-only and model-inferred rows are not folded into a
single success metric.

## Main Outcome

| axis | CK log10 RMSE | null log10 RMSE | reading |
| --- | ---: | ---: | --- |
| True mass with transit radius | 0.158170 | 0.242713 | CK clears the null floor on this axis. |
| Minimum mass with transit radius | 0.207728 | 0.031917 | Not interpretable as success; count and `M sin i` semantics block it. |

The summary verdict remains `INCONCLUSIVE` because the supported true-mass
axis and the blocked minimum-mass axis point in different directions.

## Failure Regions

| surface | count | CK log10 RMSE | reading |
| --- | ---: | ---: | --- |
| Compact radii `<1.5 R_earth` | 92 | 0.263350 | Strongest supported failure region. |
| Sub-Neptune radii `1.5-4 R_earth` | 340 | 0.204175 | Supported transition-region failure surface. |
| Neptunian mass class | 588 | 0.182790 | Largest class-level true-mass RMSE. |
| Giant radii `>=8 R_earth` | 678 | 0.091450 | Comparatively stable region. |

These patterns are residual diagnostics. They do not imply habitability,
composition, biosignature, or target-priority conclusions.

## Conservative Reading

- The true-mass axis is now a useful benchmark surface for follow-up audits.
- The minimum-mass axis should remain separated and sample-size blocked.
- Catalog selection effects are visible: host-star and uncertainty splits do
  not support simple broad wording.
- Future work should audit true-mass residual slices before proposing a tuned
  replacement baseline.

No prediction registry entry, canonical `RESULT-*`, claim, or knowledge update
is created by this summary.
