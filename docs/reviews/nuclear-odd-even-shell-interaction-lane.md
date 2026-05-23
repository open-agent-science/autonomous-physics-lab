# Nuclear odd-even shell-interaction hypothesis lane

**Task:** `TASK-0340`
**Agent run:** `AGENT-RUN-0027`
**Evidence class:** sandbox-only retrospective odd-even shell-interaction diagnostic
**Verdict:** `INCONCLUSIVE`

## Boundary

This run uses only repository-pinned rows and Z/N/A-derived parity and shell-proximity features. It writes no canonical results, prediction-registry entries, claims, or knowledge artifacts. Shell-axis and pairing-only evidence remain diagnostic context rather than promoted claims.

## Candidate And Control Results

| Candidate | Role | Full-known MAE | Holdout | Even-even | Odd-even | Odd-odd | Magic-Z | Magic-N | Light-A | Neutron-rich |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ODD-SHELL-001 | executed_interaction_candidate | +0.044032 | +0.045567 | +0.044052 | +0.000000 | +0.140635 | -0.074528 | -0.097073 | +0.070619 | +0.031707 |
| ODD-SHELL-002 | executed_interaction_candidate | +0.024887 | +0.028541 | -0.000051 | +0.000000 | +0.105825 | -0.109501 | -0.123817 | -0.001187 | +0.069455 |
| ODD-SHELL-003 | executed_interaction_candidate | +0.115684 | +0.126475 | +0.000000 | +0.224047 | +0.000000 | +0.058861 | +0.143149 | +0.377763 | +0.955020 |
| ODD-SHELL-CONTROL-001 | pairing_only_control | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | -0.000000 | -0.000000 | +0.000000 | +0.000000 |
| ODD-SHELL-CONTROL-002 | shell_only_control | -0.081085 | -0.086310 | +0.101236 | -0.109315 | -0.211586 | -0.158489 | -0.434863 | +0.177465 | -0.371997 |
| ODD-SHELL-CONTROL-003 | smooth_a_control | +0.036475 | +0.038179 | +0.045544 | +0.036253 | +0.027390 | -0.030634 | -0.030861 | +0.002871 | -0.012176 |
| ODD-SHELL-CONTROL-004 | shuffled_interaction_control | -0.028721 | -0.032050 | -0.093649 | -0.018567 | +0.017532 | +0.017613 | +0.013267 | +0.236789 | -0.154729 |

Negative deltas mean lower MAE than the frozen semi-empirical baseline on that subset. Positive deltas are regressions and remain visible.

## Lower-Complexity Control Gate

| Interaction | Best control | Candidate primary | Best control primary | Beats controls |
| --- | --- | ---: | ---: | --- |
| ODD-SHELL-001 | ODD-SHELL-CONTROL-002 | +0.044032 | -0.081085 | no |
| ODD-SHELL-002 | ODD-SHELL-CONTROL-002 | +0.024887 | -0.081085 | no |
| ODD-SHELL-003 | ODD-SHELL-CONTROL-002 | +0.115684 | -0.081085 | no |

## Interpretation

- Generated interaction variants: `6`.
- Executed interaction candidates: `3`.
- Executed controls: `4`.
- Best full-known delta: `ODD-SHELL-CONTROL-002` (-0.081085 MeV MAE; -0.161458 MeV RMSE).
- Pairing-only, shell-only, smooth-A, and shuffled-interaction controls are reported next to candidates to keep simpler explanations visible.
- The verdict stays conservative; no result here authorizes claim promotion or future-measurement comparison.

## Limitations

- These features are odd-even by shell-proximity interaction proxies, not measured nuclear-structure parameters.
- The fit surface remains the 11-row NMD-0002 training slice, so coefficient stability is not established.
- Odd-odd subset behavior is sparse and must not be overinterpreted.
- The full-known surface is retrospective committed repository data, not a future-measurement reveal.
- Lower-complexity and shuffled controls are included because aggregate improvements can reflect pairing-only, shell-only, or small-sample residual structure.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
