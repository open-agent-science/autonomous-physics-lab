# Quantum ZnSe Contract Transfer Benchmark (TASK-0914 Contract Execution)

**Task:** `TASK-0920`
**Contract:** `TASK-0914` (`STRICT_NO_REFIT_TRANSFER_CONTRACT_READY`), frozen in
[`quantum-znse-no-refit-transfer-contract.md`](quantum-znse-no-refit-transfer-contract.md)
**Campaign:** `quantum-size-effects`
**Sandbox run:** `AGENT-RUN-0090`
**Engine (reused unchanged):** `physics_lab/engines/quantum_cross_material_transfer.py`
**Runner (contract wrapper):** `scripts/run_quantum_znse_contract_transfer.py`
**Contract survival outcome:** `FAIL_TO_CLEAR_PREDECLARED_MARGIN` ->
inconclusive/borderline memory (scientific verdict `INCONCLUSIVE`, sandbox
`REVIEW_NEEDED`)

## What this task did

TASK-0914 predeclared the full admissible transfer contract — exact rows,
size harmonization, model family, controls, and survival threshold — before
this run. TASK-0920 executed exactly that contract, nothing else: no refit,
no correction search, no post-hoc threshold change, and no source-byte
redistribution. The runner verifies every frozen parameter against the
engine constants and the committed datasets **before any metric is
computed** and stops with a `ContractViolationError` on any drift (the
contract's stop condition).

## Frozen contract parameters executed

- **Rows (verified against the frozen row-id lists pre-run):** the six
  direct InP TEM rows of `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`
  (`almeida-2023-inp-460nm` ... `almeida-2023-inp-620nm`) as the calibration
  surface, and the ten direct ZnSe SAXS rows of
  `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`
  (`toufanian-2021-znse-qd361` ... `toufanian-2021-znse-qd422`) as the
  holdout. The calibration-derived Yu CdSe / Moreels PbS surfaces are
  excluded by the contract.
- **Size harmonization:** InP tetrahedral edge -> equal-volume sphere
  diameter with the frozen factor `0.608291447`; ZnSe SAXS `diameter_nm`
  verbatim. The `characteristic_length` framing (reported axes verbatim) is
  a descriptive sensitivity diagnostic only.
- **Residual axis:** confinement `conf = E1s - E_bulk` with fixed bulk-gap
  inputs InP `1.34 eV`, ZnSe `2.70 eV` (never fitted).
- **Model family:** `conf = C * d^(-n)`; `C` and `n` fitted on the
  calibration material only, then applied frozen to the holdout.
- **Controls:** `per_material_mean` (size-independent null) and
  `shuffled_size` (frozen model on a deterministically permuted holdout size
  axis, seed `842`).
- **Survival rule:** the transferred model clears only if its held-out
  confinement MAE beats the best (lowest-MAE) control by at least
  `0.05 eV`; under the margin -> inconclusive/borderline memory; not beating
  the best control -> negative memory. The margin was not relaxed.
- **Primary judge:** `InP -> ZnSe` on the `equivalent_diameter` framing;
  the reverse direction and characteristic-length framing are secondary and
  cannot change the primary verdict.

## Result

| Direction / framing | Transfer MAE (eV) | Best control | Best control MAE (eV) | Margin (eV) | Clears 0.05 eV? |
| --- | ---: | --- | ---: | ---: | :---: |
| **InP -> ZnSe (equiv-diameter, PRIMARY)** | 0.099216 | per_material_mean | 0.145800 | +0.046584 | no |
| ZnSe -> InP (equiv-diameter, secondary) | 0.119375 | per_material_mean | 0.219500 | +0.100125 | yes |
| InP -> ZnSe (characteristic-length, secondary) | 0.354724 | per_material_mean | 0.145800 | -0.208924 | no |

Frozen InP confinement model (equivalent-diameter framing):
`conf = 1.364819 * d^(-0.749421)`, calibration train confinement MAE
`0.062004 eV`. The transferred model also beats the `shuffled_size` control
in both equivalent-diameter directions (forward 0.099 vs 0.238 eV; reverse
0.119 vs 0.327 eV), so the size-energy pairing carries signal.

## Verdict (one verdict, per the frozen rule)

**FAIL_TO_CLEAR_PREDECLARED_MARGIN.** The primary InP -> ZnSe transfer beats
both frozen controls but its margin over the best control
(`+0.046584 eV`) falls short of the frozen `0.05 eV` survival threshold by
`~0.0034 eV`. Per the contract's frozen routing this is
**inconclusive/borderline memory, not a positive claim** — and not strictly
negative memory either, because the transferred model does beat both
controls. The margin was not relaxed, the model was not refitted, and no
secondary route (the reverse direction clears; the characteristic-length
framing fails badly) was used to change the primary verdict.

## Relation to the exploratory TASK-0842 run

The frozen input bytes (`qd-0003`, `qd-0004` SHA-256 unchanged) and the
committed engine are identical to the exploratory TASK-0842 run
([`quantum-znse-cross-material-transfer-benchmark.md`](quantum-znse-cross-material-transfer-benchmark.md),
`AGENT-RUN-0083`), so this contract execution reproduces those metrics
exactly. What changed is authorization and routing: TASK-0914 froze the
contract before this run, so the borderline outcome now stands as
contract-executed memory instead of an exploratory observation. This lane
should not be rerun on the same surfaces expecting a different outcome.

## Limitations (no-claim wording)

- Two materials only (InP, ZnSe). This is a bounded two-material transfer
  benchmark, NOT evidence of a universal size law, a quantum-dot design law,
  or any material, device, or biomedical recommendation.
- Confinement-term framing with fixed cited bulk gaps and the frozen
  equal-volume edge->diameter conversion; results depend on those inputs.
- Direct-size rows only; six InP and ten ZnSe rows; one source and one
  morphology per material.
- Sandbox evidence only. No RESULT, PRED, CLAIM, or KNOWLEDGE artifact is
  created; no claim is promoted.

## Replayability (Gate B)

- Pinned command: `python scripts/run_quantum_znse_contract_transfer.py --write`.
- Code reference: `physics_lab/engines/quantum_cross_material_transfer.py`
  (reused unchanged from TASK-0842).
- Input file SHA-256 hashes over `qd-0003` and `qd-0004`, engine version,
  and git commit are recorded in
  [`../../agent_runs/AGENT-RUN-0090/metrics.json`](../../agent_runs/AGENT-RUN-0090/metrics.json)
  under `run_meta`.
- Deterministic: running the writer twice yields byte-identical
  `metrics.json` (verified; identical SHA-256).
- Contract-compliance tests: `tests/test_quantum_znse_contract_transfer.py`
  (frozen rows enforced, tampered holdout stops the run, wrapper metrics
  equal the engine's, deterministic replay).

## Output routing

- **Task verdict:** `INCONCLUSIVE` (contract outcome
  `FAIL_TO_CLEAR_PREDECLARED_MARGIN`, routed as inconclusive/borderline
  memory per the frozen rule).
- **Canonical destination:** sandbox `agent_runs/AGENT-RUN-0090/` plus this
  review note. TASK-0920's scope routes the outcome to review memory; it
  does not explicitly clear Gate A for a RESULT candidate, and the
  borderline outcome reinforces that no promotion is warranted.
- **Source boundary:** re-expressed factual numeric rows only (Toufanian
  2021 ZnSe, Almeida 2023 InP); no publisher PDFs, figures, or table images
  vendored; no source-byte redistribution.
- **Frozen controls:** `per_material_mean` and `shuffled_size` (seed 842)
  with the `0.05 eV` survival margin, unchanged after reveal.
- **Review tier:** none; no RESULT/PRED/CLAIM/KNOW created.
- **Gate A:** not attempted (sandbox routing per task scope).
- **Gate B:** not attempted here; the run is replay-ready (pinned command,
  hashes, deterministic double-run) for a future independent replay.
- **Claim impact:** none. **Knowledge impact:** none. **Prediction impact:**
  none. **Dataset impact:** none (`qd-0003`, `qd-0004` unchanged).
- **Do-not-repeat lanes:** do not rerun this exact contract on the same row
  surfaces expecting a different outcome; do not reopen the
  TASK-0850/TASK-0871 effective-mass rescue (it remains negative memory per
  [`quantum-effective-mass-negative-memory-routing.md`](quantum-effective-mass-negative-memory-routing.md));
  do not run correction searches, threshold relaxations, or post-hoc
  framing selection on these holdouts. Any strengthening (more materials, a
  reviewed conversion policy) requires a new maintainer-approved task and a
  fresh contract before any metric is inspected.
