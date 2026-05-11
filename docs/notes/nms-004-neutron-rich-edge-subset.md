# NMS-004: Neutron-Rich Edge Subset for Future Holdout Use

## Proposed Subset Rule

Select nuclei satisfying both:
- Neutron excess: N − Z ≥ 20
- Mass number: A ≥ 50

Restrict to measured entries (AME flag `#` excluded) to avoid extrapolation
confounds.

## Why This Is a Harder Generalization Slice

The Bethe-Weizsäcker (BW) asymmetry term scales as `(N−Z)²/A`. For large N−Z,
this term dominates the binding energy, and fitted correction terms that do not
explicitly model:
- asymmetry saturation (isospin-dependent surface effects),
- neutron skin formation,
- pairing corrections for very neutron-rich nuclei,

will degrade faster on this subset than on the stable valley (N≈Z) training
distribution.

## Intended Stress Behaviour

A model trained on the full nuclear chart but tested on this subset should show:
- Higher mean absolute residual per nucleon compared to stable-valley nuclei.
- Larger spread in residuals near shell closures within the neutron-rich region
  (N=50, N=82 isotone chains).

If a correction formula does NOT show higher residuals on this subset, it is
likely that the formula has implicitly learned element-specific offsets from the
training data — a potential overfitting signal.

## Limitation Statement

Subset definition only. No data slice has been created or evaluated. The
difficulty of this subset is asserted from physical reasoning, not demonstrated
experimentally within this repository. Cutoff rule (N−Z ≥ 20, A ≥ 50) is
provisional and may need adjustment based on AME 2020 coverage.
