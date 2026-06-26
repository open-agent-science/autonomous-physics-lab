# AGENT-RUN-0081 Report

## Scope

`TASK-0838` is a BOUNDED computed-DFT transfer benchmark. It asks whether the frozen RESULT-0021 baseline model (the exact unordered non-oxygen cation-pair train-mean of `formation_energy_per_atom`, with a global-train-mean fallback) transfers across a chemically-disjoint A-site cation-family split of the committed MD-0002 stable ternary-oxide slice. The judge is computed-DFT (Materials Project, CC BY 4.0); this is a model-vs-model generalization benchmark, not a discovery, material-design-law, property-prediction, or device statement.

## Frozen model and predeclared split

Frozen model under test: `model_cation_pair_mean` (descriptor `exact_unordered_non_oxygen_cation_pair`), imported unchanged from the baseline engine. The model and descriptor were fixed before any transfer error was read.

Disjoint A-site cation-family partition (route selected by the TASK-0817 scout): `alkali_transition` = 225 rows, `alkaline_earth_transition` = 137 rows. The two families share no A-site cation, so leakage is none by construction.

## Predeclared pass/fail

Metric: held_out_family_holdout_mae_eV_per_atom. Rule: Frozen model must beat the BEST control's holdout MAE by at least 0.05 eV/atom on the held-out family in BOTH disjoint-family directions. Controls: null_global_mean, shuffled_cation_pair, per_class_median.

## Transfer error vs controls

| Direction | Frozen MAE | null | per-class-median | shuffled | best control | margin | clears? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hold out `alkaline_earth_transition` | 0.729781 | 0.729781 | 0.833408 | 0.729781 | `null_global_mean` 0.729781 | 0.0 | no |
| hold out `alkali_transition` | 0.791686 | 0.791686 | 0.745149 | 0.791686 | `per_class_median` 0.745149 | -0.046537 | no |

- Holding out `alkaline_earth_transition`: 137 of 137 held-out rows fall back to the global train mean (the families share no cation pair), so the frozen model cannot use any learned pair on the held-out family.
- Holding out `alkali_transition`: 225 of 225 held-out rows fall back to the global train mean (the families share no cation pair), so the frozen model cannot use any learned pair on the held-out family.

## Verdict

`SANDBOX_FAIL` -- advantage_is_family_localized. The frozen cation-pair advantage does NOT transfer across a disjoint A-site cation family on this computed-DFT slice. This is the honest negative the task accepts; no refit, feature add, or split change was made to rescue it.

## Output routing

- Canonical destination: agent_runs/AGENT-RUN-0081/ and transfer-benchmark review note
- Review tier: none
- Gate A: not_eligible_negative_transfer_result
- Gate B: replayable_not_yet_independently_replayed
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Publication blocker: A published RESULT requires linking into protected hypothesis/experiment artifacts outside this task's scope; default to sandbox.
