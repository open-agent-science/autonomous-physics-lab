# Nuclear high-error cluster hypothesis lane

**Task:** `TASK-0343`
**Agent run:** `AGENT-RUN-0030`
**Evidence class:** sandbox-only retrospective high-error cluster diagnostic
**Verdict:** `PARTIALLY_VALID`

## Boundary

This run uses only repository-pinned rows and deterministic thresholds selected before candidate fitting. It writes no canonical results, prediction-registry entries, claims, or knowledge artifacts. High-error cluster labels come from committed residuals and are therefore diagnostic rather than blind prediction features.

## High-Error Cluster Map

- High-error threshold: `6.110142` MeV at baseline absolute-error percentile `75.0`.
- High-error rows: `77`.
- Sparse local-density threshold: `6.000000` neighbors at percentile `25.0`.

| Cluster | Rows | Baseline MAE | Median A | Example nuclides |
| --- | ---: | ---: | ---: | --- |
| extrapolated_source_high_error | 14 | 8.628017 | 104.0 | Fe-70, Ni-74, Ni-75, As-88, As-89, Rb-103 |
| near_magic_high_error | 34 | 10.026167 | 128.0 | Pb-208, Ca-54, Fe-70, Ni-74, Ni-75, Cu-76 |
| neutron_rich_high_error | 20 | 11.929067 | 96.5 | Ca-54, Fe-70, Ni-75, Cu-78, Ga-83, Ga-84 |
| other_high_error | 27 | 6.773354 | 167.0 | U-238, Ge-85, As-86, As-87, Br-73, Kr-75 |
| sparse_local_high_error | 18 | 9.709595 | 133.0 | Pb-208, Ni-74, Ni-75, Cu-76, Cu-77, Cu-78 |

## Candidate And Control Results

| Candidate | Role | Verdict | Full-known MAE | Holdout | High-error | Non-high-error | Neutron-rich | Magic | Light-A | Chain improvement rate |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HIGHCLUSTER-001 | executed_candidate | PARTIALLY_VALID | -0.629378 | -0.624190 | -2.501166 | +0.000000 | -2.573153 | -1.528491 | +0.000000 | 0.229 |
| HIGHCLUSTER-002 | executed_candidate | INCONCLUSIVE | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | 0.000 |
| HIGHCLUSTER-003 | executed_candidate | PARTIALLY_VALID | -0.354350 | -0.338906 | -1.408196 | +0.000000 | -1.636198 | -0.525100 | +0.000000 | 0.104 |
| HIGHCLUSTER-CONTROL-001 | matched_random_high_error_control | INCONCLUSIVE | +0.001112 | +0.001154 | +0.010608 | -0.002081 | +0.010979 | +0.005402 | +0.002836 | 0.333 |
| HIGHCLUSTER-CONTROL-002 | smooth_a_control | INCONCLUSIVE | +0.036475 | +0.038179 | +0.066926 | +0.026236 | -0.012176 | +0.002464 | +0.002871 | 0.312 |
| HIGHCLUSTER-CONTROL-003 | cluster_label_shuffle_control | PARTIALLY_VALID | -0.022701 | -0.020936 | +0.000000 | -0.030335 | +0.198858 | +0.087065 | -0.032107 | 0.417 |

Negative deltas mean lower MAE than the frozen semi-empirical baseline on that subset. Positive deltas are regressions and remain visible.

## Matched Control Gate

| Candidate | Best control | Candidate primary | Best control primary | Beats controls |
| --- | --- | ---: | ---: | --- |
| HIGHCLUSTER-001 | HIGHCLUSTER-CONTROL-003 | -0.629378 | -0.022701 | yes |
| HIGHCLUSTER-002 | HIGHCLUSTER-CONTROL-003 | +0.000000 | -0.022701 | no |
| HIGHCLUSTER-003 | HIGHCLUSTER-CONTROL-003 | -0.354350 | -0.022701 | yes |

## Interpretation

- Generated bounded cluster explanations: `6`.
- Executed candidate explanations: `3`.
- Executed controls: `3`.
- Best full-known delta: `HIGHCLUSTER-001` (-0.629378 MeV MAE; -0.706828 MeV RMSE).
- Matched random high-error, smooth-A, and cluster-label-shuffle controls are reported to keep post-hoc cluster targeting visible.
- Candidates that improve only high-error rows while materially regressing non-high-error rows are marked `OVERFITTED` and not promoted.
- The lane verdict is conservative; no result here authorizes claim promotion or future-measurement comparison.

## Limitations

- High-error membership and cluster labels come from committed retrospective residuals, so this is a diagnostic lane rather than a blind prediction.
- Candidate thresholds are deterministic and selected before candidate fitting, but the surface is still full-known repository data.
- The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.
- Matched random, smooth-A, and cluster-label-shuffle controls are reported because high-error targeting can overfit broad residual structure.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
