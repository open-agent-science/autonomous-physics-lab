# NMD-0003 Pairing Residual-Feature Sprint

**Task:** `TASK-0594`
**Verdict:** `NEGATIVE_RESULT`

## Summary

This bounded sprint tests exactly one predeclared pairing/odd-even interaction family, `pairing_asymmetry_coupling`, under the frozen NMD-0003 stratified gate. It does not score the post-AME2020 holdout and does not create prediction, result, claim, or knowledge artifacts.

## Decision Metrics

- Candidate validation MAE improvement: `-0.010881` MeV.
- Best control validation MAE improvement: `0.005275` MeV.
- Candidate minus best control on validation: `-0.016156` MeV.
- Candidate minus best control on full known: `-0.005319` MeV.

## Candidate Surface Metrics

| surface | baseline MAE | corrected MAE | MAE improvement |
| --- | ---: | ---: | ---: |
| `train` | `1.822262` | `1.819623` | `0.002639` |
| `validation_holdout` | `1.899279` | `1.91016` | `-0.010881` |
| `sorted_aZN_diagnostic` | `2.016264` | `2.015488` | `0.000776` |
| `full_known` | `1.845344` | `1.846757` | `-0.001413` |

## Baseline Comparison

| baseline | validation MAE improvement | full-known MAE improvement |
| --- | ---: | ---: |
| `region_stratified_readiness` | `-0.010881` | `-0.001413` |
| `global_ols_audit` | `-0.014205` | `-0.003354` |
| `inherited_continuity` | `-0.014295` | `0.02502` |

## Subset Behavior

| subset | rows | baseline MAE | corrected MAE | MAE improvement |
| --- | ---: | ---: | ---: | ---: |
| `even_even` | `185` | `2.067954` | `2.089224` | `-0.02127` |
| `odd_a` | `344` | `1.871444` | `1.87048` | `0.000964` |
| `odd_odd` | `163` | `1.76658` | `1.790668` | `-0.024088` |

## Output Routing Summary

- Task verdict: `NEGATIVE_RESULT`.
- Canonical destination: `agent_runs/AGENT-RUN-0062/metrics.json`, `agent_runs/AGENT-RUN-0062/report.md`, `docs/reviews/nmd0003-pairing-residual-feature-sprint.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
