# Review Summary - AGENT-RUN-0010

Verdict: `SANDBOX_PASS` for the run.

Two neutron-rich residual candidates were executed:

- `HYP-PROPOSAL-0033` (quartic asymmetry, `r_corr = a * I^2 + b * I^4`):
  structured `OVERFITTED`; post-AME2020 primary delta MAE `+0.563 MeV`
  (regression). The quartic extension of `HYP-PROPOSAL-0022` reverses the
  sign of the prior negative-control improvement, confirming that the
  earlier `-0.389 MeV` aggregate win was shape-specific rather than a
  robust polynomial expansion.
- `HYP-PROPOSAL-0034` (asymmetric neutron-excess,
  `r_corr = c * max(N - Z, 0)^2 / A`): structured `OVERFITTED`;
  post-AME2020 effect is numerically null (~3.5e-13 MeV coefficient on
  full NMD-0002) because the heavy-weighted asymmetric feature is
  essentially orthogonal to the training residuals on the 11-row slice.

Three further proposals were rejected before execution
(`HYP-PROPOSAL-0035` In/Sb chain leakage, `HYP-PROPOSAL-0036` free-power
nonlinear knob, `HYP-PROPOSAL-0037` per-shell indicator stack leakage).

Recommended action: keep both executed families as negative-control
sandbox evidence under `docs/nuclear-mass-robustness-gate.md`
(`ALLOW_ONLY_AS_NEGATIVE_CONTROL`). The neutron-rich lane has delivered
its intended diagnostic value: it sharpens the reading on
`HYP-PROPOSAL-0022` (shape-specific aggregate improvement) and shows that
an asymmetric-by-design feature does not rescue the lane on the current
training surface. No third batch in this lane is recommended without a
broader pinned dataset.
