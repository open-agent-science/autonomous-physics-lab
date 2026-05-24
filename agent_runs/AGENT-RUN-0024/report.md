# Nuclear Shell-Axis Neutron-Rich Tail Audit

**Agent run:** `AGENT-RUN-0024`
**Task:** `TASK-0324`
**Evidence class:** retrospective committed-data neutron-rich tail audit
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`
**Script:** `scripts/run_nuclear_shell_axis_neutron_rich_tail_audit.py`
**Metrics:** `agent_runs/AGENT-RUN-0024/metrics.json`

## Scope

This sandbox audit isolates the neutron-rich high-error tail for the three primary shell-axis candidates from TASK-0310. It uses committed repository data only and does not tune a corrective term.

## Deterministic Subset Rules

- Neutron-rich: (N - Z) / A >= 0.25; this matches the TASK-0315 neutron_rich_high subset rule.
- High-error: baseline_abs_error_mev >= 75th percentile of the full-known committed surface (6.110141840131 MeV).
- Matched control: for each neutron-rich high-error row sorted by descending baseline absolute error, select one unused non-neutron-rich high-error row minimizing baseline-error distance, then A distance, source mismatch, Z distance, and row_id.

## Candidate Outcomes

| Candidate | Tail delta MAE MeV | Tail delta RMSE MeV | Tail improved rows | Drop largest 2 tail delta MAE MeV | Matched delta MAE MeV |
| --- | ---: | ---: | ---: | ---: | ---: |
| `FULLKNOWN-SHELL-001` | -0.537487 | -0.524949 | 20/20 | -0.519230 | -0.407744 |
| `FULLKNOWN-SHELL-002` | -0.355659 | -0.394825 | 17/20 | -0.308976 | -0.433131 |
| `FULLKNOWN-SHELL-003` | -0.429173 | -0.483854 | 19/20 | -0.369228 | -0.618650 |

Negative deltas mean the shell-axis correction reduced error relative to the frozen baseline.

Domain recommendation: `OUTLIER_DIAGNOSTIC`.

## Top Tail Delta Contributors

### `FULLKNOWN-SHELL-001`

| Nuclide | Z | N | A | Delta abs error MeV | Contribution to MAE MeV | Baseline abs MeV | Candidate abs MeV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `Ni-75` | 28 | 47 | 75 | -1.162736 | -0.058137 | 9.567077 | 8.404341 |
| `Ca-54` | 20 | 34 | 54 | -1.162736 | -0.058137 | 8.144288 | 6.981552 |
| `In-132` | 49 | 83 | 132 | -1.026111 | -0.051306 | 17.874900 | 16.848789 |
| `In-131` | 49 | 82 | 131 | -1.026111 | -0.051306 | 17.519141 | 16.493030 |
| `In-134` | 49 | 85 | 134 | -1.026111 | -0.051306 | 17.164453 | 16.138342 |
| `In-133` | 49 | 84 | 133 | -1.026111 | -0.051306 | 16.587561 | 15.561450 |

### `FULLKNOWN-SHELL-002`

| Nuclide | Z | N | A | Delta abs error MeV | Contribution to MAE MeV | Baseline abs MeV | Candidate abs MeV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `In-131` | 49 | 82 | 131 | -1.548619 | -0.077431 | 17.519141 | 15.970522 |
| `In-132` | 49 | 83 | 132 | -1.366651 | -0.068333 | 17.874900 | 16.508248 |
| `Cu-78` | 29 | 49 | 78 | -1.366651 | -0.068333 | 12.066053 | 10.699401 |
| `In-133` | 49 | 84 | 133 | -0.939285 | -0.046964 | 16.587561 | 15.648276 |
| `Ni-75` | 28 | 47 | 75 | -0.569705 | -0.028485 | 9.567077 | 8.997372 |
| `In-134` | 49 | 85 | 134 | -0.502763 | -0.025138 | 17.164453 | 16.661690 |

### `FULLKNOWN-SHELL-003`

| Nuclide | Z | N | A | Delta abs error MeV | Contribution to MAE MeV | Baseline abs MeV | Candidate abs MeV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `In-131` | 49 | 82 | 131 | -1.604907 | -0.080245 | 17.519141 | 15.914233 |
| `In-132` | 49 | 83 | 132 | -1.416326 | -0.070816 | 17.874900 | 16.458574 |
| `Cu-78` | 29 | 49 | 78 | -1.416326 | -0.070816 | 12.066053 | 10.649727 |
| `In-133` | 49 | 84 | 133 | -0.973425 | -0.048671 | 16.587561 | 15.614135 |
| `Ga-83` | 31 | 52 | 83 | -0.973425 | -0.048671 | 9.735227 | 8.761802 |
| `Ga-84` | 31 | 53 | 84 | -0.521037 | -0.026052 | 37.636806 | 37.115769 |

## Interpretation

The neutron-rich high-error tail remains favorable for all three primary shell-axis candidates after removing the largest one or two baseline-error rows. The effect is therefore not solely a single-row artifact, but it remains a subset diagnostic on retrospective data.

The matched non-neutron-rich high-error control is included so the tail result is not silently treated as a global support statement.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- Primary shell-axis coefficients are inherited from the committed TASK-0310 setup and are not tuned here.
- The high-error cutoff is deterministic but post hoc over the committed full-known surface.
- The matched non-neutron-rich subset is deterministic and row-count matched, not a statistical bootstrap.
- Full-known rows are committed reviewable repository data; this is not a future-measurement reveal.
- Light-nuclei regression and coefficient fragility remain active limitations for all shell-axis interpretation.

## Promotion Boundary

- Prediction registry files are not edited.
- Canonical `RESULT-*` files are not edited.
- Claims and knowledge files are not edited.
- The audit is sandbox-only and does not score `PRED-0063` through `PRED-0068`.
