# PMR-003: Quark Mass Scheme Ambiguity in Koide-Like Relations

**Microtask ID:** PMR-003  
**Queue:** particle-mass-relations  
**Run:** MICROTASK-RUN-0020  
**Verdict:** REVIEW_NEEDED  
**Review state:** UNREVIEWED  

---

## Affected Families

Up-type quarks: (u, c, t)  
Down-type quarks: (d, s, b)

Both families are subject to the ambiguity described below.

---

## The Scheme-Dependence Problem

Unlike charged leptons, quark masses are not physical observables in the same sense. They are parameters of the QCD Lagrangian and depend on the renormalization scheme and scale at which they are evaluated. The two most common choices are:

1. **Pole mass**: defined as the on-shell mass, scheme-independent at one loop. For heavy quarks, perturbatively accessible but affected by renormalon ambiguities of order Λ_QCD ≈ 200–300 MeV.
2. **MS-bar mass m̄(μ)**: defined in the modified minimal subtraction scheme at renormalization scale μ. Conventionally quoted at μ = m̄(m̄) (self-consistent scale). Free of leading renormalon but scale-dependent.

---

## PDG 2025 Approximate Values

| Quark | Pole mass (MeV) | MS-bar at self-consistent scale (MeV) | Ratio pole/MS-bar |
|---|---|---|---|
| charm (c) | ≈ 1670 | m̄_c(m̄_c) ≈ 1270 | ≈ 1.31× |
| bottom (b) | ≈ 4780 | m̄_b(m̄_b) ≈ 4180 | ≈ 1.14× |
| top (t) | ≈ 172500 | m̄_t(m̄_t) ≈ 162500 | ≈ 1.06× |

Source: S. Navas et al. (PDG), Phys. Rev. D 110, 030001 (2024) and 2025 update.

For up and down quarks, pole masses are not well-defined due to confinement. Only MS-bar values near 2 GeV are used.

---

## Nonlinear Propagation into Koide Q

The Koide Q formula is nonlinear in the masses:

```
Q = (Σ mᵢ) / (Σ √mᵢ)²
```

The square-root dependence means that multiplicative mass shifts propagate into Q in a nonlinear fashion. Specifically, replacing a pole mass m_pole by m_MS = m_pole / r (where r > 1 is the ratio above) shifts √m by 1/√r and m by 1/r, which do not cancel in Q.

Quantitatively: a 31% shift in the charm mass (r ≈ 1.31) combined with a 14% shift in the bottom mass and a 6% shift in the top mass produces a change in Q that can be of order 0.1 or larger (see PMR-011 for the up-type quark case, where Q_MS-bar ≈ 0.845 vs. the lepton Q ≈ 0.667).

A near-2/3 result for pole masses does not imply a near-2/3 result for MS-bar masses, and vice versa.

---

## Required Boundary for Quark Koide Analyses

Any quark Koide analysis submitted to this repository must:

1. **State the scheme explicitly**: pole mass or MS-bar (at what scale μ).
2. **State the PDG edition**: values change between editions; the 2025 values must be explicitly cited if used.
3. **Use a consistent scheme across all three quarks in a triplet**: mixing pole and MS-bar masses within one triplet is disallowed without explicit correction factors and propagated uncertainties.
4. **Propagate scheme uncertainty**: if the pole/MS-bar ratio is itself uncertain (it is, due to truncation of the perturbative series), this uncertainty must be propagated into Q.

Comparing Q values across mixed schemes is disallowed without explicit correction.

---

## Limitations

- This note covers the scheme ambiguity in principle; it does not compute Q for all possible scheme/scale combinations.
- The renormalon ambiguity in pole masses (order Λ_QCD) affects charm and bottom more than top.
- For up and down quarks, no pole mass exists in the usual perturbative sense due to QCD confinement.

---

## Verdict

REVIEW_NEEDED — scheme and scale dependence is a structural ambiguity that prevents direct comparison of quark Koide Q values with the charged-lepton result. Any quark Koide analysis requires explicit scheme labeling.
