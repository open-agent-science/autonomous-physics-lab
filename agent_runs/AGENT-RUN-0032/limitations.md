# Limitations

- Chen-Kipping segment slopes, changepoints, and prefactors are frozen; the snapshot is not used to refit any segment.
- The minimum-mass axis treats M sin i as a lower bound on true mass and therefore biases residuals on RV-only systems.
- Quality filters use only reported sigma_M and sigma_R; covariance with host-star parameters is not modelled.
- The per-class median null baseline shares training rows with its scoring rows; this is intentional as a non-trivial floor, not predictive evidence.
- Per-detection-method splits are computed on the post-filter included set and are sensitive to sample composition.
- No habitability, biosignature, target-priority, prediction registry, claim, or knowledge promotion is authorised.
