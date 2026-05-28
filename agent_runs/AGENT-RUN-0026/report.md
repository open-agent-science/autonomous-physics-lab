# Nuclear local residual curvature hypothesis lane

**Task:** `TASK-0339`
**Agent run:** `AGENT-RUN-0026`
**Evidence class:** sandbox-only retrospective local-curvature diagnostic
**Verdict:** `INCONCLUSIVE`

## Boundary

This run uses only repository-pinned rows and writes no canonical results, prediction-registry entries, claims, or knowledge artifacts. Neighbor-derived features use committed full-known residual context, so the output is a diagnostic stress surface rather than a blind prediction or reveal score.

## Candidate Results

| Candidate | Role | Full-known delta MAE | Holdout delta MAE | Magic | Neutron-rich | High-error |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| LOCAL-CURVATURE-001 | executed_candidate | -2.286136 | -2.360363 | -1.252110 | -5.161792 | -5.176614 |
| LOCAL-CURVATURE-002 | executed_candidate | -1.562064 | -1.605007 | -1.564166 | -3.337156 | -3.186163 |
| LOCAL-CURVATURE-003 | executed_candidate | +0.024176 | +0.025064 | +0.001336 | +0.062689 | +0.058705 |
| LOCAL-CONTROL-001 | chain_shuffled_control | -1.105310 | -1.145346 | -0.725501 | -1.392932 | -2.349781 |
| LOCAL-CONTROL-002 | smooth_local_window_control | -1.690959 | -1.737175 | -1.315575 | -3.722575 | -4.393016 |

Negative deltas mean lower MAE than the frozen semi-empirical baseline on that subset. Positive deltas are regressions and remain visible.

## Isotope-Chain Transfer

| Candidate | Interpretable groups | Improved | Regressed | Improvement rate |
| --- | ---: | ---: | ---: | ---: |
| LOCAL-CURVATURE-001 | 48 | 44 | 4 | 0.917 |
| LOCAL-CURVATURE-002 | 48 | 42 | 6 | 0.875 |
| LOCAL-CURVATURE-003 | 48 | 20 | 28 | 0.417 |
| LOCAL-CONTROL-001 | 48 | 38 | 10 | 0.792 |
| LOCAL-CONTROL-002 | 48 | 37 | 11 | 0.771 |

## Isotone-Chain Transfer

| Candidate | Interpretable groups | Improved | Regressed | Improvement rate |
| --- | ---: | ---: | ---: | ---: |
| LOCAL-CURVATURE-001 | 53 | 50 | 3 | 0.943 |
| LOCAL-CURVATURE-002 | 53 | 46 | 7 | 0.868 |
| LOCAL-CURVATURE-003 | 53 | 20 | 33 | 0.377 |
| LOCAL-CONTROL-001 | 53 | 48 | 5 | 0.906 |
| LOCAL-CONTROL-002 | 53 | 46 | 7 | 0.868 |

## Interpretation

- Generated variants: `6`.
- Executed candidate variants: `3`.
- Executed controls: `2`.
- Best full-known delta: `LOCAL-CURVATURE-001` (-2.286136 MeV).
- Chain-shuffled and smooth-window controls are included to keep local overfit and broad smooth-residual explanations visible.
- The verdict remains conservative because the controls also improve many groups; no result here authorizes a claim or future-measurement comparison.

## Limitations

- Neighbor-derived features use committed full-known residual context and therefore are diagnostic rather than predictive.
- The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.
- Chain and isotone transfer are evaluated retrospectively and include sparse groups that must not be overinterpreted.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
