# Result Promotion Scorecard

Status: review gate. This document does not promote any existing result.

## Purpose

APL stores sandbox evidence, benchmark summaries, negative results, and
prediction registries. Those artifacts are useful, but they are not claims by
default.

Before a campaign result is described as a claim candidate, public scientific
result, knowledge entry, or discovery-like story, maintainers should apply a
result-candidate review using
`physics_lab/schemas/result_candidate_review.schema.json`.

## Required Scores

Every review must score:

- baseline strength;
- source provenance;
- artifact checksums;
- holdout or reveal quality;
- uncertainty handling;
- negative controls;
- leakage risk;
- reproducibility;
- external comparability;
- public wording risk.

Scores are:

- `PASS`;
- `PARTIAL`;
- `FAIL`;
- `NOT_APPLICABLE`.

The scorecard separates three outcomes:

- sandbox follow-up eligibility;
- public benchmark-summary eligibility;
- claim-candidate eligibility.

Claim promotion is never automatic. Even a claim-candidate verdict requires a
separate maintainer-reviewed task and conservative wording.

## Verdicts

- `SANDBOX_FOLLOWUP_ONLY`: useful enough for bounded follow-up, not a public
  result or claim.
- `BENCHMARK_SUMMARY_ONLY`: useful as a reproducible benchmark/failure-map
  summary, not a physics claim.
- `CLAIM_CANDIDATE_WITH_MAINTAINER_REVIEW`: may proceed to a separate
  claim-review task; no automatic promotion.
- `BLOCKED`: source, leakage, uncertainty, or reproducibility gaps stop the
  result.
- `NEGATIVE_MEMORY`: preserve as a falsification, null, or diagnostic result.

## Example: Sandbox-Only Nuclear Signal

Candidate: a Nuclear Mass Surface sandbox signal such as a local-curvature
residual lane.

Likely review:

- baseline strength: `PARTIAL`;
- source provenance: `PASS` for committed retrospective data, but no future
  reveal yet;
- holdout or reveal quality: `PARTIAL`;
- negative controls: `PASS` only if adversarial controls survive;
- public wording risk: `PARTIAL` or `FAIL` if framed as discovery.

Verdict: `SANDBOX_FOLLOWUP_ONLY`.

Allowed wording: "bounded sandbox signal worth no-leakage follow-up."

Forbidden wording: "APL found a new nuclear law."

## Example: Benchmark-Only Exoplanet Surface

Candidate: an Exoplanet Mass-Radius baseline or residual failure map.

Likely review:

- baseline strength: `PASS` when the frozen baseline and null comparison are
  documented;
- source provenance: `PASS` for a pinned NASA Exoplanet Archive snapshot;
- holdout or reveal quality: `PARTIAL` until the failure map has robust
  slice controls;
- public wording risk: `PASS` if framed as benchmark/failure-map work.

Verdict: `BENCHMARK_SUMMARY_ONLY`.

Allowed wording: "APL reproduced and stress-tested a mass-radius benchmark and
mapped where it fails."

Forbidden wording: "APL predicts habitable planets" or "APL discovered a new
planet-composition law."

## Machine-Readable Review

Use a `result_candidate_review.yaml` file when a task asks for a formal review.
The schema requires `human_review_required: true` and blocks
`claim_promotion_allowed: true` unless the final verdict is
`CLAIM_CANDIDATE_WITH_MAINTAINER_REVIEW`.
