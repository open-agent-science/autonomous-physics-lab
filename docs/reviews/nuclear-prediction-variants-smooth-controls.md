# Nuclear Prediction Variants — Smooth Semi-Empirical Controls

Task: `TASK-0228`

## Scope

This note records two new prospective entries in the nuclear mass prediction
registry. Both entries are **smooth semi-empirical controls** in the sense
defined by
[`docs/notes/nuclear-prediction-variant-expansion-wave.md`](../notes/nuclear-prediction-variant-expansion-wave.md):
they stay in the coefficient space of the standard semi-empirical mass formula
and do not introduce shell, pairing-class, magic-number, neutron-rich, or
odd-even corrections.

The two entries are:

| Entry | Model id | Target batch |
| --- | --- | --- |
| `PRED-0021` | `RESULT-0015::model_fitted_reference_blend_50_50` | `frontier-next-row` |
| `PRED-0022` | `RESULT-0015::model_fitted_semi_empirical::volume_perturbation_plus_one_percent` | `frontier-next-row` |

Both entries target the same four nuclides as `PRED-0001` and `PRED-0005`
(`Ca-55`, `Ni-76`, `Zn-80`, `Ga-85`) so the new smooth controls can be
compared against the existing fitted and reference baselines on an identical
target list once a future reveal task exists.

## Model Choice Rationale

### `PRED-0021` — fitted/reference 50/50 blend

This control averages the RESULT-0015 fitted coefficients with the literature
`REFERENCE_SEMI_EMPIRICAL_COEFFICIENTS` defaults. The blended set is:

```text
volume   = 15.657118060534021
surface  = 17.79659060475885
coulomb  = 0.7009078045784444
asymmetry= 23.52327894197424
pairing  = 13.995422556699456
```

The full pairing term is retained. The blend is intentionally midway between
the small-slice fit (which already appears as the primary variant in
`PRED-0001`) and the literature reference (already present as the control
variant in `PRED-0005`). It tests whether intermediate coefficients yield a
predictably intermediate mass-excess curve on the same target batch, without
introducing any new correction term.

### `PRED-0022` — fitted volume +1% perturbation

This control multiplies the fitted volume coefficient by 1.01 and freezes all
other coefficients. The perturbed set is:

```text
volume   = 15.66937848227872
surface  = 17.2931812095177
coulomb  = 0.6878156091568888
asymmetry= 23.846557883948485
pairing  = 15.990845113398912
```

It is a bounded smooth-sensitivity probe: a single coefficient is perturbed
at the 1% level. Because the volume term scales linearly with `A`, a +1%
volume shift moves every predicted mass excess by a large smooth amount, which
makes this entry a useful sensitivity reference rather than a candidate fit.

Neither entry is a promoted hypothesis. Both are clearly labeled control
variants.

## Deterministic Calculation Path

For each nuclide the registered `predicted_value_mev` was produced from the
deterministic helpers:

1. `physics_lab.engines.nuclear_mass_baselines.semi_empirical_atomic_mass_u`
   converts `(Z, N, coefficients)` to an atomic mass in `u`.
2. `physics_lab.engines.nuclear_masses.mass_excess_keV_from_atomic_mass_u`
   converts atomic mass to mass excess in keV.
3. The keV value is divided by 1000 and rounded to 6 decimal places.

The values are reproducible from the repository state recorded in the
`source_state.git_commit` field. No live external source was queried during
registration.

## Reveal Rule

Both entries follow the registry policy in
[`docs/prediction-registry-policy.md`](../prediction-registry-policy.md). A
reveal step is allowed only when a future maintainer-reviewed nuclear-mass
dataset or source manifest committed after the registry timestamp contains
measured or reviewably convertible values for one or more target nuclides.

Reveal must happen in a separate maintainer-reviewed task. Neither the model
id, the coefficient note, the target nuclide list, nor the predicted values
may be modified after registration.

## Limitations

- Both entries are prospective registry variants only, not claims or result
  packages.
- The fitted baseline used as a blend partner is trained on the small pinned
  measured slice `NMD-0002`; it is not a validated universal nuclear-mass
  model.
- The 50/50 blend has no scientific motivation beyond being a smooth midpoint
  control; it is not a calibration recipe.
- The +1% volume perturbation is a sensitivity probe, not a fitted model. It
  will deliberately shift every prediction by several MeV.
- Absence of the target nuclides from committed repository datasets at
  registration time is not proof of absence from the external scientific
  record. True-world prospectiveness requires later maintainer source-state
  review.
- These entries do not address shell, pairing, magic-number, neutron-rich, or
  isotope-chain corrections; that scope belongs to the parallel
  `TASK-0229`–`TASK-0237` lanes.
