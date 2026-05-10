# Nuclear Mass Surface

## Goal

Build a verification-first nuclear mass campaign around baseline binding-energy
residuals, shell-closure structure, pairing effects, neutron-rich behavior,
and holdout-tested correction hypotheses.

The target is not a universal mass formula. The target is a disciplined
benchmark surface where compact, physically constrained correction terms can be
tested against real dataset structure, subset behavior, and negative controls.

## Orientation Note for New Contributors

This campaign started scaffold-first and now has a first benchmark stack plus
one sandbox-only autonomous pilot.

Safe contributions right now are still conservative, but they can now include
bounded sandbox follow-up work:

- campaign map and guardrail wording;
- pinned-dataset and provenance expansion work;
- subset and holdout curation;
- bounded sandbox follow-up proposals under the frozen `RESULT-0015` baseline;
- limitation notes that keep the campaign conservative.

### What not to implement yet

- do not fetch live datasets into canonical memory without pinned source and
  checksum handling;
- do not mix measured and extrapolated entries without an explicit flag and
  reviewable semantics;
- do not compare against advanced nuclear models before the simple baseline
  path is encoded and understood;
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

This campaign now has an executable first-wave benchmark stack:

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

Historical context:

- `TASK-0091` scoped a narrower magic-number correction idea.
- the broader campaign now supersedes that narrower framing by making dataset
  semantics, baselines, holdouts, and negative-result handling first-class
  surfaces instead of optional extras.

Current campaign state in one sentence:
the scientific direction is now explicit, baseline-backed, holdout-defined,
and proven once through a tightly bounded sandbox autonomy pass.

Start here:

- [Nuclear Mass Campaign Plan](../notes/nuclear-mass-campaign-plan.md)
- [TASK-0166](../../tasks/TASK-0166-create-nuclear-mass-surface-campaign-scaffold.yaml)
- [TASK-0167](../../tasks/TASK-0167-add-ame-nuclear-mass-dataset-loader-and-schema.yaml)

## Open Questions

- Which nuclear mass quantity should become the canonical first target:
  atomic-mass residuals, binding-energy residuals, or a tightly defined
  converted baseline residual?
- Which measured-versus-extrapolated semantics should be required before any
  subset metric is trusted?
- How should shell-closure diagnostics be encoded so they remain interpretable
  instead of turning into decorative fit terms?
- Which subset definitions should be mandatory in the first holdout protocol:
  isotope chains, magic-number neighborhoods, neutron-rich edge sets, or all
  of them?
- When a later curated post-baseline measurement batch exists, how should a
  time-split holdout be added without weakening source discipline?

## Recommended Tasks

- follow-up dataset expansion with pinned AME-style measured rows only;
- maintainer-reviewed decision on whether any `TASK-0170` candidate deserves a
  canonical comparison task;
- narrow queue items from `tasks/microtasks/nuclear-mass-surface.yaml` for
  subset-definition notes, provenance audits, and negative-control planning.

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
