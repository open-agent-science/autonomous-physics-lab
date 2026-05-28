# Nuclear high-error cluster adversarial stability audit

**Task:** `TASK-0367`  
**Agent run:** `AGENT-RUN-0033`  
**Predecessor:** `TASK-0343` / `AGENT-RUN-0030`  
**Lane verdict:** `INCONCLUSIVE`  
**Primary survival margin (MeV):** 0.25  
**Non-high-error regression threshold (MeV):** 0.25  
**LOO coefficient range limit:** 1.00

## Boundary

This run only uses committed repository datasets and the predecessor high-error cluster lane helpers. It writes no canonical RESULT-* artifact, no PRED-* entry, no claim, and no knowledge file. The lane verdict feeds maintainer review; it does not authorize claim promotion or future-measurement comparison.

## Variants Evaluated

| Candidate / control | Role | Family |
| --- | --- | --- |
| `HIGHCLUSTER-001` | executed_candidate | magic_proximity_high_error_cluster |
| `HIGHCLUSTER-002` | executed_candidate | neutron_rich_high_error_cluster |
| `HIGHCLUSTER-003` | executed_candidate | local_density_high_error_cluster |
| `HIGHCLUSTER-CONTROL-001` | matched_random_high_error_control | matched_random_high_error_control |
| `HIGHCLUSTER-CONTROL-002` | smooth_a_control | smooth_a_control |
| `HIGHCLUSTER-CONTROL-003` | cluster_label_shuffle_control | cluster_label_shuffle_control |
| `HIGHCLUSTER-ADV-001` **(new)** | random_permutation_cluster_label_control | random_permutation_cluster_label_control |
| `HIGHCLUSTER-ADV-002` **(new)** | pure_local_density_control | pure_local_density_control |
| `HIGHCLUSTER-ADV-003` **(new)** | near_null_jitter_control | near_null_jitter_control |

## Per-Variant Subset Deltas (MeV)

| Candidate / control | Role | Full-known | Holdout | High-error | Non-high-error | Neutron-rich | Magic | Light-A | Chain rate |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `HIGHCLUSTER-001` | executed_candidate | -0.629378 | -0.624190 | -2.501166 | +0.000000 | -2.573153 | -1.528491 | +0.000000 | 0.229 |
| `HIGHCLUSTER-002` | executed_candidate | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | 0.000 |
| `HIGHCLUSTER-003` | executed_candidate | -0.354350 | -0.338906 | -1.408196 | +0.000000 | -1.636198 | -0.525100 | +0.000000 | 0.104 |
| `HIGHCLUSTER-CONTROL-001` | matched_random_high_error_control | +0.001112 | +0.001154 | +0.010608 | -0.002081 | +0.010979 | +0.005402 | +0.002836 | n/a |
| `HIGHCLUSTER-CONTROL-002` | smooth_a_control | +0.036475 | +0.038179 | +0.066926 | +0.026236 | -0.012176 | +0.002464 | +0.002871 | n/a |
| `HIGHCLUSTER-CONTROL-003` | cluster_label_shuffle_control | -0.022701 | -0.020936 | +0.000000 | -0.030335 | +0.198858 | +0.087065 | -0.032107 | n/a |
| `HIGHCLUSTER-ADV-001` | random_permutation_cluster_label_control | +0.094676 | +0.107312 | -0.244180 | +0.208615 | -0.693155 | -0.149869 | +0.187182 | n/a |
| `HIGHCLUSTER-ADV-002` | pure_local_density_control | +0.597562 | +0.639271 | +0.381735 | +0.670133 | +2.489935 | +1.048754 | +0.035225 | n/a |
| `HIGHCLUSTER-ADV-003` | near_null_jitter_control | +0.029177 | +0.025014 | +0.002260 | +0.038228 | -0.090944 | +0.086439 | +0.378042 | n/a |

Negative deltas indicate lower MAE than the frozen semi-empirical baseline.

## Candidate vs Strongest Control (Primary Subset)

| Candidate | Strongest control on full_known | Candidate Δ MAE | Control Δ MAE | Margin (control − candidate) | Survives ≥ 0.25 MeV? |
| --- | --- | ---: | ---: | ---: | --- |
| `HIGHCLUSTER-001` | `HIGHCLUSTER-CONTROL-003` | -0.629378 | -0.022701 | +0.606677 | yes |
| `HIGHCLUSTER-002` | `HIGHCLUSTER-CONTROL-003` | +0.000000 | -0.022701 | -0.022701 | **no** |
| `HIGHCLUSTER-003` | `HIGHCLUSTER-CONTROL-003` | -0.354350 | -0.022701 | +0.331648 | yes |

## Per-Candidate Subset Win-Rate vs Strongest Control

| Candidate | Subsets evaluated | Subsets won vs strongest control | Win rate |
| --- | ---: | ---: | ---: |
| `HIGHCLUSTER-001` | 31 | 25 | 0.806 |
| `HIGHCLUSTER-002` | 31 | 0 | 0.000 |
| `HIGHCLUSTER-003` | 31 | 25 | 0.806 |

## High-Error Threshold Perturbation

| Percentile | Threshold (MeV) | High-error rows | `HIGHCLUSTER-001` Δ MAE (coef) | `HIGHCLUSTER-002` Δ MAE (coef) | `HIGHCLUSTER-003` Δ MAE (coef) |
| ---: | ---: | ---: | ---:  | ---:  | ---:  |
| 65.0 | 5.438311 | 107 | -0.658970 (+8.4537) | +0.000000 (+0.0000) | -0.216218 (+8.4537) |
| 70.0 | 5.758764 | 92 | -0.641381 (+8.4537) | +0.000000 (+0.0000) | -0.354350 (+8.4537) |
| 75.0 | 6.110142 | 77 | -0.629378 (+8.4537) | +0.000000 (+0.0000) | -0.354350 (+8.4537) |
| 80.0 | 6.497075 | 62 | -0.589145 (+8.4537) | +0.000000 (+0.0000) | -0.340979 (+8.4537) |

| Candidate | Δ MAE range (MeV) | Coefficient range | Sign flip? | Improves at every percentile? |
| --- | ---: | ---: | --- | --- |
| `HIGHCLUSTER-001` | 0.069826 | [+8.4537, +8.4537] | no | yes |
| `HIGHCLUSTER-002` | 0.000000 | [+0.0000, +0.0000] | no | **no** |
| `HIGHCLUSTER-003` | 0.138132 | [+8.4537, +8.4537] | no | yes |

## Leave-One-Out Coefficient Stability

| Candidate | Coefficient mean ± std | Coefficient range | Sign flip? | Δ MAE range (MeV) | LOO stable? |
| --- | ---: | ---: | --- | ---: | --- |
| `HIGHCLUSTER-001` | +7.6852 ± 2.4303 | [+0.0000, +8.4537] | no | 0.629378 | **no** |
| `HIGHCLUSTER-002` | +0.0000 ± 0.0000 | [+0.0000, +0.0000] | no | 0.000000 | yes |
| `HIGHCLUSTER-003` | +7.6852 ± 2.4303 | [+0.0000, +8.4537] | no | 0.354350 | **no** |

## Per-Candidate Adversarial Verdict

| Candidate | Survives primary? | Subset win rate | Threshold stable? | LOO stable? | High-error-only overfit? | Verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| `HIGHCLUSTER-001` | yes | 0.806 | yes | **no** | no | `INCONCLUSIVE` |
| `HIGHCLUSTER-002` | **no** | 0.000 | **no** | yes | no | `FALSIFIED` |
| `HIGHCLUSTER-003` | yes | 0.806 | yes | **no** | no | `INCONCLUSIVE` |

## Interpretation

- At least one candidate clears one of the adversarial gates but not all of them; the cluster signal is neither cleanly preserved nor cleanly falsified.
- Recommendation: keep the lane as sandbox diagnostic evidence and do not authorize predictive use. Maintainer review should weigh the per-candidate verdict table before any follow-up task.

## Limitations

- High-error membership and cluster labels still come from committed retrospective residuals; this lane sharpens controls but remains a diagnostic rather than a blind prediction.
- Coefficients are fit on the 11-row NMD-0002 training slice, so the leave-one-out stability check is itself a small-sample diagnostic.
- The three new adversarial controls do not exhaust the space of possible attacks (e.g. stronger label shuffles weighted by chain structure, richer non-linear smoothers, or feature-set ablations).
- Threshold perturbation rebuilds the ClusterIndex at each percentile, so cluster-membership composition shifts between thresholds; the diagnostic measures coefficient and delta stability rather than a fixed cluster definition.
- No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.

## Verdict

`INCONCLUSIVE`
