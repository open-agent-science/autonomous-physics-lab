# g-2 Formula-Search Stress Test Design

**Status:** IMPLEMENTED UNDER TASK-0127  
**Planning Task:** `TASK-0089`  
**Implementation Task:** `TASK-0127`  
**Guardrail Hardening Task:** `TASK-0147`
**Experiment:** `EXP-0010`  
**Result:** `RESULT-0012`

---

## 1. Target Observable

The muon anomalous magnetic moment discrepancy (data-driven HVP baseline):

```
Δaμ = aμ(exp) − aμ(SM) = (249 ± 48) × 10⁻¹¹
```

Significance: ~5.1σ (BNL+FNAL 2023 combined). The BMW lattice-QCD result
(Borsanyi et al., Nature 593, 2021) reduces this to ~1.5σ; the formula search
targets the data-driven baseline as a high-risk stress-test case, not as a
public success story or anomaly-resolution claim.

Uncertainty is combined in quadrature: σ_combined = √(22² + 43²) × 10⁻¹¹ ≈ 48 × 10⁻¹¹.

---

## 2. Input Constants

All dimensionless, sourced from PDG 2024:

| Symbol | Value | Motivation |
|---|---|---|
| α | 7.2973525693 × 10⁻³ | QED coupling |
| α/π | 2.3219 × 10⁻³ | Standard QED loop factor |
| mμ/me | 206.7682830 | Lepton mass ratio (QED) |
| mμ/mτ | 0.059462 | Lepton mass ratio (EW) |
| mW/mZ | 0.88145 | Encodes weak mixing angle |
| GF·mμ² | 1.302 × 10⁻⁷ | Dimensionless Fermi scale |
| mμ/mπ⁰ | 0.7830 | Hadronic mass scale proxy |

Excluded constants and reasons:
- sin²θW: algebraically dependent on mW/mZ
- Higgs mass: enters only via loop corrections already in SM prediction
- Quark masses: no direct tree-level connection to aμ

---

## 3. Formula Families

### F1 — QED Power-law
`(α/π)^a × (mμ/me)^b`, a ∈ {1,2,3,4}, b ∈ {-3,...,3}

Physical motivation: QED radiative corrections scale as powers of α/π
with mass-ratio insertions. C=0 free parameters.

### F2 — Electroweak Scale Multiple
`c × GF·mμ²/(8π²√2)`, integer c ∈ {1,...,10}

Physical motivation: the known SM EW 1-loop contribution is ~154×10⁻¹¹.
Searching for a small integer multiple tests simple EW-scale BSM. C=0.

### F2b — EW Scale with QED/Mass Corrections
`EW_scale × (α/π)^a × ratio^b`, ratio ∈ {mμ/me, mμ/mτ, mW/mZ, mμ/mπ⁰}

Extension of F2 with additional QED or mass-ratio factors. C=0.

### F3 — Hadronic Light-by-Light Inspired
`c × (α/π)³ × (mμ/mπ⁰)²`

Physical motivation: HLbL leading-log contribution scales as (α/π)³ × (mμ/mπ)².
Tests rational candidates for c ∈ {1/5, 1/4, 1/3, 3/8, 1/2, 2/3, 1}.
One free scale parameter c → C=1. The optimal fit (c = Δaμ/base) is
reported as a **reference** hit only — it is fitted to the target, not predicted.

### F4 — Lepton Mass Cascade
`α^a × (mμ/me)^b × (mμ/mτ)^c`, a,b,c ∈ {-2,...,3}

Tests all combinations of three SM lepton mass scales. C=0, no physical
loop motivation, but comprehensive coverage of the lepton sector. 215 formulas.

### F5 — Mixed EW+QED
`(α/π)^a × (mW/mZ)^b × (GF·mμ²)^c`

Tests combinations involving both QED and EW scales. Pure-QED cases
(b=c=0) excluded to avoid overlap with F1. C=0.

---

## 4. Match Criterion

A formula value `f` is a **hit** if:

```
z = |f − Δaμ| / σ_combined < 1.0
```

A hit is **guardrail-screened** if these first-pass mechanical filters pass:

| Guardrail | Criterion |
|---|---|
| G1: Random baseline | Family hit-rate P < 1% (N=100,000 uniform samples) |
| G2: Complexity | C ≤ 1 free real-valued parameter |
| G3: Dimensional | All constants are dimensionless (guaranteed by design) |
| G4: SM cross-check | Formula must not be a fitted reference row or known SM contribution |

---

## 5. Random Baseline Protocol

For each family, 100,000 parameter combinations are drawn uniformly from
the same integer range as the systematic search. Hit-rate is computed as the
fraction with z < 1.0. A family passes the guardrail if hit-rate < 1%.

Seeds are fixed per family (1001–1006) for reproducibility.

This answers: "How likely is a random combination from this family to
accidentally fall within 1σ of the target?"

---

## 6. What Constitutes a Stress-Test Result

**Guardrail-screened:** passes the first-pass mechanical screen. This is an
empirical stress-test observation only — it does not claim credibility, a
physical mechanism, or anomaly resolution.

**Numerology only:** within 1σ but fails the random baseline (too many
accidental matches in the family space). No scientific significance.

**Null:** no formula from any family within 1σ. Indicates the data-driven
target is not simply expressible as a power-law combination of these constants.

Before any stronger interpretation of a screened hit, EXP-0010 needs:

- multiple-testing correction across families and candidate counts;
- bootstrap or perturbation stability under target and constant uncertainties;
- alternate-target comparison against lattice-HVP and updated-world-average
  baselines;
- cross-observable checks against electron g-2 and other lepton precision
  observables;
- pre-registered physical-motivation review for any proposed mechanism.

---

## 7. Actual Results

See `results/EXP-0010/RUN-0001/report.md` for the full output. Summary:

- 381 formulas evaluated across 6 families
- 1 guardrail-screened hit: **F4** `α³ × (mμ/me)⁻² × (mμ/mτ)⁻²` = 257 × 10⁻¹¹, z = 0.168σ, P = 0.49%
- F3 c=1/3 within 1σ (z=0.148σ) but fails P<1% guardrail (6.25%)
- Global verdict: **STRESS_TEST_HIT**

The F4 hit is an empirical coincidence. No loop diagram generating
`α³(mμ/me)⁻²(mμ/mτ)⁻²` is known in QED or EW theory.
