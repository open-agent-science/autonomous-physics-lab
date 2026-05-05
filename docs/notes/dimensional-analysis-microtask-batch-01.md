# Dimensional Analysis Microtask Batch 01

**Task:** TASK-0080
**Campaign:** dimensional-analysis-validator
**Date:** 2026-05-05
**Status:** REVIEW_NEEDED

---

## Completed Microtasks

### DAV-001 — Add one clearly dimensionally valid formula (challenge entry)

**Item added:** DA-016 — Mean thermal speed

**Formula:** `v_th = sqrt(3 * k_B * T / m)`

**Domain:** statistical_physics

**SI dimension rationale:**

- LHS: `v_th` — [m s⁻¹] = L T⁻¹
- RHS: `sqrt(k_B * T / m)` = sqrt([kg m² s⁻² K⁻¹] · [K] / [kg]) = sqrt([m² s⁻²]) = L T⁻¹
- Factor 3 is dimensionless.

**Verdict:** VALID ✓ (confirmed by engine)

**Limitation:** The engine confirms dimensional consistency only. The factor of 3
(from the Maxwell–Boltzmann distribution) is not checked — a formula
`v_th = sqrt(k_B * T / m)` (missing the 3) would also pass as VALID dimensionally.

---

### DAV-002 — Add one clearly dimensionally invalid formula (challenge entry)

**Item added:** DA-119 — Entropy with wrong temperature exponent

**Formula:** `S = Q / T**2`

**Domain:** thermodynamics

**SI dimension rationale:**

- LHS: `S` — [kg m² s⁻² K⁻¹]
- RHS: `Q / T²` — [kg m² s⁻²] / [K²] = [kg m² s⁻² K⁻²]
- Mismatch: K⁻¹ vs K⁻². The exponent on T should be 1 (Clausius entropy S = Q/T).

**Verdict:** INVALID ✓ (confirmed by engine)

**Limitation:** The engine identifies the dimensional mismatch but cannot state
which exponent is physically correct. The reason field documents the expected
correction.

---

### DAV-008 — Add one cross-domain challenge item outside mechanics (challenge entry)

**Item added:** DA-018 — Doppler frequency shift

**Formula:** `f_obs = f_src * (v_s + v_obs) / (v_s + v_src)`

**Domain:** waves

**SI dimension rationale:**

- LHS: `f_obs` — [s⁻¹]
- RHS: `f_src * (v_s + v_obs) / (v_s + v_src)` = [s⁻¹] · [m s⁻¹] / [m s⁻¹] = [s⁻¹]
- The velocity ratio is dimensionless; addition within numerator and denominator
  requires matching dimensions (m s⁻¹ + m s⁻¹), which holds.

**Verdict:** VALID ✓ (confirmed by engine)

**Limitation:** Signs in the Doppler formula depend on convention (approaching vs
receding source/observer). The dimensional check is sign-agnostic and cannot
verify the correct sign convention.

---

### DAV-005 — Audit one existing challenge item for wording clarity

**Item audited:** DA-011 — Snell's law (`n1 * sin(theta1) = n2 * sin(theta2)`)

**Finding:**

DA-011 has `expected_verdict: VALID` and all variables are dimensionless
(refractive indices and angles). The current validator fires its
`all-variables-dimensionless` SUSPICIOUS heuristic on this formula, producing
a disagreement (expected VALID, computed SUSPICIOUS).

The same issue affects DA-406 (Snell's law as KNOWN_LIMIT_FAIL).

**Root cause:** The SUSPICIOUS heuristic is designed to catch semantically empty
formulas such as DA-310 (`r = (v/c)/(m/kg)`), but it also fires for physically
meaningful formulas whose variables happen to be dimensionless by SI convention
(refractive index, angle, ratio).

**Recommended wording clarification:**

The `reason` field for DA-011 should explicitly note that the formula is
physically meaningful despite all variables being dimensionless, and that this
class of item represents a known validator scope limit. A future schema version
could add a `validator_scope_note` field to flag such items for human review
rather than treating the SUSPICIOUS verdict as a pass or fail.

**Status:** REVIEW_NEEDED — no change made to expected_verdict or engine
(this task scope is documentation only; engine changes require a separate task).

**Limitation:** This audit identifies the wording gap but does not propose a
complete heuristic fix. Correctly distinguishing physically meaningful
dimensionless formulas from semantically empty ones likely requires domain
knowledge beyond dimensional analysis.

---

### DAV-010 — Define one boundary case between SUSPICIOUS and INVALID

**Note: SUSPICIOUS vs INVALID boundary criterion**

**Criterion as implemented in the MVP engine:**

| Condition | Verdict |
|---|---|
| LHS dimension ≠ RHS dimension | INVALID |
| LHS dimension = RHS dimension AND all variables dimensionless | SUSPICIOUS |
| LHS dimension = RHS dimension AND at least one variable is dimensional | VALID |
| Engine cannot parse the expression | INCONCLUSIVE |

**Example on each side of the SUSPICIOUS / INVALID boundary:**

- **SUSPICIOUS:** `alpha = e**2 / (h_bar * c * eps0)` with all variables
  declared dimensionless. Dimensions balance (both sides dimensionless) but
  no physical scale is checked. The engine cannot confirm the formula is
  physically meaningful.

- **INVALID:** `F = m * v` (with F: kg m s⁻², m: kg, v: m s⁻¹) gives
  RHS = kg m s⁻¹ ≠ kg m s⁻². Dimension mismatch → INVALID.

**Key boundary rule:** SUSPICIOUS requires dimensional consistency *and* a
positive trigger (currently: all-variables-dimensionless heuristic). A formula
that fails dimensional consistency is always INVALID, never SUSPICIOUS.

**Limitation:** The SUSPICIOUS heuristic is intentionally conservative and
broad. It will catch some valid formulas (e.g., DA-011) that happen to use
dimensionless quantities. This is a documented MVP scope limit, not a claim
that the formula is physically wrong.

---

## Batch Summary

| Microtask | Artifact | Verdict |
|---|---|---|
| DAV-001 | DA-016 added to challenge set | VALID (engine-confirmed) |
| DAV-002 | DA-119 added to challenge set | INVALID (engine-confirmed) |
| DAV-008 | DA-018 added to challenge set | VALID (engine-confirmed) |
| DAV-005 | DA-011 wording audit | REVIEW_NEEDED |
| DAV-010 | SUSPICIOUS/INVALID boundary note | REVIEW_NEEDED |

**Challenge set size:** 60 → 63 items

**Validator agreement after additions:** 60/63 (95.2%) — remains above the 90% threshold.

**Pre-existing disagreements not introduced by this batch:**

- DA-310: SUSPICIOUS expected, VALID computed — documented MVP scope limit (semantically empty dimensionless formula)
- DA-011: VALID expected, SUSPICIOUS computed — Snell's law triggers the dimensionless heuristic (see DAV-005 above)
- DA-406: KNOWN_LIMIT_FAIL expected, SUSPICIOUS computed — same Snell's law item at limit scope

All three disagreements pre-date this batch. No new disagreements introduced.

## Limitations and Claims Not Made

- This batch adds challenge items; it does not change the validator engine.
- Adding engine-side fixes for the DA-011 / DA-406 class of disagreements is
  outside TASK-0080 scope.
- No claim is promoted. CLAIM-0005 remains DRAFT.
- Agreement fraction (95.2%) is an observation on the current extended set, not
  a revised benchmark claim.
