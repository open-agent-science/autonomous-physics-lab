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
- `knowledge/challenge_sets/dimensional_analysis_challenge_set_mvp_50.yaml`
  stores the frozen canonical replay input.
- `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml` stores the
  live curation surface for follow-on challenge-set work.
- The benchmark uses four verdict families in the challenge set:
  `VALID`, `INVALID`, `SUSPICIOUS`, and `KNOWN_LIMIT_FAIL`.
- Known-limit and semantic-suspicion cases remain explicit MVP limitations:
  dimensional consistency is not full physical correctness.

Current campaign state in one sentence:

The validator has a frozen MVP result, while new challenge entries are
curation work until a future benchmark task intentionally rebaselines them.

Start here:

- [Dimensional Analysis Validator MVP summary](../results/dimensional-analysis-validator-summary.md)
- [RESULT-0007 report](../../results/EXP-0006/RUN-0006/report.md)
- [Dimensional Analysis Challenge Set](../notes/dimensional-analysis-challenge-set.md)
- [Reproducibility capsule](../reproducibility-capsules.md#result-0007--dimensional-analysis-validator-mvp)

## Open Questions

- How should `SUSPICIOUS` versus `INVALID` cases be exposed in result
  artifacts beyond the MVP scope?
- Which known-limit checks belong in the next benchmark version, and which
  should remain out of scope?
- How should the validator communicate that natural-unit formulas are outside
  the current SI-focused benchmark version?
- When should the live challenge-set curation surface be intentionally
  rebaselined into a new canonical benchmark run?

## Recommended Tasks

- `TASK-0134` — freeze benchmark replay scope and prevent silent challenge-set
  drift.
- `TASK-0146` — add one-command reproduction for core current results.
- narrow microtasks from `tasks/microtasks/dimensional-analysis-validator.yaml`
  for live challenge-set curation, with explicit claim ceilings.

## Recommended Contributor Types

- symbolic-math implementers;
- physics educators or curators who can author unambiguous examples;
- test engineers who enjoy classification benchmarks;
- documentation contributors focused on benchmark framing.

## What Not To Claim

- Do not let live challenge-set additions rewrite the canonical MVP result.
- Do not report follow-on curation metrics as if they were `RESULT-0007`.
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
