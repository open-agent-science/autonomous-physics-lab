# Muon g-2 Anomaly Formula Search — Design Document

**Task:** TASK-0089  
**Type:** Planning / design only — no search engine implemented here  
**Date:** 2026-05-07  
**Status:** DRAFT

---

## 1. Physics Context

The anomalous magnetic moment of the muon aμ = (g − 2)/2 is one of the most
precisely measured quantities in physics. The discrepancy between experiment
and Standard Model prediction is:

```
aμ(exp)  = 116 592 059(22) × 10⁻¹¹   [Fermilab Run-2&3 + BNL combined, PRL 131 (2023)]
aμ(SM)   = 116 591 810(43) × 10⁻¹¹   [2020 White Paper consensus, Phys. Rept. 887 (2020)]
──────────────────────────────────────────────────────────────────────
Δaμ      =         249(48) × 10⁻¹¹   [~5.1σ combined significance]
```

This discrepancy has persisted across multiple experimental generations (BNL,
Fermilab) and is currently the strongest hint of beyond-Standard-Model physics
in precision observables. The SM uncertainty is dominated by hadronic vacuum
polarization (HVP), where competing lattice-QCD and data-driven results disagree.

Note: σ_combined = √(22² + 43²) ≈ 48 × 10⁻¹¹ (experimental + theory added in
quadrature). The earlier 2021 Run-1 result reported ~4.2σ (Δaμ ≈ 251(59) × 10⁻¹¹);
the 2023 final combination gives ~5.1σ (249/48.3). Both numbers appear in the
literature — this document uses the 2023 final values throughout.

**Important caveat:** The BMW lattice-QCD 2020 result for HVP predicts a smaller
discrepancy (~1.5σ). The 4.2σ significance depends on which HVP estimate is used.
A formula search must treat this as a limitation.

---

## 2. Target Quantity

The search target is:

```
Δaμ = (249 ± 48) × 10⁻¹¹  (1σ experimental + theory combined uncertainty)
```

In natural units this corresponds to:

| Expression | Value |
| --- | ---: |
| Δaμ | 2.49 × 10⁻⁹ |
| Δaμ / (α/2π) | 2.144 × 10⁻⁶ |
| Δaμ / (α/2π)² | 1.846 × 10⁻³ |
| Δaμ / (α/π) | 1.072 × 10⁻⁶ |
| Δaμ / [GF·mμ²/(8π²√2)] | 2.135 (≈ 2) |

Note: the EW 1-loop correction to aμ is ~154 × 10⁻¹¹, which is a known SM
contribution. Δaμ here is already the residual after all SM corrections.

---

## 3. Input Constants

The formula search will use only dimensionless combinations of known SM constants.
All values from PDG 2024.

| Symbol | Value | Physical meaning |
| --- | ---: | --- |
| α | 7.2973525693 × 10⁻³ | Fine-structure constant |
| mμ/me | 206.7682830 | Muon-to-electron mass ratio |
| mμ/mτ | 0.059462 | Muon-to-tau mass ratio |
| mW/mZ | 0.88145 | Weak mixing ratio |
| GF·mμ² | 1.302 × 10⁻⁷ | Dimensionless Fermi scale at muon mass |
| mμ/mπ⁰ | 0.7830 | Muon-to-neutral-pion mass ratio (hadronic scale proxy) |

**Excluded constants (rationale):**
- mH (Higgs mass): enters at two-loop EW, suppressed by (mμ/mH)²
- mt, mb, mc: quark masses enter only through hadronic loops (already in SM prediction)
- sin²θW: algebraically related to mW/mZ; including both would be redundant

---

## 4. Formula Families

### Family 1 — QED power-law corrections
Motivated by the structure of perturbative QED contributions (Schwinger term,
Petermann-Sommerfield, etc.):

```
f₁(a, b) = (α/π)^a × (mμ/me)^b
```

Integer or half-integer a ∈ {1,2,3,4}, rational b ∈ {−3,…,3}. The Schwinger
term α/2π = 1.16×10⁻³ accounts for ~1.0×10⁻³ of the total aμ; the anomaly
Δaμ is ~10⁻⁶ relative to the Schwinger term, consistent with a ≥ 2 or a
small (α/π)² × mass-ratio formula.

### Family 2 — Electroweak scale combinations
The leading EW contribution to aμ scales as GF·mμ²/(8π²√2) ≈ 1.17 × 10⁻⁹.
Δaμ ≈ 2.1 × (GF·mμ²/(8π²√2)), suggesting:

```
f₂(c) = c × GF·mμ²/(8π²√2)
```

with c ≈ 2. Also test:

```
f₂b = (GF·mμ²) × (α/π)^n × (mass ratio)^m
```

### Family 3 — Hadronic scale with pion mass
Hadronic light-by-light (HLbL) corrections scale as (α/π)³ × (mμ/mπ)²
(leading logarithm estimate). Check:

```
f₃(c) = c × (α/π)³ × (mμ/mπ⁰)²
```

Numerically: (α/π)³ × (mμ/mπ)² ≈ 1.26 × 10⁻⁸ × 0.613 ≈ 7.68 × 10⁻⁹.
So Δaμ / f₃(1) ≈ 0.324 ≈ 1/3. Test c = 1/3 explicitly.

### Family 4 — Lepton mass ratio cascades
Inspired by Koide-like mass-ratio formulas, test:

```
f₄ = α^a × (mμ/me)^b × (mμ/mτ)^c
```

for small integer/rational exponents. These are purely empirical with no
physical motivation beyond the charged-lepton mass hierarchy.

### Family 5 — Mixed EW + QED
```
f₅ = (α/π)^a × (mW/mZ)^b × (GF·mμ²)^c
```

The mW/mZ ratio encodes the weak mixing angle; sin²θW = 1 − (mW/mZ)².
BSM contributions to aμ involving Z/W loops could produce such combinations.

### Family 6 — Polynomial combinations (up to 3 terms)
```
f₆ = c₁×X + c₂×Y + c₃×Z
```

where X, Y, Z are monomials from the constant set above. Fit c₁, c₂, c₃
by least squares. Requires complexity penalty to avoid trivial fits.

---

## 5. Matching Criterion

A formula F matches if:

```
|F − Δaμ| ≤ σ_combined = 48 × 10⁻¹¹
```

and the formula is **also** required to pass the numerology guardrail (Section 6).

The match quality score is defined as:

```
z = |F − Δaμ| / σ_combined
```

A formula is VALID if z < 1.0 (within 1σ). A formula is INTERESTING if z < 0.5.

**Important**: The match criterion alone is weak. The relative acceptance window
is ±σ/Δaμ = ±19.3%, meaning many accidental matches are possible. The
numerology guardrail is mandatory.

---

## 6. Numerology Guardrail

### 6.1 Baseline hit rate estimate

With 6 input constants and integer exponents in [−3, 3]:

- Total power-law combinations: 7⁶ = 117,649
- Log window for 2σ match: log₁₀((Δaμ + 2σ)/(Δaμ − 2σ)) ≈ 0.35 decades
- Assuming formula outputs span ~20 log-decades:
  **Expected random hits: ~2% of all combinations**

This is **not negligible**. A formula family F1 with 6 free exponents would
produce ~2,000 accidental matches out of 117,649 combinations.

### 6.2 Guardrail design

**Guardrail G1 — Random expression baseline:**
Generate N = 100,000 random dimensionless expressions from the same constant
set, drawn uniformly from the same parameter space (exponents, coefficients)
as the formula family under test. Count how many satisfy the match criterion.
Require:

```
P(random match) < 1%
```

for a formula to be flagged as potentially credible. Any formula from a family
where P(random) > 5% is automatically classified as numerology.

**Guardrail G2 — Kolmogorov complexity penalty:**
Formulas with more free parameters are penalized. The complexity score is:

```
C(F) = number of free real-valued parameters in F
```

A formula with C > 1 and only 1σ match is not credible. A formula with C = 0
(pure prediction from integer/rational exponents of known constants) that matches
within 1σ is maximally credible. C = 1 (one free overall coefficient) is
acceptable only if P(random match) < 1% and physical motivation exists.

**Guardrail G3 — Physical dimension check:**
All candidate formulas must be dimensionless. Formulas involving mμ/me (etc.)
must be verified to be true dimensionless ratios, not mass quantities in
disguised units.

**Guardrail G4 — SM cross-check:**
A formula that simply reconstructs a known SM contribution (e.g., the EW
1-loop correction ~154×10⁻¹¹, or a HVP estimate) does not count as a match
— it must reproduce Δaμ specifically, not the full aμ(SM) correction.

### 6.3 Hit-rate table (to be filled during implementation)

| Formula family | Parameter space | Random hit rate | Credible threshold |
| --- | --- | --- | --- |
| F1: (α/π)^a × (mμ/me)^b | a ∈ Z[1,4], b ∈ Z[−3,3] | TBD | < 1% |
| F2: GF·mμ² × (α/π)^a × ratio^b | a,b ∈ Z[0,3] | TBD | < 1% |
| F3: c × (α/π)³ × (mμ/mπ⁰)² | c free (1 param) | TBD | < 1% |
| F4: α^a × (mμ/me)^b × (mμ/mτ)^c | a,b,c ∈ Z[−2,3] | TBD | < 1% |
| F5: mixed EW+QED | see above | TBD | < 1% |
| F6: 3-term polynomial | c₁,c₂,c₃ free | likely > 10% | NOT CREDIBLE alone |

---

## 7. What Constitutes a Credible Result

A formula match is **credible** if ALL of the following hold:

1. **Accuracy**: z < 1.0 (within 1σ of Δaμ)
2. **Low complexity**: C(F) ≤ 1 free parameter (or C = 0 for a pure prediction)
3. **Rare under randomness**: P(random match) < 1% within the formula family
4. **Physical plausibility**: the constants in the formula appear in relevant
   SM loop diagrams (EW, hadronic, QED), not arbitrary combinations
5. **HVP robustness**: the formula should be checked against both the
   data-driven HVP (4.2σ discrepancy) and the BMW lattice-QCD HVP (~1.5σ)
   to understand how sensitive the match is to the SM uncertainty

A result meeting criteria 1–3 is **VALID (empirical)** in APL terms.
Meeting all 5 criteria would warrant a claim promotion to a higher tier.

A result meeting only criterion 1 is **numerology** and is classified INVALID.

---

## 8. What Constitutes a Null Result

A null result is scientifically valid and means:

- No formula from the tested families matches within 1σ, OR
- Every matching formula is common under the random baseline (P > 5%)

**Null result interpretation**: The g-2 anomaly Δaμ is not simply expressible
as a power-law combination of {α, mμ/me, mμ/mτ, mW/mZ, GF·mμ², mμ/mπ} with
integer exponents and ≤ 1 free coefficient. This would suggest either:
(a) the anomaly requires more exotic BSM physics with new mass scales, or
(b) the anomaly is a SM calculation artifact (as suggested by BMW lattice-QCD),
or (c) the formula space searched was too restricted.

---

## 9. Implementation Plan (follow-on task)

This design is planning-only. The implementation task would include:

1. **Dataset**: `knowledge/particle_physics/muon_g2.yaml` — store Δaμ, σ, and
   all input constants with PDG 2024 references.
2. **Engine**: `physics_lab/engines/g2_formula_search.py` — formula evaluator,
   random baseline generator, hit-rate counter.
3. **Workflow**: `physics_lab/workflows/g2_formula.py` — APL workflow pattern.
4. **Experiment**: HYP-0010, EXP-0010, result artifacts.
5. **Run config**: `examples/g2_formula_search.yaml`.

Estimated complexity: medium. The search space is small (≤ 117,649 combinations
per family) and each evaluation is O(1). Runtime: < 1 minute.

---

## 10. Limitations of This Design

- The SM prediction uncertainty is dominated by HVP; the 4.2σ discrepancy is
  contested (BMW lattice-QCD gives ~1.5σ). The search target Δaμ may narrow
  significantly with future lattice results.
- Formula families are heuristically motivated, not exhaustive. A "correct"
  BSM formula may lie outside all families listed here.
- Integer/rational exponent constraints exclude smooth BSM contributions that
  involve non-trivial loop integrals.
- The random baseline assumes uniform log distribution of formula outputs;
  actual formula outputs are not log-uniform (power-laws cluster near integer
  powers of α). A more careful baseline would weight the distribution.
- This design covers only the anomaly Δaμ, not the absolute value aμ(exp).
  A formula for the anomaly specifically is harder to justify than a formula
  for a total observable.

---

## 11. References

- Muong-2 Collaboration, Phys. Rev. Lett. 131, 161802 (2023) — Fermilab final result
- Aoyama et al., Phys. Rept. 887, 1 (2020) — White Paper SM prediction
- Borsanyi et al. (BMW), Nature 593, 51 (2021) — Lattice HVP result
- Kinoshita & Nio, Phys. Rev. D 73, 013003 (2006) — QED contributions structure
- PDG 2024 — input constant values
