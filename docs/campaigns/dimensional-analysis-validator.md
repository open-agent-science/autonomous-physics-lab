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

This campaign is still planning-first, but the design surface is already clear:

- `TASK-0017` produced the challenge-set plan and is currently `REVIEW_READY`.
- `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml` stores the
  50-item curated dataset.
- The planning note defines four verdict families used in the challenge set:
  `VALID`, `INVALID`, `SUSPICIOUS`, and `KNOWN_LIMIT_FAIL`.
- No canonical experiment run or validator implementation exists yet.

Current campaign state in one sentence:

The benchmark contract exists, but the checker itself does not.

Start here:

- [Dimensional Analysis Challenge Set](../notes/dimensional-analysis-challenge-set.md)
- [TASK-0017](../../tasks/TASK-0017-dimensional-analysis-challenge-set.yaml)

## Open Questions

- Should the first implementation live inside `physics_lab/engines/symbolic.py`
  or as a dedicated dimensional-validation module?
- How should `SUSPICIOUS` versus `INVALID` cases be exposed in result
  artifacts?
- Which known-limit checks belong in v1, and which should remain out of scope?
- How should the validator communicate that natural-unit formulas are outside
  the first benchmark version?
- What should the first canonical experiment id and hypothesis object look like
  for this validator?

## Recommended Tasks

- `TASK-0026` — add 10 more dimensional-analysis challenge items.
- maintain review and acceptance of `TASK-0017` so the benchmark contract is
  stable before implementation.
- future implementation tasks for a symbolic dimensional checker and benchmark
  wiring once the maintainer promotes them.

## Recommended Contributor Types

- symbolic-math implementers;
- physics educators or curators who can author unambiguous examples;
- test engineers who enjoy classification benchmarks;
- documentation contributors focused on benchmark framing.

## What Not To Claim

- Do not say APL already has a working dimensional validator.
- Do not report classification accuracy before a canonical run exists.
- Do not treat SI-only validation as support for natural-unit workflows.
- Do not blur dimensional consistency with full physical correctness.
- Do not promote any future claim automatically from challenge-set planning
  alone.

## Visualization Ideas

- category coverage bar chart for the 50-formula dataset;
- future confusion matrix once the checker exists;
- formula difficulty heatmap by domain and verdict class;
- pipeline diagram from symbolic parse -> unit check -> known-limit check ->
  verdict;
- examples panel showing one `VALID`, one `INVALID`, one `SUSPICIOUS`, and one
  `KNOWN_LIMIT_FAIL` formula.
