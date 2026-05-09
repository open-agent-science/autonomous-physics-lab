# Research Quality Gate

## Purpose

This gate defines the minimum quality bar for autonomous sandbox research in
APL.

Passing the gate does not promote a claim. It only means the work is coherent
enough for maintainer review.

## Required Checks

An autonomous research PR must answer each item below.

| Check | Required answer |
| --- | --- |
| Campaign scope | Which `campaign_profiles/*.yaml` profile authorized the run? |
| Claim ceiling | What is the strongest claim the work is allowed to make? |
| Input references | Which files, datasets, constants, or prior results were used? |
| Method | What deterministic method or command produced the evidence? |
| Code reference | Which repository code path performed the calculation? |
| Metrics | Which numerical or classification metrics were produced? |
| Failure conditions | What would falsify or invalidate the proposal? |
| Baseline or null | What baseline, exact reference, or negative comparison applies? |
| Limitations | What range, dataset, assumption, or interpretation limit applies? |
| Novelty check | What existing notes, results, or queues were checked for duplication? |
| Verdict | Which review verdict applies? |
| Promotion boundary | What must happen before any canonical claim or result can exist? |

## Verdicts

Use these verdicts for sandbox research handoff:

- `SANDBOX_PASS`: the proposed check ran and met its predefined sandbox
  criteria, but no claim is promoted.
- `SANDBOX_FAIL`: the proposed check ran and failed its predefined criteria.
- `FALSIFIED`: the candidate is contradicted by the configured check.
- `INCONCLUSIVE`: the run did not decide the proposed question.
- `OVERFITTED`: the candidate appears tuned to the checked slice or lacks a
  credible baseline.
- `REVIEW_NEEDED`: a maintainer or domain reviewer must decide interpretation
  before any next step.

Prefer the weakest accurate verdict.

## Hard Stops

Stop autonomous work and request maintainer review when:

- the work needs a new canonical experiment id;
- the work would edit `claims/`, canonical `hypotheses/`, canonical
  `experiments/`, or canonical `results/`;
- the work asks for public-facing discovery language;
- the result depends on uncited external data;
- the interpretation depends on domain judgment not encoded in the profile;
- the candidate needs broad parameter search without a predeclared baseline;
- the campaign profile says the direction is not whitelisted.

## Minimum Validation

For docs-only autonomous-loop changes, run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

For future sandbox runs, also run the campaign-specific commands listed in the
selected profile.

## PR Handoff Checklist

Before PR handoff, confirm:

1. The selected campaign profile is whitelisted.
2. Proposal files use the repository templates.
3. Sandbox evidence is not stored as canonical `RESULT-*` evidence.
4. The PR body names limitations before any positive interpretation.
5. The requested maintainer decision is explicit.
6. Claim promotion is deferred to a later reviewed path.
