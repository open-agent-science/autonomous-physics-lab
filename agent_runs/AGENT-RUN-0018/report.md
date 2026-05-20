# Nuclear Shell-Axis Full-Known Retrospective Audit

**Agent run:** `AGENT-RUN-0018`  
**Task:** `TASK-0310`  
**Evidence class:** retrospective full-known committed-data audit  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Script:** `scripts/run_nuclear_shell_axis_full_known_audit.py`  
**Metrics:** `agent_runs/AGENT-RUN-0018/metrics.json`

## Scope

This sandbox audit fits the shell-axis candidate family on the frozen NMD-0002 residual slice and evaluates it on the full unique committed surface currently available: NMD-0002 plus the post-AME2020 primary holdout rows. It does not score prospective registry entries.

## Dataset Surface

| Surface | Count |
| --- | ---: |
| Training slice | 11 |
| Primary holdout | 295 |
| Full-known unique surface | 306 |

## Candidate Outcomes

| Candidate | Full-known ΔMAE MeV | Holdout ΔMAE MeV | Training ΔMAE MeV | Magic Z ΔMAE MeV | Magic N ΔMAE MeV | Worst regression | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `FULLKNOWN-SHELL-001` | -0.086092 | -0.091504 | +0.059043 | -0.158489 | -0.326992 | +0.104064 (light_a_lt_50) | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-002` | -0.070030 | -0.071641 | -0.026837 | -0.001094 | -0.376547 | +0.148840 (light_a_lt_50) | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-003` | -0.060145 | -0.061969 | -0.011248 | -0.022180 | -0.512894 | +0.259976 (light_a_lt_50) | `PARTIALLY_VALID` |
| `FULLKNOWN-SHELL-004` | +0.127546 | +0.127005 | +0.142063 | +0.459333 | +0.453871 | +0.824735 (registry_repeat_chain_neighbor) | `INCONCLUSIVE` |
| `FULLKNOWN-SHELL-005` | -0.000039 | -0.000047 | +0.000178 | -0.000021 | -0.000197 | +0.000256 (light_a_lt_50) | `INCONCLUSIVE` |
| `FULLKNOWN-SHELL-006` | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 | +0.000000 (none) | `INCONCLUSIVE` |

Negative deltas mean lower retrospective MAE than the frozen baseline. Positive deltas are regressions.

## Controls

- `FULLKNOWN-SHELL-004` is the sign-inverted proton-axis control.
- `FULLKNOWN-SHELL-005` is the shuffled-feature cyclic-shift-5 control.
- `FULLKNOWN-SHELL-006` is the near-null / baseline-reference control.

## Rejected Before Execution

- `FULLKNOWN-SHELL-007` (Free-sigma proton Gaussian): Rejected before execution because sigma tuning is a nonlinear free knob on the 11-row NMD-0002 training slice and would weaken the retrospective audit boundary.
- `FULLKNOWN-SHELL-008` (Per-magic-number offsets): Rejected before execution because one offset per magic number inflates degrees of freedom and risks memorizing the training slice.
- `FULLKNOWN-SHELL-009` (SHELL-SCOUT-001 additive form re-test): Rejected before execution because the additive combined shell-axis form is already preserved as OVERFITTED in the scout synthesis; re-running it here would duplicate a known negative result.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- Candidate coefficients are still fit on the 11-row NMD-0002 residual slice.
- Full-known rows are committed reviewable repository data; this is not a future-measurement reveal.
- Post-AME2020 rows are retrospective time-split evidence, not strict blind prediction.
- Subset deltas can be fragile where row counts are small; worst-regression summaries are preserved.

## Promotion Boundary

- Prediction registry files are not edited.
- Canonical `RESULT-*` files are not edited.
- Claims and knowledge files are not edited.
- Any reveal scoring remains blocked behind a separate maintainer-reviewed source-manifest task.
