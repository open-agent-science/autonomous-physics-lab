# PMR-009 — Retrospective Fit vs Holdout-Capable Classification for Koide Relations

**Microtask:** `PMR-009`
**Campaign:** `particle-mass-relations`
**Type:** `methodology-classification`
**Status:** REVIEW_NEEDED
**Date:** 2026-05-07

---

## Classification Rule

A relation is **holdout-capable** if:
- It has at least N observed values and at most N−1 free parameters, such that
  one value can be withheld, the relation fit to the remaining N−1, and then
  compared to the withheld value on data that was not used in the fit.
- The withheld value was measured independently before or after the formula
  was proposed, with no knowledge of the formula used in the measurement.

A relation is **retrospective fit only** if:
- All observed values were used to motivate or tune the formula, with no
  remaining independent holdout.
- Or: the parameter space is flexible enough to accommodate any realization
  of the observations (effectively C = N free parameters for N observations).

---

## Koide Charged-Lepton Relation

**Classification: Holdout-Capable (historical, one-shot, charged-lepton scope)**

**Limiting assumption (read first):** The tau mass was measured (imprecisely,
~1784 MeV) before Koide published in 1981. The tau was not unknown — only
its precise value was uncertain. The "historical holdout" claim therefore
rests on the imprecision of the 1981 tau measurement, not on complete absence
of tau mass data. This cannot be verified from the stored repository data
alone; it depends on accepting the historical publication record. The
classification as holdout-capable should be read with this in mind.

Reasoning:
- The formula Q = 2/3 has zero free parameters. It can be applied to any
  two known masses and used to predict the third.
- Koide (1981) published the relation when only imprecise tau mass data were
  available; modern precision (δmτ ≈ 0.16 MeV) provides the effective
  confirmation. The tau mass was used to *check* the formula, not fit it.
- `EXP-0005/RUN-0005` operationalizes this as: fit = none (Q = 2/3 is
  fixed), prediction = tau mass from electron and muon, comparison = PDG
  measured tau mass.
- The electron and muon were the only two leptons with precisely known masses
  at that time, so the tau holdout was the *only* possible holdout in the
  family. One-of-one holdouts carry limited statistical weight.

---

## Koide Neutrino Extension

**Classification: Retrospective Fit Only (not holdout-capable in current form)**

Reasoning:
- Neutrino mass eigenvalues m₁, m₂, m₃ are not individually measured.
  Oscillation data constrains Δm₂₁² and |Δm₃₁²| but not the absolute mass
  scale. The lightest neutrino mass is unconstrained from below (could be 0).
- `EXP-0007` tests whether any Q_max (maximized over the neutrino mass
  ordering and absolute mass scale) reaches 2/3. It does not — normal
  hierarchy gives Q_max = 0.584 (gap: 70.7σ).
- Because the absolute mass scale is a free parameter, the neutrino extension
  cannot perform a genuine holdout: there is no third independently measured
  value to withhold while fitting the other two.

---

## Koide Quark Cascade (Brannen Phase Extension)

**Classification: Retrospective Fit Only (by construction)**

Reasoning:
- `EXP-0008` tests phase-modified Koide formulas Q(δ) over quark triplets.
  The phase δ is a free parameter scanned over [0, 2π].
- With one free parameter per triplet, the formula can be tuned to any
  Q value; the test checks whether the best δ brings Q close to 2/3 with
  quark masses. It found INVALID (all standard triplets fail).
- Even if a triplet had matched, the result would be retrospective: all
  quark masses are known and there is no unused holdout value within the
  triplet after δ is set.

---

## Summary Table

| Relation | Classification | Limiting Assumption |
|---|---|---|
| Charged-lepton Koide | Holdout-capable (historical, 1-of-1) | Historical timeline of tau measurement; one holdout only |
| Neutrino extension | Retrospective fit only | Absolute neutrino mass scale unmeasured |
| Quark cascade (Brannen) | Retrospective fit only | Free phase δ absorbs fitting freedom |

---

## Claim Ceiling

Classification as holdout-capable does not constitute proof of physical
truth. One holdout, in one family, with one formula is consistent evidence,
not confirmation. This note does not upgrade any verdict above VALID_IN_RANGE.
