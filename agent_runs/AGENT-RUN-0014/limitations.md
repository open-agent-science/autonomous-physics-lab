# AGENT-RUN-0014 Limitations

- This is a sandbox-only scout. It does not create or update canonical results, claims, knowledge, or prediction registry entries.
- Feature coefficients are fit on the small 11-row NMD-0002 residual slice.
- Only one NMD-0002 training row is odd-odd, so odd-odd class offsets are especially fragile.
- The post-AME2020 row-level holdout is already committed in the repository. Evaluation here is a retrospective stress check, not a live reveal or blind prediction.
- Candidate verdicts are conservative triage labels for maintainer review, not scientific acceptance.
- Most executed pairing shapes were null, near-null, or regressive; this is a useful negative result for the campaign.
