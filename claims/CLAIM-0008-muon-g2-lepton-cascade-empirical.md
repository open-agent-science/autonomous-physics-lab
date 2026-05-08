---
id: CLAIM-0008
title: Muon g-2 benchmark finds one guardrail-passing lepton-cascade hit within 1σ
domain: particle_physics
status: DRAFT
hypothesis_id: HYP-0010
evidence:
  experiments:
    - EXP-0010
  results:
    - RESULT-0012
scope: >
  Power-law formula families F1–F5 tested against data-driven HVP baseline
  Δaμ = (249 ± 48) × 10⁻¹¹ (BNL+FNAL 2023 combined). Credibility gated on
  C≤1 free parameter and family hit-rate P<1% random baseline guardrail.
---

# CLAIM-0008: Muon g-2 benchmark finds one guardrail-passing lepton-cascade hit within 1σ

## Statement

A single predicted formula from the lepton-cascade family (F4) lands within 1σ
of the data-driven muon g-2 target and passes all current numerology guardrails:

```
α³ × (mμ/me)⁻² × (mμ/mτ)⁻² ≈ 257 × 10⁻¹¹
```

z = 0.168σ from Δaμ = 249 × 10⁻¹¹, with C=0 free parameters and
random-baseline hit-rate 0.49% (< 1% threshold).

This is an **empirical benchmark hit only**. No physical mechanism,
anomaly resolution, or theoretical explanation is proposed or claimed.

## Evidence Status

`RESULT-0012` provides the first formula-search baseline run. This claim
remains `DRAFT` until maintainer review confirms scope, wording, and that
the guardrail thresholds are appropriate for the family size.

## Scope

- Six formula families (F1–F5 plus F2b) were searched, covering 381 total
  formulas.
- Constants used: α, mμ/me, mμ/mτ, mW/mZ, GF·mμ², mμ/mπ⁰ (PDG 2024).
- Target: data-driven HVP baseline only. The BMW lattice-QCD value reduces
  the discrepancy to ~1.5σ; this claim does not apply to that baseline.
- The closest overall predicted hit is F3 with c=1/3 (z=0.148σ), but it fails
  the P<1% random-baseline guardrail and is therefore not the primary hit.

## Caution

A formula coincidence within a six-family systematic search is not evidence
for a physical explanation. The lepton cascade combination has no known SM
loop-diagram motivation. The claim ceiling is "one guardrail-passing
empirical hit" — not "explains the anomaly."
