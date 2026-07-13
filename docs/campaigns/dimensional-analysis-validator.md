# Dimensional Analysis Validator

## Goal

Build a deterministic benchmark that checks whether APL can classify formulas
as dimensionally valid, invalid, suspicious, or known-limit failures using
explicit SI-dimension reasoning and simple physics sanity checks.

## Why It Matters

This campaign is the cleanest "quality floor" project in the repository:

- it does not depend on fitting quality or narrative interpretation;
- it catches a real class of physics errors early;
- it can protect later formula-discovery campaigns from obviously broken
  expressions;
- it offers a public-facing result that is easy to explain and independently
  rerun.

## Current Results

This campaign now has a completed MVP benchmark plus a growing follow-on
challenge surface:

- `EXP-0006/RUN-0006` produced `RESULT-0007`, a frozen 50-item MVP benchmark
  with **49/50 agreement (98%)**.
- `EXP-0006/RUN-0007` produced `RESULT-0020`, an `AGENT_VALIDATED` live
  74-item replay with **74/74 legacy policy-adjusted agreement**. Its item
  ledger contains 64/74 exact categorical matches; eight `KNOWN_LIMIT_FAIL ->
  VALID` and two `SUSPICIOUS -> INVALID` equivalences account for the other ten
  legacy acceptances. `TASK-0948` supplied the genuinely independent Gate B
  replay identity and reproduced all 17 tracked metrics with zero drift at
  tolerance `1e-9`.
- `knowledge/challenge_sets/dimensional_analysis_challenge_set_mvp_50.yaml`
  stores the frozen canonical replay input.
- `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml` stores the
  live curation surface for follow-on challenge-set work.
- The benchmark uses four verdict families in the challenge set:
  `VALID`, `INVALID`, `SUSPICIOUS`, and `KNOWN_LIMIT_FAIL`.
- Known-limit and semantic-suspicion cases remain explicit MVP limitations:
  dimensional consistency is not full physical correctness.

Current campaign state in one sentence:

The validator has a frozen `LEGACY_UNTIERED` MVP result and a newer
`AGENT_VALIDATED` calibration result. Gate C is deferred: the next scientific
step is a fresh role-disjoint benchmark under the label-blind v2 contract, not
promotion of the historical 74-item surface.

Start here:

- [Dimensional Analysis Validator MVP summary](../results/dimensional-analysis-validator-summary.md)
- [RESULT-0007 report](../../results/EXP-0006/RUN-0006/report.md)
- [RESULT-0020 report](../../results/EXP-0006/RUN-0007/report.md)
- [Dimensional Analysis Challenge Set](../notes/dimensional-analysis-challenge-set.md)
- [Reproducibility capsule](../reproducibility-capsules.md#result-0007--dimensional-analysis-validator-mvp)

## Open Questions

- Can a role-disjoint fresh benchmark sustain the predeclared exact-agreement
  threshold once inference is isolated from labels and curated policy metadata?
- Which known-limit checks belong in the next benchmark version, and which
  should remain out of scope?
- How should the validator communicate that natural-unit formulas are outside
  the current SI-focused benchmark version?
- Which semantic warnings should remain outside the dimensional verdict and be
  evaluated on their own axis?

## Recommended Tasks

- `TASK-0766` completed the independent replay with
  `GATE_B_CONTESTED_RESULT`; see the
  [contested replay note](../reviews/dimensional-result-0020-gate-b-contested-replay.md).
- `TASK-0948` resolved the validation-independence blocker: `RESULT-0020` is
  now `AGENT_VALIDATED` with `validation_independence: independent`.
- `TASK-0956` refreshed `CLAIM-0005` evidence to cite `RESULT-0020` while
  keeping the claim in `DRAFT`; any status change remains a maintainer Gate C
  decision.
- `TASK-1038` separates label-blind inference from benchmark scoring and keeps
  the historical 50/74 surfaces as regression/calibration memory.
- `TASK-1039` is the next scientific gate: a role-disjoint curator must freeze
  a fresh 80-120 item v2 surface without running the validator or seeing its
  outputs.
- The next result-bearing task must use a fresh role-disjoint frozen benchmark;
  do not rescore the current 74 items as confirmatory evidence.
- narrow microtasks from `tasks/microtasks/dimensional-analysis-validator.yaml`
  only when they do not rewrite canonical benchmark metrics.

## Recommended Contributor Types

- symbolic-math implementers;
- physics educators or curators who can author unambiguous examples;
- test engineers who enjoy classification benchmarks;
- documentation contributors focused on benchmark framing.

## What Not To Claim

- Do not let live challenge-set additions rewrite the canonical MVP result.
- Do not report follow-on curation metrics as if they were `RESULT-0007`.
- Do not change the frozen `RESULT-0020` input snapshot or metrics, or
  `CLAIM-0005` wording/status, outside an explicit maintainer Gate C task.
- Do not describe 74/74 legacy policy-adjusted agreement as 74 exact label
  matches; the exact historical count is 64/74.
- Do not use the current 74-item development surface as a fresh holdout after
  changing the validator or scorer.
- Do not treat SI-only validation as support for natural-unit workflows.
- Do not blur dimensional consistency with full physical correctness.
- Do not promote any claim automatically from challenge-set curation alone.

## Visualization Ideas

- category coverage bar chart for the frozen 50-formula MVP dataset and the
  live curation surface;
- confusion matrix for future intentional benchmark rebaselines;
- formula difficulty heatmap by domain and verdict class;
- pipeline diagram from symbolic parse -> unit check -> known-limit check ->
  verdict;
- examples panel showing one `VALID`, one `INVALID`, one `SUSPICIOUS`, and one
  `KNOWN_LIMIT_FAIL` formula.
