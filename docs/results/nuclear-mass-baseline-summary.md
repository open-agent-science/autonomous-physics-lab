# Nuclear Mass Baseline Summary

`TASK-0168` adds the first executable nuclear-mass baseline benchmark:

- experiment: `EXP-0012`
- result: `RESULT-0015`
- dataset: `NMD-0002`

## What Landed

- one pinned measured nuclear-mass slice for benchmark bring-up;
- three explicit semi-empirical baseline variants:
  - reference liquid-drop without pairing;
  - reference semi-empirical with pairing;
  - slice-fitted semi-empirical baseline;
- shell-sensitive and pairing-sensitive residual diagnostics;
- reviewable claim and knowledge patch artifacts.

## Current Best Model

Current best model: `model_fitted_semi_empirical`

Fitted coefficients:

- `a_v = 15.5142`
- `a_s = 17.2932`
- `a_c = 0.6878`
- `a_a = 23.8466`
- `a_p = 15.9908`

Benchmark diagnostics:

- overall MAE: `2.825 MeV`
- overall RMSE: `3.697 MeV`
- magic-subset MAE: `2.449 MeV`
- best verdict: `PARTIALLY_VALID`

Reference comparison:

- reference semi-empirical overall MAE: `3.673 MeV`
- no-pairing liquid-drop overall MAE: `4.780 MeV`

## Diagnostic Reading

What the current slice says:

- fitting the semi-empirical coefficients improves the pinned-slice residual surface;
- explicit pairing helps reduce pairing-class residual spread;
- the shell-sensitive subset is still not a solved surface, even when the fitted
  baseline wins overall;
- the heaviest residual pressure remains around very light or very heavy
  nuclei, especially `Pb-208`, `U-238`, and `He-4`.

## Guardrail

This is a baseline benchmark, not a discovery artifact.

It does **not** justify claims like:

- "APL found a nuclear mass formula"
- "APL explained magic numbers"
- "APL discovered new shell structure"

The next required step is `TASK-0169`: formal holdout structure before any
autonomous correction search is interpreted.
