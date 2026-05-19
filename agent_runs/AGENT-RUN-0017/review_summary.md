# AGENT-RUN-0017 Review Summary

## Verdict

`REVIEW_READY` for sandbox review.

## Method

`scripts/run_nuclear_asymmetry_frontier_stress_scout.py` loads the frozen
`RESULT-0015::model_fitted_semi_empirical` coefficients, computes NMD-0002
baseline residuals, fits bounded additive asymmetry-frontier residual
features, and evaluates candidate residuals on the committed post-AME2020
holdout rows. Subset metrics cover primary, asymmetry-greater-than 0.20 and
0.25, N-Z greater than 20 and 30, heavy A greater than or equal 100,
mid-mass 50 to 150, light A less than 50, and AME2020
measured/extrapolated comparison bands, plus a frontier-contrast metric
that compares the high-asymmetry improvement against the average of the
mid-mass and light bands.

ASYM-STRESS-003 is the required `OVERFITTED` negative-control neighbor and
re-uses NR-SCOUT-001/-002 scalings so the NR-SCOUT-005 catastrophic
blow-up is reproduced. ASYM-STRESS-004 is the sign-inverted adversarial
control: the runner fits the coefficient on training as in ASYM-STRESS-001
and then applies the negated coefficient on the holdout. ASYM-STRESS-005
is the clipped-above-0.25 variant. ASYM-STRESS-006 is the near-null sanity
control.

## Metrics

- Generated candidates: 9
- Executed candidates: 6 (4 hypotheses + 1 overfit-neighbor + 1 near-null control; ASYM-STRESS-004 and ASYM-STRESS-005 are adversarial/clipped variants of ASYM-STRESS-001)
- Rejected before execution: 3
- Verdict counts: `PARTIALLY_VALID` 2, `OVERFITTED` 1, `INCONCLUSIVE` 3
- Preserved near-null control: `ASYM-STRESS-006`
- Lane recommendation: `keep_as_review_surface`
- ASYM-STRESS-003 reproduces the NR-SCOUT-005 catastrophic +1.37 MeV primary blow-up by design.
- ASYM-STRESS-004's applied coefficient is the negation of ASYM-STRESS-001's fitted coefficient.

## Limitations

The run is retrospective, sandbox-only, and small-sample. It should not be
used to promote a nuclear mass claim, rewrite canonical results, or
register frozen predictions without a separate reviewed task. No training
row has asymmetry above 0.25, so the clipped variant fits a dormant column
and produces zero corrections; that is documented rather than treated as
evidence either for or against the clip-threshold idea. The lane
recommendation is a deterministic sandbox suggestion, not a maintainer
decision.
