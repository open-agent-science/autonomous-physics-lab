# AGENT-RUN-0058 — MD-0001 Band-Gap Null-Control Audit

- **Task:** TASK-0579
- **Audit:** materials-md0001-band-gap-null-control-audit
- **Axis:** band_gap (eV), computed_dft
- **Verdict:** SIGNAL_SURVIVES_CONTROLS (modest, p ≈ 0.04)

## Method

Using only committed MD-0001 rows and the frozen TASK-0550 split
(material_id mod 10; train=119, holdout=33), the audit compares the real
cation-group-mean composition baseline against the global-mean null and against
two deterministic permutation controls (seed=0, 5000 permutations each):

- **label shuffle** — permute band-gap values among train rows, refit
  cation-group means, score the true holdout;
- **cation-group shuffle** — permute cation-group labels among train rows
  (break the composition→value link), refit, score the true holdout.

The composition signal is judged to "survive" only if the real baseline beats
the global null **and** fewer than 5% of each control's permutations match or
beat its holdout MAE.

## Results (holdout, n=33)

| Predictor | Holdout MAE (eV) |
| --- | --- |
| global-mean null | 1.371747 |
| cation-group-mean (real) | 1.247901 |
| skill vs global null | 0.123846 (~9%) |

| Control (5000 perms) | mean MAE | p05 | min | fraction ≤ real |
| --- | --- | --- | --- | --- |
| label shuffle | 1.396 | 1.25 | 1.10 | **0.0428** |
| cation-group shuffle | 1.400 | 1.26 | 1.15 | **0.0378** |

Robustness (seeds 0/1/2/7, 5000 perms): label fraction 0.039–0.043, group
fraction 0.035–0.041 — the verdict is stable across seeds.

## Interpretation

The cation-group composition baseline beats the global null on the band-gap
holdout, and only ~4% of label/group shuffles match it, so the edge is
distinguishable from null at a one-sided 5% level and is seed-stable. The effect
is **modest** (≈0.12 eV, p ≈ 0.04 on a small n=33 holdout): it is enough to say
the baseline is not pure memorization noise, but not enough to justify any
benchmark promotion or band-gap prediction claim.

## Limitations

- Computed-DFT stable binary oxides only; no experimental band gaps.
- Frozen split/holdout; not retuned. Small holdout (n=33).
- Diagnostic null-control only; no PRED/CLAIM/KNOW, no material-design claim.
- Formation energy is reference context and is never pooled with band gap.

## Output Routing

- Task verdict: SIGNAL_SURVIVES_CONTROLS (diagnostic; no claim).
- Canonical destination: this run + docs/reviews/materials-md0001-band-gap-null-control-audit.md.
- Review tier: none. Gate A/B: not attempted / not applicable.
- Claim impact: none. Knowledge impact: none.
