# Quantum ZnSe No-Refit Transfer: TASK-0914 Contract Execution

**Contract survival outcome:** `FAIL_TO_CLEAR_PREDECLARED_MARGIN`
**Contract routing:** inconclusive/borderline memory, not a positive claim
**Scientific verdict:** `INCONCLUSIVE`  **Sandbox verdict:** `REVIEW_NEEDED`
**Task:** `TASK-0920`  **Contract:** `TASK-0914` (`STRICT_NO_REFIT_TRANSFER_CONTRACT_READY`)  **Sandbox run:** `AGENT-RUN-0090`

## Question

Executed exactly as frozen by the TASK-0914 contract (`docs/reviews/quantum-znse-no-refit-transfer-contract.md`): does the InP-calibrated size-confinement model predict the held-out ZnSe direct-size rows under controls, without refitting on ZnSe, clearing the frozen 0.05 eV survival margin?

## Frozen contract executed (no parameter chosen post-hoc)

- Calibration rows: the six InP TEM rows of `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml` (frozen row ids verified before the run).
- Holdout rows: the ten ZnSe SAXS rows of `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml` (frozen row ids verified before the run).
- Size harmonization: InP tetrahedral edge -> equal-volume sphere diameter with the frozen factor `0.608291447`; ZnSe SAXS diameter used verbatim. The `characteristic_length` sensitivity framing is reported as a descriptive diagnostic only.
- Residual axis: confinement `conf = E1s - E_bulk` with fixed bulk gaps InP `1.34 eV`, ZnSe `2.70 eV` (inputs, never fitted).
- Model family: `conf = C * d^(-n)`; `C` and `n` fitted on the calibration material only and applied to the holdout with NO refit.
- Controls: `per_material_mean` and `shuffled_size` (seed `842`) on the held-out material.
- Frozen survival rule: the transferred model clears only if its holdout confinement MAE beats the best control by at least `0.050 eV`; the margin is not relaxed after reveal.
- Primary judge: `InP -> ZnSe` on the `equivalent_diameter` framing. The reverse direction and the characteristic-length framing are secondary diagnostics and cannot change the primary verdict.

## Primary result: InP -> ZnSe (equivalent-diameter framing)

- Transfer confinement MAE: `0.099216 eV`.
- Best control (`per_material_mean`) MAE: `0.145800 eV`.
- Margin over best control: `0.046584 eV`.
- Clears the frozen `0.050 eV` margin: **no**.
- Contract outcome: **FAIL_TO_CLEAR_PREDECLARED_MARGIN** -> inconclusive/borderline memory, not a positive claim.

The transferred model beats both frozen controls on the held-out ZnSe rows, but its improvement over the per-material-mean null falls short of the frozen 0.05 eV survival margin. Per the contract this outcome is routed as inconclusive/borderline memory, not a positive claim; the margin was not relaxed, the model was not refitted, and no correction search was run.

## Per-row ZnSe holdout (primary framing)

| row | d (nm) | observed E1s (eV) | observed conf (eV) | predicted conf (eV) | residual (eV) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `toufanian-2021-znse-qd361` | 2.04 | 3.435 | 0.7350 | 0.7999 | +0.0649 |
| `toufanian-2021-znse-qd364` | 2.21 | 3.406 | 0.7060 | 0.7533 | +0.0473 |
| `toufanian-2021-znse-qd375` | 2.48 | 3.306 | 0.6060 | 0.6910 | +0.0850 |
| `toufanian-2021-znse-qd383` | 2.86 | 3.237 | 0.5370 | 0.6210 | +0.0840 |
| `toufanian-2021-znse-qd390` | 3.02 | 3.179 | 0.4790 | 0.5961 | +0.1171 |
| `toufanian-2021-znse-qd397` | 3.46 | 3.123 | 0.4230 | 0.5384 | +0.1154 |
| `toufanian-2021-znse-qd405` | 4.31 | 3.061 | 0.3610 | 0.4567 | +0.0957 |
| `toufanian-2021-znse-qd410` | 4.42 | 3.024 | 0.3240 | 0.4481 | +0.1241 |
| `toufanian-2021-znse-qd419` | 5.36 | 2.959 | 0.2590 | 0.3878 | +0.1288 |
| `toufanian-2021-znse-qd422` | 5.75 | 2.938 | 0.2380 | 0.3679 | +0.1299 |

## Directions and framings

### Forward InP -> ZnSe (equivalent-diameter, PRIMARY JUDGE)

- Calibration material: `InP` -> holdout material: `ZnSe`.
- Frozen confinement model: `conf = 1.364819 * d^(-0.749421)` (calibration train confinement MAE `0.062004 eV`).
- Transferred holdout confinement MAE: `0.099216 eV`.
- Control `per_material_mean` MAE: `0.145800 eV`.
- Control `shuffled_size` MAE: `0.237745 eV`.
- Best control: `per_material_mean` (`0.145800 eV`).
- Margin over best control: `0.046584 eV` (frozen requirement `>= 0.050 eV`; clears: no).

### Reverse ZnSe -> InP (equivalent-diameter, secondary symmetry check)

- Calibration material: `ZnSe` -> holdout material: `InP`.
- Frozen confinement model: `conf = 1.640706 * d^(-1.087954)` (calibration train confinement MAE `0.010853 eV`).
- Transferred holdout confinement MAE: `0.119375 eV`.
- Control `per_material_mean` MAE: `0.219500 eV`.
- Control `shuffled_size` MAE: `0.494510 eV`.
- Best control: `per_material_mean` (`0.219500 eV`).
- Margin over best control: `0.100125 eV` (frozen requirement `>= 0.050 eV`; clears: yes).

### Forward InP -> ZnSe (characteristic-length, secondary sensitivity)

- Calibration material: `InP` -> holdout material: `ZnSe`.
- Frozen confinement model: `conf = 1.980918 * d^(-0.749421)` (calibration train confinement MAE `0.062004 eV`).
- Transferred holdout confinement MAE: `0.354724 eV`.
- Control `per_material_mean` MAE: `0.145800 eV`.
- Control `shuffled_size` MAE: `0.383563 eV`.
- Best control: `per_material_mean` (`0.145800 eV`).
- Margin over best control: `-0.208924 eV` (frozen requirement `>= 0.050 eV`; clears: no).

Per the contract, neither secondary route changes the primary verdict: the reverse direction clears its margin and the characteristic-length framing fails badly, but the primary judge remains the InP -> ZnSe equivalent-diameter transfer.

## Relation to the exploratory TASK-0842 run

The frozen inputs (row bytes) and the committed engine are unchanged since the exploratory TASK-0842 run (AGENT-RUN-0083), so this contract execution reproduces those metrics exactly. The scientific difference is authorization and routing: TASK-0914 predeclared the full contract before this run, so the borderline outcome is now contract-executed memory rather than an exploratory observation.

## Limitations

- Two materials only (InP, ZnSe); this is a bounded two-material transfer benchmark, NOT evidence of a universal size law, a quantum-dot design law, or any material recommendation.
- The transfer is framed on the confinement term with the bulk gap as an explicit per-material input; results depend on those cited bulk-gap values and on the equal-volume edge->diameter conversion.
- Direct-size rows only (InP TEM edge length, ZnSe SAXS diameter); the calibration-derived Yu CdSe / Moreels PbS sets are excluded by the contract.
- Six InP rows and ten ZnSe rows; small samples, single source and single morphology per material.
- Sandbox evidence only. No RESULT, PRED, CLAIM, or KNOWLEDGE artifact is created; no claim is promoted.
