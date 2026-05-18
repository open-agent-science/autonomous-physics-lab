# AGENT-RUN-0015 Limitations

- This is a sandbox-only scout. It does not create or update canonical results, claims, knowledge, or prediction registry entries.
- Feature coefficients are fit on the small 11-row NMD-0002 residual slice.
- Isotope-chain subsets in the primary post-AME2020 holdout are very small: Z=20 has 2 rows, Z=28 has 3 rows, and Z=50 has 1 row. Per-chain deltas are highly fragile and one-row sensitive.
- The post-AME2020 row-level holdout is already committed in the repository. Evaluation here is a retrospective stress check, not a live reveal or blind prediction.
- Candidate verdicts are conservative triage labels for maintainer review, not scientific acceptance.
- All four mid-mass hypotheses regressed on the mid-mass band relative to the frozen baseline. The scout produced no PARTIALLY_VALID candidate; the lane is preserved as a useful negative result rather than a discovery.
- Sandbox effects on the holdout are sub-MeV on most subsets but escalate above 1 MeV on small isotope-chain subsets and on the isotope-chain slope candidate, which underscores how brittle features fitted on 11 rows are when extrapolated.
