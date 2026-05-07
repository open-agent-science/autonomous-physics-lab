# PMR-006 — Limitation Note for the Tau Holdout Interpretation

**Microtask:** `PMR-006`
**Campaign:** `particle-mass-relations`
**Type:** `limitation-note`
**Status:** REVIEW_NEEDED
**Date:** 2026-05-07

---

## Reference Result

`EXP-0005/RUN-0005` (RESULT-0006) — Historical Tau Holdout Prediction  
Verdict: `VALID_IN_RANGE`  
Key metrics: predicted tau mass differs from measured by 0.039 MeV (z = 0.43σ)

---

## What the Tau Holdout Does Support

Under the stored PDG-backed charged-lepton inputs and the exact Koide formula:

- The tau mass predicted from electron and muon masses lands within 0.43σ of
  the measured tau mass.
- This is a *historical* holdout in the narrow sense: the tau mass was measured
  after Koide (1981) published the formula, so the formula was not fit to the
  tau mass directly.
- The result confirms that the stored benchmark computation reproduces the
  familiar numerical closeness reported in the original literature.

## What the Tau Holdout Does Not Support

1. **Origin of charged-lepton masses.** Closeness of a predicted value to a
   measured value does not explain why the masses take the values they do. The
   Koide formula is a constraint, not a mechanism.

2. **Extension to other lepton families.** The neutrino holdout is not possible
   in the same sense: neutrino mass eigenvalues are not known precisely enough
   to perform an analogous 2-of-3 fit, and the neutrino consistency test
   (`EXP-0007`) found a 70.7σ gap under the normal hierarchy.

3. **Extension to the quark sector.** The quark Koide cascade (`EXP-0008`)
   returned INVALID for all standard triplets. The tau holdout result does not
   transfer to quark physics.

4. **Cross-family generalization.** The holdout applies exclusively to the
   three charged leptons in the stored PDG 2024 dataset. Claiming that "the
   Koide formula holds for particle masses in general" is not supported by a
   three-point single-family holdout.

5. **Statistical significance beyond coincidence.** The formula has no free
   parameters after fixing the target Q = 2/3, but it was applied to precisely
   the family where the closeness to 2/3 was originally noticed. The number of
   particle families tested at the time of Koide's publication was small (one),
   so the effective trials count is limited, and the post-diction character of
   the tau prediction must be acknowledged.

---

## Conservative Wording Guidance

Acceptable framing:
> "Under stored PDG 2024 charged-lepton inputs and the Koide formula Q = 2/3,
> the historical tau holdout lands 0.43σ from the measured tau mass."

Framing to avoid:
> "The Koide formula correctly predicts the tau mass" — implies causal or
> explanatory status beyond the stored benchmark computation.
> "The holdout validates the Koide hypothesis" — overstates the scope; this is
> a single-family, single-holdout benchmark, not a multi-domain validation.
> "The tau result shows particle masses follow a deeper structure" — no
> cross-family evidence supports this at VALID tier.

---

## Claim Ceiling

This note confirms the historical tau holdout is narrow,
retrospective in character, and does not support extrapolation beyond the
charged-lepton sector.
