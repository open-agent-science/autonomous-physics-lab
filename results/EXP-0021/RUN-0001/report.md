# RESULT-0027: Exoplanet null-baseline control sensitivity

This Gate-B-replayable negative/control result packages committed EXO-0001 evidence.
It does not rerun residual scoring or establish a positive mass-radius law.

## Diagnostic nearest-radius control

| Slice | Rows | CK17 RMSE | Nearest-radius null RMSE | Classification |
| --- | ---: | ---: | ---: | --- |
| `compact_radius_lt1p5Re` | 92 | 0.263350 | 0.019905 | `null_family_matches_or_beats_ck17` |
| `sub_neptune_radius_1p5_4Re` | 340 | 0.204175 | 0.000858 | `null_family_matches_or_beats_ck17` |
| `jovian_radius_8_16Re` | 567 | 0.083354 | 0.000432 | `null_family_matches_or_beats_ck17` |
| `hot_jupiter_period_lt10d_radius_ge8Re` | 445 | 0.069788 | 0.000349 | `null_family_matches_or_beats_ck17` |

The nearest-radius control uses observed radius and is not a deployable predictor.

## Fair-null comparators

| Slice | CK17 RMSE | Nearest-mass fair null RMSE | Per-class-median fair null RMSE | Fair-null note |
| --- | ---: | ---: | ---: | --- |
| `compact_radius_lt1p5Re` | 0.263350 | 0.283224 | 0.316492 | both trail CK17 |
| `sub_neptune_radius_1p5_4Re` | 0.204175 | 0.237837 | 0.173173 | at least one fair null matches or beats CK17 |
| `jovian_radius_8_16Re` | 0.083354 | 0.158724 | 0.263262 | both trail CK17 |
| `hot_jupiter_period_lt10d_radius_ge8Re` | 0.069788 | 0.153819 | 0.257985 | both trail CK17 |

The fair-null rows make the comparison surface explicit: nearest-mass and per-class-median controls trail the frozen CK17 baseline in three of four highlighted true-mass slices. This transparency addition does not change the packaged metrics, result verdict, or monitor-only campaign posture.

## Routing

All four highlighted true-mass slices retain `null_family_matches_or_beats_ck17`.
Minimum-mass slices remain underpowered and are not pooled with true-mass rows.
The artifact is replayable through `physics-lab run examples/exoplanet_null_baseline_result.yaml`.
