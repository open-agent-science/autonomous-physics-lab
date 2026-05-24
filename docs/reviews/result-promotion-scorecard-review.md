# Result Promotion Scorecard Review

Task: `TASK-0380`
Status: review-ready gate definition; no claim promotion.

## What Changed

This task defines a cross-campaign result-promotion gate for APL. It adds:

- a human-readable scorecard in `docs/result-promotion-scorecard.md`;
- a machine-readable `result_candidate_review` schema;
- schema tests covering valid reviews and rejection cases.

## Why It Matters

APL now has several strong sandbox and benchmark surfaces, especially Nuclear
Mass Surface and Exoplanet Mass-Radius. Without a promotion gate, agents could
accidentally turn sandbox evidence into public claims. The scorecard forces
maintainers to check source provenance, holdout/reveal quality, uncertainty,
negative controls, leakage risk, reproducibility, external comparability, and
public wording before any claim-candidate path opens.

## Boundaries

- No existing result is promoted.
- No existing claim is modified.
- Nuclear sandbox evidence remains sandbox-only unless a future task passes a
  separate maintainer review.
- Exoplanet benchmarks remain benchmark/failure-map outputs, not habitability
  or composition-law claims.

## Recommended Next Use

Use the schema for the first result-candidate review only after a campaign has
a concrete result package that maintainers want to evaluate for public summary
or claim-candidate status.
