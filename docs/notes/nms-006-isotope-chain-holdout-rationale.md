# NMS-006: Isotope-Chain Holdout vs Random Nuclide Masking

## The Comparison

| Method | What is withheld |
|---|---|
| Random nuclide masking | ~10% of nuclei chosen randomly across all (N,Z) |
| Isotope-chain holdout | All isotopes of one element (fixed Z, all measured N) |

## What Should Remain Invariant

In both cases the training set covers a broad (N,Z) surface. The mean residual
on the training set, and the overall BW baseline performance, should be similar.

## What Should NOT Remain Invariant

**Test residual.** For an isotope-chain holdout:
- The model must extrapolate to unseen N values for a specific Z.
- It cannot interpolate from same-Z neighbours (all are withheld).
- Any element-specific bias learned during training (e.g., magic-number
  structure for Z=50 tin isotopes) is directly tested.

For random masking, the withheld nuclei have same-Z neighbours in the training
set. A model can interpolate rather than extrapolate — this underestimates the
true generalisation error for new elements.

## Generalisation Risk Exposed

A correction formula that implicitly learns Z-dependent offsets (for example, a
formula that over-fits residuals for a common isotope chain) will show:
- Small error on random-masking holdout (interpolation succeeds).
- Large error on isotope-chain holdout (extrapolation to new Z fails).

Isotope-chain holdout exposes this overfitting; random masking misses it.

## Recommendation

Isotope-chain holdout should be the preferred validation mode for correction
terms that claim generality across elements. Random masking may be used as a
secondary check for coverage breadth.

## Limitation Statement

No holdout has been run in this repository yet. This note is a methodological
rationale for future experimental design. One holdout split does not prove
robustness — multiple chains should be tested if resources allow.
