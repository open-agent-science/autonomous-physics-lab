# AGENT-RUN-0062 - MD-0001 Formation-Energy Null-Control Audit

- **Task:** TASK-0600
- **Audit:** materials-md0001-formation-energy-null-control-audit
- **Axis:** formation_energy_per_atom (eV_per_atom), computed_dft
- **Verdict:** SIGNAL_SURVIVES_CONTROLS (diagnostic; no claim)

## Method

Using only committed MD-0001 rows and the frozen TASK-0550 split
(material_id mod 10; train=119, holdout=33), the audit compares the real
cation-group-mean composition baseline against the global-mean null and against
two deterministic permutation controls (seed=0, 5000 permutations each):

- **label shuffle** - permute formation-energy values among train rows, refit
  cation-group means, score the true holdout;
- **cation-group shuffle** - permute cation-group labels among train rows
  (break the composition-to-value link), refit, score the true holdout.

The composition signal is judged to "survive" only if the real baseline beats
the global null and fewer than 5% of each control's permutations match or beat
its holdout MAE. Band gap is not loaded or pooled.

## Results (holdout, n=33)

| Predictor | Holdout MAE (eV/atom) |
| --- | ---: |
| global-mean null | 1.020563 |
| cation-group-mean (real) | 0.646030 |
| skill vs global null | 0.374534 |

| Control (5000 perms) | mean MAE | p05 | min | fraction <= real |
| --- | ---: | ---: | ---: | ---: |
| label shuffle | 1.028194 | 0.899633 | 0.750556 | 0.000000 |
| cation-group shuffle | 1.029574 | 0.899988 | 0.738206 | 0.000000 |

Robustness seeds 0/1/2/7 all produced 0.000000 for both control fractions at
5000 permutations.

## Interpretation

The formation-energy cation-group baseline beats the global null by 0.374534
eV/atom on the frozen holdout, and no deterministic label or cation-group
shuffle matched the real baseline in the checked 5000-permutation runs. This is
a stronger null-control survival than the earlier band-gap audit on the same
MD-0001 split.

The result remains sandbox diagnostic evidence only. It uses computed DFT
stable binary oxides, a small frozen holdout, and simple baselines. It does not
support material-design guidance, synthesis recommendations, prediction
registry entries, claims, or knowledge entries.

## Limitations

- Computed-DFT stable binary oxides only; no experimental formation energies.
- Frozen split/holdout; not retuned. Small holdout (n=33).
- Diagnostic null-control only; no RESULT/PRED/CLAIM/KNOW promotion.
- Band gap is not loaded or pooled with formation energy.

## Output Routing

- Task verdict: SIGNAL_SURVIVES_CONTROLS (diagnostic; no claim).
- Canonical destination: this run +
  docs/reviews/materials-md0001-formation-energy-null-control-audit.md.
- Review tier: none. Gate A/B: not attempted / not applicable.
- Claim impact: none. Knowledge impact: none.
