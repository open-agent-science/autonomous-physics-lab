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

Safe contributions right now are still conservative, and should now emphasize
post-registry stress review, reveal readiness, and evidence packaging:

- campaign map and guardrail wording;
- pinned-dataset and provenance expansion work;
- subset and holdout curation;
- registry coverage audits across frozen `PRED-*` entries;
- synthetic reveal dry-runs that use fake data only;
- sandbox-only adversarial stress lanes for the strongest scout families;
- direct reveal-readiness checklists that do not touch live measurements;
- conservative status summaries that separate baseline evidence, sandbox
  evidence, and unvalidated prospective predictions;
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
- `TASK-0264` reviewed feature-term factory slate-002 with 48 sandbox
  candidates, preserving extreme-sensitivity and near-null outcomes as
  review evidence.
- `TASK-0265` registered the selected feature-term factory wave as
  `PRED-0051` through `PRED-0062`.
- `TASK-0266` defined the reveal protocol for future reviewed measurement
  comparisons.
- `TASK-0272` audited registry coverage across 54 committed entries and 213
  target rows, surfacing repeated-target pressure and thin mid-mass coverage.
- `TASK-0273` added a synthetic reveal dry-run harness that exercises partial
  reveal behavior with fabricated toy values only.
- `TASK-0274` summarizes the post-`PRED-0062` evidence state and keeps the
  registry framed as prospective rather than validated.
- `TASK-0285` synthesizes the completed scout lanes and ranks the strongest
  follow-up surface as the shell-axis pair `SHELL-SCOUT-003` plus
  `SHELL-SCOUT-005`, with smaller asymmetry-frontier behavior preserved as a
  secondary review surface.
- `TASK-0286` records a useful negative result for naive mid-mass and
  isotope-chain gap features: all executed candidates regress the primary
  holdout or remain null, so that lane should not be promoted.

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
- [Feature-Term Factory Slate 002](../reviews/nuclear-prediction-factory-slate-002-feature-terms.md)
- [Feature-Term Selected Registry Wave 001](../reviews/nuclear-prediction-factory-feature-term-selected-registry-001.md)
- [Registry Status After PRED-0062](../reviews/nuclear-prediction-registry-status-after-pred-0062.md)
- [Registry Coverage Audit](../reviews/nuclear-prediction-registry-coverage-audit.md)
- [Synthetic Reveal Dry-Run](../reviews/nuclear-prediction-synthetic-reveal-dry-run.md)
- [Scout Lane Synthesis After PRED-0062](../reviews/nuclear-scout-lane-synthesis-after-pred-0062.md)
- [Nuclear Prediction Reveal Protocol](../nuclear-prediction-reveal-protocol.md)
- [Nuclear Reveal Source Readiness Checklist](../nuclear-reveal-source-readiness-checklist.md)
- [TASK-0272](../../tasks/TASK-0272-audit-nuclear-prediction-registry-coverage.yaml)
- [TASK-0273](../../tasks/TASK-0273-add-nuclear-synthetic-reveal-dry-run-harness.yaml)
- [TASK-0274](../../tasks/TASK-0274-summarize-nuclear-prediction-registry-evidence.yaml)
- [TASK-0278](../../tasks/TASK-0278-run-nuclear-shell-neighborhood-variant-scout.yaml)
- [TASK-0279](../../tasks/TASK-0279-run-nuclear-neutron-rich-variant-scout.yaml)
- [TASK-0280](../../tasks/TASK-0280-run-nuclear-pairing-odd-even-variant-scout.yaml)
- [TASK-0285](../../tasks/TASK-0285-synthesize-nuclear-scout-lanes-after-registry-status.yaml)

## Open Questions

- Which registry families are overrepresented or underrepresented after
  `PRED-0062`?
- Which targets or batches are repeated often enough that future reveal
  coverage could be misleading?
- How should a future reveal task handle partial measurement availability
  while preserving the no-peek boundary?
- Which existing manual blocked lanes should remain fallback references versus
  being represented only through factory slates?
- Does the shell-axis pair survive adversarial sign, null, repeated-target,
  and subset-pressure checks?
- Should the smaller asymmetry-frontier signal remain a future review surface
  after explicit stress testing, or be demoted to negative/supporting evidence?
- Which future measurement source can satisfy the source-readiness checklist
  without weakening the no-peek boundary?

## Recommended Tasks

- `TASK-0288` — run a shell-axis adversarial stress scout for
  `SHELL-SCOUT-003` / `SHELL-SCOUT-005`, including sign and null controls.
- `TASK-0289` — run an asymmetry-frontier stress scout with `NR-SCOUT-005` as
  the required overfit negative control.
- `TASK-0290` — package the latest Nuclear scout evidence card for maintainers
  and future communication without discovery framing.
- Future reveal tasks should use the `TASK-0266` protocol and the source
  readiness checklist instead of ad hoc source comparison.
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
- Do not open public-facing scientific claims from prospective registry entries
  before a reviewed future-measurement reveal exists.

## Visualization Ideas

- nuclide-chart heatmap of baseline residuals once the first benchmark exists;
- shell-closure strip overlays for `N` and `Z` magic-number regions;
- error-by-subset scorecards for isotope chains, neutron-rich subsets, and
  shell neighborhoods;
- campaign flow diagram from pinned dataset -> baseline -> holdout -> sandbox
  pilot -> maintainer review;
- negative-control panel showing one visually plausible correction family that
  fails under holdout.
