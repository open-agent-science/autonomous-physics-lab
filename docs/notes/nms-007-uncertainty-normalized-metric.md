# NMS-007: Uncertainty-Normalized Residual Metric for Nuclear Mass Reports

## What the Metric Adds

Raw MeV residual |Δ| = |E_exp − E_model| treats all nuclides equally regardless
of measurement precision. An uncertainty-normalized residual:

```
χ̄ = (1/N) Σᵢ |Eᵢ_exp − Eᵢ_model| / σᵢ
```

down-weights well-measured nuclei (small σ) and up-weights poorly-measured
entries (large σ), making the summary statistic more sensitive to systematic
failures where the model is confidently wrong relative to experimental precision.

## Why It Cannot Replace All Other Metrics

1. **Extrapolated-entry problem:** for AME extrapolated entries, σ is itself
   derived from nuclear models. Using model-derived σ in the denominator makes
   the normalized metric circular — it penalises departures from the same models
   that generated the uncertainty.

2. **Interpretability:** raw MeV residual is directly interpretable for nuclear
   physics applications (e.g., r-process nucleosynthesis paths require accuracy
   to ~100 keV). The normalised metric is dimensionless and less directly
   actionable.

3. **Outlier sensitivity:** mean |Δ|/σ is sensitive to a few nuclei with
   unusually small reported uncertainties — a single very-precise measurement
   near a shell closure can dominate the metric if the model fails there.

## Dataset Constraint

AME 2020 provides per-entry experimental uncertainties for measured nuclei.
Extrapolated entries carry model-derived uncertainties that must not be used in
the normalized metric without an explicit caveat in the report.

## Recommendation

Report both raw mean |Δ| (MeV) and the normalized χ̄ for measured-only entries.
Use raw |Δ| as the primary metric; χ̄ as a secondary diagnostic for
precision-weighted performance.

## Limitation Statement

No numerical implementation of this metric exists in the repository. Metric note
only. One metric cannot settle model quality; multiple metrics and limitations
must be reported together.
