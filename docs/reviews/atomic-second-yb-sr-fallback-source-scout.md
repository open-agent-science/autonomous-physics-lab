# Atomic Second Yb/Sr Fallback Source Scout

Task: `TASK-0606`
Domain: Atomic clock residuals
Mode: planning only
Verdict: `FALLBACK_CANDIDATE_BLOCKED_ON_ARTIFACT_LOCATOR`

## Context

Pizzocaro remains the primary Atomic row-admissibility path. This scout checks
whether a second Yb/Sr or closely compatible optical-clock comparison source can
be prepared without weakening the existing covariance and campaign-window
policy.

Inputs reviewed:

- `docs/reviews/atomic-pizzocaro-source-artifact-review.md`
- `docs/reviews/atomic-second-source-fallback-triage.md`
- `docs/reviews/atomic-first-benchmark-covariance-policy.md`
- `data/atomic_clocks/source_manifest.yaml`

## Candidate

Candidate: Lange et al. 2021 / PTB Yb+ E3/Cs optical-clock comparison source.

Prior triage posture: ranked as the best breadth fallback after Pizzocaro, but
not as a direct replacement for a Yb/Sr ratio source. It is useful because it
tests whether the Atomic lane can support a second institution/source family
with compatible optical-clock semantics.

Stable locator status: not pinned in the committed repo. A follow-up artifact
task must verify the exact publication locator, table/supplement endpoint,
source timestamp if any, and checksum path before any manifest entry or row
curation.

Publication/release timing: literature source after the already-pinned Beloy and
Pizzocaro sources; exact publication metadata must be verified by the artifact
task.

Value-bearing availability: not inspected in this planning task. The artifact
task must determine whether the relevant values are in a machine-readable table,
supplement, PDF table, or figure. No frequency-ratio values were copied here.

## Covariance and Campaign Notes

The candidate remains scientifically plausible only if the artifact task can
state:

- Whether the comparison is direct, derived, or chained through a reference.
- Whether Cs reference uncertainty is part of the benchmark target or only a
  calibration context.
- Whether systematic uncertainty terms are separable enough for the first
  benchmark covariance policy.
- Whether the measurement campaign window is explicit and not merged across
  incompatible runs.
- Whether the row should be treated as a different source family rather than a
  second Yb/Sr direct-ratio row.

If these conditions cannot be resolved from the publication artifacts, the
candidate should be rejected rather than added as a weak source.

## License and Reuse

License/reuse posture is unresolved. The artifact task must verify whether the
publisher, supplement, or institutional release allows storing the artifact
metadata and extracting row-level values into APL source packages.

No metadata-only source-manifest entry is added by this scout because the stable
locator and checksum path are not yet pinned.

## Decision

Decision: keep Lange et al. 2021 / PTB Yb+ E3/Cs as the single named fallback
candidate, but leave it blocked until a source-artifact locator review verifies
the exact artifact and reuse path.

Recommended follow-up task:

- Pin the exact Lange/PTB artifact locator.
- Verify table/figure availability without copying values into the review.
- Record checksum feasibility and license/reuse posture.
- Decide whether the candidate is admissible as a second Atomic source package
  or should be rejected as too indirect for the first cross-source benchmark.

## Output Routing

This scout does not add rows, source-manifest entries, constants-drift fits,
derived constraints, cross-source metrics, canonical results, predictions, or
claims.
