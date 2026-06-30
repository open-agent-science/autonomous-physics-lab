# AGENT-RUN-0089 - NMD-0003 GP Uncertainty Calibration Audit

**Task:** `TASK-0899`
**Benchmark:** `nmd0003-gp-uncertainty-calibration-audit`
**Source:** `TASK-0824` / `AGENT-RUN-0080` (merged GP engine `physics_lab/engines/nmd0003_residual_gp.py`)
**Verdict:** `NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED`
**Prediction-freeze impact:** `unchanged_task_0827_remains_blocked`

## Summary

This is a *no-peek* calibration audit of the merged NMD-0003 residual GP predictive uncertainty. The calibration config is frozen from train / leave-one-out (LOO) diagnostics only, using exactly the three `TASK-0865` route families. The post-AME2020 holdout (`295` rows; `0` used for calibration) is scored only after the config is frozen. The merged GP is not re-fit or modified. No PRED/RESULT/CLAIM/KNOW artifact is created and RESULT-0025 is unchanged.

## Provenance (Gate-B-replayable)

- Pinned command: `python3 scripts/run_nmd0003_gp_calibration_audit.py`.
- Code reference: `physics_lab/engines/nmd0003_gp_calibration_audit.py`; engine version `0.1.0`; physics_lab `0.1.0`.
- git commit: `ef12778c67ba349759d97b31611602308503c78e`.
- Determinism: no random seed consumed; closed-form GP fit and LOO identities. Re-running reproduces identical metrics.
- Input file hashes (sha256):
  - dataset `f36ca012704ad8d5ffd039f2b8f01b5553690685d447aee3bab0f9983edf9d52`
  - frozen gate `2988c2eb28e0e1bee783bd4824a9680313b5ef81f1e9ae96698893e4525b8cd2`
  - post-AME2020 holdout `47bfe520df8ca4a95c1614192c5da165782b2308ba58110e6832afb1b8151e49`

## Frozen config (set from train/LOO diagnostics BEFORE holdout scoring)

- `frozen_before_holdout_scoring`: `True`.
- Route preflight: `TASK-0865`; region partition: `a_band`; minimum region LOO count: `40`.
- Train-only LOO standardized residual: RMS `1.08951`, abs p68 `0.652357`, abs p95 `1.814057`, abs p99 `4.10063`, abs max `19.017237` over `2309` rows.

### Family 1 - `global_robust_tail` (Student-t on LOO standardized residuals)

- Student-t `nu` = `3` (LOO abs p95/p68 ratio `2.780771` matched to the Student-t ratio); scale `0.545048`.
- Frozen interval multipliers: 1-sigma `0.652357`, 2-sigma `1.802377` (multipliers on the raw GP 1-sigma).

### Family 2 - `region_quantile_min_count` (per-`a_band` LOO quantiles)

- Partition `a_band`; minimum LOO count `40`; fallback family `global_robust_tail`.

| region | LOO count | uses fallback | 1-sigma mult | 2-sigma mult |
| --- | ---: | --- | ---: | ---: |
| `light_A_lt_60` | `384` | `False` | `1.333223` | `4.929897` |
| `medium_60_le_A_lt_140` | `773` | `False` | `0.701762` | `1.411984` |
| `heavy_A_ge_140` | `1152` | `False` | `0.45567` | `1.103774` |

### Family 3 - `conformal_global` (global LOO absolute-standardized quantiles)

- Frozen interval multipliers: 1-sigma `0.652357`, 2-sigma `1.814057`.

### Predeclared success conditions (fixed before scoring)

- Central calibration: |1-sigma coverage - 0.682689| <= `0.05` AND |2-sigma coverage - 0.9545| <= `0.03`.
- Tail control: `0.85` <= RMS standardized residual <= `1.2`.
- Sharpness: median width inflation <= `3.0` AND p90 width inflation <= `4.0`.
- Coverage surface: every fallback/abstained region reported explicitly; no holdout target silently dropped.
- Scope: calibration audit only; TASK-0827 stays blocked unless all conditions pass.

## Holdout scoring (AFTER freeze)

Uncalibrated raw-GP reference: 1-sigma coverage `0.823729` (nominal `0.682689`), 2-sigma `0.966102` (nominal `0.9545`), RMS standardized residual `2.826769`, abs max `46.302384`.

| family | 1-sigma cov | 2-sigma cov | RMS z | median width infl | p90 width infl | all pass |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `global_robust_tail` | `0.623729` | `0.959322` | `4.333163` | `0.652357` | `0.652357` | `False` |
| `region_quantile_min_count` | `0.654237` | `0.949153` | `4.003043` | `0.701762` | `1.333223` | `False` |
| `conformal_global` | `0.623729` | `0.959322` | `4.333163` | `0.652357` | `0.652357` | `False` |

- Any family passes the predeclared success conditions: `False`.
- Passing families: `none`.
- Tripped stop conditions: `none`.

### Holdout tail outlier ledger (top 5 by |standardized residual|)

| nuclide | Z | N | A | corrected residual (MeV) | raw sigma (MeV) | z | a_band | eta band | magic |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| `Ga-84` | `31` | `53` | `84` | `26.33775` | `0.568821` | `46.302384` | `medium_60_le_A_lt_140` | `high_eta_ge_0_25` | `not_near_magic` |
| `Si-23` | `14` | `9` | `23` | `4.121917` | `1.019401` | `4.043471` | `light_A_lt_60` | `low_eta_lt_0_15` | `near_magic_within_2` |
| `P-26` | `15` | `11` | `26` | `2.722282` | `0.718036` | `3.791288` | `light_A_lt_60` | `low_eta_lt_0_15` | `not_near_magic` |
| `Si-24` | `14` | `10` | `24` | `2.317138` | `0.674248` | `3.436624` | `light_A_lt_60` | `low_eta_lt_0_15` | `near_magic_within_2` |
| `Sc-51` | `21` | `30` | `51` | `-1.498195` | `0.482504` | `-3.105043` | `light_A_lt_60` | `mid_0_15_le_eta_lt_0_25` | `near_magic_within_2` |

## Verdict and prediction-freeze impact

- Audit verdict: `NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED`.
- Prediction-freeze impact: `unchanged_task_0827_remains_blocked`.
- No frozen route family meets the predeclared success conditions, so `TASK-0827` stays blocked. This is preserved as honest negative/blocker memory; the config was not tuned to the holdout.

## Limitations

- Calibration audit only: no PRED/RESULT/CLAIM/KNOW artifact is created and RESULT-0025 is not modified.
- Retrospective post-AME2020 time-split holdout, not a strict blind prediction reveal.
- Single GP model class (RBF on [Z, N] residuals) and one frozen liquid-drop baseline; a different baseline or model would shift the residual surface and the LOO diagnostics.
- Three predeclared TASK-0865 route families only; no broader calibration-method search is performed (by design, to stay no-peek).
- LOO diagnostics use the exact closed-form GP leave-one-out identities on the cached training kernel; they characterize the training surface and need not match the heavier-tailed holdout, which is exactly what this audit measures.

## Output-routing summary

- Task verdict: `NO_PEEK_CALIBRATION_FAIL_TASK_0827_STILL_BLOCKED`.
- Scope: calibration audit only.
- Canonical destination: `sandbox_agent_run_plus_review_note` (`agent_runs/AGENT-RUN-0089/` plus this review note).
- Review tier: none; sandbox blocker/calibration memory.
- Gate A status: not attempted (no RESULT/PRED artifact). Gate B: not attempted; the run is deterministic and replayable from committed inputs.
- Claim impact: `none`. Knowledge impact: `none`. Result impact: `none` (RESULT-0025 unchanged). Prediction impact: `none`.
- Prediction-freeze impact: `unchanged_task_0827_remains_blocked`; `TASK-0827` stays blocked unless the predeclared success conditions pass.
