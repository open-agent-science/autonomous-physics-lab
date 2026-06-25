# TASK-0823 Duflo-Zuker-Structured Baseline Benchmark

Sandbox benchmark for a deterministic 10-term Duflo-Zuker-structured nuclear
mass baseline on the committed NMD-0003 training surface and the reviewed
post-AME2020 retrospective holdout.

This is not a canonical DZ10-code reproduction. The feature basis follows the
published DZ10 anatomy: macroscopic liquid-drop/DZ asymptotic terms plus
harmonic-oscillator and extruder-intruder shell occupancy proxies. The
publication blocker is therefore explicit: The implementation uses DZ10-published term structure and shell occupancy proxies, but it is not the archival Duflo-Zuker code. Any canonical RESULT publication would need maintainer review or a direct published-code parity check.

## Inputs

- Training dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- Retrospective holdout: `data/nuclear_masses/post_ame2020_holdout.yaml`
- Inherited baseline: `results/EXP-0012/RUN-0001/result.yaml`
- Post-AME2020 rows used for fitting: `0`

## Metrics

| surface | MAE (MeV) | RMSE (MeV) | count |
| --- | ---: | ---: | ---: |
| train | 1.022981 | 1.366094 | 1616 |
| sorted validation holdout | 3.986128 | 4.564872 | 693 |
| post-AME2020 holdout | 1.134513 | 2.063269 | 295 |

## Controls

| control | post-AME2020 MAE (MeV) |
| --- | ---: |
| inherited RESULT-0015 frozen | 4.552569 |
| NMD-0003 train-fitted liquid drop | 3.447464 |
| smooth-A quadratic control | 13.645968 |

Best control: `nmd0003_train_fitted_liquid_drop`
with MAE `3.447464` MeV.
The DZ-structured proxy margin vs best control is
`2.312951` MeV against the predeclared
`0.250000` MeV survival margin.

## Verdict

`VALID_IN_RANGE`

## Output Routing

- Verdict: `VALID_IN_RANGE`
- Canonical destination: agent_runs/AGENT-RUN-0078/ plus docs/reviews/
- Review tier: `none`
- Gate A status: `not_attempted`
- Gate B status: `not_applicable`
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Routing decision: `RESULT_CANDIDATE_REQUIRES_GATE_A`

## Limitations

- This is a DZ-structured proxy, not an archival DZ10 reproduction.
- The post-AME2020 surface is retrospective time-split evidence, not a strict
  blind reveal.
- The model is fitted by ordinary least squares on the committed NMD-0003 train
  split only.
- No `PRED`, `CLAIM`, `KNOW`, or canonical `RESULT` artifact is created.
