# Quantum Size Baseline Readiness for Autonomous Pilot (TASK-0277)

**Task:** `TASK-0277`
**Campaign:** `quantum-size-effects`
**Mode:** scientific validation (readiness review only; no benchmark rerun)
**Gate verdict:** `PILOT_BLOCKED` — keep `TASK-0226` blocked for autonomous
correction-hypothesis search; allow only a maintainer-approved **narrowed**
methodology stress test if the goal is pipeline validation rather than residual
law discovery.

## Scope

This review evaluates whether the committed `TASK-0225` sandbox baseline
(`AGENT-RUN-0076`) is strong enough to unblock `TASK-0226` (first autonomous
quantum-size-effect hypothesis pilot). It uses only committed repository
artifacts. No baseline rerun, no new metrics, no autonomous hypotheses, and no
RESULT / PRED / CLAIM / KNOW mutation.

## Evidence Reviewed

| Input | Role |
| --- | --- |
| `tasks/TASK-0225-implement-quantum-size-effect-baseline-residual-benchmark.yaml` | Baseline benchmark contract (DONE). |
| `tasks/TASK-0226-run-first-autonomous-quantum-size-effect-hypothesis-pilot.yaml` | Downstream pilot contract (BLOCKED). |
| `agent_runs/AGENT-RUN-0076/` | Committed baseline run: metrics, report, limitations, preflight. |
| `docs/results/quantum-size-effects-baseline-summary.md` | Public baseline summary. |
| `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml` | Six direct InP rows (figure-digitised TEM + optical labels). |
| `docs/reviews/quantum-size-row-level-data-readiness-after-direct-seed.md` | TASK-0293 row-level gate (PASS). |
| `docs/quantum-size-effect-holdout-protocol.md` | Holdout families and property-separation policy. |
| `docs/campaigns/quantum-size-effects.md` | Campaign boundaries and forbidden wording. |

## Baseline Surface Summary

The frozen baseline is a **source-scoped consistency check**, not independent
validation of a physical size law:

- **Dataset:** `qd-0003-almeida-2023-inp-optical` — six InP tetrahedral rows,
  one material, one publication (`almeida-2023-nano-letters-inp-optical`).
- **Property axis:** `absorption_peak_eV` only; emission and bandgap are not
  mixed (PASS per preflight).
- **Size axis:** tetrahedral `edge_length_nm` with per-row TEM distribution
  sigma propagated into size-sensitivity diagnostics.
- **Split:** five train rows, one largest-size holdout (`almeida-2023-inp-620nm`,
  L = 4.112 nm).
- **Selected model:** `almeida_fixed_reference` — the published Almeida relation
  `E = 1.33 + 9.128 * L_A^-0.684` with **zero fitted parameters** on this run.
- **Scientific verdict:** `VALID_IN_RANGE` / `SANDBOX_PASS`.

### Key metrics (selected model)

| Metric | Value |
| --- | ---: |
| Train MAE | 0.066897 eV |
| Holdout MAE (620 nm) | 0.048395 eV |
| Constant train-mean holdout MAE | 0.420200 eV |
| Shuffled-size control holdout MAE | 0.375676 eV |
| Required holdout improvement vs null | 0.050 eV (met) |

The holdout beats both negative controls, confirming that size ordering carries
signal on this six-row slice. That does **not** establish that a richer
correction search on five training points would generalize.

### Per-row residual structure (selected model)

| entry_id | split | L (nm) | residual (eV) |
| --- | --- | ---: | ---: |
| `almeida-2023-inp-460nm` | train | 1.498 | +0.068 |
| `almeida-2023-inp-480nm` | train | 2.002 | −0.078 |
| `almeida-2023-inp-510nm` | train | 2.602 | −0.119 |
| `almeida-2023-inp-550nm` | train | 2.787 | +0.013 |
| `almeida-2023-inp-580nm` | train | 3.136 | +0.057 |
| `almeida-2023-inp-620nm` | holdout | 4.112 | +0.048 |

The largest train residual (−0.119 eV at 510 nm) is more than double the
holdout residual. Any autonomous correction search would be strongly incentivized
to fit this single mid-range train point.

### Fitted alternatives already in the slate

The committed metrics include train-fitted `inverse_edge_fit` and
`inverse_square_fit`. Both **worsen** holdout MAE (0.116 eV and 0.195 eV
respectively) relative to the fixed published relation (0.048 eV). This is
early evidence that additional flexibility on five training rows does not
improve the one-point holdout and may overfit train structure.

## Readiness Checks

### 1. Dataset provenance — PASS (with limits)

- Six rows are admitted direct measurement seeds (TASK-0293 PASS), not
  calibration-derived formula rows.
- Provenance is figure-digitised (SI Figure S2b TEM histograms + published
  lambda labels), second-agent audited, CC-BY 4.0 pinned.
- **Limit:** all rows share one source series and morphology; provenance is
  strong for a sandbox baseline, weak for cross-source generalization.

### 2. Property-kind separation — PASS

- Single residual axis: `absorption_peak_eV`.
- No absorption/emission/bandgap mixing.

### 3. Holdout leakage risks — PARTIAL PASS / PILOT BLOCKER

| Risk | Assessment |
| --- | --- |
| Same-source circularity | **High.** The selected baseline is the source's own published sizing relation evaluated on the source's own digitised rows. Holdout success measures internal consistency, not independent model validation. |
| One-point holdout | **High.** A single largest-size holdout cannot support multi-parameter correction search; one lucky/unlucky point dominates the verdict. |
| Material holdout | **Unavailable.** InP-only dataset; protocol material holdout cannot be exercised. |
| Size-range holdout | **Minimal.** Only extrapolation to the largest dot is tested; no smallest-dot or leave-one-out rotation is frozen in the baseline package. |
| Pre-reveal freeze | **PASS.** Holdout, model slate, controls, and threshold were committed before execution (`AGENT-RUN-0076/preflight.md`). |

### 4. Baseline metrics and outliers — ADEQUATE FOR BASELINE, INSUFFICIENT FOR PILOT

- Baseline MAE and controls are reproducible and beat null/shuffled controls.
- Train outlier at 510 nm (−0.119 eV) is the dominant correction target.
- Size-bin diagnostics show mid-range (2–3 nm) is the noisiest bin (MAE 0.070 eV,
  max residual 0.119 eV on three rows).
- **Conclusion:** sufficient to record a sandbox baseline; insufficient to gate
  autonomous correction discovery.

### 5. Negative controls — PASS for baseline, not for pilot expansion

- Constant train-mean and deterministic shuffled-size controls are present and
  informative.
- No leave-one-out rotation, no complexity-penalized model-selection audit, and
  no cross-source holdout exist for a pilot to inherit.

## Decision for TASK-0226

**Recommendation: stay blocked** for the stated purpose of autonomous
correction-hypothesis search.

`TASK-0226` requires maintainer acceptance that the baseline is sufficient for
sandbox follow-up. On the evidence above, the baseline is sufficient as **frozen
negative/positive sandbox memory** and as a **pipeline anchor**, but not as a
holdout surface strong enough to trust 1–3 executed correction candidates.

### Why unblock is not recommended

1. **Five training points** for open-ended correction search is below any
   reasonable complexity floor; overfit is the default outcome, not a edge case.
2. **Same-source baseline** means improvements risk re-fitting publication
   scatter, not discovering independent structure.
3. **Single holdout point** cannot discriminate among correction families that
   fit train residuals.
4. **Existing fitted alternatives already fail holdout** relative to the fixed
   relation, signaling that train-side flexibility is misleading on this slice.
5. **Material and source holdouts are absent**, so the pilot cannot satisfy the
   campaign protocol's structured-holdout intent.

### Optional narrowed path (maintainer-only)

If the maintainer wants to test the **autonomous pilot machinery** without
implying scientific discovery, `TASK-0226` may be narrowed to a **methodology
stress test** with all of the following frozen before execution:

**Allowed hypothesis families (at most one executed candidate plus one control):**

- Single-parameter additive offset on the fixed Almeida reference (complexity 1).
- Single-parameter power-law exponent perturbation on `L_A` with fixed
  intercept/coefficient from the published relation (complexity 1).
- One explicit **overfit control**: a train-only polynomial or multi-parameter
  fit that must be labeled `OVERFITTED` if holdout does not beat the frozen
  baseline.

**Forbidden search behavior:**

- No material-transfer, cross-publication, or multi-dataset proposals.
- No more than **one free parameter** beyond the published relation for any
  surviving candidate.
- No bandgap/emission targets or mixed property axes.
- No spherical-radius conversion or morphology change.
- No claim, RESULT, PRED, KNOW, synthesis, device, biomedical, or universal
  size-law wording.
- No rerunning or editing `AGENT-RUN-0076` metrics or the baseline selection.

**Required evaluation discipline for any narrowed pilot:**

- Report train MAE, the frozen single holdout MAE, and **leave-one-out**
  holdout MAE across all six rows (diagnostic only; not a promotion gate).
- Preserve null/shuffled/overfit outcomes as sandbox-only memory regardless of
  train improvement.
- Verdict vocabulary: expect `OVERFITTED`, `INCONCLUSIVE`, or
  `PARTIALLY_VALID` at best — not `VALID` for a new correction law.

Even under this narrowed shape, the scientific value is **workflow validation**,
not residual-law discovery. Default posture remains **blocked** until additional
independent rows or a reviewed cross-source holdout exist.

## Stop Conditions and Reopen Criteria

Keep `TASK-0226` blocked while all of the following remain true:

- Row count ≤ 6 on a single source/material slice.
- Holdout count = 1 with no committed leave-one-out or alternate holdout rotation.
- No independent second-source direct rows admitted under TASK-0293-equivalent
  gates.

Reopen autonomous correction search only after a maintainer-approved task adds at
least one of:

- a second independent direct-measurement source with ≥ 3 admissible rows, or
- a committed six-row leave-one-out evaluation package with frozen complexity
  caps and predeclared overfit controls, or
- an explicit maintainer waiver accepting a narrowed methodology stress test as
  defined above.

## Limitations of This Review

- No code rerun; conclusions are from committed `AGENT-RUN-0076` artifacts only.
- Size sensitivity uses TEM distribution sigma, not optical energy measurement
  uncertainty; residual magnitudes should not be over-interpreted as
  measurement precision.
- Figure-digitised rows inherit digitization uncertainty (cross-checked but not
  table-extracted).
- This review does not change `TASK-0226` YAML status; maintainer merge and
  closeout handle task-state transitions.

## Output Routing

| Field | Value |
| --- | --- |
| Task verdict | `PILOT_BLOCKED` (primary); optional `NARROW_METHODOLOGY_ONLY` if maintainer waives |
| Canonical destination | this review note (`docs/reviews/`) |
| RESULT / PRED / CLAIM / KNOW impact | none |
| Review tier | sandbox readiness review |
| Gate A / Gate B | not applicable |
| Claim impact | none |
| Knowledge impact | none |
| Publication blocker | autonomous correction search blocked on current six-row same-source slice |
| Next recommended task | add independent direct rows or a maintainer-approved narrowed `TASK-0226` methodology waiver task — not open-ended pilot execution |
