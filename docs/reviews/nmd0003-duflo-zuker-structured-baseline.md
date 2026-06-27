# TASK-0823 DZ10 Published-Variant Stronger-Baseline Benchmark (scope A')

Deterministic 10-term DZ10 published-equation nuclear mass baseline on the
committed NMD-0003 training surface and the reviewed post-AME2020 retrospective
holdout.

This follows the published equations in Mendoza-Temis, Hirsch, and Zuker
(arXiv:0912.0882). It is a **clearly-cited published variant** (which TASK-0823
explicitly allows), NOT a parity run of the unavailable AMDC/archival DZ10 code.
Per the maintainer **A'** decision (PR #1218), this **completes** `TASK-0823` as a
DZ10-published-variant **stronger baseline** that beats the weak baseline under
controls by extrapolation. It does **not** claim canonical DZ ~0.5 MeV parity;
that higher bar is an optional non-blocking follow-up (`TASK-0853`), not a
TASK-0823 requirement.

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

`VALID_IN_SCOPE` (DZ10-published-variant stronger baseline; canonical-DZ parity NOT established).

Outcome: `CONTROL_SURVIVING_GAIN_UNDER_REVIEWABLE_DZ10_EQUATION_VARIANT` — the
variant's post-AME2020 MAE (`1.256383` MeV) beats the inherited frozen baseline
(`4.552569` MeV) and the best control (train-fitted liquid drop, `2.923573` MeV)
by a `1.667190` MeV margin, well above the `0.250000` MeV survival margin.

Task completion: `True` under the maintainer scope A' (PR #1218). The
published-equation variant satisfies TASK-0823's allowance for "a clearly-cited
published variant" and its success criterion (beat the baseline under controls by
extrapolation). It is explicitly NOT an archival DZ10 parity reproduction;
canonical-DZ parity is the optional non-blocking follow-up `TASK-0853`.

## Output Routing

- Verdict: `VALID_IN_SCOPE` (DZ10-published-variant stronger baseline)
- Canonical destination: agent_runs/AGENT-RUN-0078/ plus docs/reviews/
- Review tier: `sandbox` (an `AGENT_PUBLISHED` RESULT packaging + Gate B by a different agent are the next step, not a TASK-0823 blocker)
- Gate A status: `not_attempted` (replayable AGENT-RUN; canonical RESULT packaging is a follow-up)
- Gate B status: `replayable` (independent-agent replay must verify formula implementation, train-fit freeze, post-AME2020 evaluation, controls margin, and no target leakage)
- Claim impact: no claim change (no `CLAIM`; not a discovery)
- Knowledge impact: no knowledge change
- Routing decision: `DZ10_VARIANT_STRONGER_BASELINE_COMPLETES_TASK_0823_SCOPE_A_PRIME`

## Limitations

- This follows published DZ10 equations, but is not an archival DZ10-code parity
  reproduction.
- The post-AME2020 surface is retrospective time-split evidence, not a strict
  blind reveal.
- The model is fitted by ordinary least squares on the committed NMD-0003 train
  rows in the paper's `N,Z >= 8` domain only.
- No `PRED`, `CLAIM`, `KNOW`, or canonical `RESULT` artifact is created.
