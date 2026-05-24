# Nuclear local-curvature adversarial controls lane

**Task:** `TASK-0351`  
**Agent run:** `AGENT-RUN-0031`  
**Predecessor:** `TASK-0339` / `AGENT-RUN-0026`
**Lane verdict:** `PARTIALLY_VALID`  
**Primary survival margin (MeV):** 0.25

## Boundary

This run uses only repository-pinned rows and writes no canonical results, prediction-registry entries, claims, or knowledge artifacts. It re-evaluates the TASK-0339 / AGENT-RUN-0026 local-curvature candidates against three new adversarial controls in addition to the two controls the predecessor lane already carried.

## Variants Evaluated

| Candidate / control | Role | Family |
| --- | --- | --- |
| `LOCAL-CURVATURE-001` | executed_candidate | isotope_local_residual |
| `LOCAL-CURVATURE-002` | executed_candidate | isotone_local_residual |
| `LOCAL-CURVATURE-003` | executed_candidate | local_kink_contrast |
| `LOCAL-CONTROL-001` | chain_shuffled_control | chain_shuffled_control |
| `LOCAL-CONTROL-002` | smooth_local_window_control | smooth_local_window_control |
| `LOCAL-CONTROL-003` **(new)** | neighbor_availability_leakage_control | neighbor_availability_leakage_control |
| `LOCAL-CONTROL-004` **(new)** | chain_label_shuffle_control | chain_label_shuffle_control |
| `LOCAL-CONTROL-005` **(new)** | smooth_local_regression_control | smooth_local_regression_control |

## Per-Variant Subset Deltas (MeV)

| Candidate | Full-known | Holdout | Magic | Neutron-rich | High-error |
| --- | ---: | ---: | ---: | ---: | ---: |
| `LOCAL-CURVATURE-001` | -2.286136 | -2.360363 | -1.252110 | -5.161792 | -5.176614 |
| `LOCAL-CURVATURE-002` | -1.562064 | -1.605007 | -1.564166 | -3.337156 | -3.186163 |
| `LOCAL-CURVATURE-003` | +0.024176 | +0.025064 | +0.001336 | +0.062689 | +0.058705 |
| `LOCAL-CONTROL-001` | -1.105310 | -1.145346 | -0.725501 | -1.392932 | -2.349781 |
| `LOCAL-CONTROL-002` | -1.690959 | -1.737175 | -1.315575 | -3.722575 | -4.393016 |
| `LOCAL-CONTROL-003` | -1.476848 | -1.527188 | -1.151664 | -3.036198 | -3.220167 |
| `LOCAL-CONTROL-004` | +0.494408 | +0.518151 | +0.703833 | +0.960842 | +0.755940 |
| `LOCAL-CONTROL-005` | -1.741840 | -1.791797 | -1.077160 | -4.114535 | -4.884656 |

Negative deltas indicate lower MAE than the frozen semi-empirical baseline.

## Candidate vs Strongest Control (Primary Subset)

| Candidate | Strongest control on full_known | Candidate Δ MAE | Strongest control Δ MAE | Margin (control − candidate) | Survives ≥ 0.25 MeV? |
| --- | --- | ---: | ---: | ---: | ---: |
| `LOCAL-CURVATURE-001` | `LOCAL-CONTROL-005` | -2.286136 | -1.741840 | +0.544296 | yes |
| `LOCAL-CURVATURE-002` | `LOCAL-CONTROL-005` | -1.562064 | -1.741840 | -0.179776 | **no** |
| `LOCAL-CURVATURE-003` | `LOCAL-CONTROL-005` | +0.024176 | -1.741840 | -1.766016 | **no** |

## Per-Candidate Subset Win-Rate vs Strongest Control

| Candidate | Subsets evaluated | Subsets won vs strongest control | Win rate |
| --- | ---: | ---: | ---: |
| `LOCAL-CURVATURE-001` | 19 | 13 | 0.684 |
| `LOCAL-CURVATURE-002` | 19 | 7 | 0.368 |
| `LOCAL-CURVATURE-003` | 19 | 0 | 0.000 |

## Interpretation

- At least one candidate beats the strongest control on the primary subset by at least `0.25` MeV AND wins more than half of the per-subset comparisons.
- The signal is preserved as sandbox evidence that survived adversarial controls. It does not authorize a claim, a prediction-registry entry, or a reveal.
- Recommendation: pass through the TASK-0352 no-leakage freeze protocol before any predictive implementation.

## Limitations

- Features still use committed full-known neighbor residual context and are retrospective diagnostics, not blind predictions.
- Coefficients are fit on the 11-row NMD-0002 residual slice; small-sample fit variance limits the precision of the survival margin check (set to 0.25 MeV).
- The label-shuffle control uses a deterministic Z permutation; different permutation schemes may produce stronger or weaker controls.
- The chain-blind smoother uses a simple 1-D linear regression over the A-window; richer smoothers (e.g. local quadratic, loess-style) are not exercised in this lane.
- No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.

## Verdict

`PARTIALLY_VALID`
