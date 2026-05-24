# Nuclear Mass Surface

## Goal

Build a verification-first nuclear mass campaign around baseline binding-energy
residuals, shell-closure structure, pairing effects, neutron-rich behavior,
and holdout-tested correction hypotheses.

The target is not a universal mass formula. The target is a disciplined
benchmark surface where compact, physically constrained correction terms can be
tested against real dataset structure, subset behavior, and negative controls.

New-reader summary: Nuclear is APL's flagship validation surface, but it is
currently in diagnostic and source-gated mode. The useful work is stress
review, no-peek reveal readiness, domain-limit mapping, and negative-result
preservation, not new broad prediction waves.

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

Fresh source or reveal-adjacent data work should also follow the
[Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md), so source
candidate, pinned artifact, extraction, row curation, baseline readiness, and
benchmark readiness remain separate gates.

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
- `TASK-0288` stress-tests the strongest shell-axis lane and preserves it as
  the current best sandbox signal: the shell-axis candidates survive
  sign-inversion, shuffled-feature, and near-null controls.
- `TASK-0289` stress-tests the asymmetry-frontier lane and keeps it as a
  smaller review surface, with the catastrophic quadratic/cubic neighbor
  preserved as overfit negative evidence.
- `TASK-0294` synthesizes the post-stress evidence into a maintainer decision
  surface: shell-axis advances to target-batch design, asymmetry-frontier stays
  as a review surface, and mid-mass/isotope-chain remains preserved negative
  evidence.
- `TASK-0295` compares agent-designed scout lanes against deterministic
  factory slates and records a mixed operating-model verdict: factory runs are
  better for broad reproducible coverage, while agent scouts add value as a
  review, rejection, adversarial-stress, and negative-result synthesis layer.
- `TASK-0296` designed the conservative `shell-axis-balanced-001` target
  batch.
- `TASK-0297` registers the bounded shell-axis mini-wave as `PRED-0063`
  through `PRED-0068`, with paired candidate, sign-inverted, near-null, and
  baseline-reference controls.
- `TASK-0303` prepared a no-peek source-manifest preflight template for the
  shell-axis mini-wave without recording target mass values.
- `TASK-0304` added a synthetic reveal dry-run using fabricated values only,
  so reveal reporting plumbing can be reviewed without weakening the no-peek
  boundary.
- `TASK-0307` reviewed the first concrete source-manifest attempt and found no
  acceptable pinned post-registration source; this is a useful negative
  readiness result and keeps `TASK-0305` blocked.
- `TASK-0310` adds a sandbox-only full-known retrospective audit for the
  shell-axis family: the three primary shell-axis candidates keep small
  full-known and primary-holdout MAE improvements, while the sign-inverted,
  shuffled-feature, and near-null controls remain conservative.
- `TASK-0315` maps the post-0310 shell-axis validity domain: support is
  concentrated around near-magic, magic-N, mid-mass, neutron-rich, and
  measured/extrapolated comparison subsets, while light `A<50` is an explicit
  regression zone.
- `TASK-0316` stress-tests the post-0310 shell-axis coefficients under
  deterministic leave-one-out and exhaustive 8-of-11 resampling. The result is
  `FRAGILE`: leave-one-out fits preserve the signal, but smaller resamples
  produce coefficient sign flips and some full-known or holdout regressions.
- `TASK-0317` runs specificity controls against the shell-axis lane. The best
  shell-axis candidate remains stronger than smooth-A, asymmetry,
  mass-region, baseline, and deterministic random matched-degree controls on
  full-known and primary-holdout MAE, but smooth-A and asymmetry controls are
  not inert; the verdict is `SHELL_SPECIFIC_BUT_BOUNDED`.
- `TASK-0320` isolates the light `A<50` regression zone and keeps that region
  as a warning zone rather than a positive support surface.
- `TASK-0321` checks whether support is magic-N dominant, magic-Z dominant,
  symmetric, or too sparse to interpret.
- `TASK-0321` records the magic-axis asymmetry audit as
  `NEUTRON_DOMINANT_BUT_SPARSE`: all three primary shell-axis candidates
  improve magic-N more than magic-Z, while double-magic and matched
  double-magic remain sparse diagnostic panels.
- `TASK-0323` and `TASK-0324` add isotope-chain transfer and neutron-rich tail
  audits. They keep the campaign in falsification/domain-mapping mode rather
  than adding more prediction-registry entries.
- `TASK-0333` synthesizes the completed shell-axis post-audit wave and
  recommends `DIAGNOSTIC_ONLY`: preserve shell-axis as sandbox diagnostic
  evidence, but stop additional retrospective shell-axis audits, registry
  expansion, reveal scoring, and claim promotion unless a later
  maintainer-approved source-gated task changes the scope.

Historical context:

- `TASK-0091` scoped a narrower magic-number correction idea.
- the broader campaign now supersedes that narrower framing by making dataset
  semantics, baselines, holdouts, and negative-result handling first-class
  surfaces instead of optional extras.

Current campaign state in one sentence:
the scientific direction is now explicit, baseline-backed, holdout-defined,
factory-supported, and prospectively frozen through selected registry entries,
but it has not yet reached a future-measurement reveal; until a source
manifest is accepted, the safest Nuclear follow-up is retrospective
full-known-data stress review rather than reveal scoring. The first such audit
is now recorded as sandbox evidence in `AGENT-RUN-0018`; reveal scoring remains
blocked.

Start here:

- [Nuclear Mass Blind Prediction Challenge](../challenges/nuclear-mass-blind-prediction.md)
- [Nuclear Mass Campaign Plan](../notes/nuclear-mass-campaign-plan.md)
- [Nuclear Prediction Variant Factory](../notes/nuclear-prediction-variant-factory.md)
- [Selected Factory Registry Wave 001](../reviews/nuclear-prediction-factory-selected-registry-001.md)
- [Feature-Term Factory Slate 002](../reviews/nuclear-prediction-factory-slate-002-feature-terms.md)
- [Feature-Term Selected Registry Wave 001](../reviews/nuclear-prediction-factory-feature-term-selected-registry-001.md)
- [Registry Status After PRED-0062](../reviews/nuclear-prediction-registry-status-after-pred-0062.md)
- [Registry Coverage Audit](../reviews/nuclear-prediction-registry-coverage-audit.md)
- [Synthetic Reveal Dry-Run](../reviews/nuclear-prediction-synthetic-reveal-dry-run.md)
- [Scout Lane Synthesis After PRED-0062](../reviews/nuclear-scout-lane-synthesis-after-pred-0062.md)
- [Adversarial Stress Synthesis After TASK-0289](../reviews/nuclear-adversarial-stress-synthesis-after-0289.md)
- [Shell-Axis Target Batch Design](../reviews/nuclear-shell-axis-registry-target-batch-design.md)
- [Shell-Axis Prospective Mini-Wave Review](../reviews/nuclear-shell-axis-prospective-mini-wave-review.md)
- [Nuclear Scout Evidence Card](../results/nuclear-scout-evidence-card.md)
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
- Does the agent-designed scout process add value beyond the deterministic
  factory/grid path, or should more of this campaign become automated search
  plus human review?
- How should the newly frozen shell-axis mini-wave be handled if a future
  source manifest reveals only a subset of `shell-axis-balanced-001` targets?
- What exact source-manifest, checksum, and no-peek evidence must exist before
  a real reveal comparison is allowed?
- Which future measurement source can satisfy the source-readiness checklist
  without weakening the no-peek boundary?
- Which shell-axis subset regressions should block, limit, or merely annotate
  any future source-gated follow-up after the full-known retrospective audit?
- Do the TASK-0310 shell-axis coefficients remain stable under leave-one-out
  or jackknife stress, or is the signal dominated by one or two training rows?
- Is the light `A<50` regression a true exclusion zone, a baseline-quality
  artifact, or a sparse subset diagnostic?
- Is the strongest shell-axis support driven by neutron magic structure,
  proton magic structure, both, or neither after matched controls?

## Recommended Tasks

- Future reveal tasks should use the `TASK-0266` protocol and the source
  readiness checklist instead of ad hoc source comparison.
- Use the Nuclear scout evidence card as the compact maintainer orientation
  surface for the current shell-axis, asymmetry-frontier, and negative
  mid-mass/isotope-chain evidence.
- Use the adversarial stress synthesis as the maintainer decision surface for
  post-0288/0289 Nuclear scout evidence.
- Use the TASK-0295 comparison before expanding the factory or scout surface:
  keep broad candidate generation in deterministic factory runs, then use
  agent-led triage for bounded adversarial review and negative-result
  packaging.
- Do not score the shell-axis mini-wave until a future source-manifest/no-peek
  reveal task is explicitly approved.
- Use the full-known retrospective audit
  (`docs/reviews/nuclear-shell-axis-full-known-retrospective-audit.md`) as a
  sandbox stress reference before any future shell-axis registry expansion or
  reveal task.
- Use the specificity-control audit
  (`docs/reviews/nuclear-shell-axis-specificity-controls.md`) as bounded
  context: simple non-shell controls do not match the strongest shell-axis
  candidate on the key aggregate surfaces, but they are not fully inert and
  should remain visible in future evidence packages.
- Use the magic-axis asymmetry audit
  (`docs/reviews/nuclear-shell-axis-magic-asymmetry-audit.md`) as bounded
  context: current retrospective support is magic-N dominant, but sparse
  subset warnings and coefficient fragility remain active limitations.
- Keep the current Nuclear executor buffer at several independent READY
  scientific tasks where possible: light-regression, isotope-chain transfer,
  neutron-rich tail behavior, and later source-gated review work can run in
  separate branches/worktrees without sharing write surfaces.
- Use the `TASK-0333` decision synthesis
  (`docs/reviews/nuclear-shell-axis-post-audit-decision.md`) as the current
  shell-axis lane status: `DIAGNOSTIC_ONLY`. Do not add more retrospective
  shell-axis audits unless a maintainer-approved source-gated task changes the
  scope.
- `TASK-0304` exercised shell-axis mini-wave reveal scoring on
  fabricated values only (see
  `docs/reviews/nuclear-shell-axis-mini-wave-synthetic-reveal-dry-run.md`,
  `examples/nuclear_shell_axis_mini_wave_synthetic_reveal.yaml`, and
  `tests/test_nuclear_shell_axis_mini_wave_reveal.py`); per-entry MAE/RMSE,
  candidate-vs-baseline, and candidate-vs-negative-control reporting are
  now pre-reviewed plumbing.
- `TASK-0303` prepared the source-manifest and no-peek preflight for
  `PRED-0063` through `PRED-0068` without recording measured values (see
  `docs/reviews/nuclear-shell-axis-mini-wave-source-preflight.md` and the
  manifest template at
  `data/nuclear_masses/shell_axis_reveal_source_manifest_template.yaml`).
- `TASK-0307` should prepare one concrete source-manifest candidate for the
  shell-axis mini-wave without recording target mass values or scoring the
  registry entries.
- `TASK-0307` currently records a metadata-only source-manifest review outcome:
  no acceptable source candidate was prepared, so `TASK-0305` remains blocked
  behind a future pinned post-registration source or a separately scoped weaker
  diagnostic task.
- `TASK-0310` should audit the shell-axis signal against the full known
  committed measured-data surface as retrospective sandbox evidence, with
  baseline comparison, subset behavior, and explicit null controls.
- `TASK-0315`, `TASK-0316`, `TASK-0317`, `TASK-0320`, and `TASK-0321` are the
  post-0310 follow-up wave: map the validity domain, test coefficient
  stability, run specificity controls, audit the light-nuclei regression, and
  separate magic-N versus magic-Z behavior before any future shell-axis
  expansion or public evidence package.
- Use the TASK-0315 validity-domain map
  (`docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`) as the
  conservative scope note for shell-axis evidence: treat light `A<50` as a
  regression zone, keep sparse double-magic and registry-repeat-chain-neighbor
  behavior diagnostic-only, and run `TASK-0316` coefficient stability next.
- Use the TASK-0316 coefficient-stability audit
  (`docs/reviews/nuclear-shell-axis-coefficient-stability-audit.md`) before
  any future shell-axis expansion: the lane remains bounded sandbox evidence,
  but coefficient sign flips under exhaustive 8-of-11 resampling block broad
  robustness wording.
- Use the TASK-0321 magic-axis asymmetry audit
  (`docs/reviews/nuclear-shell-axis-magic-asymmetry-audit.md`) as a bounded
  directionality note: the committed retrospective signal is magic-N dominant
  across the three primary shell-axis candidates, but the relevant magic
  subsets remain sparse.
- `TASK-0305` should stay blocked until source preflight, dry-run review, a
  reviewed `TASK-0307` source manifest, and explicit maintainer approval make
  a real reveal comparison legitimate.
- Keep broad `TASK-0178` blocked until the narrower factory and reveal
  protocol work is reviewed.

## New-Lanes Decision After Uncertainty And Adversarial Controls (TASK-0365)

`docs/reviews/nuclear-new-lanes-decision-after-uncertainty.md` is
the maintainer-facing go/no-go for the recent Nuclear hypothesis
wave. Summary:

- **GO** on a no-leakage local-curvature predictive implementation
  for `LOCAL-CURVATURE-001` (only F1-admissible candidate);
- **HOLD diagnostic** on high-error cluster (label refactor
  required before predictive use);
- **STOP** on odd-even shell interaction, deformation proxy, and
  measured/extrapolated boundary (preserved sandbox memory only);
- **HOLD diagnostic** on uncertainty-weighted residual as the
  TASK-0368 F5 anchor.

## Residual-Feature No-Leakage Contract (TASK-0368)

`docs/nuclear-residual-feature-no-leakage-contract.md` is the
cross-family eligibility gate for any future no-leakage predictive
implementation. It classifies the five surfaced residual feature
families (local curvature, high-error cluster, shell axis, source
status, uncertainty-weighted) into predictive-eligible,
diagnostic-only, and blocked, and defines the minimum artifact
checklist any later predictive task must deliver before a
`PRED-XXXX.yaml` entry or reveal-scoring task is opened. The
companion review at
`docs/reviews/nuclear-residual-feature-no-leakage-contract-review.md`
records the rationale and explicit non-goals. Read both before
proposing any Nuclear predictive lane.

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
