# Dimensional Analysis Validator

## Role-Disjoint V2 Surface Freeze

`TASK-1039` freezes an 80-item `label_blind_exact_v2` surface under
`knowledge/challenge_sets/dimensional_analysis_challenge_set_v2.yaml`. Its
curation identity is `same_owner_role_disjoint_agent`, so the bounded outcome
is `CALIBRATION_ONLY_ROLE_LIMIT`, not a confirmatory holdout. No validator run,
score, metric, or computed verdict was inspected during curation.

That surface has now been scored once as `RESULT-0030` and passed all frozen
calibration thresholds, but it remains same-owner calibration memory. The next
trust paths are disjoint: `TASK-1062` independently replays the frozen result,
while `TASK-1071` is reserved for a different human to author and freeze a
fresh blind surface without scoring. Neither task changes `CLAIM-0005`.

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
- `EXP-0006/RUN-0008` produced AGENT_PUBLISHED `RESULT-0030` on the frozen
  exact-v2 calibration surface: **80/80 exact agreement**, **100% VALID
  recall**, **100% INVALID recall**, and **0% INCONCLUSIVE**. Gate A passed;
  Gate B has not yet been attempted.

Current campaign state in one sentence:

The validator has a frozen `LEGACY_UNTIERED` MVP result, AGENT_VALIDATED
historical calibration memory, and AGENT_PUBLISHED `RESULT-0030` on the 80-item
exact-v2 surface. Because benchmark authorship is same-owner role-disjoint, the
new result remains calibration-only and cannot promote `CLAIM-0005`.

Start here:

- [Dimensional Analysis Validator MVP summary](../results/dimensional-analysis-validator-summary.md)
- [RESULT-0007 report](../../results/EXP-0006/RUN-0006/report.md)
- [RESULT-0020 report](../../results/EXP-0006/RUN-0007/report.md)
- [RESULT-0030 report](../../results/EXP-0006/RUN-0008/report.md)
- [Dimensional Analysis Challenge Set](../notes/dimensional-analysis-challenge-set.md)
- [Reproducibility capsule](../reproducibility-capsules.md#result-0007--dimensional-analysis-validator-mvp)

## Open Questions

- Can an independent human Gate B replay reproduce all RESULT-0030 metrics and
  verification fields exactly?
- Can a different human author a fresh blind benchmark with enough source,
  label, and exposure independence for a later one-shot generalization test?
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
- `TASK-1039` froze 80 v2 items without running the validator and returned
  `CALIBRATION_ONLY_ROLE_LIMIT` because curation was same-owner role-disjoint.
- `TASK-1051` scored the 80 frozen items once and published `RESULT-0030` after
  all exact-agreement, class-recall, and inconclusive-rate gates passed.
- `TASK-1062` is the independent-human replay gate, with no row, label,
  threshold, engine, metric, or scope change.
- `TASK-1071` is a separate external benchmark-freeze gate. It forbids
  validator execution and requires a different controlling human; later
  one-shot scoring must be another task. The current session stopped with
  `EXTERNAL_EXPOSURE_BLOCKED` before curation; no candidate rows, labels, or
  score were created. See [blocker record](../reviews/dimensional/task1071-external-exposure-blocker.md).
- The current evidence remains calibration-only. Neither replay nor benchmark
  curation automatically changes `CLAIM-0005`.
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
