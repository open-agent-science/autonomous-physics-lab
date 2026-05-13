# AGENT-RUN-0011 Limitations

- Sandbox-only run for `TASK-0201`; no canonical result, claim, accepted
  knowledge, or canonical dataset is updated.
- NMD-0002 contains 11 nuclides, so structured holdout coefficients are fitted
  on only 8-9 rows.
- The post-AME2020 evaluation is retrospective time-split evidence, not blind
  prediction.
- `HYP-PROPOSAL-0038` improves or ties all internal structured holdouts, but
  regresses the post-AME2020 primary MAE by `+0.0796 MeV` and the odd-A subset
  by `+0.1506 MeV`.
- `HYP-PROPOSAL-0039` improves the neutron-rich post-AME2020 subset by
  `-0.4575 MeV`, but regresses the primary by `+0.0876 MeV`, proton-rich rows
  by `+0.5577 MeV`, and heavy rows by `+0.2508 MeV`.
- The rejected proposals are preserved as negative-control context; they were
  not evaluated.
- No follow-up from this lane should be recommended without a broader pinned
  training surface and maintainer review under
  `docs/nuclear-mass-robustness-gate.md`.
