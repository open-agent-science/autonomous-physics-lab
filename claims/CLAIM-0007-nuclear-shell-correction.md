---
id: CLAIM-0007
title: Analytic Shell Correction Reduces Bethe-Weizsäcker RMS by 28.8%
domain: nuclear_physics
status: DRAFT
hypothesis_id: HYP-0009
evidence:
  experiments:
    - EXP-0009
  results:
    - RESULT-0011
scope: >
  AME2020-based curated subset of ~97 nuclides (A = 4–210) covering all
  magic neutron numbers N ∈ {2,8,20,28,50,82,126} and magic proton numbers
  Z ∈ {2,8,20,28,50,82}. Standard BW liquid-drop coefficients; no radioactive
  or neutron-rich nuclides.
---

# CLAIM-0007: Analytic Shell Correction Reduces Bethe-Weizsäcker RMS by 28.8%

## Statement

An analytic shell correction based on per-magic-number Gaussian bumps
(`multi_gauss_NZ_shared_sigma`) reduces the RMS residual of the
Bethe-Weizsäcker formula by **28.8%** on a held-out test set of AME2020-based
nuclear binding energies, exceeding the 20% threshold stated in HYP-0009.

The correction formula is:

```
δ_shell = Σᵢ aᵢ · exp(−(N − Nᵢ)² / σ²)  +  Σⱼ bⱼ · exp(−(Z − Zⱼ)² / σ²)
```

where Nᵢ ∈ {2, 8, 20, 28, 50, 82, 126} and Zⱼ ∈ {2, 8, 20, 28, 50, 82}.

## Key Metrics

| Metric | Value |
| --- | ---: |
| BW baseline RMS (test) | 8.978 MeV |
| Best correction RMS (test) | 6.393 MeV |
| RMS improvement (test) | 28.8% |
| Training set nuclides | 78 |
| Test set nuclides | 19 |
| Formula family | multi_gauss_NZ_shared_sigma |

## Auxiliary Finding

Simple Gaussian/Lorentzian/exponential corrections based on d_N = min|N−m|
or d_Z = min|Z−m| (distance to nearest magic number) give <1% improvement.
Different magic number closures require different amplitudes — no universal
correction shape exists based on distance alone.

## Evidence Status

`RESULT-0011` provides the primary evidence. This claim remains `DRAFT`
until the maintainer reviews the scope and wording.

## Scope

- AME2020 curated subset (~97 nuclides, A = 4–210). Not the full table.
- Standard BW coefficients used (not jointly refit).
- Several fitted amplitudes hit ±20 MeV bounds (especially for lightest nuclei
  N=2, Z=2). These likely absorb non-shell BW errors for A < 10.
- Heavier nuclides (A > 140) have ~0.5 MeV dataset uncertainty.
- No radioactive or neutron-rich nuclides tested.
