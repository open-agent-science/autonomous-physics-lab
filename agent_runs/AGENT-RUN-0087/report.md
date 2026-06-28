# ThermoML Tb Family-Stratified Transfer

**Task:** `TASK-0851`; **Run:** `AGENT-RUN-0087`
**Verdict:** `TRANSFER_SUPPORTED_IN_SCOPE`

## Scope

The frozen Joback Tb estimator is scored on a value-blind, balanced 40-row audit fixture extracted from the checksum-verified NIST ThermoML archive. APL fits no Joback parameter. Raw archive bytes and a substantial normalized corpus are not committed.

The implementation-fidelity gate passed with 0/25 mismatches.

## Aggregate metrics

| Model/control | MAE (K) | RMSE (K) | uncertainty-weighted MAE (K) |
| --- | ---: | ---: | ---: |
| `joback` | 14.926 | 27.344 | 9.430 |
| `global_median` | 62.081 | 79.099 | 46.529 |
| `molecular_weight_only` | 43.428 | 53.299 | 37.208 |
| `nearest_homolog` | 69.864 | 83.042 | 67.320 |
| `shuffled_group_counts` | 86.815 | 120.770 | 85.833 |
| `within_family_constant` | 50.420 | 62.983 | 45.979 |

Best non-oracle control: `molecular_weight_only`; Joback margin `28.502 K` against a required `5.0 K`.

## Per-family outcome

| Held-out family | Joback MAE (K) | best control | margin (K) | clears |
| --- | ---: | --- | ---: | :---: |
| acids | 23.878 | `global_median` | 20.322 | yes |
| alcohols/phenols | 18.530 | `molecular_weight_only` | 39.095 | yes |
| alkanes/cycloalkanes | 11.540 | `molecular_weight_only` | 24.466 | yes |
| aromatic hydrocarbons | 12.301 | `molecular_weight_only` | 25.359 | yes |
| esters/lactones | 26.134 | `molecular_weight_only` | -5.550 | no |
| ethers | 7.452 | `molecular_weight_only` | 24.812 | yes |
| halocarbons | 14.126 | `global_median` | 32.880 | yes |
| ketones | 5.446 | `molecular_weight_only` | 17.992 | yes |

## Routing

- Gate A: not promoted; bounded sandbox benchmark.
- Gate B: fixture hash, command, code references, engine version, and git commit recorded.
- Claim / knowledge impact: none.
- Limitations: Tb only; 40-row balanced audit slice; family taxonomy and   Joback coverage exclusions are explicit; no universal accuracy claim.
