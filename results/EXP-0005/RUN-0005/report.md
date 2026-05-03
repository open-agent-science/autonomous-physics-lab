# Historical Tau Holdout Prediction

- Result: `RESULT-0006`
- Run: `RUN-0005`
- Hypothesis: `HYP-0005`
- Task: `TASK-0038`

## Inputs

- `electron` input: `0.51099895` MeV +/- `1.5e-10` MeV (2025 update, `pole` mass)
- `muon` input: `105.6583755` MeV +/- `2.3e-06` MeV (2025 update, `pole` mass)

## Holdout Comparison

- Prediction rule: solve the exact Koide relation for tau using only electron and muon masses.
- Predicted `m_tau`: `1776.969027083014` MeV
- Measured `m_tau`: `1776.930000000000` MeV
- Absolute difference: `3.902708301416e-02` MeV
- Relative difference: `2.196320790023e-05`
- Predicted one-sigma uncertainty: `3.529382100432e-05` MeV
- Measured one-sigma uncertainty: `9.000000000000e-02` MeV
- Combined one-sigma uncertainty: `9.000000692030e-02` MeV
- Within combined uncertainty: `True`

## Source Note

- Holdout tau comparison entry: `1776.93` MeV +/- `0.09` MeV (2025 update, `pole` mass)

## Limitations

- This is a charged-lepton holdout benchmark only.
- The benchmark tests predictive discipline under the exact Koide assumption; it does not explain mass generation.
- Prediction uncertainty uses first-order propagation from electron and muon input uncertainties only.

## Verification

- Verification gate passed: `True`
- charged_lepton_holdout_inputs_complete: `PASS`
- tau_holdout_applied: `PASS`
- koide_prediction_branch_selected: `PASS`
- prediction_uncertainty_propagated: `PASS`

## Verdict

Repository verdict: `VALID`.

The historical tau holdout benchmark records that the exact Koide assumption predicts a tau mass numerically close to the measured charged-lepton value under explicit uncertainty-aware comparison.
