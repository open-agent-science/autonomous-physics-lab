# AGENT-RUN-0034 - Exoplanet True-Mass Residual Slice Audit

**Task:** `TASK-0369`
**Snapshot:** `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
**Baseline input:** `AGENT-RUN-0032`
**Axis:** `true_mass_with_transit_radius`
**Verdict:** `INCONCLUSIVE`

## Boundary

This run audits the true-mass residual axis from the frozen TASK-0361
Chen-Kipping benchmark. It does not fetch live archive data, refit the
baseline, tune a replacement model, score minimum-mass rows as headline
evidence, create a canonical result, or promote claims.

## Overall Axis

| count | CK log10 MAE | CK log10 RMSE | CK bias | null log10 RMSE | delta null - CK |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1207 | 0.104430 | 0.158170 | -0.040844 | 0.242713 | +0.084543 |

The true-mass axis clears the per-class median null floor overall. The
campaign-level verdict remains `INCONCLUSIVE` because the minimum-mass axis is
sparse and loses to the null.

## Slice Summary

| slice | label | count | CK log10 RMSE | CK bias | classification |
| --- | --- | ---: | ---: | ---: | --- |
| planet class | terran | 39 | 0.124740 | -0.018562 | weak count-limited |
| planet class | neptunian | 588 | 0.182790 | -0.064723 | robust failure region |
| planet class | jovian | 580 | 0.130933 | -0.018134 | comparatively stable |
| radius regime | compact `<1.5 R_earth` | 92 | 0.263350 | -0.146837 | robust failure region |
| radius regime | sub-Neptune `1.5-4 R_earth` | 340 | 0.204175 | -0.100080 | robust failure region |
| radius regime | intermediate `4-8 R_earth` | 97 | 0.202360 | -0.028622 | weak supported |
| radius regime | giant `>=8 R_earth` | 678 | 0.091450 | +0.001496 | comparatively stable |
| detection method | transit | 1205 | 0.158272 | -0.040788 | dominant supported surface |
| detection method | transit timing variation | 2 | 0.074741 | -0.074548 | sample-size blocked |

## Host-Star And Uncertainty Notes

| slice | label | count | CK log10 RMSE | CK bias | classification |
| --- | --- | ---: | ---: | ---: | --- |
| host Teff | M `<3900 K` | 140 | 0.193176 | -0.076306 | supported but selection-sensitive |
| host Teff | K `3900-5200 K` | 235 | 0.197335 | -0.093840 | supported failure region |
| host Teff | G `5200-6000 K` | 492 | 0.146600 | -0.047956 | supported comparison region |
| host Teff | F `6000-7500 K` | 285 | 0.113904 | +0.020702 | comparatively stable |
| host Teff | hot `>=7500 K` | 14 | 0.145129 | +0.127844 | sample-size blocked |
| uncertainty | tight `<=5%` | 194 | 0.187349 | -0.078760 | supported failure region |
| uncertainty | moderate `5-15%` | 627 | 0.156610 | -0.039395 | supported comparison band |
| uncertainty | loose `>15%` | 378 | 0.122158 | -0.013640 | catalog-selection diagnostic |
| uncertainty | missing | 8 | 0.544066 | -0.520279 | metadata blocked |

## Reading

The strongest supported failure surfaces are compact-radius rows,
sub-Neptune-radius rows, neptunian mass-class rows, and K/M host-temperature
bins. The stable comparison surface is giant-radius rows. Tight reported
uncertainty does not imply lower residual, so measurement-quality splits should
be read as catalog-selection diagnostics.

## Blocked Surfaces

Minimum-mass rows stay out of headline metrics. The sparse two-row
minimum-mass diagnostic has CK log10 RMSE `0.207728` versus null log10 RMSE
`0.031917`, so it cannot support success wording. Transit-timing, hot-host,
and uncertainty-missing slices are count or metadata blocked.
