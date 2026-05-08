# Dimensional Analysis Microtask Batch 02

**Campaign:** dimensional-analysis-validator
**Date:** 2026-05-08
**Branch:** agent/oleg/claude/microtask-dav-003-004-008-challenge-entries
**Status:** REVIEW_NEEDED

---

## Completed Microtasks

### DAV-008 — Add one cross-domain challenge item outside mechanics

**Item added:** DA-019 — de Broglie wavelength

**Formula:** `lambda_dB = h / (m * v)`

**Domain:** quantum_mechanics

**SI dimension rationale:**
- LHS: `lambda_dB` — [m] = L
- RHS: `h / (m * v)` = [kg·m²·s⁻¹] / ([kg]·[m·s⁻¹]) = [kg·m²·s⁻¹] / [kg·m·s⁻¹] = [m] = L ✓

**Expected verdict:** VALID

**Limitation:** Dimensional check confirms unit balance only. The formula assumes
non-relativistic regime (v << c). For relativistic momenta the correct form is
λ = h / p where p = γmv, which also passes dimensionally but requires a
different physical context. The factor of 1 (numerator) hides no approximation
in the non-relativistic case, but the regime restriction is not detectable by
dimensional analysis alone.

**Novelty check:** No prior quantum_mechanics entry used de Broglie wavelength.
DA-116 in the same file covers `lambda = 1/p` (missing h, INVALID) — DA-019 is
the complementary correct form and fills a gap in non-mechanics VALID coverage.

---

### DAV-003 — Add one SUSPICIOUS challenge item

**Item added:** DA-311 — Undamped spring period (missing 2π)

**Formula:** `T = sqrt(m / k)`

**Domain:** mechanics

**SI dimension rationale:**
- LHS: `T` — [s] = T
- RHS: `sqrt(m / k)` = sqrt([kg] / [kg·s⁻²]) = sqrt([s²]) = [s] = T ✓

**Expected verdict:** SUSPICIOUS

**Why SUSPICIOUS, not VALID:** The formula is dimensionally balanced but
numerically wrong by a factor of 2π ≈ 6.28. The correct small-amplitude spring
period is T = 2π·sqrt(m/k). A purely dimensional engine accepts this formula
while the numerical prediction is incorrect. This is a prototype example of why
passing dimensional checks is necessary but not sufficient for physical
correctness.

**Missing physical assumption:** The dimensionless coefficient 2π arises from
integrating the equation of motion for a simple harmonic oscillator. It is not
detectable by unit analysis.

**Limitation:** The SUSPICIOUS classification assumes the reviewer knows the
correct coefficient. The formula would pass any dimensional-only check without
additional physical knowledge. Classification depends on domain expertise, not
on the unit balance alone.

**Novelty check:** DA-311 is the first explicit missing-coefficient SUSPICIOUS
example in the mechanics domain. Prior suspicious entries (DA-306, DA-307, DA-310)
focus on physically meaningless composite ratios, not on missing dimensionless
prefactors. This adds a distinct failure-mode variant to the challenge set.

---

### DAV-004 — Add one KNOWN_LIMIT_FAIL challenge item

**Item added:** DA-407 — Small-angle pendulum period (large-angle regime)

**Formula:** `T = 2 * pi * sqrt(L / g)`

**Domain:** mechanics

**SI dimension rationale:**
- LHS: `T` — [s] = T
- RHS: `2π·sqrt(L / g)` = sqrt([m] / [m·s⁻²]) = sqrt([s²]) = [s] = T ✓

**Expected verdict:** KNOWN_LIMIT_FAIL

**Violated limit:** The small-angle approximation sin(θ) ≈ θ is assumed. The
formula is exact for infinitesimally small amplitudes. Relative error exceeds 1%
above ~14° (~0.24 rad), exceeds 18% at 90°, and diverges as θ → π (the
separatrix). The exact period is:

```
T_exact = (2/π) · T₀ · K(sin²(θ/2))
```

where K is the complete elliptic integral of the first kind and T₀ = 2π·sqrt(L/g).

**Limitation:** The KNOWN_LIMIT_FAIL verdict is specific to the large-angle
regime. For θ << 1 rad this formula is physically correct. The dimensional check
does not detect the limit violation — it requires domain knowledge of the
elliptic integral correction. This entry is intentionally related to the
pendulum-formula-falsification campaign, which has studied this breakdown
in detail via EXP-0001.

**Novelty check:** DA-407 is the first pendulum entry in the KNOWN_LIMIT_FAIL
category. Existing DA-4XX entries cover relativistic kinematics (DA-401),
thermal expansion (DA-402, DA-403), ideal gas at extreme conditions (DA-404,
DA-405), and refractive index limits (DA-406). The pendulum entry adds a
classical-mechanics limit-failure example.

---

## Summary

| ID | DAV Task | Verdict | Domain | Failure mode |
|----|----------|---------|--------|--------------|
| DA-019 | DAV-008 | VALID | quantum_mechanics | — |
| DA-311 | DAV-003 | SUSPICIOUS | mechanics | missing dimensionless coefficient (2π) |
| DA-407 | DAV-004 | KNOWN_LIMIT_FAIL | mechanics | small-angle approximation breakdown |

**total_items updated:** 64 → 67

All three entries are draft additions pending maintainer review. No canonical
result artifacts were changed. No claims were promoted. All verdicts are scoped
to the challenge-set context and do not constitute repository-level conclusions.
