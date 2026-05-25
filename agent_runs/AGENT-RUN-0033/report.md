# Nuclear high-error cluster adversarial stability audit

Task: `TASK-0367`
Agent run: `AGENT-RUN-0033`
Predecessor: `TASK-0343` / `AGENT-RUN-0030`

## Boundary

Sandbox-only retrospective audit. No live data, reveal scoring, prediction registry entry, canonical result, claim, or knowledge update is produced.

## Summary

- Lane verdict: `INCONCLUSIVE`.
- High-error threshold: 6.110142 MeV at p75.0.
- Perturbed threshold control: 6.497075 MeV at p80.0.
- Executed candidates: 3; controls: 6.

## Subset Delta MAE

| Variant | Role | full-known | holdout | high-error | non-high-error | neutron-rich | magic | light-A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HIGHCLUSTER-001` | `executed_candidate` | -0.629378 | -0.624190 | -2.501166 | +0.000000 | -2.573153 | -1.528491 | +0.000000 |
| `HIGHCLUSTER-002` | `executed_candidate` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| `HIGHCLUSTER-003` | `executed_candidate` | -0.354350 | -0.338906 | -1.408196 | +0.000000 | -1.636198 | -0.525100 | +0.000000 |
| `HIGHCLUSTER-CONTROL-001` | `matched_random_high_error_control` | +0.001112 | +0.001154 | +0.010608 | -0.002081 | +0.010979 | +0.005402 | +0.002836 |
| `HIGHCLUSTER-CONTROL-002` | `smooth_a_control` | +0.036475 | +0.038179 | +0.066926 | +0.026236 | -0.012176 | +0.002464 | +0.002871 |
| `HIGHCLUSTER-CONTROL-003` | `cluster_label_shuffle_control` | -0.022701 | -0.020936 | +0.000000 | -0.030335 | +0.198858 | +0.087065 | -0.032107 |
| `HIGHCLUSTER-CONTROL-004` | `high_error_threshold_perturbation_control` | -0.589145 | -0.582456 | -2.341276 | +0.000000 | -2.434335 | -1.430780 | +0.000000 |
| `HIGHCLUSTER-CONTROL-005` | `smooth_a_local_density_control` | +1.808602 | +1.895241 | +1.482683 | +1.918190 | +4.443386 | +2.255015 | -0.189428 |
| `HIGHCLUSTER-CONTROL-006` | `near_null_control` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |

## Candidate vs Strongest Control

| Candidate | Strongest control on full-known | Margin | Subset win-rate | Non-high-error regression flag |
| --- | --- | ---: | ---: | --- |
| `HIGHCLUSTER-001` | `HIGHCLUSTER-CONTROL-004` | +0.040234 | 0.645 | False |
| `HIGHCLUSTER-002` | `HIGHCLUSTER-CONTROL-004` | -0.589145 | 0.000 | False |
| `HIGHCLUSTER-003` | `HIGHCLUSTER-CONTROL-004` | -0.234795 | 0.161 | False |

## Coefficient Stability

| Candidate | Folds | Sign flip? | full-known delta range | high-error delta range | non-high-error delta range |
| --- | ---: | --- | ---: | ---: | ---: |
| `HIGHCLUSTER-001` | 11 | False | -0.629378 to +0.000000 | -2.501166 to +0.000000 | +0.000000 to +0.000000 |
| `HIGHCLUSTER-002` | 11 | False | +0.000000 to +0.000000 | +0.000000 to +0.000000 | +0.000000 to +0.000000 |
| `HIGHCLUSTER-003` | 11 | False | -0.354350 to +0.000000 | -1.408196 to +0.000000 | +0.000000 to +0.000000 |

## Chain Transfer

| Candidate | Isotope interpretable groups | Isotope improvement rate | Isotone interpretable groups | Isotone improvement rate |
| --- | ---: | ---: | ---: | ---: |
| `HIGHCLUSTER-001` | 48 | 0.229 | 53 | 0.264 |
| `HIGHCLUSTER-002` | 48 | 0.000 | 53 | 0.000 |
| `HIGHCLUSTER-003` | 48 | 0.104 | 53 | 0.208 |

## Interpretation

The audit preserves the predecessor high-error cluster lane only as sandbox diagnostic evidence if a candidate beats the strongest control by the configured margin and does not materially regress non-high-error rows. Negative or inconclusive outcomes are retained in the artifacts and do not authorize claim promotion.
