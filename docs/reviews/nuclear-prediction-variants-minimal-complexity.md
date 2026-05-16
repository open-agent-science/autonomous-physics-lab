# Nuclear Prediction Variants: Minimal-Complexity Form Controls

**Task:** TASK-0236
**Entries:** PRED-0037, PRED-0038
**Status:** REGISTERED (prospective; not a claim or result)

## Summary

This review note documents the model choice, deterministic calculation path,
target batch, and limitations for the two minimal-complexity form-variant
controls registered in TASK-0236.

The agent-designed lane (`TASK-0236`) of
`docs/notes/nuclear-prediction-variant-expansion-wave.md` invites bounded
low-complexity variants. Both variants in this PR change exactly one structural
form of the canonical SEMF binding-energy formula. No new free parameter is
introduced; all RESULT-0015 fitted coefficients remain frozen.

## Model Variants

Both entries derive from the same frozen baseline:
`RESULT-0015::model_fitted_semi_empirical`

Baseline coefficients (from `results/EXP-0012/RUN-0001/result.yaml`):

| Term | Coefficient |
|------|-------------|
| volume | 15.51423612106804 MeV |
| surface | 17.29318120951770 MeV |
| coulomb | 0.68781560915689 MeV |
| asymmetry | 23.84655788394849 MeV |
| pairing | 15.99084511339891 MeV |

### PRED-0037: Coulomb Z^2 form simplification

The Coulomb term factor `Z·(Z−1)` is replaced with `Z²` (self-Coulomb-included
textbook form). All other coefficients and term forms are unchanged.

`aC · Z·(Z−1) · A^(−1/3)  →  aC · Z² · A^(−1/3)`

**Purpose:** Quantify the per-target shift caused by adopting the
self-Coulomb-included Coulomb energy. The deterministic shift relative to
PRED-0001 is `+aC · Z / A^(1/3)` for every target and grows with Z.

### PRED-0038: Pairing 1/A scaling simplification

The pairing term scaling `1/√A` is replaced with `1/A`. The pairing sign rule
(+1 for even-even, −1 for odd-odd, 0 for odd-A) is unchanged.

`pairing_sign(Z, N) · aP / √A  →  pairing_sign(Z, N) · aP / A`

**Purpose:** Quantify the per-target shift caused by an alternate
inverse-A pairing scaling. Odd-A targets are identical to PRED-0001 by
construction; only even-even and odd-odd parity classes are sensitive.

## Deterministic Calculation

Both variants reuse the same helper path used by the canonical
`physics_lab.engines.nuclear_mass_baselines` helpers, with one structural
rewrite each:

```
PRED-0037:
  B(Z, N) = aV·A − aS·A^(2/3) − aC·Z²·A^(−1/3) − aA·(N−Z)²/A + δ_std
  δ_std    = +aP/√A   for even-even
           = −aP/√A   for odd-odd
           = 0         for odd-A

PRED-0038:
  B(Z, N) = aV·A − aS·A^(2/3) − aC·Z·(Z−1)·A^(−1/3) − aA·(N−Z)²/A + δ_1A
  δ_1A     = +aP/A    for even-even
           = −aP/A    for odd-odd
           = 0         for odd-A

atomic_mass_u   = Z·HYDROGEN_ATOM_MASS_U + N·NEUTRON_MASS_U − B / ATOMIC_MASS_UNIT_MEV
mass_excess_mev = (atomic_mass_u − A) · ATOMIC_MASS_UNIT_MEV
```

Physical constants used (matching `physics_lab.engines.nuclear_masses`):

- HYDROGEN_ATOM_MASS_U = 1.00782503223 u
- NEUTRON_MASS_U = 1.00866491595 u
- ATOMIC_MASS_UNIT_MEV = 931.49410242 MeV/u

## Target Batch

All four targets reuse the `frontier-next-row` batch already covered by
PRED-0001 (base fitted SEMF), PRED-0021 (50/50 coefficient blend), and
PRED-0023 (pairing +10%). Reusing the same batch makes per-target
variant-to-variant deltas directly comparable.

Each target is absent from both `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`
and `data/nuclear_masses/post_ame2020_holdout.yaml` at registration time.

| Nuclide | Z | N | A | Parity | PRED-0001 (MeV) | PRED-0037 (MeV) | PRED-0038 (MeV) | Δ vs PRED-0001 (0037) | Δ vs PRED-0001 (0038) |
|---------|---|---|---|--------|-----------------|-----------------|-----------------|----------------------|----------------------|
| Ca-55 | 20 | 35 | 55 | odd-A | −8.623439 | −5.006168 | −8.623439 | +3.617 | 0.000 |
| Ni-76 | 28 | 48 | 76 | even-even | −30.856074 | −26.309417 | −29.232204 | +4.547 | +1.624 |
| Zn-80 | 30 | 50 | 80 | even-even | −41.511297 | −36.722461 | −39.923352 | +4.789 | +1.588 |
| Ga-85 | 31 | 54 | 85 | odd-A | −28.69329  | −23.843823 | −28.693290 | +4.850 | 0.000 |

**Key observations (pre-reveal, no measurement comparison):**

- PRED-0037 shifts every target up by approximately `+aC · Z / A^(1/3)`,
  matching the closed-form Coulomb-form difference. The shift is uniform
  across parity classes because the Coulomb-term rewrite is parity-blind.
- PRED-0038 leaves odd-A targets identical to PRED-0001 because
  `pairing_sign = 0` zeroes the pairing term for both forms. Only even-even
  and odd-odd targets are affected. The frontier batch contains two odd-A
  and two even-even nuclides, so PRED-0038's deltas exhibit two invariance
  rows and two negative-binding-shift rows by construction.
- Comparing the two variants on the same target batch isolates a
  Coulomb-form effect (PRED-0037) from a pairing-scaling effect
  (PRED-0038); both shifts are positive in mass excess and bounded by the
  underlying coefficients with no fitted improvement.

## Why These Variants Are Bounded For The Minimal-Complexity Lane

Both entries satisfy the `TASK-0236` bounded-variant requirements:

1. **One-line structural change per variant.** Neither variant adds shell,
   magic-number, odd-even-stratified, or neutron-rich correction terms.
2. **No new free parameters.** All RESULT-0015 fitted coefficients remain
   frozen with identical numeric values.
3. **No promoted model status.** Both variants are textbook-style
   simplification controls; neither is presented as a candidate improvement.
4. **Deterministic value reproduction.** Tests in
   `tests/test_prediction_registry_minimal_complexity_controls.py`
   recompute every predicted value from the frozen formula and constants.
5. **Repo-prospective target list.** The frontier-next-row batch is absent
   from committed measured and post-AME2020 holdout datasets.

## Limitations

- Prospective registry entries only; no claim, canonical result, or
  knowledge promotion.
- The variant forms are deliberate simplifications, not fitted
  improvements; both are expected to degrade agreement with future
  measurements relative to the base PRED-0001 entry.
- Odd-A nuclides in PRED-0038 are identical to PRED-0001 by construction;
  this is an invariance check, not new prediction information for those
  targets.
- The target batch is small (four nuclides) and tightly coupled to other
  frontier-next-row variants; broader coverage requires separate tasks.
- True prospective prediction status requires later maintainer
  source-state review to confirm the target nuclides were not measured in
  any committed dataset at registration time.
- The Coulomb Z² form ignores the self-Coulomb subtraction and is
  expected to systematically overestimate Coulomb repulsion at non-trivial Z.
- The 1/A pairing scaling falls off faster than 1/√A and is expected to
  underweight pairing for medium and heavy nuclei.

## Verdict

Both entries are correctly structured prospective minimal-complexity form
controls. They are registered for future reveal comparison only.
No claim, result, or knowledge promotion is implied.
