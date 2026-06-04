# Materials MD-0001 Band-Gap Null-Control Audit

**Task:** `TASK-0579`
**Run:** `agent_runs/AGENT-RUN-0058/`
**Axis:** band_gap (eV), computed_dft
**Decision:** `SIGNAL_SURVIVES_CONTROLS` — modest (p ≈ 0.04, n=33), diagnostic only

## Question

Does the cation-group-mean composition baseline genuinely predict band gap
better than a null on the frozen MD-0001 holdout, or is its ~9% edge within the
noise of label/composition shuffles?

## Method

Committed MD-0001 rows + frozen TASK-0550 split only (train=119, holdout=33). Two
deterministic permutation controls (seed=0, 5000 permutations):

- **label shuffle** — permute band-gap values among train, refit cation-group
  means, score true holdout.
- **cation-group shuffle** — permute cation-group labels among train (break the
  composition→value link), refit, score true holdout.

Survival rule (pre-stated): real baseline beats the global null **and** < 5% of
each control's permutations match or beat its holdout MAE. Formation energy is
reference context only and is never pooled.

## Result

| Predictor | Holdout MAE (eV) |
| --- | --- |
| global-mean null | 1.371747 |
| cation-group-mean (real) | 1.247901 |
| skill vs null | 0.123846 (~9%) |

| Control (5000 perms) | fraction of permutations ≤ real holdout MAE |
| --- | --- |
| label shuffle | 0.0428 |
| cation-group shuffle | 0.0378 |

Seed robustness (0/1/2/7): label 0.039–0.043, group 0.035–0.041 — stable.

## Interpretation (conservative)

The composition baseline beats the global null and is matched by only ~4% of
either shuffle control, so the edge is distinguishable from null at a one-sided
5% level and is seed-stable — it is **not pure memorization noise**. But the
effect is **modest** (≈0.12 eV) on a **small** holdout (n=33) with p ≈ 0.04, so
this is weak supporting evidence, not a strong result.

**No promotion.** This audit is a control gate, not a benchmark result: it does
not justify a band-gap PRED/CLAIM, a tuned model, or material-design guidance.
If MD-0001 band gap is ever promoted, this margin should be re-tested on a larger
or held-out-by-design slice.

## Output Routing Summary

- Task verdict: `SIGNAL_SURVIVES_CONTROLS` (diagnostic; no scientific claim).
- Canonical destination: `agent_runs/AGENT-RUN-0058/` + this review +
  `physics_lab/engines/materials_md0001_band_gap_null_control.py`.
- Review tier: `none` (no RESULT/PRED promoted).
- Gate A/B: not attempted / not applicable.
- Claim impact: none. Knowledge impact: none.
- Limitations / blockers: computed-DFT stable binary oxides; frozen split; small
  holdout; modest borderline effect; diagnostic only.

## Limitations

- Computed-DFT values, not experimental band gaps.
- Small holdout (n=33): a survived control test here is weak evidence; absence
  would have been a null result, not a falsification of band-gap structure.
- No rows added, no holdout membership changed, no parameters tuned.
