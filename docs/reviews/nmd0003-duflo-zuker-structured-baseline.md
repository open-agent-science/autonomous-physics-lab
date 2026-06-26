# TASK-0823 DZ10 Published-Equation Diagnostic Benchmark

Sandbox diagnostic for a deterministic 10-term DZ10 published-equation nuclear
mass baseline on the committed NMD-0003 training surface and the reviewed
post-AME2020 retrospective holdout.

This follows the published equations in Mendoza-Temis, Hirsch, and Zuker
(arXiv:0912.0882), but it is not a parity run of the unavailable AMDC/archival
DZ10 code. This PR therefore does not complete `TASK-0823`; the task remains
`READY` for a future true published-code or published-fixture parity
implementation.

## Inputs

- Training dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- Retrospective holdout: `data/nuclear_masses/post_ame2020_holdout.yaml`
- Inherited baseline: `results/EXP-0012/RUN-0001/result.yaml`
- Post-AME2020 rows used for fitting: `0`
- Code reference: `physics_lab/engines/nmd0003_duflo_zuker_baseline.py::run_nmd0003_duflo_zuker_baseline`
- Engine version: `nmd0003_dz10_published_equation_variant_v2`
- Git commit at generation: `cd8e92c8c8a293247aedd9b61c269f611a905b6a`

## Metrics

| surface | MAE (MeV) | RMSE (MeV) | count |
| --- | ---: | ---: | ---: |
| NMD-0003 fit surface | 1.230832 | 1.506930 | 2217 |
| post-AME2020 holdout | 1.256383 | 2.105379 | 295 |

## Controls

| control | post-AME2020 MAE (MeV) |
| --- | ---: |
| inherited RESULT-0015 frozen | 4.552569 |
| NMD-0003 train-fitted liquid drop | 2.923573 |
| smooth-A quadratic control | 13.610999 |

Best control: `nmd0003_train_fitted_liquid_drop`
with MAE `2.923573` MeV.
The DZ10 published-equation variant margin vs best control is
`1.667190` MeV against the predeclared
`0.250000` MeV survival margin.

## Verdict

`INCONCLUSIVE`

Diagnostic outcome: `CONTROL_SURVIVING_GAIN_UNDER_REVIEWABLE_DZ10_EQUATION_VARIANT`.

Task completion: `False`. Reason:
The reviewable published-equation variant is useful diagnostic evidence, but it is not an archival DZ10 parity reproduction. TASK-0823 therefore remains READY for a true published-code or published-fixture parity implementation.

## Output Routing

- Verdict: `INCONCLUSIVE`
- Canonical destination: agent_runs/AGENT-RUN-0078/ plus docs/reviews/
- Review tier: `sandbox`
- Gate A status: `not_attempted`
- Gate B status: `replayable`
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Routing decision: `SANDBOX_ONLY_DZ10_PARITY_BLOCKED_TASK_REMAINS_READY`

## Limitations

- This follows published DZ10 equations, but is not an archival DZ10-code parity
  reproduction.
- The post-AME2020 surface is retrospective time-split evidence, not a strict
  blind reveal.
- The model is fitted by ordinary least squares on the committed NMD-0003 train
  rows in the paper's `N,Z >= 8` domain only.
- No `PRED`, `CLAIM`, `KNOW`, or canonical `RESULT` artifact is created.
