# Review Summary - AGENT-RUN-0011

Verdict: `SANDBOX_PASS` for the run.

Two pairing-lane residual candidates were executed:

- `HYP-PROPOSAL-0038` (pairing A-inverse refinement,
  `r_corr = c * pairing_sign(Z, N) / A`): structured `OVERFITTED` (worst
  per-complement coefficient swing `-35.26` vs `+4.6` on the other three
  holdouts); post-AME2020 primary delta MAE `+0.0067 MeV` (numerically
  near-null). The feature is sign-colinear with the existing baseline
  `pairing_sign / sqrt(A)` term; per-subset deltas are all
  `< +0.04 MeV`.
- `HYP-PROPOSAL-0041` (per-parity-class free offsets, in-batch negative
  control): structured `OVERFITTED` (worst regression `+0.65 MeV` on
  `random_stratified`); post-AME2020 primary delta MAE `+0.167 MeV`.
  Fitted coefficients on full NMD-0002 are `c_ee=+0.190`,
  `c_oo=+4.172`, `c_oA=-1.456`. The `c_oo = +4.172 MeV` term memorizes
  the single NMD-0002 odd-odd row (N-14) and applies it uniformly to
  the 71 odd-odd rows in the post-AME2020 primary holdout, producing
  the `odd_odd` subset regression `+0.333 MeV`.

Three further proposals were rejected before execution
(`HYP-PROPOSAL-0039` free-power nonlinear knob,
`HYP-PROPOSAL-0040` N=82 pairing override leakage,
`HYP-PROPOSAL-0042` per-nuclide row memorization).

Recommended action: keep both executed families as negative-control
sandbox evidence under `docs/nuclear-mass-robustness-gate.md`
(`ALLOW_ONLY_AS_NEGATIVE_CONTROL`). The pairing lane has delivered its
intended diagnostic value:

1. an explicit in-batch overfit reference (HYP-PROPOSAL-0041) that
   confirms the protocol still flags trivially-flexible feature stacks
   in this lane;
2. a clean negative result on whether the baseline `1/sqrt(A)` pairing
   scaling can be refined by an `A^-1` term on the available training
   surface (HYP-PROPOSAL-0038 primary delta MAE at machine precision).

No third batch in this lane is recommended without a broader pinned
training surface.
