# Nuclear Prediction Variant Slate Ranking Report

**Factory:** `nuclear-prediction-factory-slate-002-feature-terms`
**Task:** `TASK-0264`
**Candidates:** 48
**Generated at:** 2026-05-16T20:57:50Z

> This report is a deterministic review aid. It does not assign scientific success scores and does not compare candidates against future or holdout measurements.

## Coverage Summary

**Target batches (4):** `mid-mass-region-probe`, `neutron-rich-stress`, `nickel-isotope-chain`, `shell-magic-probe`

**Candidates per target batch:**

- `mid-mass-region-probe`: 12
- `neutron-rich-stress`: 12
- `nickel-isotope-chain`: 12
- `shell-magic-probe`: 12

**Model family prefixes (1):** `RESULT-0015`

## Duplicate Analysis

No duplicate prediction IDs detected.

No near-duplicate value vectors detected (threshold 0.0001 MeV).

## Delta Sensitivity Table

Candidates sorted by largest absolute delta from baseline (MeV). Large deltas are not evidence of predictive value; they indicate coefficient sensitivity and should be reviewed for plausibility.

| variant_id | target_batch | max_abs_delta_mev | mean_abs_delta_mev | nuclide_count |
|-----------|-------------|------------------|--------------------|--------------|
| `asymmetry-quartic-only-minus-neutron-rich` | `neutron-rich-stress` | 64.182491 | 37.402622 | 4 |
| `asymmetry-quartic-only-plus-neutron-rich` | `neutron-rich-stress` | 64.182491 | 37.402622 | 4 |
| `asymmetry-quartic-plus-coefficient-scale-neutron-rich` | `neutron-rich-stress` | 49.359720 | 26.721454 | 4 |
| `asymmetry-quartic-reviewed-neutron-rich` | `neutron-rich-stress` | 48.476174 | 25.795785 | 4 |
| `asymmetry-quartic-sign-inverted-neutron-rich` | `neutron-rich-stress` | 48.476174 | 25.795785 | 4 |
| `asymmetry-quadratic-plus-neutron-rich` | `neutron-rich-stress` | 15.706317 | 11.606837 | 4 |
| `asymmetry-quadratic-minus-neutron-rich` | `neutron-rich-stress` | 15.706317 | 11.606837 | 4 |
| `asymmetric-neutron-excess-cubic-plus-neutron-rich` | `neutron-rich-stress` | 4.860000 | 3.428579 | 4 |
| `asymmetric-neutron-excess-cubic-minus-neutron-rich` | `neutron-rich-stress` | 4.860000 | 3.428579 | 4 |
| `shell-zn-reviewed-coefficients-shell-magic` | `shell-magic-probe` | 3.207681 | 2.258996 | 4 |
| `shell-zn-sign-inverted-shell-magic` | `shell-magic-probe` | 3.207681 | 2.258996 | 4 |
| `shell-z-plus-coulomb-scale-mid-mass` | `mid-mass-region-probe` | 3.182662 | 1.654094 | 4 |
| `shell-n-plus-surface-scale-mid-mass` | `mid-mass-region-probe` | 2.330755 | 2.010451 | 4 |
| `asymmetry-quadratic-plus-nickel-chain` | `nickel-isotope-chain` | 2.010708 | 1.696702 | 4 |
| `asymmetry-quadratic-minus-nickel-chain` | `nickel-isotope-chain` | 2.010708 | 1.696702 | 4 |
| `shell-plus-neutron-excess-nickel-chain` | `nickel-isotope-chain` | 1.915164 | 1.278642 | 4 |
| `shell-minus-neutron-excess-nickel-chain` | `nickel-isotope-chain` | 1.915164 | 1.278642 | 4 |
| `asymmetry-quadratic-plus-mid-mass` | `mid-mass-region-probe` | 1.632653 | 1.173327 | 4 |
| `asymmetry-quadratic-minus-mid-mass` | `mid-mass-region-probe` | 1.632653 | 1.173327 | 4 |
| `shell-n-reviewed-coefficient-shell-magic` | `shell-magic-probe` | 1.604907 | 1.447037 | 4 |
| `shell-n-sign-inverted-shell-magic` | `shell-magic-probe` | 1.604907 | 1.447037 | 4 |
| `shell-n-narrow-sigma-shell-magic` | `shell-magic-probe` | 1.604907 | 1.257981 | 4 |
| `shell-n-broad-sigma-shell-magic` | `shell-magic-probe` | 1.604907 | 1.557762 | 4 |
| `shell-n-reviewed-nickel-chain` | `nickel-isotope-chain` | 1.604907 | 0.942240 | 4 |
| `shell-n-sign-inverted-nickel-chain` | `nickel-isotope-chain` | 1.604907 | 0.942240 | 4 |
| `shell-z-magic-reviewed-nickel-chain` | `nickel-isotope-chain` | 1.559985 | 1.559985 | 4 |
| `shell-z-magic-sign-inverted-nickel-chain` | `nickel-isotope-chain` | 1.559985 | 1.559985 | 4 |
| `shell-z-reviewed-mid-mass` | `mid-mass-region-probe` | 1.559985 | 0.390130 | 4 |
| `shell-z-sign-inverted-mid-mass` | `mid-mass-region-probe` | 1.559985 | 0.390130 | 4 |
| `shell-z-reviewed-coefficient-shell-magic` | `shell-magic-probe` | 1.376682 | 0.633626 | 4 |
| `shell-z-sign-inverted-shell-magic` | `shell-magic-probe` | 1.376682 | 0.633626 | 4 |
| `shell-n-plus-asymmetry-scale-shell-magic` | `shell-magic-probe` | 1.333167 | 0.818098 | 4 |
| `shell-n-minus-asymmetry-scale-shell-magic` | `shell-magic-probe` | 1.333167 | 0.818098 | 4 |
| `asymmetry-damped-quartic-mid-mass` | `mid-mass-region-probe` | 1.249922 | 1.123531 | 4 |
| `asymmetry-damped-quartic-sign-inverted-mid-mass` | `mid-mass-region-probe` | 1.249922 | 1.123531 | 4 |
| `asymmetric-neutron-excess-plus-neutron-rich` | `neutron-rich-stress` | 0.900000 | 0.776354 | 4 |
| `asymmetric-neutron-excess-minus-neutron-rich` | `neutron-rich-stress` | 0.900000 | 0.776354 | 4 |
| `shell-n-plus-asymmetry-scale-nickel-chain` | `nickel-isotope-chain` | 0.865052 | 0.522907 | 4 |
| `asymmetric-neutron-excess-plus-nickel-chain` | `nickel-isotope-chain` | 0.824390 | 0.672805 | 4 |
| `asymmetric-neutron-excess-minus-nickel-chain` | `nickel-isotope-chain` | 0.824390 | 0.672805 | 4 |
| `asymmetric-neutron-excess-plus-mid-mass` | `mid-mass-region-probe` | 0.571429 | 0.340490 | 4 |
| `asymmetric-neutron-excess-minus-mid-mass` | `mid-mass-region-probe` | 0.571429 | 0.340490 | 4 |
| `shell-zn-small-balanced-shell-magic` | `shell-magic-probe` | 0.249916 | 0.123864 | 4 |
| `shell-n-reviewed-mid-mass` | `mid-mass-region-probe` | 0.000538 | 0.000136 | 4 |
| `shell-n-sign-inverted-mid-mass` | `mid-mass-region-probe` | 0.000538 | 0.000136 | 4 |
| `shell-zn-near-null-shell-magic` | `shell-magic-probe` | 0.000000 | 0.000000 | 4 |
| `asymmetric-neutron-excess-near-null-neutron-rich` | `neutron-rich-stress` | 0.000000 | 0.000000 | 4 |
| `asymmetric-neutron-excess-near-null-nickel-chain` | `nickel-isotope-chain` | 0.000000 | 0.000000 | 4 |

## Heuristic Flags

**Total flags: 14**

- `[ALL_ZERO_DELTA]` `shell-zn-near-null-shell-magic`: All delta_from_baseline_mev values are 0.0. The coefficient transform may have had no effect on this target batch (e.g., pairing-only transform on odd-A targets only).
- `[EXTREME_SENSITIVITY]` `asymmetry-quartic-reviewed-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 48.476 MeV). Review coefficient transform plausibility.
- `[EXTREME_SENSITIVITY]` `asymmetry-quartic-sign-inverted-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 48.476 MeV). Review coefficient transform plausibility.
- `[EXTREME_SENSITIVITY]` `asymmetry-quadratic-plus-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 15.706 MeV). Review coefficient transform plausibility.
- `[EXTREME_SENSITIVITY]` `asymmetry-quadratic-minus-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 15.706 MeV). Review coefficient transform plausibility.
- `[EXTREME_SENSITIVITY]` `asymmetry-quartic-only-minus-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 64.182 MeV). Review coefficient transform plausibility.
- `[EXTREME_SENSITIVITY]` `asymmetry-quartic-only-plus-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 64.182 MeV). Review coefficient transform plausibility.
- `[ALL_ZERO_DELTA]` `asymmetric-neutron-excess-near-null-neutron-rich`: All delta_from_baseline_mev values are 0.0. The coefficient transform may have had no effect on this target batch (e.g., pairing-only transform on odd-A targets only).
- `[EXTREME_SENSITIVITY]` `asymmetry-quartic-plus-coefficient-scale-neutron-rich`: 4 target(s) exceed ±5.0 MeV delta (max observed: 49.360 MeV). Review coefficient transform plausibility.
- `[ALL_ZERO_DELTA]` `asymmetric-neutron-excess-near-null-nickel-chain`: All delta_from_baseline_mev values are 0.0. The coefficient transform may have had no effect on this target batch (e.g., pairing-only transform on odd-A targets only).
- `[REDUNDANT_TARGET_BATCH]` `<batch:shell-magic-probe>`: Target batch 'shell-magic-probe' is used by 12 candidates. Consider whether target diversity is sufficient.
- `[REDUNDANT_TARGET_BATCH]` `<batch:neutron-rich-stress>`: Target batch 'neutron-rich-stress' is used by 12 candidates. Consider whether target diversity is sufficient.
- `[REDUNDANT_TARGET_BATCH]` `<batch:nickel-isotope-chain>`: Target batch 'nickel-isotope-chain' is used by 12 candidates. Consider whether target diversity is sufficient.
- `[REDUNDANT_TARGET_BATCH]` `<batch:mid-mass-region-probe>`: Target batch 'mid-mass-region-probe' is used by 12 candidates. Consider whether target diversity is sufficient.

---

*This report was generated by `scripts/rank_nuclear_prediction_variant_slate.py`. No scientific claim is made or implied by this ranking output.*
