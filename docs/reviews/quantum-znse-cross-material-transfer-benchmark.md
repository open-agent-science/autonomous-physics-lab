# Quantum Cross-Material Confinement Transfer Benchmark (InP -> ZnSe)

**Task:** `TASK-0842`
**Campaign:** `quantum-size-effects`
**Sandbox run:** `AGENT-RUN-0083`
**Engine:** `physics_lab/engines/quantum_cross_material_transfer.py`
**Runner:** `scripts/run_quantum_cross_material_transfer.py`
**Verdict:** `INCONCLUSIVE` (sandbox `REVIEW_NEEDED`)

## Question

Does the InP-calibrated size-confinement model predict the held-out ZnSe
direct-size rows under controls, without refitting on ZnSe? This is the quantum
campaign's first genuine cross-material transfer test now that a direct-size,
independent second material (ZnSe SAXS, `qd-0004`) exists alongside the direct
InP TEM rows (`qd-0003`).

## What was frozen before the reveal

The full design was committed in the engine code before any held-out ZnSe
confinement error was inspected:

- **Residual axis = confinement term.** `conf = E1s - E_bulk` (eV), not the
  absolute 1S energy. The absolute 1S energies differ between materials mostly
  because the bulk gap differs, so an absolute-energy transfer would fail
  trivially and uninformatively. Framing on the confinement term tests the
  *size scaling*, not the band-edge offset.
- **Bulk gap is an explicit per-material INPUT, never fitted.**
  - InP `E_bulk = 1.34 eV` (the value cited in the `qd-0004` planning context;
    standard InP room-temperature gap ~1.344 eV).
  - ZnSe `E_bulk = 2.70 eV` (reported by the Toufanian 2021 ZnSe source; standard
    ZnSe room-temperature gap ~2.7 eV).
- **Confinement form `conf = C * d^(-n)`.** A particle-in-a-box-like power law.
  The ideal-box exponent is 2, but the exponent is fitted on the calibration
  material because Coulomb and finite-barrier corrections soften it. Both `C`
  and `n` are frozen from the calibration material and applied to the holdout
  with **no refit**.
- **Size-axis comparability (the key morphology decision).** The two datasets
  report different size axes: InP is a tetrahedral TEM `edge_length_nm`; ZnSe is
  a spherical SAXS `diameter_nm`. The PRIMARY framing converts the InP
  tetrahedral edge to an equal-volume sphere diameter
  (`d_eq = 0.608291 * a_edge`) so confinement is compared on a
  physically-comparable axis. A linear size-axis rescale leaves the fitted
  exponent `n` and the InP train residuals invariant; it only repositions the
  InP confinement curve onto the shared diameter axis. A
  `characteristic_length` sensitivity framing (each reported size axis used
  verbatim, no morphology conversion) is reported alongside.
- **Controls-first with a predeclared margin.** Controls on the held-out
  material are `per_material_mean` (size-independent null) and `shuffled_size`
  (the frozen model applied to a deterministically permuted size axis, seed
  842). The predeclared survival rule, frozen before the reveal: the transferred
  model clears the controls only if its held-out confinement MAE beats the best
  control by at least **0.05 eV** (the campaign baseline convention).

Only direct-size rows enter the judge: six InP TEM rows (`qd-0003`) and ten ZnSe
SAXS rows (`qd-0004`). The calibration-derived Yu CdSe (`qd-0001`) and Moreels
PbS (`qd-0002`) sets are excluded by construction.

## Result

| Direction / framing | Transfer MAE (eV) | Best control | Best control MAE (eV) | Margin (eV) | Clears 0.05 eV? |
| --- | ---: | --- | ---: | ---: | :---: |
| **InP -> ZnSe (equiv-diameter, PRIMARY)** | 0.099216 | per_material_mean | 0.145800 | +0.046584 | no |
| ZnSe -> InP (equiv-diameter) | 0.119375 | per_material_mean | 0.219500 | +0.100125 | yes |
| InP -> ZnSe (characteristic-length) | 0.354724 | per_material_mean | 0.145800 | -0.208924 | no |

Frozen InP confinement model (equivalent-diameter framing):
`conf = 1.364819 * d^(-0.749421)`, calibration train confinement MAE
`0.062004 eV`.

In both equivalent-diameter directions the transferred model also beats the
`shuffled_size` control (0.099 vs 0.238 eV forward; 0.119 vs 0.327 eV reverse),
so the size-energy pairing carries real signal.

## Reading (honest)

The primary direction is **INCONCLUSIVE**. The InP-calibrated confinement curve,
transferred onto the equal-volume ZnSe diameter axis, reduces the held-out ZnSe
confinement error below both controls, but the improvement over the
per-material-mean null does **not** reach the predeclared 0.05 eV survival
margin (it lands at +0.0466 eV, short by ~0.0034 eV). Per the honest-stop rule,
the margin was not relaxed, the model was not refitted, and no absolute-energy
fallback was used to rescue the result.

Two informative observations:

- **Direction asymmetry.** The ZnSe-calibrated curve (10 rows, exponent ~1.09)
  extrapolates onto the held-out InP rows and clears the margin, while the
  InP-calibrated curve (6 rows, exponent ~0.75) does not quite clear it on
  ZnSe. The richer, larger ZnSe calibration set transfers more cleanly than the
  sparser InP set.
- **Morphology conversion matters.** The characteristic-length framing (raw
  tetrahedral edge vs spherical diameter, no conversion) fails badly. The
  equal-volume edge->diameter conversion is what brings the InP curve into the
  ZnSe size regime. This is a modeling choice declared up front, not a tuned
  knob.

## Limitations

- Two materials only (InP, ZnSe). This is a bounded two-material transfer
  benchmark, NOT evidence of a universal size law, a quantum-dot design law, or
  any material recommendation.
- The transfer is framed on the confinement term with the bulk gap as an
  explicit per-material input; results depend on those cited bulk-gap values and
  on the equal-volume edge->diameter conversion.
- Direct-size rows only; six InP and ten ZnSe rows; one source and one
  morphology per material.
- Sandbox evidence only. No RESULT, PRED, CLAIM, or KNOWLEDGE artifact is
  created; no claim is promoted.

## Replayability (Gate B)

- Pinned command: `python scripts/run_quantum_cross_material_transfer.py --write`.
- Code reference: `physics_lab/engines/quantum_cross_material_transfer.py`.
- Input file hashes (SHA-256) over `qd-0003` and `qd-0004`, engine version, and
  git commit are recorded in
  [`../../agent_runs/AGENT-RUN-0083/metrics.json`](../../agent_runs/AGENT-RUN-0083/metrics.json)
  under `run_meta`.
- Deterministic: re-running the writer twice yields byte-identical
  `metrics.json` (verified).

## Output routing

- **Canonical destination:** sandbox `agent_runs/AGENT-RUN-0083/` (metrics +
  report) and this review note. A published RESULT would require protected
  hypothesis/experiment links outside this task's scope, so the default
  destination is sandbox; the borderline INCONCLUSIVE verdict reinforces that no
  promotion is warranted.
- **Review tier:** none; no RESULT/PRED/CLAIM/KNOW created.
- **Gate A:** not passed (the primary transfer does not clear the predeclared
  margin); no AGENT_PUBLISHED artifact.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Next gate:** maintainer review of the frozen design and the borderline
  margin. Any future strengthening (more materials, a per-material effective-mass
  prefactor, or a reviewed equivalent-diameter policy) must be a separate task;
  it must not be back-fitted onto this holdout.

See the baseline context in
[`../results/quantum-size-effects-baseline-summary.md`](../results/quantum-size-effects-baseline-summary.md)
and the ZnSe source ledger in
[`quantum-toufanian-2021-znse-source-artifact-and-extraction.md`](quantum-toufanian-2021-znse-source-artifact-and-extraction.md).
