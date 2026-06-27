# NMD-0003 GP Extrapolation Independent Replay

**Task:** `TASK-0843`
**Source task:** `TASK-0824`
**Source metrics:** `agent_runs/AGENT-RUN-0080/metrics.json`
**Replay command:** `python3 scripts/run_nmd0003_residual_gp.py --output-dir C:\tmp\apl-task0843-replay-output --review-path C:\tmp\apl-task0843-replay-review.md`
**Result-package command:** `python3 scripts/run_nmd0003_residual_gp.py --skip-sandbox-output --no-review --result-out-dir results/EXP-0018/RUN-0001`

## Replay Verdict

The independent replay reproduced the committed TASK-0824 metrics exactly on
the required comparison set. The route is a scoped `AGENT_PUBLISHED`
retrospective RESULT candidate, not a prediction, claim, knowledge entry, or
discovery claim.

## Metric Comparison

| Metric | AGENT-RUN-0080 | TASK-0843 replay | abs delta |
| --- | ---: | ---: | ---: |
| Frozen-baseline holdout MAE (MeV) | `2.979273` | `2.979273` | `0.0` |
| Frozen-baseline holdout RMS (MeV) | `4.028345` | `4.028345` | `0.0` |
| GP-corrected holdout MAE (MeV) | `0.462129` | `0.462129` | `0.0` |
| GP-corrected holdout RMS (MeV) | `1.638935` | `1.638935` | `0.0` |
| GP MAE improvement (MeV) | `2.517144` | `2.517144` | `0.0` |
| GP RMS improvement (MeV) | `2.38941` | `2.38941` | `0.0` |
| Best-control MAE improvement (MeV) | `0.647832` | `0.647832` | `0.0` |
| GP minus best-control margin (MeV) | `1.869312` | `1.869312` | `0.0` |
| Empirical 1-sigma coverage | `0.823729` | `0.823729` | `0.0` |
| Empirical 2-sigma coverage | `0.966102` | `0.966102` | `0.0` |
| RMS standardized residual | `2.826769` | `2.826769` | `0.0` |

- Maximum absolute drift across the required numeric comparison set: `0.0`.
- Verdict unchanged: `CONTROL_SURVIVING_GAIN_MISCALIBRATED_UNCERTAINTY`.
- Calibration verdict unchanged: `HEAVY_TAILED_MISCALIBRATED`.
- Best control unchanged: `smooth_a_gp`.
- Survival margin: replayed GP-minus-best-control margin `1.869312` MeV
  against the predeclared `0.25` MeV margin; clears margin: `True`.

## Gate A Routing

Gate A is treated as `PASS` for a narrow retrospective RESULT candidate:

- deterministic run: replayed from committed code and pinned repository inputs;
- verification block: populated in `results/EXP-0018/RUN-0001/result.yaml`;
- input hashes: config, experiment, hypothesis, task, and holdout fixture
  snapshots are recorded in the result package;
- limitations: retrospective split, single model class, frozen residual surface,
  and miscalibrated uncertainty are explicit;
- engine version and git commit: recorded in the result package;
- schema validation: required before PR publication;
- protected rewrite: no existing `RESULT-*`, `PRED-*`, `CLAIM-*`, `KNOW-*`,
  `TASK-0824`, or `results/golden-results.yaml` artifact is rewritten;
- overclaim guard: result wording stays at "retrospective control-surviving
  accuracy gain with miscalibrated uncertainty";
- dataset provenance: committed NMD-0003/post-AME2020 inputs only; no live fetch.

The result verdict is `PARTIALLY_VALID`: the extrapolation accuracy signal
survives the controls, but uncertainty calibration remains heavy-tailed and
therefore blocks prediction-freeze use.

## Output-Routing Summary

- Canonical destination: `results/EXP-0018/RUN-0001/result.yaml` plus companion
  result package artifacts, with `hypotheses/HYP-0018-nmd0003-gp-extrapolation-replay.yaml`
  and `experiments/EXP-0018-nmd0003-gp-extrapolation-replay.yaml`.
- Gate A status: `PASS` for scoped `AGENT_PUBLISHED` result packaging if final
  repository validation passes.
- Gate B status: `not attempted`; the artifact is not independently validated
  by a separate result-replay gate yet.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Prediction impact: `none`; no `PRED-*` entry and no prediction freeze.
- Publication blockers: calibrated-uncertainty and prediction-freeze decisions
  remain blocked outside this RESULT by the dedicated follow-up path.
