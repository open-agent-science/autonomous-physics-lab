# ThermoML Tb Bounded Joback Transfer Result

Task: `TASK-0869`
Source sandbox run: `AGENT-RUN-0087` from `TASK-0851`
Canonical result: `RESULT-0026` (`EXP-0020` / `RUN-0001`)

## Scope

This package promotes the checksum-pinned ThermoML Tb family-stratified transfer audit into an agent-published, bounded result artifact. The scored property is normal boiling temperature only. The committed fixture contains 40 factual audit rows, five rows in each of eight predeclared chemical families. Raw ThermoML archive bytes and a substantial normalized corpus are not committed.

## Aggregate Outcome

| Model/control | MAE (K) | RMSE (K) | uncertainty-weighted MAE (K) |
| --- | ---: | ---: | ---: |
| `joback` | 14.926 | 27.344 | 9.430 |
| `molecular_weight_only` | 43.428 | 53.299 | 37.208 |

Best non-oracle control: `molecular_weight_only`. Joback margin: `28.502 K` against the required `5.0 K` aggregate margin.

## Family Outcome

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

## Rights Boundary

The source route is the NIST TRC ThermoML Archive, DOI `10.18434/mds2-2422`, with published archive SHA-256 `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2`. The result uses only the committed bounded factual extract with attribution. It does not vendor the archive bytes, broaden the normalized corpus, or relicense the source compilation.

## Output Routing

- Verdict: `VALID_IN_RANGE` for the bounded 40-row Tb fixture.
- Canonical destination: `results/EXP-0020/RUN-0001/result.yaml`.
- Review tier: `AGENT_PUBLISHED`; Gate B independent replay is still required before any tier upgrade.
- Gate A: PASS by deterministic runner metadata, fixture/input hashes, verification block, source-rights boundary, and schema validation.
- Claim impact: none.
- Knowledge impact: none.
- Limitation to preserve: esters/lactones failed the family-survival margin; no broad property-estimation or chemical-design claim follows.
