# AGENT-RUN-0013 Limitations

- This is a sandbox-only scout. It does not create or update canonical results, claims, knowledge, or prediction registry entries.
- Feature coefficients are fit on the small 11-row NMD-0002 residual slice, so candidate behavior is vulnerable to small-sample instability.
- The post-AME2020 row-level holdout is already committed in the repository. Evaluation here is a retrospective stress check, not a live reveal or blind prediction.
- Candidate verdicts are conservative triage labels for maintainer review, not scientific acceptance.
- `NR-SCOUT-001` is effectively near-zero under the fitted coefficient and is kept as `INCONCLUSIVE` rather than treated as improvement.
- `NR-SCOUT-005` shows a clear subset tradeoff and is preserved as an `OVERFITTED` negative result.
