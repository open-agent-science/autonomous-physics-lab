# Nuclear Next Non-F2 Lane Selection

- Task: `TASK-0746`
- Campaign: Nuclear Mass Surface
- Mode: planning only — lane selection and controls-first contract; **no scoring**
- Unblocking decision: `OPEN_ONE_NON_F2_LANE_SELECTION_NO_SCORING`
  ([nuclear-result0018-diagnostic-negative-memory-and-next-lane.md](nuclear-result0018-diagnostic-negative-memory-and-next-lane.md))
- Selected lane: **F6 — Wigner cusp term** (candidate `WIGNER-CUSP-001`)
- Verdict: `not_applicable` (selection only; the sprint is a separate future task)

## Scope

This note selects exactly one bounded, materially non-F2, no-leakage Nuclear
hypothesis family and defines its controls-first contract per
[`nuclear-controls-first-hypothesis-gauntlet.md`](../notes/nuclear-controls-first-hypothesis-gauntlet.md).
It does **not** run the sprint, fit a model, score any candidate, fetch reveal
data, inspect post-AME2020 holdout values, or promote any `RESULT`/`PRED`/
`CLAIM`/`KNOW` artifact. It uses committed `NMD-0003` artifacts and committed
Nuclear review memory only.

## Why F2 (and the other exhausted lanes) are excluded

`RESULT-0018` exhausted the F2 component-ablation lane: the best single component
(`magic_n_near`, +0.0748 MeV full-known) does not clear the 0.25 MeV survival
margin, and no variant survives. F2 must not be reopened on the current contract.

The selected family is also checked against every entry in the
[do-not-repeat ledger](nuclear-do-not-repeat-diagnostic-lanes.md). The following
families are already `NEGATIVE` / `CONTROL_DOMINATED` / `STOP` / diagnostic-only
and are **not** eligible: local curvature (F1), high-error cluster (F2),
shell-axis (F3), source-status (F4), pairing-asymmetry interaction,
magic-parity boundary, magic-distance interaction, neutron-rich boundary
transfer, isotope-chain leave-family-out, residual-free high-error cluster,
coulomb–surface interaction, odd-even shell interaction, deformation proxy,
measured/extrapolated boundary, mid-mass isotope-chain gap, and the broad
factory slates.

## Material disjointness of the Wigner cusp term

The Wigner energy is an extra binding contribution that peaks as a **sharp cusp
at `N = Z`**, attributed to the isospin / approximate SU(4) symmetry of the
nuclear force. The standard liquid-drop symmetry energy (`∝ (N − Z)² / A`) and
its even-power refinements are **smooth and differentiable through `N = Z`** and
cannot, by construction, represent a cusp. The Wigner feature is an **odd,
non-smooth** function of `N − Z` (e.g. `|N − Z|`), which is structurally
orthogonal to:

- shell / magic-proximity features (F2/F3) — these key on `{2,8,20,28,50,82,126}`
  proximity, not on the `N = Z` line;
- pairing / odd-even features — these key on the parities of `Z` and `N`, not on
  `|N − Z|`;
- even-power asymmetry refinements already proposed
  (`HYP-PROPOSAL-0022` quadratic, `HYP-PROPOSAL-0033` quartic,
  `HYP-PROPOSAL-0034` neutron-excess) — all smooth even functions;
- local curvature / deformation / neutron-rich-boundary lanes.

This disjointness is **operationalized as a control** (the asymmetry-only
control in section 5): the candidate must beat a smooth `(N − Z)/A` control,
otherwise it is not materially distinct from bulk asymmetry and is rejected.

Data support is adequate for a retrospective test: the `NMD-0003` training split
has **185** rows with `|N − Z| ≤ 2` (40 exactly on `N = Z`, up to `A ≈ 108`), so
the cusp region is populated rather than empty, while remaining sparse enough
that the holdout signal is expected to be weak (see scope/stop conditions).

## Controls-First Lane Contract (`WIGNER-CUSP-001`)

### 1. Hypothesis family and candidate identity
- Family: **F6 — Wigner cusp** (new family; classified here under the
  cross-family no-leakage contract before any run).
- Candidate: `WIGNER-CUSP-001`.
- Hypothesis: adding a Wigner-style cusp term keyed on `|N − Z|` reduces
  baseline mass residuals near `N = Z` beyond what smooth asymmetry and
  shell/pairing features achieve.
- Mechanism: isospin/SU(4) symmetry produces extra binding peaking at `N = Z`; a
  smooth even-power symmetry energy cannot reproduce the cusp.
- Not in scope: heavy neutron-rich behavior, deformation, shell structure, or any
  reveal/prediction scoring.

### 2. Allowed inputs
- `Z`, `N`, `A`, their parities, and deterministic functions thereof — in
  particular `|N − Z|` and a Wigner cusp indicator `W = |N − Z|` (optionally a
  bounded `1/(1 + |N − Z|)` cusp-sharpness form with a single shape parameter).
- Committed baseline residuals (baseline-only) as the comparison surface.
- Committed measurement uncertainties from `data/nuclear_masses/nmd-*.yaml`.
- All inputs are deterministic functions of `Z`, `N`, `A` only, so the family is
  `predictive_eligible` by construction under
  [`nuclear-residual-feature-no-leakage-contract.md`](../nuclear-residual-feature-no-leakage-contract.md).

### 3. Forbidden inputs
- The target row's own residual, mass, or binding energy, or any function
  thereof.
- Any candidate-fit residual (only baseline residuals are admissible).
- Post-AME2020 comparison values for any holdout / `PRED-*` row.
- Training-membership flags, residual-quantile flags, source-status (F4), or any
  feature that differs between the same row in training vs holdout.

### 4. Baseline
- Baseline: the canonical committed `NMD-0003` baseline binding-energy/mass-excess
  fit used by prior Nuclear lanes; pin its canonical artifact path / commit SHA in
  the sprint preflight.
- Only baseline residuals (never candidate-fit residuals) feed the comparison
  surface.

### 5. Controls (minimum two; three declared)
1. **Asymmetry-only control** — feature `(N − Z)² / A` (and/or `|N − Z| / A`),
   a smooth even/normalized asymmetry surrogate. Proves the cusp carries
   information **beyond bulk asymmetry**. (Primary disjointness control.)
2. **Matched random control** — same `|N − Z|` marginal distribution shuffled
   across rows. Proves the candidate is not fitting the residual distribution at
   random.
3. **Smooth-A control** — a smooth monotonic function of `A` alone, matched in
   coarse scale. Proves the candidate is not a mass-smoothness artifact.

The candidate must beat **all** declared controls; beating only one defaults the
verdict to `DIAGNOSTIC_ONLY` / `INCONCLUSIVE`.

### 6. Holdout, split, and leave-one-out logic
- Splits from the frozen `data/nuclear_masses/nmd-0003-split-manifest.yaml`:
  training `ame2020_measured_training_excluding_post_ame2020_primary_holdout`
  (2309 rows); retrospective time-split holdout `primary_post_ame2020_holdout`
  (295 rows). Declare an internal validation slice from the training rows
  **before** scoring.
- The Wigner feature is a pure per-row function of `Z`, `N`, `A`, so no neighbor
  cache or leave-one-out window is required; coefficient stability is checked by
  leave-one-out resampling of the fitted Wigner coefficient(s).
- No-peek boundary: the lane may not see post-AME2020 values for any holdout row.

### 7. Leakage audit (to be confirmed in the sprint preflight)
- No input crosses train/validation/holdout/reveal boundaries.
- No input is a function of the target row's residual/mass/binding energy.
- No candidate-fit residual reused; only baseline residuals.
- No future comparison row contributes to the feature.
- Feature is a deterministic function of `Z`, `N`, `A` only.

### 8. Failure / stop conditions (declared before scoring)
- Classify as `NEGATIVE_RESULT` / `INCONCLUSIVE` if the candidate fails to beat
  **both** the asymmetry-only and the matched-random control on `full_known` by
  the inherited survival margin (≥ 0.25 MeV); or
- beats controls on `full_known` but regresses the primary holdout panel; or
- the leakage audit fails any item; or
- the Wigner coefficient is unstable under leave-one-out resampling; or
- the cusp is not materially distinct from the asymmetry-only control (control
  matches the candidate within margin).

### 9. Output routing (for the future sprint)
- May write: `agent_runs/AGENT-RUN-NNNN/*` (schema-valid), a
  `docs/reviews/nuclear-f6-wigner-cusp.md` lane note, and tests for any reusable
  feature/runner code, with a `promotion_boundary` block
  (`writes_canonical_result: false`, `claim_promotion_allowed: false`,
  `prediction_registry_allowed: false`).
- May **not** write `PRED-*`, `CLAIM-*`, `KNOW-*`, `results/.../result.yaml`, or
  any reveal score without a separate maintainer-approved task.

### 10. Public wording boundary
- Allowed: "retrospective", "sandbox evidence", "negative result", "diagnostic
  only", "bounded follow-up candidate", "inconclusive", "beats/fails declared
  controls by X on subset Y".
- Forbidden: "discovery", "new nuclear law", "broad formula", "explains nuclear
  masses", "predicts" without a frozen `PRED-*`, "we have found", "Wigner-energy
  breakthrough".

## Recommended future task (maintainer-assigned id)

A single bounded sprint task should execute `WIGNER-CUSP-001` under this
contract — for example *"Run bounded no-leakage Wigner-cusp (`|N − Z|`) residual
sprint under the controls-first gauntlet"*. It must stay sandbox-only, run the
three declared controls, and report one verdict from the gauntlet vocabulary.
This selection note does **not** assign a canonical `TASK-XXXX` id; canonical id
assignment is maintainer-only.

## Output Routing Summary

- Task verdict: `not_applicable` (lane selection / planning only).
- Canonical destination:
  `docs/reviews/nuclear-next-non-f2-lane-selection.md`.
- Review tier: `none`.
- Gate A status: `not_attempted`.
- Gate B status: `not_applicable`.
- Claim impact: none; `CLAIM-0010` remains `DRAFT`.
- Knowledge impact: none.
- Result artifact impact: none; no `RESULT`/`PRED` created or changed.
- Limitations / blockers: the Wigner cusp region is populated but sparse
  (185 rows `|N − Z| ≤ 2`), and the post-AME2020 holdout is neutron-rich, so the
  retrospective signal is expected to be weak; the lane defaults to
  `INCONCLUSIVE` under time-split unless it clears all controls and the survival
  margin. Execution, controls, and any promotion remain a separate
  maintainer-approved task.
