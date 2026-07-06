# RESULT-0028: ThermoML Tb esters/lactones failed-family negative control

This agent-published negative/control result packages committed RESULT-0026
evidence. It does not rerun the benchmark, refit Joback, or expand data.

On the committed 40-row ThermoML normal-boiling-temperature fixture, the frozen Joback estimator cleared the aggregate and seven of eight held-out family margins, but esters/lactones did not clear the predeclared +5 K family-survival margin: Joback MAE was 26.134 K versus 20.584245 K for the molecular-weight-only control across five rows.

## Esters/lactones family scores (5 rows)

| Estimator | MAE (K) | RMSE (K) | Uncertainty-weighted MAE (K) | Rows |
| --- | ---: | ---: | ---: | ---: |
| `joback` | 26.134000 | 45.894144 | 22.672456 | 5 |
| `molecular_weight_only` | 20.584245 | 24.507742 | 25.312300 | 5 |
| `global_median` | 96.716000 | 121.786295 | 66.226697 | 5 |
| `within_family_constant` | 81.654400 | 97.905602 | 104.711767 | 5 |
| `nearest_homolog` | 78.028000 | 95.160336 | 59.306956 | 5 |
| `shuffled_group_counts` | 146.142000 | 207.989384 | 193.284172 | 5 |

Family margin: `-5.549755` K versus required `+5.0` K (shortfall `10.549755` K).

## Aggregate-positive context (preserved, unchanged)

RESULT-0026 remains aggregate-positive: Joback clears the aggregate margin (28.502118 K over the best non-oracle control) and 7 of 8 held-out family margins on 40 rows. This package records the one failed family as first-class negative memory; it does not weaken or replace the aggregate verdict.

No chemical-design, safety, synthesis, process-design, universal Joback
validation/falsification, or broad property-estimation claim is made.
