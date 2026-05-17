# AGENT-RUN-0013 Review Summary

## Verdict

`REVIEW_READY` for sandbox review.

## Method

`scripts/run_nuclear_neutron_rich_variant_scout.py` loads the frozen
`RESULT-0015::model_fitted_semi_empirical` coefficients, computes NMD-0002
baseline residuals, fits bounded additive residual features, and evaluates the
resulting candidate residuals on the committed post-AME2020 holdout rows.

## Metrics

- Generated candidates: 9
- Executed candidates: 6
- Rejected before execution: 3
- Verdict counts: `PARTIALLY_VALID` 2, `INCONCLUSIVE` 3, `OVERFITTED` 1
- Best material subset scouts: `NR-SCOUT-003` and `NR-SCOUT-004`
- Preserved negative result: `NR-SCOUT-005`
- Preserved null/near-null controls: `NR-SCOUT-001`, `NR-SCOUT-006`

## Limitations

The run is retrospective, sandbox-only, and small-sample. It should not be used
to promote a nuclear mass claim, rewrite canonical results, or register frozen
predictions without a separate reviewed task.
