# AGENT-RUN-0085 - Stellar M-L high-mass DEBCat transfer benchmark

**Task:** `TASK-0837`
**Benchmark:** `stellar-ml-high-mass-debcat-transfer`
**Verdict:** `TRANSFER_NOT_SUPPORTED_BEST_CONTROL`

## Summary

This run freezes the `RESULT-0022` best relation
`log10(L/L_sun) = 4.526004 * log10(M/M_sun)` and transfers it onto committed
DEBCat Route 2 rows with `mass_solar > 2.0`. It performs no live fetch, no
alpha refit, no RESULT-0022 edit, and no rescue model.

The frozen relation scores `MAE=0.409289` dex on
the high-mass holdout. The best control is
`mass_matched_high_mass_train_nearest` with `MAE=0.306352` dex,
so the survival margin (best control minus relation) is
`-0.102937` dex against the predeclared
`0.02` dex threshold.

## Transfer Slice

- Source: committed DEBCat Route 2 normalized rows.
- Filter: admitted rows with `mass_solar > 2.0`.
- Rows/systems: `217` rows across
  `121` systems.
- Lane counts: `{'train': 110, 'validation': 51, 'holdout': 56}`.
- Holdout rows: `56` rows across `32`
  systems.

## Controls

| control | MAE dex | note |
| --- | --- | --- |
| null_high_mass_train_massband_median | 0.457384 |  |
| shuffled_relation_predictions | 1.317412 |  |
| mass_matched_high_mass_train_nearest | 0.306352 | best |

## Stage Strata

| stage | holdout rows | MAE dex | median residual dex |
| --- | --- | --- | --- |
| evolved | 18 | 0.395773 | 0.399606 |
| main_sequence_compatible | 24 | 0.334564 | -0.293168 |
| subgiant | 4 | 0.643122 | -0.726096 |
| unknown | 10 | 0.519425 | -0.328433 |

## Judge And Provenance

DEBCat detached-eclipsing-binary dynamical masses as inputs; catalogue-reported or Stefan-Boltzmann-derived luminosities as the observed log_luminosity_solar target. No row is excluded or
weighted after metric inspection; luminosity provenance and uncertainty classes
are recorded as strata in `metrics.json`.

## Decision

`TRANSFER_NOT_SUPPORTED_BEST_CONTROL`: Frozen RESULT-0022 relation does not transfer under controls: the best mass-matched control has lower MAE on the high-mass holdout. This is a regime-limited boundary
for the frozen RESULT-0022 transfer route, not a universal stellar-law claim.

## Replay

- Command: `python3 scripts/run_stellar_ml_high_mass_transfer.py --output-dir agent_runs/AGENT-RUN-0085 --review-note docs/reviews/stellar-ml-high-mass-transfer-benchmark.md`
- Code reference: `scripts/run_stellar_ml_high_mass_transfer.py`
- Engine version: `0.1.0`
- Git commit: `52535ea9ea71a1f60a6bf0cc7fafc5651fb745f9`

## Output Routing Summary

- Canonical destination: `sandbox_agent_run_plus_review_note`.
- Gate A status: `not_attempted_relation_failed_best_control`.
- Gate B status: `replayable_metadata_recorded`.
- RESULT artifact created: `False`.
- Claim impact: `none`.
- Knowledge impact: `none`.
