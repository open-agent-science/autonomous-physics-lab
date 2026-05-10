# Nuclear Mass Baseline Residual Benchmark

- Result: `RESULT-0015`
- Run: `RUN-0001`
- Hypothesis: `HYP-0012`
- Task: `TASK-0168`
- Dataset: `NMD-0002`

## Assumptions

- The current benchmark slice contains measured entries only and is not the full AME surface.
- Atomic masses are converted deterministically into binding energy with explicit uncertainty propagation.
- Residual structure near shell closures is treated as a diagnostic target, not as evidence of new nuclear theory.
- Any fitted coefficients remain slice-specific until a separate holdout protocol exists.

## Limitations

- This benchmark uses a small pinned measured slice rather than the full AME2020 surface.
- Residual maps here characterize a simple semi-empirical baseline only; they do not imply a new shell model or universal mass law.
- The fitted coefficient set is slice-specific and should not be treated as a holdout-validated predictive model before TASK-0169 lands.

## Verification

- Verification gate passed: `True`
- dataset_slice_loaded: `PASS`
- binding_energy_reconstruction: `PASS`
- fitted_baseline_improves_overall_mae: `PASS`
- pairing_term_reduces_pairing_spread: `PASS`
- magic_subset_diagnostics_present: `PASS`
- uncertainty_normalized_residuals_present: `PASS`

## Candidate Models

| Model | Complexity | Overall MAE (MeV) | Magic-subset MAE (MeV) | Odd-even MAE (MeV) | Verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| model_fitted_semi_empirical | 5 | 2.825 | 2.449 | 2.716 | PARTIALLY_VALID |
| model_reference_semi_empirical | 5 | 3.673 | 3.481 | 4.318 | PARTIALLY_VALID |
| model_reference_liquid_drop_no_pairing | 4 | 4.780 | 5.561 | 4.934 | INCONCLUSIVE |

## Residual Diagnostics

### model_reference_liquid_drop_no_pairing

- Overall RMSE: `5.864` MeV
- Magic-subset MAE inflation factor: `1.163`
- Mean abs normalized residual: `513.13`
- Pairing-class MAE spread: `4.934` MeV

Top absolute residual entries:

- `He-4`: residual `12.108` MeV (magic_any=`True`, pairing=`even_even`)
- `Pb-208`: residual `8.804` MeV (magic_any=`True`, pairing=`even_even`)
- `U-238`: residual `-7.083` MeV (magic_any=`False`, pairing=`even_even`)
- `O-16`: residual `6.885` MeV (magic_any=`True`, pairing=`even_even`)
- `Ca-48`: residual `4.892` MeV (magic_any=`True`, pairing=`even_even`)

### model_reference_semi_empirical

- Overall RMSE: `4.521` MeV
- Magic-subset MAE inflation factor: `0.948`
- Mean abs normalized residual: `394.30`
- Pairing-class MAE spread: `4.318` MeV

Top absolute residual entries:

- `Pb-208`: residual `7.972` MeV (magic_any=`True`, pairing=`even_even`)
- `U-238`: residual `-7.861` MeV (magic_any=`False`, pairing=`even_even`)
- `He-4`: residual `6.108` MeV (magic_any=`True`, pairing=`even_even`)
- `N-14`: residual `5.409` MeV (magic_any=`False`, pairing=`odd_odd`)
- `O-16`: residual `3.885` MeV (magic_any=`True`, pairing=`even_even`)

### model_fitted_semi_empirical

- Overall RMSE: `3.697` MeV
- Magic-subset MAE inflation factor: `0.867`
- Mean abs normalized residual: `303.22`
- Pairing-class MAE spread: `2.716` MeV

Top absolute residual entries:

- `Pb-208`: residual `8.454` MeV (magic_any=`True`, pairing=`even_even`)
- `U-238`: residual `-6.226` MeV (magic_any=`False`, pairing=`even_even`)
- `N-14`: residual `4.172` MeV (magic_any=`False`, pairing=`odd_odd`)
- `He-4`: residual `2.686` MeV (magic_any=`True`, pairing=`even_even`)
- `Ca-40`: residual `-2.358` MeV (magic_any=`True`, pairing=`even_even`)

## Verdict

`model_fitted_semi_empirical` is the current best semi-empirical baseline on the pinned slice, reported as `PARTIALLY_VALID`.

## Conclusion

This benchmark establishes a first reviewable nuclear-mass residual surface: a pinned measured slice, explicit semi-empirical baselines, and shell-aware diagnostics ready for later holdout work.
