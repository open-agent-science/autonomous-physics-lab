# Nuclear local-curvature negative-control expansion

Task: `TASK-0397`
Agent run: `AGENT-RUN-0041`
Predecessor: `TASK-0351` / `AGENT-RUN-0031`

## Boundary

Sandbox-only retrospective audit. No live data, reveal scoring, prediction registry entry, canonical result, claim, or knowledge update is produced.

## Summary

- Lane verdict: `PARTIALLY_VALID`.
- Control explanation verdict: `NOT_EXPLAINED_BY_TESTED_CONTROLS`.
- Best candidate: `LOCAL-CURVATURE-001` with full-known delta MAE -2.286136 MeV.
- Strongest control: `LOCAL-NEGCTRL-006` with full-known delta MAE -1.741840 MeV.
- Control-minus-candidate margin: +0.544296 MeV.

## Per-Variant Subset Deltas

| Variant | Role | full-known | holdout | magic | neutron-rich | high-error |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `LOCAL-CURVATURE-001` | `executed_candidate` | -2.286136 | -2.360363 | -1.252110 | -5.161792 | -5.176614 |
| `LOCAL-CURVATURE-002` | `executed_candidate` | -1.562064 | -1.605007 | -1.564166 | -3.337156 | -3.186163 |
| `LOCAL-CURVATURE-003` | `executed_candidate` | +0.024176 | +0.025064 | +0.001336 | +0.062689 | +0.058705 |
| `LOCAL-NEGCTRL-001` | `chain_shuffled_control` | -1.105310 | -1.145346 | -0.725501 | -1.392932 | -2.349781 |
| `LOCAL-NEGCTRL-002` | `chain_label_permutation_control` | +0.494408 | +0.518151 | +0.703833 | +0.960842 | +0.755940 |
| `LOCAL-NEGCTRL-003` | `mass_number_only_control` | -0.010280 | -0.008702 | -0.021227 | -0.012911 | -0.035178 |
| `LOCAL-NEGCTRL-004` | `magic_distance_only_control` | +0.015761 | +0.017233 | -0.260620 | -0.207004 | -0.461383 |
| `LOCAL-NEGCTRL-005` | `smooth_window_control` | -1.690959 | -1.737175 | -1.315575 | -3.722575 | -4.393016 |
| `LOCAL-NEGCTRL-006` | `smooth_local_regression_control` | -1.741840 | -1.791797 | -1.077160 | -4.114535 | -4.884656 |
| `LOCAL-NEGCTRL-007` | `neighbor_availability_control` | -1.476848 | -1.527188 | -1.151664 | -3.036198 | -3.220167 |
| `LOCAL-NEGCTRL-008` | `near_null_neighborhood_control` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |

## Candidate vs Strongest Negative Control

| Candidate | Strongest control | Margin | Subset win-rate | Survives? |
| --- | --- | ---: | ---: | --- |
| `LOCAL-CURVATURE-001` | `LOCAL-NEGCTRL-006` | +0.544296 | 0.684 | True |
| `LOCAL-CURVATURE-002` | `LOCAL-NEGCTRL-006` | -0.179776 | 0.368 | False |
| `LOCAL-CURVATURE-003` | `LOCAL-NEGCTRL-006` | -1.766016 | 0.000 | False |

## Chain Transfer

| Candidate | Isotope groups | Isotope improvement rate | Isotone groups | Isotone improvement rate |
| --- | ---: | ---: | ---: | ---: |
| `LOCAL-CURVATURE-001` | 48 | 0.917 | 53 | 0.943 |
| `LOCAL-CURVATURE-002` | 48 | 0.875 | 53 | 0.868 |
| `LOCAL-CURVATURE-003` | 48 | 0.417 | 53 | 0.377 |

## Interpretation

Negative controls do not publish or promote a result. They only record whether the retrospective local-curvature signal is plausibly explained by chain shuffling, mass-number locality, shell proximity, generic smoothing, or near-null neighborhood structure.
