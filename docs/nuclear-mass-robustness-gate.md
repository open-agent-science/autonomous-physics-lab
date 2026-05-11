# Nuclear Mass Candidate Robustness Gate

**Task:** `TASK-0190`
**Scope:** nuclear-mass residual candidates and follow-up sandbox batches
**Status:** review-ready gate
**Claim boundary:** advisory for sandbox follow-up, strict for claim or result promotion

This gate defines the minimum evidence package required before APL expands a
nuclear-mass residual candidate into a follow-up batch or considers any stronger
scientific status.

It exists because the first nuclear pilot found a promising sandbox candidate,
but the split-sensitivity replay showed that the signal is not uniformly stable
across same-shape holdout splits. The correct response is disciplined follow-up,
not broader formula search.

## Required Evidence Package

Every nuclear residual candidate reviewed under this gate must include:

- task id and candidate id;
- dataset identifier and checksum when row-level data are used;
- baseline reference, including the frozen baseline result or run id;
- exact candidate formula or feature family before evaluation;
- fitted parameter count and any region-specific switches;
- active holdout definitions;
- train, primary holdout, structured holdout, and split-sensitivity metrics;
- leakage and cherry-pick review;
- negative-control comparison;
- limitations and verdict.

For current work, the baseline reference is the frozen nuclear surface from
`EXP-0012` / `RESULT-0015`, unless a later task explicitly supersedes it.

## Gate Outcomes

Use one of these gate outcomes in future nuclear reviews:

- `ALLOW_BOUNDED_SANDBOX_FOLLOWUP`
- `ALLOW_ONLY_AS_NEGATIVE_CONTROL`
- `REQUIRES_TIME_SPLIT_REPLAY`
- `BLOCK_PROMOTION`

These outcomes do not replace scientific verdicts such as `PARTIALLY_VALID` or
`OVERFITTED`. They decide what the next workflow is allowed to do.

## Minimum Robustness Checks

| Check | Minimum for sandbox follow-up | Minimum for claim or canonical result promotion |
| --- | --- | --- |
| Primary holdout | Report every active holdout from `docs/nuclear-mass-holdout-protocol.md`; no hidden failed slice. | Improve or tie the primary aggregate and avoid material regression on any active structured slice. |
| Split sensitivity | Replay at least three same-shape alternatives, or enumerate the family when feasible. Report improved, tied, regressed, median delta, worst delta, and pilot-split rank. | Stable across the split family. A candidate with many same-shape regressions or a large worst regression cannot be promoted. |
| Leakage review | State whether candidate selection happened before or after holdout visibility, and preserve that boundary in the report. | Candidate family, subset definitions, and pass rule must be frozen before any promotion-grade reveal or external validation. |
| Complexity penalty | Report parameter count, new discontinuities, magic-number switches, chain-specific terms, and any piecewise behavior. | Modest complexity increase only; no decorative terms, direct row memorization, or uncontrolled region switches. |
| Negative control | Compare against at least one rejected, overfit, or plausibly wrong residual family when search-style work is used. | Negative-control failure must remain visible and materially worse than the promoted candidate. |
| Limitation wording | State sandbox-only limitations and dataset-size risk. | No discovery, universal-formula, or breakthrough wording without maintainer review and external-style validation. |

## Post-AME2020 Time-Split Rule

`TASK-0187` provides a reviewed post-AME2020 source manifest, but it does not
commit row-level holdout values and does not activate time-split scoring.

Until a reviewed row-level post-AME2020 dataset or an explicit maintainer
source-audit dry run exists:

- post-AME2020 behavior is a required limitation note;
- second-batch sandbox candidates may run only as bounded internal follow-up;
- no candidate may be promoted to a canonical result or claim on internal
  slices alone.

`TASK-0188` now records the conservative source-manifest-only guard. It is
useful evidence that active benchmark metrics are not yet available, but it is
not a row-level time-split result.

After `TASK-0195` and `TASK-0196`, or an equivalent reviewed row-level
time-split benchmark, exist:

- post-AME2020 behavior becomes a required check before claim or canonical
  result promotion;
- a candidate that improves internal splits but fails the time-split surface
  should receive `REQUIRES_TIME_SPLIT_REPLAY` or `ALLOW_ONLY_AS_NEGATIVE_CONTROL`,
  not success framing;
- retrospective post-AME2020 evidence must not be described as strict blind
  prediction unless a prediction registry entry predates the measurement.

## Decision Rules

Use these rules before follow-up batches:

- `ALLOW_BOUNDED_SANDBOX_FOLLOWUP` when the candidate is compact, leakage is
  disclosed, primary holdouts are reported, split sensitivity is acceptable or
  explicitly bounded, and the next batch will preserve negative controls.
- `ALLOW_ONLY_AS_NEGATIVE_CONTROL` when a candidate is useful mainly because it
  demonstrates overfit, leakage sensitivity, chain specificity, or split
  fragility.
- `REQUIRES_TIME_SPLIT_REPLAY` when internal evidence is promising but too
  selection-sensitive to expand without a harder post-AME2020 or equivalent
  validation surface.
- `BLOCK_PROMOTION` whenever leakage, unreported failed slices, unstable split
  behavior, excessive complexity, or missing negative controls make the result
  unsuitable for public scientific memory.

## Current Candidate Reading

`HYP-PROPOSAL-0021` remains sandbox-only partial evidence.

Supporting evidence:

- `AGENT-RUN-0005` found favorable active holdout behavior on the first pilot;
- `AGENT-RUN-0006` replayed same-shape alternatives and found split
  sensitivity;
- the independent review recommends no claim or canonical result promotion.

Gate outcome:

`HYP-PROPOSAL-0021` may inform a bounded second sandbox batch only if the batch
keeps this split sensitivity visible, includes negative controls, and does not
use the candidate as a public success story. Promotion is blocked until a
harder external-style validation surface exists.

## Output Contract For Follow-Up PRs

Any future nuclear follow-up PR should include a short gate section:

```text
Robustness gate:
- outcome:
- baseline:
- active holdouts:
- split-sensitivity summary:
- leakage review:
- complexity note:
- negative control:
- post-AME2020 status:
- limitations:
```

If any field is missing, the PR should be treated as incomplete for
claim-bearing work and may be incomplete even for sandbox follow-up.
