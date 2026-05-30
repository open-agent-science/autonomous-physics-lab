# Limitations

- Compact slice is small; quartile bins fall below the 30-row floor.
- Mass-half partition is a coarse fallback diagnostic, not a localized subrange.
- Controls use committed snapshot fields and frozen CK17 residuals only.
- Matched controls are diagnostic slices, not causal adjustments.
- Per-class median control is a residual shift on the bin's own rows, not an independent slice.
- Bin edges are equal-count contiguous chunks of mass-sorted rows, not fixed physical boundaries.
- Random outside-compact control is deterministic but seed-dependent; the seed is recorded in thresholds.
- Minimum-mass rows are excluded; only true-mass/transit-radius rows are used.
- No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.
