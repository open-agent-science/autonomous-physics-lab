# Nuclear local-curvature no-leakage prototype

Task: `TASK-0394`
Agent run: `AGENT-RUN-0039`
Predecessor: `TASK-0397` / `AGENT-RUN-0041`

## Boundary

Sandbox-only retrospective prototype. No live data, reveal scoring, prediction registry entry, canonical result, claim, or knowledge update is produced.

## Summary

- Lane verdict: `FALSIFIED`.
- LOCAL-CURVATURE-001 assessment: `FALSIFIES_LOCAL_CURVATURE_001_UNDER_NO_LEAKAGE`.
- Best candidate full-known delta MAE: +0.019599 MeV.
- Self-inclusion ablation full-known delta MAE: -3.904855 MeV.
- Per-fold cache audit pass: `True`.

## Per-Variant Subset Deltas

| Variant | Role | full-known | holdout | training | magic | neutron-rich | high-error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `LOCAL-CURVATURE-001` | `executed_candidate` | +0.019599 | +0.003628 | +0.447927 | +0.093010 | -0.000385 | +0.003546 |
| `LOCAL-NOLEAK-CTRL-001` | `chain_shuffled_control` | +0.140940 | +0.139570 | +0.177699 | +0.414911 | +0.484228 | +0.260562 |
| `LOCAL-NOLEAK-CTRL-002` | `smooth_window_control` | -0.040028 | -0.052572 | +0.296378 | +0.061755 | +0.013716 | -0.089423 |
| `LOCAL-NOLEAK-CTRL-003` | `mass_number_only_control` | +0.053170 | -0.008702 | +1.712477 | +0.189730 | -0.012911 | +0.186001 |
| `LOCAL-NOLEAK-CTRL-004` | `near_null_control` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 |
| `LOCAL-NOLEAK-ABL-001` | `leakage_ablation_control` | -3.904855 | -3.983899 | -1.785032 | -3.940559 | -8.579699 | -7.928065 |

## Candidate vs Strongest No-Leakage Control

| Candidate | Strongest control | Margin | Subset win-rate | Survives? |
| --- | --- | ---: | ---: | --- |
| `LOCAL-CURVATURE-001` | `LOCAL-NOLEAK-CTRL-002` | -0.059627 | 0.000 | False |

## No-Leakage Contract Checks

- Target row excluded from admissible caches: `True`.
- Holdout rows excluded from admissible caches: `True`.
- Missing-neighbor strategy: `zero_fill_when_no_left_or_right_neighbor`.
- Neighbor inputs are baseline-only residuals from the active fold cache.
