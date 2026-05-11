# Agent Run AGENT-RUN-0006 - Nuclear Split-Sensitivity Replay

**Task:** `TASK-0183`
**Candidate:** `HYP-PROPOSAL-0021`
**Source sandbox run:** `AGENT-RUN-0005`
**Status:** `REVIEW_READY`
**Boundary:** sandbox-only evidence

## Purpose

This run replays the strongest nuclear residual sandbox candidate under
alternative frozen split configurations before any second nuclear batch expands
the campaign surface.

The goal is not to promote a claim. The goal is to test whether the candidate
looks stable, weakens, or appears split-sensitive when the holdout choice is
varied.

## Inputs

- `hypothesis_proposals/nuclear-mass/HYP-PROPOSAL-0021-shell-dual-heavy-anchor-odd-a.yaml`
- `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0005-nuclear-mass-sandbox-batch.yaml`
- `agent_runs/AGENT-RUN-0005/metrics.json`
- `results/EXP-0012/RUN-0001/result.yaml`
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
- `docs/nuclear-mass-holdout-protocol.md`

## Method

The replay uses the frozen `RESULT-0015` fitted semi-empirical baseline as
read-only input. For each holdout split, the candidate correction family

```text
r_corr = c1*m2 + c2*mh + c3*oa
```

is fit on the complement of the holdout and evaluated on the holdout rows.

The committed metrics include:

- the original pilot random stratified split;
- three named alternative frozen splits;
- an aggregate enumeration of all 48 same-shape light/medium/heavy stratified
  splits from the same tiny pinned slice.

## Selected Split Results

| Split | Holdout | Delta MAE (MeV) | Delta RMSE (MeV) | Reading |
| --- | --- | ---: | ---: | --- |
| `pilot_random_stratified` | `He-4`, `Fe-57`, `Pb-208` | -0.255130 | 0.098282 | MAE improves, RMSE worsens slightly. |
| `alt_split_light_medium_heavy_a` | `N-14`, `Fe-56`, `Sn-120` | 0.000000 | 0.000000 | Ties the frozen baseline. |
| `alt_split_light_medium_heavy_b` | `O-17`, `Ca-48`, `U-238` | -0.382875 | -0.089860 | Improves this alternative split. |
| `alt_split_magic_stress` | `O-16`, `Ca-40`, `Pb-208` | 0.312559 | -0.489452 | MAE regresses while RMSE improves. |

## Same-Shape Split Sensitivity

Across all 48 same-shape stratified light/medium/heavy splits:

- improved MAE on `28/48` splits;
- regressed MAE on `13/48` splits;
- tied MAE on `7/48` splits;
- mean `delta_mae_mev`: `-0.057605339747111635`;
- median `delta_mae_mev`: `-0.135265169994792`;
- best `delta_mae_mev`: `-0.7440386250631548`;
- worst `delta_mae_mev`: `0.9480738911860487`;
- pilot split rank by MAE delta: `18/48`.

Relative to `HYP-PROPOSAL-0020`, the odd-A extension is:

- better on `18/48` splits;
- worse on `0/48` splits;
- tied on `30/48` splits.

This supports a narrow partial signal, not a stable general correction.

## Leakage And Cherry-Pick Notes

The replay is deterministic and uses committed inputs, but it is not blind
validation. `HYP-PROPOSAL-0021` was highlighted after the active holdout package
in `AGENT-RUN-0005` was visible.

The pilot split is not the luckiest split in the enumerated family, but the
candidate can still regress on same-shape alternatives. This makes the honest
interpretation split-sensitive.

## Complexity And Overfit Notes

Compared with `HYP-PROPOSAL-0020`, the candidate adds one odd-A feature and one
parameter. That is a modest complexity increase, but the observed benefit is
narrowly tied to odd-A rows in the tiny pinned slice.

The overfit risk is therefore not "too many parameters." It is selection and
surface-size risk.

## Verdict

**Scientific verdict:** `PARTIALLY_VALID` as sandbox follow-up evidence.

**Agent-run verdict:** `REVIEW_NEEDED`.

The candidate remains useful enough for review-gated follow-up, but it should
not be promoted to a canonical result or claim. A second bounded nuclear batch
can be considered only if maintainers accept this split-sensitivity profile as
an explicit guardrail.
