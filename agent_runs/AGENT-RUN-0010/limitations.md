# Limitations - AGENT-RUN-0010

- Sandbox-only second nuclear batch; no canonical result, claim,
  hypothesis, experiment, knowledge, or dataset is updated.
- NMD-0002 has 11 nuclides. Structured-holdout coefficients for each of
  the four holdouts are fitted on 8-9 rows. Coefficient instability
  dominates the `OVERFITTED` verdicts on the structured protocol.
- The post-AME2020 evaluation fits coefficients once on the full NMD-0002
  residual surface and applies them to the 295-row primary holdout. This
  is retrospective time-split evaluation, not blind prediction.
- `HYP-PROPOSAL-0033` extends `HYP-PROPOSAL-0022` by one polynomial degree.
  The two-parameter fit on the small training slice produces extreme
  coefficients (`i_sq = +82.66`, `i_quartic = -1777.78`) that overshoot on
  extreme neutron-rich rows on the time-split surface.
- `HYP-PROPOSAL-0034` is asymmetric by construction (feature is zero on
  proton-rich rows). This is a design choice intended to address the
  one-way subset trade; it is not a discovered asymmetry of nuclear-mass
  residuals.
- `HYP-PROPOSAL-0034`'s fitted coefficient on full NMD-0002 is
  approximately `3.5e-13` MeV, which is numerical noise. The feature's
  `(N - Z)^2 / A` scaling weights heavy nuclei strongly; on the 11-row
  training slice the feature is essentially orthogonal to the residual
  vector. As a result the post-AME2020 effect is null at machine
  precision, while the structured-holdout protocol still records
  `OVERFITTED` because per-complement fits behave differently.
- The In/Sb N=82 worst-residual cluster is not resolved by either
  executed candidate. For `HYP-PROPOSAL-0033`, the `Ga-84` residual
  actually grows from `37.64 MeV` (baseline) to `40.33 MeV` after
  correction.
- The negative-control reference is `HYP-PROPOSAL-0022` metrics from
  `AGENT-RUN-0008`; that reference is itself retrospective and remains
  sandbox-only under `docs/nuclear-mass-robustness-gate.md`.
