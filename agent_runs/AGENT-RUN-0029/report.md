# Nuclear uncertainty-weighted residual hypothesis lane

**Task:** `TASK-0342`
**Agent run:** `AGENT-RUN-0029`
**Evidence class:** sandbox-only retrospective uncertainty diagnostic
**Verdict:** `INCONCLUSIVE`

## Boundary

This run uses only repository-pinned rows. It writes no canonical results, prediction-registry entries, claims, or knowledge artifacts. The uncertainty fields are treated as review-only weighting/filtering metadata, not as a fit-grade likelihood surface.

## Uncertainty Audit

- Field grade: `review_only`.
- Rows with positive uncertainty: `306`.
- Fit-grade uncertainty rows: `0`.
- Review-only uncertainty rows: `306`.
- Missing positive uncertainty rows: `0`.

## Variant Results

| Variant | Role | Count | MAE | RMSE | Weighted MAE | Mean sigma-norm err | Delta weighted MAE | Top-10 weight share |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| UNCERTAINTY-BASELINE-001 | unweighted_reference | 306 | 4.490449 | 5.815391 | 4.490449 | 258.969 | +0.000000 | 0.033 |
| UNCERTAINTY-WEIGHT-001 | uncertainty_weighted_diagnostic | 306 | 4.490449 | 5.815391 | 4.113714 | 258.969 | -0.376736 | 0.047 |
| UNCERTAINTY-WEIGHT-002 | uncertainty_weighted_diagnostic | 306 | 4.490449 | 5.815391 | 3.986084 | 258.969 | -0.504366 | 0.063 |
| UNCERTAINTY-FILTER-001 | uncertainty_filter_diagnostic | 155 | 3.467672 | 4.438814 | 3.467672 | 396.700 | -1.022777 | 0.065 |
| UNCERTAINTY-FILTER-002 | uncertainty_filter_diagnostic | 151 | 5.540320 | 6.950425 | 5.540320 | 117.590 | +1.049871 | 0.066 |

Negative delta MAE means the selected/weighted view has lower unweighted MAE than the full-known unweighted baseline reference. This is a diagnostic stability check, not a candidate improvement.

## Subset Diagnostics

| Subset | Count | MAE | RMSE | Median sigma | Mean sigma-norm err |
| --- | ---: | ---: | ---: | ---: | ---: |
| full_known | 306 | 4.490449 | 5.815391 | 0.028000 | 258.969 |
| training_slice | 11 | 2.824522 | 3.697117 | 0.009315 | 303.225 |
| primary_holdout | 295 | 4.552569 | 5.879637 | 0.029000 | 257.319 |
| low_uncertainty_half | 155 | 3.467672 | 4.438814 | 0.012000 | 396.700 |
| high_uncertainty_half | 151 | 5.540320 | 6.950425 | 0.047000 | 117.590 |
| post_ame2020_measured_comparison | 240 | 4.461256 | 5.885456 | 0.025500 | 273.188 |
| post_ame2020_extrapolated_comparison | 55 | 4.951025 | 5.854176 | 0.046000 | 188.072 |
| magic_any | 25 | 4.654025 | 6.392309 | 0.012000 | 357.930 |
| neutron_rich_high | 31 | 9.451698 | 11.501040 | 0.031000 | 344.565 |

## Prior Lane Sensitivity

- Gate status: `sensitive_review_gate`.
- High-minus-low uncertainty MAE gap: `+2.072648` MeV.
- Observed-uncertainty weighted delta MAE: `-0.376736` MeV.
- Interpretation: Prior unweighted retrospective lanes should treat uncertainty handling as a review gate before any follow-up because the committed residual surface changes materially under the conservative uncertainty split.

## Limitations

- Uncertainty fields are review-only for this lane because baseline model uncertainty is not represented.
- The NMD-0002 training slice uses a coarse curated uncertainty floor and must not be treated as a fit-grade likelihood surface.
- Inverse-variance weighting can concentrate effective weight on small-uncertainty rows even with a median-sigma floor.
- The lane audits baseline residual stability only; it does not re-score or promote prior candidate lanes.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
