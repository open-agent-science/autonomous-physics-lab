# PMR-011: Up-Type Quark Koide Q Attempt

**Microtask ID:** PMR-011  
**Queue:** particle-mass-relations  
**Run:** MICROTASK-RUN-0023  
**Verdict:** INCONCLUSIVE  
**Review state:** UNREVIEWED  

---

## Input Masses

PDG 2025 approximate values, up-type quark triplet (u, c, t):

| Quark | Scheme | Mass (MeV) |
|---|---|---|
| up (u) | MS-bar at 2 GeV | 2.16 |
| charm (c) | MS-bar at m_c | 1270.0 |
| top (t) | MS-bar at m_t | 162500.0 |

For the pole-approximation comparison:

| Quark | Scheme | Mass (MeV) |
|---|---|---|
| up (u) | MS-bar at 2 GeV | 2.16 (pole undefined due to confinement) |
| charm (c) | pole | 1670.0 |
| top (t) | pole | 172500.0 |

Source: S. Navas et al. (PDG), Phys. Rev. D 110, 030001 (2024) and 2025 update.

---

## Computation

```
Q (MS-bar scheme):
  numerator   = 2.16 + 1270.0 + 162500.0 = 163772.16 MeV
  denominator = (√2.16 + √1270.0 + √162500.0)²
  Q_msbar     = 0.845087

Q (pole-approximation, mixed scheme):
  numerator   = 2.16 + 1670.0 + 172500.0 = 174172.16 MeV
  denominator = (√2.16 + √1670.0 + √172500.0)²
  Q_pole      = 0.831535

2/3           = 0.666667

|Q_msbar − 2/3| = 0.1784
|Q_pole  − 2/3| = 0.1649
```

---

## Interpretation

Both Q values deviate significantly from 2/3:

- MS-bar: Q ≈ 0.845, deviation ≈ 0.178 (about 27% above 2/3)
- Pole approximation: Q ≈ 0.832, deviation ≈ 0.165 (about 25% above 2/3)

By contrast, the charged lepton pole mass Q = 0.6666644634, deviating from 2/3 by only 2.2×10⁻⁶.

The up-type quark Q deviates from 2/3 by roughly five orders of magnitude more than the charged lepton Q. This supports falsification of a universal Koide law — one that applies to all fermion mass triplets with Q = 2/3.

---

## Failure Mode: Scheme Mixing

The pole-approximation row above mixes schemes: the up quark pole mass is ill-defined (the up quark is confined), while the charm and top pole masses are used. This mixing is methodologically unreliable. The mixed-scheme Q = 0.831535 is therefore not a valid comparison point.

The MS-bar row is self-consistent in scheme (all three quarks at their respective MS-bar self-consistent scales), but note that these scales are different for each quark (2 GeV for up, m_c ≈ 1.27 GeV for charm, m_t ≈ 162.5 GeV for top). Strictly, a scheme-consistent analysis would evaluate all three at the same scale, requiring perturbative running, which is not performed here.

---

## Limitations

- Quark masses are scheme- and scale-dependent; no unambiguous quark mass exists in the same sense as charged-lepton pole masses.
- The up quark pole mass is not defined due to QCD confinement.
- The large value of Q for up-type quarks may partly reflect the enormous mass hierarchy (m_t / m_u ≈ 7.5×10⁷), not the same physics as the lepton sector.
- MS-bar scales differ between quarks; a fully consistent comparison requires running to a common scale.

---

## Verdict

INCONCLUSIVE — the up-type quark Q deviates significantly from 2/3 (|Q_msbar − 2/3| ≈ 0.178), supporting falsification of a universal Koide Q = 2/3 law across all fermion triplets. However, the comparison is complicated by scheme ambiguity and the absence of a well-defined up-quark pole mass. The falsification signal is present but cannot be declared definitive until a consistent scheme analysis is performed.
