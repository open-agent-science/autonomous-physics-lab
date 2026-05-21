# Nuclear Shell-Axis Coefficient Stability Audit

**Agent run:** `AGENT-RUN-0019`
**Task:** `TASK-0316`
**Evidence class:** retrospective committed-data coefficient stability audit
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`
**Script:** `scripts/run_nuclear_shell_axis_stability_audit.py`

## Scope

This sandbox audit stress-tests whether the TASK-0310 shell-axis coefficients survive deterministic resampling of the 11-row NMD-0002 fit surface. It does not fetch live data, score prediction registry entries, or promote claims.

## Resampling Design

- Leave-one-out / jackknife: 11 deterministic fits.
- Small resamples: all 165 deterministic 8-of-11 training-row combinations.
- Evaluation surfaces: NMD-0002 training slice, post-AME2020 primary holdout, and full-known unique committed surface.

## Candidate Summary

| Candidate | Full-fit coeff | LOO coeff range | 8-of-11 coeff range | LOO holdout Δ range | 8-of-11 holdout Δ range | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `STABILITY-SHELL-001` | 1.162736 | 0.192492..1.631302 | -0.857925..2.591746 | -0.112994..-0.016874 | -0.137953..+0.088887 | `FRAGILE` |
| `STABILITY-SHELL-002` | 1.754815 | 0.549861..2.494664 | -0.728035..3.835149 | -0.097988..-0.024218 | -0.133419..+0.032935 | `FRAGILE` |
| `STABILITY-SHELL-003` | 1.604907 | 0.469288..2.262065 | -0.831858..3.356622 | -0.076070..-0.020779 | -0.078746..+0.045148 | `FRAGILE` |

Negative delta ranges mean lower MAE than the frozen baseline. Positive ranges are regressions.

## Controls

- Sign-inverted proton-axis control is included under the same resampling designs.
- Near-null control is preserved as an exact zero reference because it has no coefficient to resample.
- Shuffled-feature control is not rerun as a coefficient-stability fit because cyclic row-feature shuffling depends on stable row correspondence; this remains a TASK-0310 null-control reference.

## Verdict

`FRAGILE`: leave-one-out fits preserve the small retrospective improvements, but exhaustive 8-of-11 resampling introduces coefficient sign flips and some full-known/holdout regressions for all three primary candidates.

The stability evidence remains sandbox-only. It can guide specificity controls, but it does not justify registry expansion, reveal scoring, or claim promotion.

## Limitations

- Sandbox-only retrospective audit; no prediction registry, canonical result, claim, or knowledge artifact is updated.
- All coefficient stability tests still resample only the 11-row NMD-0002 training slice.
- Full-known and post-AME2020 rows are committed reviewable repository data, not future-measurement reveal data.
- The deterministic 8-of-11 design is exhaustive for that size but does not replace a larger independent training surface.
- Subset deltas remain fragile where row counts are small; light-nuclei regressions remain a domain limitation.
