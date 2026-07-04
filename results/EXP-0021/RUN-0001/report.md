# RESULT-0027: Exoplanet null-baseline control sensitivity

This agent-published negative/control result packages committed EXO-0001 evidence.
It does not rerun residual scoring or establish a positive mass-radius law.

| Slice | Rows | CK17 RMSE | Nearest-radius null RMSE | Classification |
| --- | ---: | ---: | ---: | --- |
| `compact_radius_lt1p5Re` | 92 | 0.263350 | 0.019905 | `null_family_matches_or_beats_ck17` |
| `sub_neptune_radius_1p5_4Re` | 340 | 0.204175 | 0.000858 | `null_family_matches_or_beats_ck17` |
| `jovian_radius_8_16Re` | 567 | 0.083354 | 0.000432 | `null_family_matches_or_beats_ck17` |
| `hot_jupiter_period_lt10d_radius_ge8Re` | 445 | 0.069788 | 0.000349 | `null_family_matches_or_beats_ck17` |

All four highlighted true-mass slices retain `null_family_matches_or_beats_ck17`.
Minimum-mass slices remain underpowered and are not pooled with true-mass rows.
The nearest-radius control uses observed radius and is not a deployable predictor.
