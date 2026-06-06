# AGENT-RUN-0066 - Materials MD-0001 Split-Sensitivity Audit

**Task:** `TASK-0601`
**Verdict:** `INCONCLUSIVE`

## Summary

This audit measures whether the committed MD-0001 formation-energy and band-gap
baseline conclusions (TASK-0550 / TASK-0578, `AGENT-RUN-0057`) are stable under
predeclared alternative splits, or whether they depend on the single committed
33-row holdout. It reuses the committed baseline primitives (row inclusion, the
three declared baselines, residual metrics), keeps the two axes separate, fetches
no data, and promotes no claim or materials guidance.

## Predeclared Alternative Splits

- `seeded_random_70_30`: five fixed-seed shuffles, each split 70/30 train/holdout.
- `leave_one_cation_group_out`: each cation group held out once (extrapolation).
- `leave_one_formula_family_out`: each oxide stoichiometry held out once. All rows
  are oxides, so the anion family is degenerate and replaced by this diagnostic.

Robustness rule (predeclared): the committed-holdout winner is `split_robust` only
if it is also the seeded mean winner with `>= 4 / 5` seed wins AND its seeded-mean
margin over the runner-up exceeds the larger across-seed standard deviation.

## Result

### Formation energy -> `split_robust`

- Committed holdout winner: `cation_group_mean` (MAE `0.646030`).
- Seeded random holdout mean MAE: `cation_group_mean` `0.636112`,
  `global_median` `0.978580`, `global_mean` `0.988409`.
- Seed wins: `cation_group_mean` `5 / 5`.
- Margin over runner-up `0.342468` >> across-seed noise `0.043917`.

The formation-energy conclusion does not depend on the particular holdout. Under
leave-one-cation-group-out the advantage vanishes (`cation_group_mean` degenerates
to the global mean, `1.164998`), so the signal is interpolative within known
cation families rather than extrapolative to unseen ones.

### Band gap -> `split_sensitive`

- Committed holdout winner: `cation_group_mean` (MAE `1.247901`), but it is the
  *worst* baseline on the committed validation split.
- Seeded random holdout mean MAE: `cation_group_mean` `1.207487`,
  `global_median` `1.266347`, `global_mean` `1.321399`.
- Seed wins: `cation_group_mean` `3 / 5`, `global_median` `2 / 5`.
- Margin over runner-up `0.058860` < across-seed noise `0.064471`.

The band-gap baseline ordering flips with the split: `cation_group_mean` wins only
a bare majority of seeds and its edge is smaller than the split-to-split noise. The
committed-split holdout "win" is not robust, reinforcing the committed
`INCONCLUSIVE` band-gap reading.

## Implication For Wider Materials Work

Formation energy is a stable enough single-axis benchmark signal to carry into a
wider MD-0002 slice; the band-gap conclusion should be treated as split-fragile and
not used as a settled baseline ordering. This is a methodological note, not
materials guidance.

## Output Routing Summary

- Task verdict: `INCONCLUSIVE`.
- Canonical destination: `agent_runs/AGENT-RUN-0066/metrics.json`, `agent_runs/AGENT-RUN-0066/report.md`, `docs/reviews/materials-md0001-split-sensitivity-audit.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: `none`.
- Result impact: `no RESULT artifact created`.
