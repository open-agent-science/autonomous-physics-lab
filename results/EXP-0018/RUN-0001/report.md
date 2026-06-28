# RESULT-0025 - NMD-0003 GP Residual Extrapolation Replay

**Task:** `TASK-0843`
**Source sandbox run:** `agent_runs/AGENT-RUN-0080/`
**Review tier proposed:** `AGENT_PUBLISHED`
**Best verdict:** `PARTIALLY_VALID`

## Replay

- Max absolute metric drift versus AGENT-RUN-0080: `0.0`.
- Verdict unchanged: `True`.
- Calibration verdict unchanged: `True`.

## Retrospective Holdout Accuracy

- Frozen baseline MAE/RMS: `2.979273` / `4.028345` MeV.
- GP-corrected MAE/RMS: `0.462129` / `1.638935` MeV.
- Best control: `smooth_a_gp`; GP minus best-control margin `1.869312` MeV versus predeclared `0.25` MeV.

## Calibration Boundary

- Calibration verdict: `HEAVY_TAILED_MISCALIBRATED`.
- Empirical 1 sigma coverage: `0.823729` (expected `0.682689`).
- Empirical 2 sigma coverage: `0.966102` (expected `0.9545`).
- RMS standardized residual: `2.826769`.

## Output-Routing Summary

- Canonical destination: `results/EXP-0018/RUN-0001/`.
- Gate A status: `PASS` for a scoped retrospective RESULT candidate if repository validation passes.
- Gate B status: `not attempted`; this is agent-published, not independently validated.
- Claim impact: `none`. Knowledge impact: `none`. Prediction impact: `none`.
- Publication blocker: predictive uncertainty remains miscalibrated, so prediction freeze remains blocked.
