# Nuclear Shell-Axis Specificity Controls

**Agent run:** `AGENT-RUN-0020`  
**Task:** `TASK-0317`  
**Evidence class:** retrospective full-known specificity-control audit  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_shell_axis_specificity_controls.py`  
**Metrics:** `agent_runs/AGENT-RUN-0020/metrics.json`

## Scope

This sandbox audit compares the three primary TASK-0310 shell-axis candidates against predeclared low-complexity non-shell controls on the same committed training, primary-holdout, and full-known surfaces. It does not score prospective predictions or promote claims.

## Specificity Verdict

`SHELL_SPECIFIC_BUT_BOUNDED`

Some non-shell controls improve one or both key surfaces, but they do not match the best shell-axis candidate on both full-known and primary-holdout MAE.

| Comparator | Candidate | Full-known ΔMAE | Holdout ΔMAE |
| --- | --- | ---: | ---: |
| Best shell-axis | `FULLKNOWN-SHELL-001` | -0.086092 | -0.091504 |
| Best non-shell control | `SPECIFICITY-CONTROL-001` | -0.049223 | -0.049534 |

Negative deltas mean lower retrospective MAE than the frozen baseline. Positive deltas are regressions.

## Shell-Axis Candidates

| Candidate | Full-known ΔMAE | Holdout ΔMAE | Training ΔMAE | Magic-Z ΔMAE | Magic-N ΔMAE | Light ΔMAE | Worst regression |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `FULLKNOWN-SHELL-001` | -0.086092 | -0.091504 | +0.059043 | -0.158489 | -0.326992 | +0.104064 | +0.104064 (light_a_lt_50) |
| `FULLKNOWN-SHELL-002` | -0.070030 | -0.071641 | -0.026837 | -0.001094 | -0.376547 | +0.148840 | +0.148840 (light_a_lt_50) |
| `FULLKNOWN-SHELL-003` | -0.060145 | -0.061969 | -0.011248 | -0.022180 | -0.512894 | +0.259976 | +0.259976 (light_a_lt_50) |

## Non-Shell Controls

| Candidate | Full-known ΔMAE | Holdout ΔMAE | Training ΔMAE | Magic-Z ΔMAE | Magic-N ΔMAE | Light ΔMAE | Worst regression |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `SPECIFICITY-CONTROL-000` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 (none) |
| `SPECIFICITY-CONTROL-001` | -0.049223 | -0.049534 | -0.040867 | -0.013187 | -0.074624 | +0.038573 | +0.038573 (light_a_lt_50) |
| `SPECIFICITY-CONTROL-002` | -0.023366 | -0.024623 | +0.010329 | -0.040672 | -0.040074 | -0.003718 | +0.010329 (training_slice) |
| `SPECIFICITY-CONTROL-003` | +0.013189 | +0.016965 | -0.088079 | +0.049766 | -0.009468 | +0.168159 | +0.168159 (light_a_lt_50) |
| `SPECIFICITY-CONTROL-004` | +0.028133 | +0.033245 | -0.108958 | +0.234682 | +0.269621 | +0.178236 | +0.289878 (magic_any) |

## Interpretation

The specificity outcome is bounded by the TASK-0316 stability result. A favorable specificity result does not remove coefficient fragility, and an unfavorable one would demote the shell-axis lane to a narrow retrospective artifact. In either case, this output remains sandbox-only.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- All fitted coefficients use only the 11-row NMD-0002 residual slice.
- The full-known surface is committed repository data; this is not a future-measurement reveal.
- Low-degree controls are diagnostic, not new candidate formulas for promotion.
- TASK-0316 coefficient fragility remains a hard limitation even if specificity controls are favorable.

## Promotion Boundary

- Prediction registry files are not edited.
- Canonical `RESULT-*` files are not edited.
- Claims and knowledge files are not edited.
- No future measurement reveal is scored.
