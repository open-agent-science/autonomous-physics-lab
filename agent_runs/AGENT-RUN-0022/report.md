# Nuclear Shell-Axis Light-Nuclei Regression Audit

**Agent run:** `AGENT-RUN-0022`
**Task:** `TASK-0320`
**Evidence class:** retrospective committed-data light-regression audit
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`
**Script:** `scripts/run_nuclear_shell_axis_light_regression_audit.py`
**Metrics:** `agent_runs/AGENT-RUN-0022/metrics.json`

## Scope

This sandbox audit isolates the light `A<50` failure mode for the three primary shell-axis candidates from TASK-0310. It uses committed repository data only and does not tune a corrective term.

## Matched Subset Rule

first N committed rows with A >= 50 sorted by A, Z, N, row_id; N equals the light A<50 row count

## Candidate Outcomes

| Candidate | Light delta MAE MeV | Light regress rows | Matched delta MAE MeV | Matched regress rows | Worst light row regression MeV |
| --- | ---: | ---: | ---: | ---: | ---: |
| `FULLKNOWN-SHELL-001` | +0.104064 | 15/24 | -0.096672 | 13/24 | 1.162736 |
| `FULLKNOWN-SHELL-002` | +0.148840 | 15/24 | -0.026320 | 13/24 | 1.754815 |
| `FULLKNOWN-SHELL-003` | +0.259976 | 15/24 | +0.047315 | 13/24 | 1.604907 |

Positive deltas mean the shell-axis correction increased MAE relative to the frozen baseline.

Domain recommendation: `WARNING_ZONE`.

## Worst Light Row Regressions

### `FULLKNOWN-SHELL-001`

| Nuclide | Z | N | A | Surface | Delta abs error MeV | Baseline abs MeV | Candidate abs MeV |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `Ca-40` | 20 | 20 | 40 | nmd_0002_training_slice | 1.162736 | 2.358333 | 3.521069 |
| `Ca-36` | 20 | 16 | 36 | post_ame2020_primary_holdout | 1.162736 | 1.474376 | 2.637112 |
| `O-17` | 8 | 9 | 17 | nmd_0002_training_slice | 1.162736 | 1.263248 | 2.425984 |
| `K-36` | 19 | 17 | 36 | post_ame2020_primary_holdout | 1.026111 | 0.292845 | 1.318956 |
| `Ne-24` | 10 | 14 | 24 | post_ame2020_primary_holdout | 0.705235 | 2.519621 | 3.224856 |
| `Ar-36` | 18 | 18 | 36 | post_ame2020_primary_holdout | 0.705235 | 2.175098 | 2.880333 |

### `FULLKNOWN-SHELL-002`

| Nuclide | Z | N | A | Surface | Delta abs error MeV | Baseline abs MeV | Candidate abs MeV |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `Ca-40` | 20 | 20 | 40 | nmd_0002_training_slice | 1.754815 | 2.358333 | 4.113148 |
| `O-17` | 8 | 9 | 17 | nmd_0002_training_slice | 1.548619 | 1.263248 | 2.811867 |
| `Ti-43` | 22 | 21 | 43 | post_ame2020_primary_holdout | 0.939285 | 4.442511 | 5.381796 |
| `O-16` | 8 | 8 | 16 | nmd_0002_training_slice | 0.785948 | 0.484434 | 1.270381 |
| `Ar-36` | 18 | 18 | 36 | post_ame2020_primary_holdout | 0.645560 | 2.175098 | 2.820658 |
| `Cl-36` | 17 | 19 | 36 | post_ame2020_primary_holdout | 0.502763 | 1.204897 | 1.707660 |

### `FULLKNOWN-SHELL-003`

| Nuclide | Z | N | A | Surface | Delta abs error MeV | Baseline abs MeV | Candidate abs MeV |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `Ca-40` | 20 | 20 | 40 | nmd_0002_training_slice | 1.604907 | 2.358333 | 3.963241 |
| `S-36` | 16 | 20 | 36 | post_ame2020_primary_holdout | 1.604907 | 3.327781 | 4.932688 |
| `Cl-36` | 17 | 19 | 36 | post_ame2020_primary_holdout | 1.416326 | 1.204897 | 2.621223 |
| `Ti-43` | 22 | 21 | 43 | post_ame2020_primary_holdout | 1.416326 | 4.442511 | 5.858837 |
| `O-17` | 8 | 9 | 17 | nmd_0002_training_slice | 1.416326 | 1.263248 | 2.679574 |
| `Si-24` | 14 | 10 | 24 | post_ame2020_primary_holdout | 0.973425 | 0.411095 | 1.384520 |

## Interpretation

All three primary shell-axis candidates regress the light `A<50` subset. The matched non-light control subset is preserved so the result is not silently folded into aggregate full-known improvements.

This is negative sandbox evidence for the current shell-axis scope. It should constrain future work before any expansion or reveal scoring.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- Primary shell-axis coefficients are inherited from the committed TASK-0310 setup and are not tuned here.
- The matched non-light subset is deterministic and row-count matched, not a statistical bootstrap.
- Full-known rows are committed reviewable repository data; this is not a future-measurement reveal.
- Negative light-zone evidence is preserved even when aggregate shell-axis metrics improve elsewhere.

## Promotion Boundary

- Prediction registry files are not edited.
- Canonical `RESULT-*` files are not edited.
- Claims and knowledge files are not edited.
- The audit is sandbox-only and does not score `PRED-0063` through `PRED-0068`.
