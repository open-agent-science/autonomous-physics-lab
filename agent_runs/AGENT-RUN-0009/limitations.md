# Limitations - AGENT-RUN-0009

- Sandbox-only second nuclear batch; no canonical result, claim,
  hypothesis, experiment, knowledge, or dataset is updated.
- NMD-0002 has 11 nuclides. Structured-holdout coefficients for each of the
  four holdouts are fitted on 8-9 rows. Coefficient instability dominates
  the OVERFITTED verdicts on the structured protocol.
- The post-AME2020 evaluation fits coefficients once on the full NMD-0002
  residual surface and applies them to the 295-row primary holdout. This is
  retrospective time-split evaluation, not blind prediction.
- `SHELL_SIGMA = 2` is frozen at design time and is not a fitted parameter;
  varying it would expand the search space and would require a separate,
  registered proposal lane.
- The continuous shell-proximity features fire on every NMD-0002 and
  post-AME2020 row, so the dormant-feature failure mode from `AGENT-RUN-0008`
  no longer applies in this lane. The remaining failure modes are
  structured-holdout instability and proton-rich subset regression on the
  time-split surface.
- The In/Sb N=82 worst-residual cluster is not resolved by either executed
  candidate. The Ga-84 light-medium neutron-rich outlier
  (`|err| ~ 37 MeV` after correction) is also not resolved.
- Both executed candidates exhibit a one-way subset trade similar to
  `HYP-PROPOSAL-0022`: improvement on the dominant neutron-rich / near-magic
  subsets at the cost of regression on the smaller proton-rich subset.
  This is preserved as a negative signal under
  `docs/nuclear-mass-robustness-gate.md`.
