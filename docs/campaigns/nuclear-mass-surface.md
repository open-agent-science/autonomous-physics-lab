# Nuclear Mass Surface

## Goal

Build a verification-first nuclear mass campaign around baseline binding-energy
residuals, shell-closure structure, pairing effects, neutron-rich behavior,
and holdout-tested correction hypotheses.

The target is not a universal mass formula. The target is a disciplined
benchmark surface where compact, physically constrained correction terms can be
tested against real dataset structure, subset behavior, and negative controls.

## Orientation Note for New Contributors

This campaign started scaffold-first and now has a benchmark stack,
retrospective time-split evidence, a deterministic prediction factory, reusable
target batches, and frozen prospective prediction registry entries.

Safe contributions right now are still conservative, but they can now include
factory-slate and reveal protocol work:

- campaign map and guardrail wording;
- pinned-dataset and provenance expansion work;
- subset and holdout curation;
- bounded feature-term factory slates under the frozen `RESULT-0015` baseline;
- prospective prediction registry selection after reviewed slates only;
- reveal protocol work that preserves the no-peek boundary;
- limitation notes that keep the campaign conservative.

### What not to implement yet

- do not fetch live datasets into canonical memory without pinned source and
  checksum handling;
- do not mix measured and extrapolated entries without an explicit flag and
  reviewable semantics;
- do not compare registered predictions against live or future measurements
  outside a maintainer-reviewed reveal task;
- do not write result artifacts or claims that imply a broad nuclear mass
  law.

## Why It Matters

This campaign is a stronger scientific target than another approximation-only
exercise because it combines:

- real measured nuclear mass data with explicit uncertainties;
- interpretable baseline structure rather than pure unconstrained search;
- known systematic residual regions near shell closures and related subsets;
- realistic holdout opportunities across isotope chains, magic-number regions,
  neutron-rich edges, and possible later time-split data updates;
- valuable negative results when pretty correction families fail to
  generalize.

If APL can stay honest here, it moves closer to a serious benchmark workflow:
dataset provenance, baseline diagnostics, holdout discipline, sandbox evidence,
and reviewable failure modes.

## Current Results

This campaign now has an executable benchmark, sandbox, and prediction stack:

- `TASK-0166` created the campaign scaffold, guardrails, autonomy posture, and
  microtask queue.
- `TASK-0167` added the nuclear mass loader and schema layer.
- `TASK-0168` added the first baseline benchmark:
  - `EXP-0012`
  - `RESULT-0015`
  - pinned measured slice `NMD-0002`
- `TASK-0169` now defines the structured holdout contract for random,
  chain-based, shell-region, and neutron-rich generalization tests.
- `TASK-0170` now packages the first sandbox-only residual pilot:
  - `experiment_proposals/nuclear-mass/EXP-PROPOSAL-0005-nuclear-mass-sandbox-batch.yaml`
  - `agent_runs/AGENT-RUN-0005/`
  - `docs/reviews/autonomous-nuclear-mass-pilot-01.md`
- `TASK-0197` added a retrospective post-AME2020 row-level time-split
  benchmark, currently treated as useful but inconclusive evidence.
- `TASK-0205` registered the first prospective prediction entries,
  `PRED-0001` through `PRED-0020`.
- `TASK-0228` through `TASK-0232` and `TASK-0236` added bounded manual
  prediction-control families through `PRED-0030`, `PRED-0037`, and
  `PRED-0038`.
- `TASK-0249`, `TASK-0252`, `TASK-0253`, and `TASK-0254` added the nuclear
  prediction factory, feature-term support, deterministic slate ranking, and
  reusable target-batch library.
- `TASK-0251` registered the selected coefficient-transform factory wave as
  `PRED-0041` through `PRED-0050`.

Historical context:

- `TASK-0091` scoped a narrower magic-number correction idea.
- the broader campaign now supersedes that narrower framing by making dataset
  semantics, baselines, holdouts, and negative-result handling first-class
  surfaces instead of optional extras.

Current campaign state in one sentence:
the scientific direction is now explicit, baseline-backed, holdout-defined,
factory-supported, and prospectively frozen through selected registry entries,
but it has not yet reached a future-measurement reveal.

Start here:

- [Nuclear Mass Campaign Plan](../notes/nuclear-mass-campaign-plan.md)
- [Nuclear Prediction Variant Factory](../notes/nuclear-prediction-variant-factory.md)
- [Selected Factory Registry Wave 001](../reviews/nuclear-prediction-factory-selected-registry-001.md)
- [Nuclear Prediction Reveal Protocol](../nuclear-prediction-reveal-protocol.md)
- [TASK-0264](../../tasks/TASK-0264-run-nuclear-feature-term-factory-slate.yaml)
- [TASK-0266](../../tasks/TASK-0266-define-nuclear-prediction-reveal-readiness-protocol.yaml)

## Open Questions

- Which feature-term slate-002 candidates add review value beyond the
  coefficient-transform `PRED-0041` through `PRED-0050` wave?
- Which target batches best expose shell, neutron-rich, isotope-chain, and
  mass-region behavior without creating leakage or false precision?
- How should a future reveal task handle partial measurement availability
  while preserving the no-peek boundary?
- Which existing manual blocked lanes should remain fallback references versus
  being represented only through factory slates?

## Recommended Tasks

- `TASK-0264` — run a feature-term factory slate using shell, magic-number,
  neutron-excess, and combined coefficient-plus-feature variants.
- `TASK-0265` — keep blocked until slate-002 is reviewed, then register only a
  selected feature-term subset as prospective predictions.
- `TASK-0266` — define reveal protocol before any future
  measurement comparison; after this lands, future reveal tasks should use
  the protocol checklist instead of ad hoc source comparison.
- Keep broad `TASK-0178` blocked until the narrower factory and reveal
  protocol work is reviewed.

## Recommended Contributor Types

- nuclear-data curators;
- scientific software contributors who like schema and parser work;
- benchmark designers comfortable with baselines and subset metrics;
- reviewers focused on overclaim resistance and experimental provenance.

## What Not To Claim

- Do not say APL found a nuclear mass formula.
- Do not say shell-aware corrections imply new nuclear theory.
- Do not report sandbox fit improvements as canonical benchmark results.
- Do not blur measured values, extrapolated values, and derived targets.
- Do not describe baseline residual maps as evidence of a broader conclusion by
  themselves.
- Do not open public-facing scientific claims before the first baseline and
  residual benchmark exists.

## Visualization Ideas

- nuclide-chart heatmap of baseline residuals once the first benchmark exists;
- shell-closure strip overlays for `N` and `Z` magic-number regions;
- error-by-subset scorecards for isotope chains, neutron-rich subsets, and
  shell neighborhoods;
- campaign flow diagram from pinned dataset -> baseline -> holdout -> sandbox
  pilot -> maintainer review;
- negative-control panel showing one visually plausible correction family that
  fails under holdout.
