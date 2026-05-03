# Historical Tau Holdout Prediction

## Scope

`TASK-0038` extends the Koide track from reproduction to a real holdout-style
benchmark: use only electron and muon pole masses plus the exact Koide
assumption to predict tau, then compare that prediction against the measured
charged-lepton tau mass.

This result remains narrow:

- charged leptons only;
- one explicit PDG-backed dataset snapshot;
- historical holdout benchmark only, not explanation.

## Canonical Result

- Result: `RESULT-0006`
- Run: `RUN-0005`
- Experiment: `EXP-0005`
- Hypothesis: `HYP-0005`
- Claim status target: keep `CLAIM-0004` as `DRAFT`

Primary comparison:

- predicted `m_tau`: `1776.9690270830142` MeV
- measured `m_tau`: `1776.93` MeV
- absolute difference: `3.902708301422477e-02` MeV
- relative difference: `2.196856963501105e-05`
- predicted one-sigma uncertainty: `3.5293821004320466e-05` MeV
- measured one-sigma uncertainty: `9.000000000000000e-02` MeV
- combined one-sigma uncertainty: `9.000000692181969e-02` MeV
- within combined uncertainty: `true`
- z-score: `0.4336341771479451`

Repository verdict:

- `VALID`

## Interpretation

The benchmark records that the exact Koide assumption produces a tau holdout
prediction numerically close to the measured tau mass under an explicit
uncertainty-aware comparison.

That is enough to store a disciplined historical prediction result. It is not
enough to:

- promote an explanatory claim;
- generalize across particle families;
- treat the benchmark as evidence of deeper structure by itself.

## Canonical Artifacts

- [result.yaml](../../results/EXP-0005/RUN-0005/result.yaml)
- [report.md](../../results/EXP-0005/RUN-0005/report.md)
- [metrics.json](../../results/EXP-0005/RUN-0005/metrics.json)
- [review_summary.md](../../results/EXP-0005/RUN-0005/review_summary.md)
- [review_metadata.yaml](../../results/EXP-0005/RUN-0005/review_metadata.yaml)
