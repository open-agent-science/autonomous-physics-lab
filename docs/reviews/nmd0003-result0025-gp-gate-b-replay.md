# RESULT-0025 NMD-0003 GP Residual Gate B Replay

- Task: `TASK-0864`
- Result: `RESULT-0025`
- Replay command:
  `python3 scripts/run_nmd0003_residual_gp.py --skip-sandbox-output --no-review --result-out-dir <untracked-replay-output>`
- Verdict: `GATE_B_PASS_POINT_METRICS_UNCERTAINTY_BLOCKED`

## Scope

This note records an independent replay of `RESULT-0025`, the retrospective
post-AME2020 NMD-0003 GP residual extrapolation result. It validates the point
estimator metrics and preserves the uncertainty blocker. It does not create or
edit any `PRED-*`, prediction freeze, `CLAIM-*`, or `KNOW-*` artifact.

No GP hyperparameter retuning, future reveal target inspection, holdout-row
mutation, prediction-registry write, or uncertainty-calibration upgrade was
performed.

## Replay Outcome

The replay reproduced the required point metrics and calibration diagnostics at
the published precision. `best_verdict` remains `PARTIALLY_VALID`, because the
accuracy signal survives controls while uncertainty calibration remains
heavy-tailed and miscalibrated.

| Metric | Published | Replay | Abs drift |
| --- | ---: | ---: | ---: |
| holdout rows | `295` | `295` | `0` |
| frozen baseline MAE (MeV) | `2.979273` | `2.979273` | `0.000000` |
| GP-corrected MAE (MeV) | `0.462129` | `0.462129` | `0.000000` |
| GP MAE improvement (MeV) | `2.517144` | `2.517144` | `0.000000` |
| best control | `smooth_a_gp` | `smooth_a_gp` | `0` |
| GP minus best-control margin (MeV) | `1.869312` | `1.869312` | `0.000000` |
| predeclared survival margin (MeV) | `0.250000` | `0.250000` | `0.000000` |
| empirical 1-sigma coverage | `0.823729` | `0.823729` | `0.000000` |
| empirical 2-sigma coverage | `0.966102` | `0.966102` | `0.000000` |
| RMS standardized residual | `2.826769` | `2.826769` | `0.000000` |

## Metadata Comparison

| Metadata field | Published | Replay | Assessment |
| --- | --- | --- | --- |
| `best_verdict` | `PARTIALLY_VALID` | `PARTIALLY_VALID` | match |
| calibration verdict | `HEAVY_TAILED_MISCALIBRATED` | `HEAVY_TAILED_MISCALIBRATED` | match |
| `code_reference` | `physics_lab/engines/nmd0003_residual_gp.py` | same | match |
| `engine_version` | `0.1.0` | `0.1.0` | match |
| config input hash | `faa899ec66b51a1730596be48f558fbda02c95388577b29b30131f85e748a9ec` | same | match |
| experiment input hash | `fc39d43d37ad6f2e55808276547873d6240df2f320eeafb34064e05f030145ee` | same | match |
| hypothesis input hash | `d47217c16705e3f1c70a034e82d234b460978e23fd6e41b42bdd43e9a8d9b7dc` | same | match |
| holdout fixture hash | `47bfe520df8ca4a95c1614192c5da165782b2308ba58110e6832afb1b8151e49` | same | match |
| task input hash | `a0944cdc957afe24a5d07144ddd920b8b0120ec82ca52ae673e3b0ffeca054c2` | current task YAML hash differs | expected lifecycle drift |
| git commit | `ed0f54cf22d129892296207c748830951bcacf11` | current replay commit differs | replay environment drift |

The task hash drift comes from the result-packaging script copying the current
`TASK-0843` YAML into the disposable replay output after publication/closeout.
The committed `RESULT-0025` package still preserves the originally published
input task file. Scientific inputs, fixture hash, verdicts, and metrics match.

## Prediction-Freeze Blocker

Replay does not unblock prediction freeze. The GP point estimator is strong on
this retrospective holdout, but the uncertainty envelope is not calibrated for
future prediction semantics:

- empirical 1-sigma coverage: `0.823729` vs expected `0.682689`;
- empirical 2-sigma coverage: `0.966102` vs expected `0.954500`;
- RMS standardized residual: `2.826769`, far from the well-calibrated target
  near `1.0`;
- calibration verdict remains `HEAVY_TAILED_MISCALIBRATED`.

This matches the dedicated uncertainty adjudication: point-estimator evidence
may be carried forward, but prediction freeze remains blocked until a separate
uncertainty model and freeze task clears.

## Limitations Preserved

- Retrospective post-AME2020 time-split replay, not a strict blind prediction
  reveal.
- One frozen NMD-0003 residual surface and one RBF GP model on `[Z, N]`.
- No model-class sweep or hyperparameter retuning on the holdout.
- No prediction registry write and no future reveal target inspection.
- No claim, knowledge, or prediction artifact is justified by this replay.

## Output Routing

- Canonical destination: `docs/reviews/nmd0003-result0025-gp-gate-b-replay.md`.
- Review tier: review note only; `RESULT-0025` remains unchanged in this PR.
- Gate A: previously `PASS` for `RESULT-0025`.
- Gate B: `PASS` for point metrics with metadata drift recorded.
- Claim impact: none.
- Prediction impact: none; prediction freeze remains blocked.
- Knowledge impact: none.
- Result impact: no mutation.
- Publication blocker: calibrated uncertainty and prediction freeze remain
  blocked outside this replay; maintainer decision required for any later
  review-tier metadata update.

## Final Verdict

`RESULT-0025` point-estimator metrics replay exactly: GP-corrected holdout MAE
is `0.462129` MeV versus frozen baseline `2.979273` MeV, clearing the best
control by `1.869312` MeV. The uncertainty calibration blocker is also
reproduced unchanged, so the result remains retrospective `PARTIALLY_VALID`
evidence only.
