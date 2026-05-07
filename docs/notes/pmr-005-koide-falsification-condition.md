# PMR-005 — Falsification Condition for the Charged-Lepton Koide Relation

**Microtask:** `PMR-005`
**Campaign:** `particle-mass-relations`
**Type:** `falsification-condition`
**Status:** REVIEW_NEEDED
**Date:** 2026-05-07

---

## Relation Under Evaluation

The original Koide relation for charged leptons:

```
Q(me, mμ, mτ) = (me + mμ + mτ) / (√me + √mμ + √mτ)² = 2/3
```

This is the exact formulation used in `EXP-0004/RUN-0004` (RESULT-0005),
which reproduced `Q = 0.6666644634145` against the benchmark target `2/3 = 0.6666...`,
with a gap smaller than the propagated one-sigma uncertainty.

---

## Falsification Conditions

The following observations would count against the charged-lepton Koide relation,
ordered from most to least decisive:

### F1 — PDG mass update moves Q outside the 1σ combined uncertainty band

If a future PDG revision shifts any of the three charged-lepton masses such that

```
|Q(me_new, mμ_new, mτ_new) − 2/3| > σ_propagated
```

the relation would be falsified at the stored input level. The current propagated
uncertainty is dominated by the tau mass (δmτ ≈ 0.16 MeV at 1σ); a shift larger
than ~0.2 MeV in the PDG tau mass central value would move Q by roughly one stored
sigma. This is operationally testable whenever PDG updates the charged-lepton masses.

### F2 — A credible alternative formula fits equally well with fewer degrees of freedom

If an unrelated combination of physical constants (not the Koide expression) were
shown to reproduce `Q ≈ 2/3` with the same or higher precision under the same inputs,
and with no more free parameters, that would demonstrate that closeness to `2/3` is
not specific to the Koide combination — weakening but not formally falsifying the
relation as a descriptive statement.

### F3 — The relation fails a blind prospective test on a fourth lepton

If a fourth charged lepton were discovered, the Koide formula could in principle be
used to predict its mass (given the other three). A failure beyond 1σ would falsify
the four-lepton extension. This condition is currently untestable (no fourth
charged lepton is known).

---

## What Does NOT Count as Falsification

- The neutrino sector result (`EXP-0007`, INVALID) is a falsification of the
  **direct neutrino extension**, not of the charged-lepton relation itself. The
  two statements are logically independent.
- Quark-sector cascade failure (`EXP-0008`, INVALID) is likewise not a
  falsification of the charged-lepton relation; it tests a different triplet and
  extension hypothesis.
- Low Q values in random triplets from the same mass table do not falsify the
  relation; they establish that Q ≈ 2/3 is unusual, which is a prerequisite for
  the relation to be interesting, not a test of it.

---

## Limitation

This falsification note covers the original three-lepton Koide relation only.
Extended Brannen-type variants (with a free phase δ) have additional free
parameters and require separate falsification analysis — a more permissive
criterion would apply.

---

## Claim Ceiling

This note does not assert that the relation is validated,
explained, or derivable from first principles. It only states what would
operationally count against it.
