# Nuclear Prediction Variants: Isotope-Chain Extrapolation Controls

**Task:** TASK-0232
**Entries:** PRED-0029, PRED-0030
**Status:** REGISTERED (prospective; not a claim or result)

## Summary

This review note documents the model choice, deterministic calculation path,
target batch, and limitations for the two isotope-chain extrapolation control
variants registered in TASK-0232.

Isotope-chain extrapolation is methodologically distinct from random-nuclide
target selection. By stepping along a single element's isotope chain, these
entries expose how the smooth semi-empirical formula generalizes as the
neutron-proton imbalance grows within a fixed-Z family. This is a recognized
generalization stress test because:

1. Shell effects, pairing regularity, and deformation can produce systematic
   deviations along a chain that the smooth SEMF cannot capture.
2. The chain-wise target design makes the extrapolation direction explicit and
   reviewable: targets are ordered by increasing neutron number, not by
   residual magnitude.

## Model Variants

### PRED-0029: Base fitted model — Tin chain (Z=50)

**Model id:** `RESULT-0015::model_fitted_semi_empirical`

Base coefficients (from `results/EXP-0012/RUN-0001/result.yaml`):

| Term | Coefficient |
|------|-------------|
| volume | 15.51423612106804 MeV |
| surface | 17.29318120951770 MeV |
| coulomb | 0.68781560915689 MeV |
| asymmetry | 23.84655788394849 MeV |
| pairing | 15.99084511339891 MeV |

No coefficient is modified. The base model is applied directly to four
even-even Sn isotopes beyond the NMD-0002 training anchor Sn-120.

**Chain selection rule:** Start from Sn-120 (the last Sn entry in NMD-0002,
Z=50, N=70), then step by +2 neutrons four times: Sn-122, Sn-124, Sn-126,
Sn-128. All targets have Z=50 (magic proton number), so the proton shell
structure is fixed while the neutron number walks away from the training point.

**Why this is a generalization stress test:** The SEMF was fitted on Sn-120 as
its only Sn anchor. Extrapolation to Sn-128 (N=78, four neutrons below the
N=82 shell closure) tests whether the smooth formula tracks the known Sn chain.
The model has no sub-shell or shell-quenching correction, so any shell-driven
staggering near N=82 would appear as a systematic residual at reveal time.

### PRED-0030: Asymmetry-enhanced (+15%) — Zinc chain (Z=30)

**Model id:** `RESULT-0015::model_fitted_semi_empirical::asymmetry_plus_fifteen_percent`

Perturbed asymmetry coefficient:
`aA_030 = 23.846557883948485 × 1.15 = 27.423541566540756 MeV`

All other coefficients are identical to the base model.

**Chain selection rule:** Zinc (Z=30) is entirely absent from NMD-0002. Targets
are four consecutive even-even Zn isotopes with increasing neutron excess:
Zn-68, Zn-70, Zn-72, Zn-74 (N from 38 to 44). The chain has no training
anchor; every prediction is a pure extrapolation.

**Why this is a generalization stress test:** Without any Zn training anchor,
PRED-0030 is a harder extrapolation than PRED-0029. The +15% asymmetry
perturbation is layered on top to expose how the asymmetry term's magnitude
interacts with growing (N-Z)^2/A along the chain. The perturbation effect
grows from +3.4 MeV at Zn-68 to +9.5 MeV at Zn-74, making Zn-74 the most
asymmetry-sensitive target in this batch. Comparing PRED-0029 and PRED-0030
at reveal time will show whether the asymmetry divergence or the chain
extrapolation error dominates the residual.

## Deterministic Calculation

All predicted values are computed by the following closed-form path:

```
B(Z, N) = aV·A − aS·A^(2/3) − aC·Z·(Z−1)·A^(−1/3) − aA·(N−Z)²/A + δ

δ = +aP/√A   for even-even (Z even, N even)
δ = −aP/√A   for odd-odd  (Z odd,  N odd)
δ = 0         for odd-A    (exactly one of Z, N is odd)

atomic_mass_u = Z·m_H + N·m_n − B / u_to_MeV
mass_excess_mev = (atomic_mass_u − A) · u_to_MeV
```

Physical constants (from `physics_lab/engines/nuclear_masses.py`):
- `m_H = 1.00782503223 u`
- `m_n = 1.00866491595 u`
- `1 u = 931.49410242 MeV`

Engine helpers used:
- `physics_lab.engines.nuclear_mass_baselines.semi_empirical_atomic_mass_u`
- `physics_lab.engines.nuclear_masses.mass_excess_keV_from_atomic_mass_u`

## Target Batches

All eight targets are absent from both NMD-0002 and the post-AME2020 holdout
dataset at registration time.

### PRED-0029: Sn chain (base fitted model)

| Nuclide | Z | N | A | N−Z | Pairing class | Predicted (MeV) |
|---------|---|---|---|-----|---------------|-----------------|
| Sn-122 | 50 | 72 | 122 | 22 | even-even | −88.842564 |
| Sn-124 | 50 | 74 | 124 | 24 | even-even | −84.750178 |
| Sn-126 | 50 | 76 | 126 | 26 | even-even | −79.643018 |
| Sn-128 | 50 | 78 | 128 | 28 | even-even | −73.568894 |

Key observations (pre-reveal):
- Mass excess increases (less binding) with each +2 neutron step; the asymmetry
  penalty `aA*(N-Z)^2/A` grows as N-Z widens from 22 to 28.
- The pairing contribution (+aP/√A) decreases slowly from 1.448 to 1.413 MeV
  across the chain (all even-even), providing a minor and nearly constant offset.
- No shell-closure correction is present; the approaching N=82 shell at Sn-128
  is expected to produce a residual at reveal time.

### PRED-0030: Zn chain (asymmetry +15%)

| Nuclide | Z | N | A | N−Z | Base model (MeV) | Asym+15% (MeV) | Δ (MeV) |
|---------|---|---|---|-----|-----------------|----------------|---------|
| Zn-68 | 30 | 38 | 68 | 8 | −74.374277 | −71.007705 | +3.367 |
| Zn-70 | 30 | 40 | 70 | 10 | −73.397550 | −68.287573 | +5.110 |
| Zn-72 | 30 | 42 | 72 | 12 | −70.418668 | −63.264701 | +7.154 |
| Zn-74 | 30 | 44 | 74 | 14 | −65.601422 | −56.127249 | +9.474 |

Key observations (pre-reveal):
- The asymmetry perturbation Δ grows with `(N-Z)^2/A`, confirming correct
  formula implementation: `ΔaA*(N-Z)^2/A = 3.576983*(N-Z)^2/A`.
- All targets are even-even; the pairing contribution is identical between
  the base model and PRED-0030 (only the asymmetry term is perturbed).
- Zn-74 has the largest (N-Z) = 14 in this batch, making it maximally sensitive.

## Limitations

- Prospective registry entries only; no claim or result promotion.
- No sandbox candidate is being promoted by either entry.
- The target batches are small (four nuclides each); broader coverage requires
  a separate task.
- PRED-0029 has a single Sn training anchor (Sn-120) and no shell correction;
  the N=82 shell closure effect at Sn-128 is unmodeled.
- PRED-0030 has no Zn training anchor; the entire chain is extrapolated and the
  +15% asymmetry perturbation is a known empirical overfit that is expected to
  worsen predictions for well-measured nuclei.
- True prospective prediction status requires later maintainer source-state
  review to confirm the target nuclides were not measured in any committed
  dataset at registration time.

## Verdict

Both entries are correctly structured prospective isotope-chain extrapolation
control variants. They are registered for future reveal comparison only.
No claim, result, or knowledge promotion is implied.
