# Charged-Lepton Koide Reproduction

## Scope

`TASK-0037` adds the first canonical particle-mass benchmark result in APL:
an uncertainty-aware reproduction of the charged-lepton Koide quantity from an
explicit repository dataset.

This result is intentionally narrow:

- charged leptons only;
- one explicit PDG-backed dataset snapshot;
- reproduction of a benchmark quantity, not an explanation of mass generation.

## Canonical Result

- Result: `RESULT-0005`
- Run: `RUN-0004`
- Experiment: `EXP-0004`
- Hypothesis: `HYP-0004`
- Claim status target: keep `CLAIM-0003` as `DRAFT`

Primary comparison:

- observed `Q`: `0.6666644634145`
- reference `2/3`: `0.6666666666666666`
- absolute difference: `2.2032521665993343e-06`
- relative difference: `3.3048782498990015e-06`
- propagated one-sigma uncertainty in `Q`: `5.080958197422744e-06`
- within propagated uncertainty: `true`
- z-score: `0.43362926459755324`

Repository verdict:

- `VALID`

## Interpretation

The benchmark reproduces a charged-lepton Koide quantity numerically close to
`2/3` using explicit pole-mass inputs and first-order uncertainty
propagation.

That is enough to record a scoped reproduction result. It is not enough to:

- generalize across particle families;
- promote an explanatory claim;
- treat the result as evidence for deeper structure by itself.

## Verification Summary

All configured verification checks passed for the stored benchmark inputs:

- `charged_lepton_dataset_complete`
- `mass_definition_consistency`
- `koide_quantity_computed`
- `uncertainty_propagated`

## Canonical Artifacts

- [result.yaml](../../results/EXP-0004/RUN-0004/result.yaml)
- [report.md](../../results/EXP-0004/RUN-0004/report.md)
- [metrics.json](../../results/EXP-0004/RUN-0004/metrics.json)
- [review_summary.md](../../results/EXP-0004/RUN-0004/review_summary.md)
- [review_metadata.yaml](../../results/EXP-0004/RUN-0004/review_metadata.yaml)

## Why This Matters

This is the first Koide-track result that uses:

- the particle-mass dataset scaffold from `TASK-0036`;
- numerology guardrails from `TASK-0042`;
- reproduction-oriented benchmark schemas from `TASK-0048`.

That makes `RESULT-0005` a better foundation for the next Koide tasks:

- `TASK-0038` historical tau holdout prediction;
- later search/falsifier work only after holdout discipline remains intact.
