# Quantum ZnSe no-refit transfer contract

Task: `TASK-0914`
Campaign: `quantum-size-effects`
Primary future task: `TASK-0920`
Verdict: `STRICT_NO_REFIT_TRANSFER_CONTRACT_READY`
Review date: 2026-07-02

## Scope

This note freezes the admissible contract for any next ZnSe/InP transfer task.
It runs no benchmark metrics, adds or edits no rows, vendors no source bytes,
refits no model input, and creates no `RESULT`, `PRED`, `CLAIM`, or `KNOW`
artifact.

The contract is intentionally narrow. It allows a strict no-refit transfer run
or publication-preflight over the existing direct InP and ZnSe row surfaces. It
does not reopen the failed effective-mass route, and it does not authorize a new
correction search.

## Decision

`STRICT_NO_REFIT_TRANSFER_CONTRACT_READY`.

A future task may execute only the contract below. If it needs different rows,
size semantics, model family, controls, margin, or output routing, it must stay
blocked and ask for a new maintainer decision before any metric is inspected.

## Frozen Input Rows

Use exactly these committed direct-size absorption rows.

InP calibration surface:

- path: `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`
- material: `InP`
- morphology: `tetrahedral`
- size axis as recorded: `edge_length_nm`
- property axis: `absorption_peak_eV`
- row count: 6
- row ids:
  - `almeida-2023-inp-460nm`
  - `almeida-2023-inp-480nm`
  - `almeida-2023-inp-510nm`
  - `almeida-2023-inp-550nm`
  - `almeida-2023-inp-580nm`
  - `almeida-2023-inp-620nm`

ZnSe holdout/source surface:

- path: `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`
- material: `ZnSe`
- morphology: `spherical`
- size axis as recorded: `diameter_nm`
- property axis: `absorption_peak_eV`
- row count: 10
- row ids:
  - `toufanian-2021-znse-qd361`
  - `toufanian-2021-znse-qd364`
  - `toufanian-2021-znse-qd375`
  - `toufanian-2021-znse-qd383`
  - `toufanian-2021-znse-qd390`
  - `toufanian-2021-znse-qd397`
  - `toufanian-2021-znse-qd405`
  - `toufanian-2021-znse-qd410`
  - `toufanian-2021-znse-qd419`
  - `toufanian-2021-znse-qd422`

Excluded surfaces:

- `qd-0001-yu-2003-absorption.yaml`
- `qd-0002-moreels-2009-pbs-absorption.yaml`
- any calibration-curve-derived, emission, band-edge, device, biomedical, or
  non-direct-size row surface
- any new ZnSe or InP row not present in the two frozen paths above

## Size And Residual Contract

Primary size-axis harmonization:

- Convert InP tetrahedral edge length `a_edge` to equal-volume spherical
  diameter with the frozen factor `0.608291447`.
- Use ZnSe SAXS `diameter_nm` verbatim.
- Treat the converted InP equivalent diameter and ZnSe diameter as the primary
  transfer size axis.

Sensitivity framing:

- A future task may also report the `characteristic_length` sensitivity where
  each source size axis is used as recorded.
- The sensitivity framing is descriptive only. It must not override, rescue, or
  replace the primary verdict after metrics are known.

Residual axis:

- Score confinement energy only: `confinement_ev = E1s - E_bulk`.
- Use fixed bulk-gap inputs: `InP = 1.34 eV`, `ZnSe = 2.70 eV`.
- Do not fit bulk gaps to either material.
- Do not score absolute `E1s` as the primary quantity.

## Fixed Model And Directions

Model family:

- `confinement_ev = C * d^(-n)`
- Fit `C` and `n` only on the calibration material for a direction.
- Apply the frozen `C` and `n` to the held-out material without refit.

Primary judge:

- Direction: `InP -> ZnSe`
- Framing: `equivalent_diameter`
- Calibration rows: the six InP rows above
- Holdout rows: the ten ZnSe rows above

Secondary reporting allowed:

- `ZnSe -> InP` under the same `equivalent_diameter` rule may be reported as a
  symmetry check.
- `characteristic_length` sensitivity may be reported as a morphology-sensitivity
  check.
- Neither secondary route may change the primary verdict.

Forbidden model changes:

- no effective-mass scaling
- no tuned masses
- no target-material coefficient, exponent, intercept, bulk gap, geometry, or
  threshold fit
- no residual correction, ensemble, or post-hoc route selection
- no material-specific rescue after seeing holdout errors

## Controls And Survival Threshold

Required controls on each held-out material:

- `per_material_mean`: size-independent held-out-material mean confinement
- `shuffled_size`: frozen transferred model applied to a deterministic
  permutation of the held-out size axis, seed `842`

Survival rule:

- Let the best control be the required control with the lower MAE.
- The transferred model clears only if its held-out confinement MAE beats the
  best control MAE by at least `0.05 eV`.
- If the transferred model beats the best control by less than `0.05 eV`, route
  the primary outcome as inconclusive/borderline memory, not a positive claim.
- If it does not beat the best control, route as negative memory.
- The margin must not be relaxed after reveal.

## Effective-Mass Negative-Memory Boundary

The TASK-0850/TASK-0871 effective-mass route remains negative memory. A future
ZnSe/InP task must not rerun that route as a rescue unless a separate task first
changes the scientific surface before scoring. Disallowed repeat conditions are:

- same six InP rows and same ten ZnSe rows;
- same equivalent-diameter primary mapping;
- same scalar bulk masses;
- `C_target = C_source * mu_source / mu_target`;
- same controls and `0.05 eV` margin.

Changing only scalar masses, selecting the favorable size framing after reveal,
or adding a fitted residual term does not reopen the lane.

## Future Task Shape

`TASK-0920` may be made executable after `TASK-0914` closeout if it adopts this
contract unchanged.

Suggested execution scope:

- run the existing deterministic no-refit transfer implementation or an exact
  workflow wrapper around it;
- record input hashes for `qd-0003`, `qd-0004`, and the implementation path;
- report primary verdict from `InP -> ZnSe` / `equivalent_diameter` only;
- report reverse and characteristic-length outcomes as secondary diagnostics;
- preserve source-rights and row-provenance wording;
- route output as a bounded review note or a `RESULT` candidate only if the
  task explicitly clears the result-promotion gates.

Suggested validation:

- `python -m ruff check .`
- `python -m pytest tests/test_docs_links.py tests/test_quantum_cross_material_transfer.py`
- `python -m physics_lab.cli validate-repo . --strict --fail-on-warnings`

## Stop Conditions

Stop before running or packaging metrics if a future task tries to:

- add, remove, relabel, reorder, or rederive any row;
- vendor publisher PDFs, figures, supporting information, screenshots, or table
  images;
- mix ZnSe rows with Yu/Moreels calibration-derived rows or any non-direct-size
  source;
- tune masses, exponents, coefficients, bulk gaps, geometry maps, or thresholds
  on the held-out material;
- promote a result because a secondary direction or sensitivity framing looks
  favorable while the primary judge does not clear;
- make material recommendation, biomedical, device-performance, design-law, or
  universal quantum-size wording.

## Output Routing

- Task verdict: `STRICT_NO_REFIT_TRANSFER_CONTRACT_READY`.
- Canonical destination:
  `docs/reviews/quantum-znse-no-refit-transfer-contract.md`.
- Result impact: none; no `RESULT` artifact is created or edited.
- Gate A status: not attempted; this is pre-metric transfer readiness only.
- Gate B status: not attempted.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Dataset impact: none; `qd-0003`, `qd-0004`, and source manifests are unchanged.
- Safe public boundary: two-material, direct-size, no-refit transfer contract
  only; no material recommendation, device-performance, biomedical, design-law,
  or universal quantum-size claim.