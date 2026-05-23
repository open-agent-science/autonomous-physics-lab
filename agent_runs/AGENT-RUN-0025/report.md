# Nuclear deformation-proxy hypothesis lane

**Task:** `TASK-0338`
**Agent run:** `AGENT-RUN-0025`
**Evidence class:** sandbox-only retrospective deformation-proxy diagnostic
**Verdict:** `INCONCLUSIVE`

## Boundary

This run uses only repository-pinned rows and Z/N/A-derived proxy features. It writes no canonical results, prediction-registry entries, claims, or knowledge artifacts. The proxy features are not measured deformation parameters, so the output is a bounded retrospective diagnostic surface.

## Candidate Results

| Candidate | Role | Full-known MAE | Full-known RMSE | Holdout | Magic-Z | Magic-N | Mid-mass | Heavy | Neutron-rich | Light-A |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DEFORM-PROXY-001 | executed_candidate | +0.008451 | -0.001343 | +0.007924 | +0.000000 | +0.000000 | -0.011940 | -0.039240 | -0.447730 | +0.067371 |
| DEFORM-PROXY-002 | executed_candidate | +0.088308 | +0.149722 | +0.100728 | +0.022294 | +0.080531 | +0.309463 | +0.012317 | +1.195138 | +0.107391 |
| DEFORM-PROXY-003 | executed_candidate | +0.059232 | +0.075858 | +0.060433 | +0.000000 | +0.000000 | +0.049890 | -0.209691 | -1.683751 | +0.321042 |
| DEFORM-CONTROL-001 | smooth_a_control | +0.036475 | +0.036355 | +0.038179 | -0.030634 | -0.030861 | -0.001746 | +0.070477 | -0.012176 | +0.002871 |
| DEFORM-CONTROL-002 | shuffled_proxy_control | +0.054900 | +0.077725 | +0.060371 | +0.054682 | +0.187860 | +0.101483 | +0.081700 | +0.422399 | -0.108102 |

Negative deltas mean lower error than the frozen semi-empirical baseline on that subset. Positive deltas are regressions and remain visible.

## Isotope-Chain Diagnostics

| Candidate | Interpretable Z chains | Improved | Regressed | Improvement rate |
| --- | ---: | ---: | ---: | ---: |
| DEFORM-PROXY-001 | 48 | 17 | 25 | 0.354 |
| DEFORM-PROXY-002 | 48 | 21 | 27 | 0.438 |
| DEFORM-PROXY-003 | 48 | 14 | 28 | 0.292 |
| DEFORM-CONTROL-001 | 48 | 15 | 33 | 0.312 |
| DEFORM-CONTROL-002 | 48 | 25 | 21 | 0.521 |

## Interpretation

- Generated proxy variants: `6`.
- Generated controls: `2`.
- Executed candidate variants: `3`.
- Executed controls: `2`.
- Best full-known delta: `DEFORM-PROXY-001` (+0.008451 MeV MAE; -0.001343 MeV RMSE).
- Smooth-A and shuffled controls are reported next to candidates to keep non-deformation and small-sample explanations visible.
- The verdict stays conservative; no result here authorizes claim promotion or future-measurement comparison.

## Limitations

- These features are deformation-like proxies derived from Z, N, and A, not measured deformation parameters.
- The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.
- The full-known surface is retrospective committed repository data, not a future-measurement reveal.
- Smooth-A and shuffled controls are included because aggregate improvements can reflect small-sample residual structure.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
