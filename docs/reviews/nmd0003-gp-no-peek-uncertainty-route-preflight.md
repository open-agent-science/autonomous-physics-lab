# NMD-0003 GP No-Peek Uncertainty Route Preflight

Task: `TASK-0865`
Primary evidence: `docs/reviews/nmd0003-gp-uncertainty-calibration-adjudication.md`, `RESULT-0025`, and `agent_runs/AGENT-RUN-0080/metrics.json`
Verdict: `UNCERTAINTY_ROUTE_CONDITIONAL_GO_TASK_0827_STILL_BLOCKED`

## Executive Decision

A future uncertainty-calibration metric task is defensible, but prediction freeze is not. `RESULT-0025` remains point-estimator evidence only: the GP residual model has a strong retrospective post-AME2020 MAE gain, but its predictive uncertainty is still heavy-tailed and miscalibrated. `TASK-0827` should therefore stay blocked until a later task freezes a train-only uncertainty route, scores it without holdout retuning, and shows that both central coverage and tail behavior meet predeclared thresholds.

This preflight does not create `PRED-*`, `RESULT-*`, `CLAIM-*`, or `KNOW-*` artifacts. It records the allowed route families, leakage risks, stop conditions, and future task shape.

## Evidence Boundary

Used inputs:

- `docs/reviews/nmd0003-gp-uncertainty-calibration-adjudication.md`
- `results/EXP-0018/RUN-0001/result.yaml` (`RESULT-0025`)
- `agent_runs/AGENT-RUN-0080/metrics.json`
- `tasks/TASK-0827-extrapolation-model-comparison-and-freeze-for-reveal.yaml`
- `docs/nuclear-prediction-reveal-protocol.md`

No post-AME2020 target values or future target values were used to choose a new calibration rule in this task. The post-AME2020 holdout diagnostics are treated only as the already-recorded blocker that motivates a later predeclared route test.

## Starting Diagnostics

| Diagnostic | Train-only LOO | Post-AME2020 holdout |
| --- | ---: | ---: |
| count | `2309` | `295` |
| RMS standardized residual | `1.089510` | `2.826769` |
| abs p68 | `0.652357` | `0.725497` |
| abs p95 | `1.705723` | `1.707069` |
| abs p99 | `4.100630` | `3.457904` |
| abs max | `19.017237` | `46.302384` |
| fraction beyond 2 sigma | `0.038545` | `0.033898` |
| fraction beyond 3 sigma | `0.018623` | `0.016949` |

The blocker is the central/tail mismatch. The holdout 1-sigma coverage is already too high (`0.823729` against expected `0.682689`), while RMS standardized residual is also too high (`2.826769`). Uniform interval inflation cannot fix both at once.

## Candidate No-Peek Route Families

| Route family | Train-only inputs | Leakage risk | Stop condition | Future success condition |
| --- | --- | --- | --- | --- |
| Region-stratified scale or quantile calibration | LOO residuals, LOO predictive sigmas, and predeclared labels such as `a_band`, `neutron_excess_band`, and `magic_neighborhood` | High if regions or intersections are selected after reading holdout failures | Stop if a stratum lacks enough LOO examples, if intersections are chosen from holdout outliers, or if the rule only inflates all intervals | Before holdout scoring, freeze region rules and minimum counts; pass only if 1-sigma and 2-sigma coverage move toward nominal while tail metrics do not worsen |
| Robust global tail model | LOO standardized residual distribution only, using a predeclared Student-t, winsorized, or mixture-tail rule | Medium if tail parameters are tuned to the known holdout outlier ledger | Stop if the fitted tail mostly reacts to one or two LOO extremes or produces unbounded interval width | Pass only if tail exceedance/RMS behavior improves without making the central interval substantially less calibrated |
| Train-only conformal residual quantiles | LOO absolute residuals or sigma-normalized residual quantiles, optionally stratified by predeclared region labels | Medium if conformal bins are introduced after seeing holdout region failures | Stop if conformal intervals become so wide that the point-estimator gain is no longer operationally useful, or if bins are underpopulated | Pass only if nominal 68/95 percent coverage is met by a predeclared conformal rule with bounded interval-width inflation |
| Explicit abstention or exclusion policy | Source-independent support labels from training geometry, model support, or predeclared nuclear regions | Very high if exclusions are chosen from the post-AME2020 outlier ledger | Stop if any target is excluded because it was a known holdout outlier or because its revealed error is large | Pass only if the abstention rule is value-free, target-list coverage remains meaningful, and excluded regions are reported as non-predicted rather than silently omitted |

## Recommended Future Route

Use a small, predeclared comparison between three train-only candidates:

1. `global_robust_tail`: fit one robust tail or Student-t style calibration on LOO standardized residuals.
2. `region_quantile_min_count`: apply predeclared region quantile calibration only for labels with a minimum LOO count; otherwise fall back to the global robust route.
3. `conformal_global`: use a global train-only conformal quantile route as a conservative baseline.

The future task must freeze these definitions in a config before scoring the post-AME2020 holdout. It must not add regions, exclusions, thresholds, or fallback rules after inspecting holdout performance.

## Required Inputs For The Future Metric Task

- LOO predictions, residuals, predictive sigmas, and nuclide identifiers from the frozen GP training surface.
- Predeclared region labels computed from `Z`, `N`, `A`, neutron excess, and magic-neighborhood definitions already used in the adjudication note.
- Frozen post-AME2020 holdout table only for after-freeze scoring.
- A deterministic calibration runner that writes metrics and a review note, but no `PRED-*` entries.
- A config file that declares route families, minimum stratum counts, interval-width limits, and pass/fail thresholds before scoring.

## Predeclared Stop Conditions

Stop with `UNCERTAINTY_ROUTE_STOP` if any of these occur:

- The route needs post-AME2020 holdout values to select regions, thresholds, exclusions, or tail parameters.
- Region-stratified bins are too sparse for stable LOO quantiles and no global fallback is predeclared.
- Any route improves the tail only by making central coverage more overcovered than the current blocker.
- Any route excludes future targets based on a known or suspected revealed error.
- Interval widths inflate so much that the output is no longer useful for `PRED-*` uncertainty semantics.
- The calibrated uncertainty route cannot be reproduced from committed inputs without live external fetches.

## Predeclared Success Conditions

A future route may unblock only if all are true in the later metric task:

- No-peek: all route choices are frozen from training/LOO diagnostics before holdout scoring.
- Central calibration: 1-sigma and 2-sigma coverage both move closer to nominal than the uncalibrated GP, or a conformal route meets its stated nominal coverage.
- Tail control: RMS standardized residual or the stated robust-tail diagnostic improves materially without hiding named outliers.
- Sharpness: median and p90 interval widths remain within the predeclared inflation limits.
- Coverage surface: any abstained/excluded target class is reported explicitly, with no silent target removal.
- Scope: the output remains a calibration audit, not a prediction freeze or claim.

## TASK-0827 Decision

`TASK-0827` remains blocked. The GP may enter a future model-comparison/freeze task only as a point estimator unless the later calibration metric task passes the success conditions above. No `PRED-*` entries should be frozen from `RESULT-0025` uncertainty values now.

## Output-Routing Summary

- Task verdict: `UNCERTAINTY_ROUTE_CONDITIONAL_GO_TASK_0827_STILL_BLOCKED`.
- Canonical destination: `docs/reviews/nmd0003-gp-no-peek-uncertainty-route-preflight.md`.
- Review tier: none; this is blocker/preflight memory.
- Gate A status: not applicable; no RESULT or PRED artifact is produced.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: none; `RESULT-0025` remains point-estimator evidence only until a later task validates uncertainty calibration.
- Prediction impact: none; no prediction entries are created or modified.
- Blocker: `TASK-0827` stays blocked pending a future no-peek calibration metric task.
