# Materials MD-0001 Formation-Energy Null-Control Audit

**Task:** `TASK-0600`
**Run:** `agent_runs/AGENT-RUN-0064/`
**Axis:** formation_energy_per_atom (eV_per_atom), computed_dft
**Decision:** `SIGNAL_SURVIVES_CONTROLS` - diagnostic only

## Question

Does the cation-group-mean composition baseline genuinely predict formation
energy better than a global null on the frozen MD-0001 holdout, or is its
advantage within deterministic label/composition shuffles?

## Method

Committed MD-0001 formation-energy rows + frozen TASK-0550 split only
(train=119, holdout=33). Two deterministic permutation controls
(seed=0, 5000 permutations):

- **label shuffle** - permute formation-energy values among train rows, refit
  cation-group means, score true holdout.
- **cation-group shuffle** - permute cation-group labels among train rows
  (break the composition-to-value link), refit, score true holdout.

Survival rule: real baseline beats the global null and fewer than 5% of each
control's permutations match or beat its holdout MAE. Band gap is not loaded or
pooled.

## Result

| Predictor | Holdout MAE (eV/atom) |
| --- | ---: |
| global-mean null | 1.020563 |
| cation-group-mean (real) | 0.646030 |
| skill vs null | 0.374534 |

| Control (5000 perms) | fraction of permutations <= real holdout MAE |
| --- | ---: |
| label shuffle | 0.000000 |
| cation-group shuffle | 0.000000 |

Seed robustness (0/1/2/7): both fractions stayed at 0.000000 with 5000
permutations.

## Interpretation (conservative)

The formation-energy composition baseline clearly beats the global null on the
frozen holdout and was not matched by either deterministic control in the
checked permutation runs. This is stronger control survival than the earlier
MD-0001 band-gap audit.

No promotion is made. This audit is a control gate over computed DFT stable
binary oxides, not a material-design result, prediction, claim, or knowledge
entry. Any promotion would require a separate Gate A result task, provenance
checks, and maintainer review of scope wording.

## Output Routing Summary

- Task verdict: `SIGNAL_SURVIVES_CONTROLS` (diagnostic; no scientific claim).
- Canonical destination: `agent_runs/AGENT-RUN-0064/` + this review +
  `physics_lab/engines/materials_md0001_formation_energy_null_control.py`.
- Review tier: `none` (no RESULT/PRED promoted).
- Gate A/B: not attempted / not applicable.
- Claim impact: none. Knowledge impact: none.
- Limitations / blockers: computed-DFT stable binary oxides; frozen split;
  small holdout; diagnostic only.

## Limitations

- Computed-DFT values, not experimental formation energies.
- Small holdout (n=33): survived controls are diagnostic evidence, not a
  promoted result.
- No rows added, no holdout membership changed, no parameters tuned.
- No formation-energy and band-gap pooling.
