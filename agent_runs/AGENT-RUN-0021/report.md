# Nuclear Shell-Axis Magic-Axis Asymmetry Audit

**Agent run:** `AGENT-RUN-0021`  
**Task:** `TASK-0321`  
**Evidence class:** retrospective full-known magic-axis asymmetry audit  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_shell_axis_magic_asymmetry_audit.py`  
**Metrics:** `agent_runs/AGENT-RUN-0021/metrics.json`

## Scope

This sandbox audit separates magic-N, magic-Z, near-magic, double-magic, and deterministic non-magic A-matched control behavior for the committed TASK-0310 candidate family. It does not score future measurements or promote claims.

## Subset Counts

| Subset | Rows | Sparse warning |
| --- | ---: | --- |
| `primary_holdout` | 295 | no |
| `magic_n` | 17 | no |
| `magic_z` | 13 | no |
| `near_magic` | 126 | no |
| `double_magic` | 5 | yes |
| `non_magic_matched_magic_n` | 17 | no |
| `non_magic_matched_magic_z` | 13 | no |
| `non_magic_matched_near_magic` | 126 | no |
| `non_magic_matched_double_magic` | 5 | yes |

Subsets with fewer than 10 rows are explicit sparse diagnostics.

## Directional Verdict

`NEUTRON_DOMINANT_BUT_SPARSE`

Primary shell-axis candidates favor magic-N more than magic-Z, but magic subsets are sparse and the result remains sandbox-only.

## Candidate Outcomes

| Candidate | Magic-N ΔMAE | Magic-Z ΔMAE | Near-magic ΔMAE | Double-magic ΔMAE | Matched-N ΔMAE | Matched-Z ΔMAE | Label |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `FULLKNOWN-SHELL-001` | -0.326992 | -0.158489 | -0.224264 | -0.412072 | -0.197071 | +0.057011 | `NEUTRON_DOMINANT` |
| `FULLKNOWN-SHELL-002` | -0.376547 | -0.001094 | -0.169194 | -0.293656 | -0.190732 | +0.025462 | `NEUTRON_DOMINANT` |
| `FULLKNOWN-SHELL-003` | -0.512894 | -0.022180 | -0.156882 | -0.323638 | -0.395316 | +0.052776 | `NEUTRON_DOMINANT` |
| `FULLKNOWN-SHELL-004` | +0.453871 | +0.459333 | +0.322204 | +0.697641 | +0.197071 | +0.079456 | `NO_MAGIC_AXIS_SUPPORT` |
| `FULLKNOWN-SHELL-005` | -0.000197 | -0.000021 | -0.000216 | -0.000151 | -0.000120 | +0.000011 | `SYMMETRIC_OR_TIED` |
| `FULLKNOWN-SHELL-006` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | `NO_MAGIC_AXIS_SUPPORT` |

Negative deltas mean lower retrospective MAE than the frozen baseline. Positive deltas are regressions.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- Magic-N, magic-Z, and double-magic subsets are sparse and cannot carry standalone conclusions.
- Matched controls are deterministic A-nearest non-magic diagnostics, not causal controls.
- All coefficients are fit on the 11-row NMD-0002 residual slice.
- The full-known surface is committed repository data; this is not a future-measurement reveal.

## Promotion Boundary

- Prediction registry files are not edited.
- Canonical `RESULT-*` files are not edited.
- Claims and knowledge files are not edited.
- No future measurement reveal is scored.
