# Materials MD-0002 Disjoint A-Site Cation-Family Transfer Benchmark (TASK-0838)

**Task:** `TASK-0838`
**Campaign:** Materials Property Residuals
**Sandbox run:** `AGENT-RUN-0081` (sandbox-only; no canonical result written)
**Verdict:** `SANDBOX_FAIL` — the frozen advantage is family-localized; it does
not transfer across the disjoint A-site cation family.

## Question

Does the frozen `RESULT-0021` baseline model transfer across a chemically
disjoint A-site cation-family split of the committed MD-0002 stable
ternary-oxide slice? The model under test is the exact unordered non-oxygen
cation-pair train-mean of `formation_energy_per_atom` with a global-train-mean
fallback (`model_cation_pair_mean`, the `RESULT-0021` best model). The split is
the single route the `TASK-0817` transfer scout selected and that the MD-0002
holdout manifest pre-authorizes under `pre_score_split_axes.cation_pair_family`.

This is a BOUNDED, computed-DFT, model-vs-model generalization benchmark. The
judge is computed-DFT (Materials Project, CC BY 4.0), so per the
computed/simulated-is-not-the-judge guardrail this is **not** a
materials-discovery, material-design-law, property-prediction, synthesis, or
device statement.

## Freeze-first discipline

- The frozen model and its descriptor (the exact unordered non-oxygen cation
  pair) were imported unchanged from
  `physics_lab/engines/materials_md0002_baseline.py` and fixed **before** any
  transfer error was read. No post-hoc descriptor, feature, or hyperparameter
  change was made after seeing the transfer error.
- MD-0002 rows, the frozen baseline engine, and the `RESULT-0021` artifact were
  not edited.
- Only committed MD-0002 rows are used; no live fetch.

## Predeclared split (frozen before any metric)

Each of the 362 included formation-energy rows carries exactly one alkali **or**
alkaline-earth A-site cation and exactly one first-row (3d) transition cation, so
the A-site family label is total and the two classes are mutually exclusive:

| A-site family class | Rows |
| --- | --- |
| `alkali_transition` (alkali + 3d transition) | 225 |
| `alkaline_earth_transition` (alkaline-earth + 3d transition) | 137 |
| total | 362 |

This reproduces the deterministic 225 / 137 partition the `TASK-0817` scout read
from the committed rows. Leakage is **none by construction**: the two families
share no A-site cation, and (as the run confirms) no unordered cation pair.

Both holdout directions are evaluated:

1. train on `alkali_transition` (225), hold out `alkaline_earth_transition` (137);
2. train on `alkaline_earth_transition` (137), hold out `alkali_transition` (225).

## Predeclared pass/fail metric and margin (frozen before any metric)

- **Metric:** held-out-family holdout MAE (eV/atom).
- **Controls:** `null_global_mean` (global train mean), `shuffled_cation_pair`
  (cation-pair labels permuted on train before grouping; min over seeds
  `[0, 1, 2, 7, 11]`), and `per_class_median` (train-family median).
- **Survival margin (stated explicitly):** the frozen model must beat the **best**
  control's held-out MAE by at least **0.05 eV/atom** on the held-out family, in
  **both** disjoint-family directions, to count as transferring. (The 0.05
  eV/atom floor mirrors the in-split baseline contract's absolute-improvement
  gate; transfer is a strictly harder regime, so the same floor over the best
  control is a conservative, non-trivial bar.)

## Result vs controls

| Direction | Frozen MAE | null | per-class-median | shuffled | best control | margin | clears ≥0.05? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| hold out `alkaline_earth_transition` | 0.729781 | 0.729781 | 0.833408 | 0.729781 | `null_global_mean` 0.729781 | 0.0 | no |
| hold out `alkali_transition` | 0.791686 | 0.791686 | 0.745149 | 0.791686 | `per_class_median` 0.745149 | -0.046537 | no |

Because the two families share no cation pair, the frozen exact-cation-pair model
falls back to the global train mean on **every** held-out row (137 / 137 and
225 / 225). It is therefore numerically identical to the `null_global_mean` and
`shuffled_cation_pair` controls in both directions, and it is **worse** than the
`per_class_median` control when holding out `alkali_transition`.

## Verdict and honest stop

`SANDBOX_FAIL` — `advantage_is_family_localized`. The frozen cation-pair
advantage that `RESULT-0021` shows on the within-family random split does **not**
transfer across a chemically disjoint A-site cation family on this computed-DFT
slice. This is the honest negative the task explicitly accepts (the cation-pair
signal is localized, consistent with the `TASK-0789` random-pair-holdout collapse
and the `TASK-0790` descriptor-ablation finding). No refit, feature addition, or
split change was made to rescue it.

## Gate-B-replayable provenance

Deterministic: re-running the command reproduces identical metrics, and
`tests/test_materials_md0002_transfer.py` asserts the committed
`agent_runs/AGENT-RUN-0081/metrics.json` equals a fresh in-process replay.

- **Command:** `python scripts/run_materials_md0002_transfer.py --config examples/benchmarks/materials_md0002_formation_energy.yaml --output-dir agent_runs/AGENT-RUN-0081 --write-report`
- **code_reference:** `physics_lab/engines/materials_md0002_transfer.py`
- **engine_version:** `0.1.0`
- **git_commit (branch point):** `fb2c2920701ee1b8ddd9fba69e9c27d45eb40b8a`
- **Seeds:** shuffle-control seeds `[0, 1, 2, 7, 11]` (no other randomness).
- **input_file_hashes (sha256):**
  - `examples/benchmarks/materials_md0002_formation_energy.yaml`: `cb18158c21904341d64d22bdea8c4c265badf76297ad1331184d645948467e51`
  - `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`: `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1`
  - `data/materials/md0002_holdout_manifest.yaml`: `c98c6e699d5fd0146f3456c4726bf71adbd5aeea2cff6aada9190671095e5451`

## Provenance / no-claim

Computed-DFT MD-0002 stable ternary-oxide slice only (Materials Project, CC BY
4.0; cite Jain et al., APL Materials 1, 011002 (2013),
`doi:10.1063/1.4812323`), declared in `data/DATA_LICENSES.yaml`
(`materials-project-ternary-oxides-md0002`). MD-0002 is internally reusable but
not externally published; this is an internal scoped benchmark, not a dataset
release. No `RESULT-0021` metric or review tier is changed; no MD-0002 row,
holdout membership, claim, or knowledge artifact is edited.

## Output-routing summary

- **Task verdict:** `FALSIFIED` for the transfer hypothesis on this slice (the
  frozen advantage does not transfer); recorded as a sandbox negative.
- **Canonical destination:** sandbox-only `agent_runs/AGENT-RUN-0081/` plus this
  transfer-benchmark review note. No `results/`, `prediction_registry/`,
  `claims/`, or `knowledge/` artifact is created.
- **Review tier:** `none`.
- **Gate A:** not eligible (negative transfer result). **Gate B:** replayable
  (pinned command, code reference, input hashes, engine version, git commit;
  re-run twice → identical metrics), not yet independently replayed.
- **Transfer margin vs controls:** frozen model fails the predeclared
  ≥0.05 eV/atom margin over the best control in both directions (margins 0.0 and
  -0.046537 eV/atom).
- **Claim impact:** none (no `CLAIM-*` change).
- **Knowledge impact:** none (no `KNOW-*` change).
- **Limitations / blockers:** computed-DFT judge → bounded benchmark only; a
  single disjoint A-site cation-family split; the disjoint families share no
  cation pair, forcing the global fallback on every held-out row; a published
  RESULT would require linking into protected hypothesis/experiment artifacts
  outside this task's scope, so the run defaults to sandbox.
