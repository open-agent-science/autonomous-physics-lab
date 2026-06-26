# Cross-Material Confinement Transfer Benchmark (InP <-> ZnSe)

**Scientific verdict:** `INCONCLUSIVE`
**Sandbox verdict:** `REVIEW_NEEDED`
**Task:** `TASK-0842`  **Sandbox run:** `AGENT-RUN-0083`

## Question

Does an InP-calibrated size-confinement model predict the held-out ZnSe direct-size rows under controls, without refitting on ZnSe?

## Frozen design

- Residual axis is the SIZE-CONFINEMENT term `conf = E1s - E_bulk` (eV), not absolute energy. The bulk gap is an explicit per-material INPUT, never fitted to a holdout:
  - InP `E_bulk = 1.34 eV` (room-temperature bulk gap cited in the qd-0004 planning context; standard InP Eg(300 K) ~1.344 eV.)
  - ZnSe `E_bulk = 2.70 eV` (room-temperature bulk gap reported by the Toufanian 2021 ZnSe source; standard ZnSe Eg(300 K) ~2.7 eV.)
- Confinement form `conf = C * d^(-n)` (particle-in-a-box-like; the exponent is fitted on the calibration material because Coulomb and finite-barrier corrections soften it). Both `C` and `n` are frozen from the calibration material and applied to the holdout with NO refit.
- The two datasets report different size axes: InP is a tetrahedral TEM `edge_length_nm`; ZnSe is a spherical SAXS `diameter_nm`. The PRIMARY framing converts the InP tetrahedral edge to an equivalent spherical diameter (`d_eq = 0.608291 * a_edge`, equal-volume sphere) so confinement is compared on a physically-comparable axis. A `characteristic_length` sensitivity framing (reported size axes used verbatim) is also computed.
- Controls on the held-out material: `per_material_mean` (size-independent null) and `shuffled_size` (frozen model on a deterministically permuted size axis, seed `842`).
- PREDECLARED survival rule (frozen before reveal): the transferred model clears the controls only if its holdout confinement MAE beats the best control by at least `0.050 eV`.

## Primary result: InP -> ZnSe (equivalent-diameter framing)

- Transfer confinement MAE: `0.099216 eV`.
- Best control (`per_material_mean`) MAE: `0.145800 eV`.
- Margin over best control: `0.046584 eV`.
- Clears predeclared `0.050 eV` margin: **no**.

The InP-calibrated confinement curve, transferred onto the equal-volume ZnSe diameter axis, reduces the held-out ZnSe confinement error below both controls, but the improvement over the per-material-mean null does NOT reach the predeclared survival margin. The honest reading is INCONCLUSIVE: there is a size-confinement signal that survives shuffling and beats the null, but it is not strong enough to call a clean cross-material transfer pass under the frozen rule. Per the honest-stop rule, the margin was not relaxed and the model was not refitted to rescue the result.

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

### Forward InP -> ZnSe (equivalent-diameter, PRIMARY)

- Calibration material: `InP` -> holdout material: `ZnSe`.
- Frozen confinement model: `conf = 1.364819 * d^(-0.749421)` (calibration train confinement MAE `0.062004 eV`).
- Transferred holdout confinement MAE: `0.099216 eV`.
- Control `per_material_mean` MAE: `0.145800 eV`.
- Control `shuffled_size` MAE: `0.237745 eV`.
- Best control: `per_material_mean` (`0.145800 eV`).
- Margin over best control: `0.046584 eV` (predeclared requirement `>= 0.050 eV`; clears: no).

### Reverse ZnSe -> InP (equivalent-diameter)

- Calibration material: `ZnSe` -> holdout material: `InP`.
- Frozen confinement model: `conf = 1.640706 * d^(-1.087954)` (calibration train confinement MAE `0.010853 eV`).
- Transferred holdout confinement MAE: `0.119375 eV`.
- Control `per_material_mean` MAE: `0.219500 eV`.
- Control `shuffled_size` MAE: `0.494510 eV`.
- Best control: `per_material_mean` (`0.219500 eV`).
- Margin over best control: `0.100125 eV` (predeclared requirement `>= 0.050 eV`; clears: yes).

### Forward InP -> ZnSe (characteristic-length sensitivity)

- Calibration material: `InP` -> holdout material: `ZnSe`.
- Frozen confinement model: `conf = 1.980918 * d^(-0.749421)` (calibration train confinement MAE `0.062004 eV`).
- Transferred holdout confinement MAE: `0.354724 eV`.
- Control `per_material_mean` MAE: `0.145800 eV`.
- Control `shuffled_size` MAE: `0.383563 eV`.
- Best control: `per_material_mean` (`0.145800 eV`).
- Margin over best control: `-0.208924 eV` (predeclared requirement `>= 0.050 eV`; clears: no).

The asymmetry is informative: the ZnSe-calibrated curve (10 rows, exponent ~1.09) extrapolates onto the held-out InP rows and clears the margin, while the InP-calibrated curve (6 rows, exponent ~0.75) does not quite clear it on ZnSe. The characteristic-length framing (raw tetrahedral edge vs spherical diameter, no morphology conversion) fails badly, confirming that the morphology-comparability conversion is what brings the InP curve into the ZnSe size regime; this is a modeling choice, declared up front, not a tuned knob.

## Limitations

- Two materials only (InP, ZnSe); this is a bounded two-material transfer benchmark, NOT evidence of a universal size law, a quantum-dot design law, or any material recommendation.
- The transfer is framed on the confinement term with the bulk gap as an explicit per-material input; results depend on those cited bulk-gap values and on the equal-volume edge->diameter conversion.
- Direct-size rows only (InP TEM edge length, ZnSe SAXS diameter); the calibration-derived Yu CdSe / Moreels PbS sets are excluded by design.
- Six InP rows and ten ZnSe rows; small samples, single source per material, single morphology per material.
- Sandbox evidence only. No RESULT, PRED, CLAIM, or KNOWLEDGE artifact is created; no claim is promoted.
