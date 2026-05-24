# Nuclear Shell-Axis Coefficient Stability Audit

**Task:** `TASK-0316`
**Agent run:** `agent_runs/AGENT-RUN-0019/`
**Script:** `scripts/run_nuclear_shell_axis_stability_audit.py`
**Metrics:** `agent_runs/AGENT-RUN-0019/metrics.json`
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`
**Evidence class:** sandbox-only retrospective coefficient-stability audit

## Scope

This review stress-tests the main limitation left by `TASK-0310`: the primary
shell-axis coefficients were learned from only 11 NMD-0002 training rows.

The audit reuses only committed repository data:

- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `data/nuclear_masses/post_ame2020_holdout.yaml`
- `results/EXP-0012/RUN-0001/result.yaml`
- `agent_runs/AGENT-RUN-0018/metrics.json`

It does not fetch live data, score `PRED-0063` through `PRED-0068`, create or
edit prediction registry entries, modify canonical results, promote claims, or
write knowledge artifacts.

## Resampling Design

| Design | Fits per candidate | Fit rows | Purpose |
| --- | ---: | ---: | --- |
| Leave-one-out / jackknife | 11 | 10 of 11 | Test single-row sensitivity. |
| Exhaustive small resamples | 165 | 8 of 11 | Test whether the coefficient survives smaller deterministic training subsets. |

Every fit is evaluated on the same committed full-known surface used by
`TASK-0310`: the NMD-0002 training slice plus the post-AME2020 primary holdout
rows.

## Candidate Stability Summary

Negative delta means lower MAE than the frozen baseline. Positive delta means
regression.

| Candidate | Full-fit coefficient | LOO coefficient range | 8-of-11 coefficient range | LOO holdout delta range | 8-of-11 holdout delta range | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `STABILITY-SHELL-001` proton-axis Gaussian | 1.162736 | 0.192492..1.631302 | -0.857925..2.591746 | -0.112994..-0.016874 | -0.137953..+0.088887 | `FRAGILE` |
| `STABILITY-SHELL-002` proton x neutron product | 1.754815 | 0.549861..2.494664 | -0.728035..3.835149 | -0.097988..-0.024218 | -0.133419..+0.032935 | `FRAGILE` |
| `STABILITY-SHELL-003` neutron-axis Gaussian | 1.604907 | 0.469288..2.262065 | -0.831858..3.356622 | -0.076070..-0.020779 | -0.078746..+0.045148 | `FRAGILE` |

## What Survives

The leave-one-out surface is supportive but bounded:

- all three primary candidates keep positive coefficient signs across all 11
  leave-one-out fits;
- all three improve full-known and primary-holdout MAE in all 11
  leave-one-out fits;
- the sign-inverted proton-axis control regresses full-known and holdout MAE
  in all 11 leave-one-out fits.

This means the TASK-0310 signal is not immediately dominated by one omitted
training row under a simple jackknife check.

## What Fails

The exhaustive 8-of-11 resampling surface is fragile:

| Candidate | Negative coefficient fits | Full-known regressions | Holdout regressions | Worst subset regression max |
| --- | ---: | ---: | ---: | ---: |
| `STABILITY-SHELL-001` | 15 of 165 | 15 of 165 | 15 of 165 | +0.608531 MeV |
| `STABILITY-SHELL-002` | 7 of 165 | 7 of 165 | 7 of 165 | +0.582080 MeV |
| `STABILITY-SHELL-003` | 8 of 165 | 8 of 165 | 8 of 165 | +0.746201 MeV |

The coefficient signs are therefore not stable under smaller deterministic
training subsets. Some 8-of-11 fits also turn the full-known and holdout
deltas positive, which is enough to prevent any broad robustness statement.

The recurring worst-regression subset remains light `A<50` for most primary
candidate fits. That agrees with the `TASK-0315` validity-domain map and keeps
light nuclei outside the safe support domain.

## Control Behavior

The controls keep the audit conservative:

- the sign-inverted proton-axis control is included under the same
  leave-one-out and 8-of-11 designs;
- the near-null / baseline-reference control is preserved as an exact zero
  reference because there is no coefficient to resample;
- the shuffled-feature control from `TASK-0310` is not rerun as a
  coefficient-stability fit because cyclic row-feature shuffling is a
  row-correspondence null, and changing resample membership changes the
  permutation semantics.

The sign-inverted control behaves as expected under leave-one-out, but 15 of
165 8-of-11 sign-inverted fits also become small apparent improvements. That
is another warning that the 11-row fit surface is too thin for broad
interpretation.

## Interpretation

`TASK-0316` weakens the shell-axis evidence boundary. The best interpretation
is not that the candidate lane failed completely, but that the coefficient
surface is too fragile for expansion:

- keep the `TASK-0310` aggregate improvements as bounded sandbox evidence;
- do not add new shell-axis registry entries;
- do not score the prospective mini-wave;
- do not promote the shell-axis family to a claim or canonical result;
- use follow-up tasks only for adversarial specificity, light-subset failure
  analysis, or source-gated reveal readiness.

## Recommended Next Step

Run specificity controls (`TASK-0317`) before any further shell-axis
interpretation. If specificity controls also show comparable non-shell
behavior, the shell-axis lane should be demoted to a narrow retrospective
artifact. If specificity controls are clean, the lane can remain a bounded
sandbox candidate, but coefficient fragility must stay visible in every
future evidence package.

`TASK-0305` should remain blocked until a reviewed post-registration source
manifest exists.

## Verdict

`FRAGILE`

Leave-one-out fits preserve the small retrospective improvements, but
exhaustive 8-of-11 resampling introduces coefficient sign flips and some
full-known or holdout regressions for all three primary candidates. The
correct action is to preserve the negative stability finding and avoid any
registry expansion, reveal scoring, or claim promotion.
