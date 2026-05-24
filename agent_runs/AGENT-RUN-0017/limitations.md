# AGENT-RUN-0017 Limitations

- This is a sandbox-only adversarial stress scout. It does not create or update canonical results, claims, knowledge, or prediction registry entries.
- Feature coefficients are fit on the small 11-row NMD-0002 residual slice.
- No training row has `(N - Z) / A` above 0.25, so the clipped variant `ASYM-STRESS-005` fits an effectively dormant column and produces zero corrections everywhere. The candidate is preserved so the clip-threshold probe is documented even when the fit cannot speak.
- `ASYM-STRESS-003` (matched quadratic+cubic neutron-excess pair) is included as the required `OVERFITTED` negative-control neighbor. Its primary delta of about +1.37 MeV and asymmetry-greater-than-0.25 delta of about +4.81 MeV reproduce the NR-SCOUT-005 catastrophic blow-up by design and are recorded as negative evidence, not as a discovery candidate.
- `ASYM-STRESS-004` (sign-inverted positive asymmetry fraction) negates the fitted coefficient on the holdout to probe sign-direction stability; it is an adversarial control, not a physical correction proposal.
- The post-AME2020 row-level holdout is already committed in the repository. Evaluation here is a retrospective stress check, not a live reveal or blind prediction.
- The `asymmetry_ge_0_25` subset is small relative to the primary holdout, so concentrated deltas on it should be read as scout-grade triage signal rather than a precise effect size.
- Candidate verdicts are conservative triage labels for maintainer review, not scientific acceptance. The lane-recommendation block is deterministic but is a sandbox suggestion, not a maintainer decision.
