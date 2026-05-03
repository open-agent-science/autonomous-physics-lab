# Charged-Lepton Koide Reproduction

- Result: `RESULT-0005`
- Run: `RUN-0004`
- Hypothesis: `HYP-0004`
- Task: `TASK-0037`

## Dataset

- `electron`: `0.51099895` MeV +/- `1.5e-10` MeV (2025 update, `pole` mass)
- `muon`: `105.6583755` MeV +/- `2.3e-06` MeV (2025 update, `pole` mass)
- `tau`: `1776.93` MeV +/- `0.09` MeV (2025 update, `pole` mass)

## Comparison Target

- Target quantity: `Q = (m_e + m_mu + m_tau) / (sqrt(m_e) + sqrt(m_mu) + sqrt(m_tau))^2`
- Observed `Q`: `0.666664463415`
- Reference `2/3`: `0.666666666667`
- Absolute difference: `2.203252166599e-06`
- Relative difference: `3.304878249899e-06`
- Propagated one-sigma uncertainty in `Q`: `5.080958197423e-06`
- Within propagated uncertainty: `True`

## Limitations

- Charged-lepton scope only; no cross-family generalization is implied.
- This is a reproduction benchmark, not an explanation claim.
- Uncertainty propagation assumes independent one-sigma input uncertainties.

## Verification

- Verification gate passed: `True`
- charged_lepton_dataset_complete: `PASS`
- mass_definition_consistency: `PASS`
- koide_quantity_computed: `PASS`
- uncertainty_propagated: `PASS`

## Verdict

Repository verdict: `VALID`.

The benchmark reproduces a Koide quantity numerically close to `2/3` from explicit charged-lepton pole masses while preserving uncertainty-aware wording.
