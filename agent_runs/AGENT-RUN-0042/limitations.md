# Limitations

- Controls use committed snapshot fields and frozen CK17 residuals only.
- Matched controls are diagnostic slices, not causal adjustments.
- Per-class median control is a target-row residual shift rather than an independent row slice.
- Host-temperature control excludes rows without host effective temperature.
- Detection-method control excludes rows missing detection_method.
- Uncertainty band control excludes rows whose combined uncertainty cannot be computed.
- Negative controls are deterministic but seed-dependent; the seed is recorded in thresholds.
- Minimum-mass rows are sparse diagnostics only and excluded from headline metrics.
- No composition, inflation-physics, habitability, target-priority, prediction, claim, or knowledge output is authorized.
