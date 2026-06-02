# AGENT-RUN-0055 — NMD-0003 Broad-Surface Baseline Freeze (TASK-0531)

Sandbox benchmark run comparing the inherited RESULT-0015 / NMD-0002 frozen
semi-empirical baseline against a train-fitted NMD-0003 baseline on the
committed AME2020 measured training surface. No live fetch, post-AME2020 reveal
scoring, residual-feature family test, prediction, claim, or knowledge artifact
is included.

- Config: `examples/benchmarks/nuclear_mass_baseline_nmd0003.yaml`
- Dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- Split manifest: `data/nuclear_masses/nmd-0003-split-manifest.yaml`
- Rows: 2309 total; 1616 deterministic train rows; 693 deterministic validation
  rows
- Baselines: inherited `RESULT-0015` coefficients versus NMD-0003 train-fitted
  frozen coefficients

## Result

**Verdict: INCONCLUSIVE sandbox benchmark evidence.**

The NMD-0003 train-fitted baseline improves the train split and the full
NMD-0003 measured surface, but it worsens the predeclared validation holdout.

| comparison surface | MAE relative improvement | RMSE relative improvement |
| --- | ---: | ---: |
| train | 0.441918 | 0.444909 |
| validation holdout | -0.341856 | -0.513482 |
| full NMD-0003 measured surface | 0.155469 | 0.005639 |

Validation holdout MAE moves from 5.760713 MeV under inherited NMD-0002
coefficients to 7.730045 MeV under the NMD-0003 train-fitted coefficients. That
is a holdout regression, not a promotable baseline improvement.

## Interpretation

TASK-0517 remains control-dominated factory memory. The inherited NMD-0002
baseline was a mismatch for the larger NMD-0003 surface, but a simple
broad-surface least-squares refit does not solve the problem on the predeclared
validation holdout. A future Nuclear factory sprint should first define a
better broad-surface baseline protocol, rather than assuming this fitted
baseline is ready for residual-family testing.

## Residual Map Scope

The metrics file records residual summaries overall and by:

- A range;
- Z range;
- N range;
- magic-distance bin;
- odd/even pairing class;
- neutron-richness bin;
- top absolute residual rows for each baseline.

## Output Routing

- **Verdict:** `INCONCLUSIVE`
- **Canonical destination:** sandbox evidence in `agent_runs/AGENT-RUN-0055/`
  plus review note in `docs/reviews/nmd0003-broad-surface-baseline.md`.
- **Review tier:** not applicable.
- **Gate A / Gate B:** not applicable; no canonical `RESULT-*` or `PRED-*`
  artifact is published.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** validation holdout regression and benchmark scope;
  no canonical result promotion in this task.

## Limitations

- The validation split is retrospective inside AME2020 measured rows, not a
  post-AME2020 reveal.
- The broad-surface baseline is a liquid-drop-style least-squares baseline, not
  a new residual-feature family.
- The primary post-AME2020 holdout remains excluded and unscored.
- This task does not test new Nuclear residual hypotheses.
