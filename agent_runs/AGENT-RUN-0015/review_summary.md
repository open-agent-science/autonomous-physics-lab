# AGENT-RUN-0015 Review Summary

## Verdict

`REVIEW_READY` for sandbox review.

## Method

`scripts/run_nuclear_midmass_isotope_gap_scout.py` loads the frozen
`RESULT-0015::model_fitted_semi_empirical` coefficients, computes NMD-0002
baseline residuals, fits bounded additive mid-mass and isotope-chain residual
features, and evaluates candidate residuals on the committed post-AME2020
holdout rows. Subset metrics cover primary, mid-mass, light, heavy, and
Z=20/Z=28/Z=50 isotope chains, plus a frontier-contrast metric that compares
mid-mass improvement against the average of light and heavy regressions.

## Metrics

- Generated candidates: 8
- Executed candidates: 5 (4 hypotheses + 1 near-null control)
- Rejected before execution: 3
- Verdict counts: `OVERFITTED` 4, `INCONCLUSIVE` 1
- Preserved near-null control: `MIDMASS-SCOUT-005`
- No `PARTIALLY_VALID` candidate emerged; lane preserved as negative evidence.

## Limitations

The run is retrospective, sandbox-only, and small-sample. It should not be used
to promote a nuclear mass claim, rewrite canonical results, or register frozen
predictions without a separate reviewed task. Isotope-chain subsets are very
small in the primary holdout (Z=20: 2 rows, Z=28: 3 rows, Z=50: 1 row), so
per-chain deltas are highly fragile and should be read as scout signals only.
