# Limitations - AGENT-RUN-0011

- Sandbox-only second nuclear batch in the pairing lane; no canonical
  result, claim, hypothesis, experiment, knowledge, or dataset is updated.
- NMD-0002 has 11 nuclides. Structured-holdout coefficients for each of
  the four holdouts are fitted on 8-9 rows. Coefficient instability
  dominates the `OVERFITTED` verdicts on the structured protocol for
  both candidates.
- The post-AME2020 evaluation fits coefficients once on the full NMD-0002
  residual surface and applies them to the 295-row primary holdout. This
  is retrospective time-split evaluation, not blind prediction.
- `HYP-PROPOSAL-0038` (pairing A-inverse) is sign-colinear with the
  existing baseline pairing term: both activate on even-even and odd-odd
  rows with `pairing_sign(Z, N)`, differing only by `1/A` vs
  `1/sqrt(A)`. The lane cannot distinguish a true pairing-physics
  refinement from a noise fit on the tiny training surface; the
  post-AME2020 effect (`+0.0067 MeV`) is at the level of subset-level
  variation seen in `AGENT-RUN-0006`'s 48-split envelope.
- `HYP-PROPOSAL-0038`'s structured-holdout instability is driven by
  the `random_stratified` per-complement fit: removing
  `He-4 + Fe-57 + Pb-208` produces a coefficient of `-35.26 MeV` versus
  `+4.23` to `+4.59 MeV` on the other three holdouts. This is a single
  catastrophic complement; without it, the candidate would be three
  near-zero improvements rather than one improvement and three
  regressions.
- `HYP-PROPOSAL-0041` (per-parity-class free offsets) is the in-batch
  negative control by design. Its `OVERFITTED` verdict is the diagnostic
  value of the candidate, not a scientific result. Do not promote or
  describe its post-AME2020 behavior as evidence of any pairing physics.
- `HYP-PROPOSAL-0041`'s `c_oo = +4.172 MeV` is fit on a **single**
  NMD-0002 odd-odd row (`N-14`, baseline residual `+4.17 MeV`). When
  applied to the 71 odd-odd rows in the post-AME2020 primary holdout
  (whose mean residual is `-2.11 MeV`), this is a textbook one-row
  memorization failure: the candidate uniformly subtracts a memorized
  N-14 offset from rows that are nothing like N-14. This is exactly the
  diagnostic the in-batch negative control exists to expose.
- The apparent `Ga-84` improvement under `HYP-PROPOSAL-0041`
  (`37.64 MeV` baseline → `33.47 MeV` candidate) is coincidental sign
  alignment between the memorized `c_oo` and Ga-84's odd-odd residual;
  it does not generalize to the other In/Sb worst-case rows because most
  of them are odd-A.
- The In/Sb N=82 worst-residual cluster is not resolved by either
  executed candidate. Neither was designed to.
- The external negative-control reference is `HYP-PROPOSAL-0022` metrics
  from `AGENT-RUN-0008`; that reference is itself retrospective and
  remains sandbox-only under `docs/nuclear-mass-robustness-gate.md`.
