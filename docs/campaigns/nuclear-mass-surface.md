# Nuclear Mass Surface

## Goal

Build a verification-first nuclear mass campaign around baseline binding-energy
residuals, shell-closure structure, pairing effects, neutron-rich behavior,
and holdout-tested correction hypotheses.

The target is not a universal mass formula. The target is a disciplined
benchmark surface where compact, physically constrained correction terms can be
tested against real dataset structure, subset behavior, and negative controls.

New-reader summary: Nuclear is APL's flagship validation surface, and it has
now moved from an 11-row bootstrap slice to a source-gated AME2020 measured-row
training surface (`NMD-0003`). The first large Research Factory sprint on that
surface produced control-dominated negative memory with no shortlist. The first
simple broad-surface baseline refit improved train/full-surface metrics but
regressed on the validation holdout. `TASK-0552` then froze a stratified
NMD-0003 readiness split where the region-stratified diagnostic validation
MAE is `1.899279` MeV. `TASK-0583` independently replayed that gate and matched
the frozen metrics exactly after a narrow path-normalization portability fix.
`TASK-0625` then ran the only authorized F2 component-ablation follow-up and
classified the lane as `COMPONENT_DIAGNOSTIC_ONLY`: the full aggregate remains
replayable, but no component clears the survival-margin gate. `TASK-0633`
packaged that memory as `RESULT-0018`, `TASK-0713` independently replayed it
as `AGENT_VALIDATED`, and `TASK-0743` records the do-not-repeat boundary.
`TASK-0746` selected exactly one next non-F2 lane, the Wigner-cusp candidate
`WIGNER-CUSP-001`. `TASK-0777` has now run that bounded sprint and rejected the
candidate as `NEGATIVE_RESULT`: it failed the 0.25 MeV margin against all three
declared controls despite passing leakage and coefficient-stability checks.
The next source-safe Nuclear work is value-blind reveal-source readiness, not a
new Wigner-shape search, broad prediction wave, or another F2 loop.

## Public Monitoring Snapshot

**Current question:** can APL identify a broad-surface `NMD-0003`
baseline-family and validation policy strong enough to justify any new bounded
residual-feature family after the first large factory sprint produced no
control-surviving shortlist and the first simple refit regressed on validation?

**Shareable result:** APL tested `LOCAL-CURVATURE-001`, a promising
local-curvature residual candidate, under a bounded no-leakage prototype and
falsified it. This is useful negative scientific memory, not a failure of the
campaign.

**Not a claim:** APL has not found a nuclear mass formula, has not scored the
frozen prospective registry against future measurements, and should not
describe shell-axis or local-curvature evidence as discovery-level physics.

**Active next work:** `TASK-0507` ran the first Research Factory sprint over
`NMD-0002` and produced no shortlist. `TASK-0516` landed `NMD-0003`: a
source-gated AME2020 measured training surface with 2309 committed rows and
frozen exclusion of the primary post-AME2020 holdout. `TASK-0517` then ran the
first large `NMD-0003` factory sprint: 73 candidates generated, 72 executed, 0
shortlisted, 30 rejected by controls, 42 negative, and 1 data-quality-blocked.
`TASK-0518` preserved the `NMD-0002` uncertainty perturbation lane as
`INCONCLUSIVE` control evidence only. `TASK-0531` froze a first broad-surface
baseline refit and found a useful blocker: train/full-surface MAE improved, but
validation-holdout MAE regressed.

**Expected next decision:** F2 and Wigner-cusp no longer need another hypothesis burst or
publication preflight. `TASK-0633` packaged F2 as diagnostic `RESULT-0018`, and
`TASK-0713` replayed it through Gate B without changing the `INCONCLUSIVE`
scientific verdict. `TASK-0777` rejected the selected Wigner-cusp lane under
its controls-first contract. The next useful Nuclear path is to test whether
any value-blind source manifest can satisfy reveal-readiness without scoring
frozen predictions. Reveal scoring remains source-gated.

## Orientation Note for New Contributors

This campaign started scaffold-first and now has a benchmark stack,
retrospective time-split evidence, a deterministic prediction factory, reusable
target batches, and frozen prospective prediction registry entries.

Safe contributions right now are still conservative, and should now emphasize
post-registry stress review, reveal readiness, and evidence packaging:

- campaign map and guardrail wording;
- pinned-dataset and provenance expansion work;
- source-gated `NMD-0003` factory sprint work;
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
- do not run another large Nuclear factory sprint on `NMD-0002` as if it were
  an independent training surface.

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
- `TASK-0368` locks the residual-feature no-leakage contract. Only explicitly
  classified families may enter a future predictive implementation task, and
  source-status features are permanently blocked from predictive use.
- `TASK-0365` synthesizes the post-uncertainty Nuclear lanes. The strongest
  remaining signal is `LOCAL-CURVATURE-001`, which receives a guarded **GO**
  only for a future no-leakage implementation task. High-error cluster work is
  held diagnostic until labels are rebuilt from residual-free Z/N/A features.
  Odd-even shell interaction, deformation proxy, and measured/extrapolated
  boundary lanes are stopped as negative or control-dominated evidence.
- `TASK-0394` implements the no-leakage local-curvature prototype and
  falsifies `LOCAL-CURVATURE-001` under the bounded no-leakage/control panel.
  The candidate regresses full-known MAE (+0.019599 MeV), loses to the
  strongest no-leakage control, and has subset win-rate 0.000. This supersedes
  the earlier guarded implementation GO as a positive path and should be
  preserved as negative/inconclusive memory through `TASK-0428`.
- `TASK-0448` defines the controls-first Nuclear hypothesis gauntlet. Future
  Nuclear lanes must predeclare allowed/forbidden inputs, at least two negative
  controls, leakage checks, stop conditions, and output routing before fitting.
- `TASK-0449` runs the residual-free high-error cluster audit. The setup is
  no-leakage compliant, but the current NMD-0002 training slice has only one
  cluster with at least two training rows, so the lane lands at
  `INCONCLUSIVE`; the candidate also regresses full-known MAE by about
  1.2 MeV versus the frozen baseline and controls. F2 stays diagnostic-only.
- `TASK-0450` runs the neutron-rich boundary transfer lane and records a
  negative result: the compact boundary candidate regresses the primary
  holdout and full-known surfaces, improves only 5 of 61 isotope-chain
  transfer checks, and loses interpretability because the sparse neutron-rich
  training rows have opposing residual signs.
- `TASK-0451` runs the magic-distance interaction control lane and records a
  control-dominated result: the candidate has a small full-known improvement,
  but it fails the predeclared survival margin and is matched by a
  deterministic same-degree random control, so it does not support a
  shell-specific follow-up.
- `TASK-0474` runs the pairing-asymmetry interaction control lane and records
  a negative result: the candidate regresses the frozen full-known baseline
  and does not justify a follow-up formula lane.
- `TASK-0475` runs the magic-parity boundary control lane and records a
  negative/control result: the candidate regresses the frozen full-known
  baseline and should not be treated as a shell-specific near-miss.
- `TASK-0476` runs isotope-chain leave-family-out transfer and records a mixed
  chain-local result: shell-axis variants improve some chains but regress a
  comparable or larger number of chains, blocking broad transfer wording.
- `TASK-0479` reviews whether the 11-row `NMD-0002` training slice can be
  expanded safely and records `BLOCKED_FOR_SOURCE_SAFE_EXPANSION`: the broader
  AME2020 measured-row training table is not yet committed, and the existing
  `post_ame2020_holdout.yaml` surface must remain holdout/time-split evidence,
  not training data.
- `TASK-0504`, `TASK-0505`, and `TASK-0506` establish the bounded Research
  Factory layer: reusable protocol, `factory_summary` schema, shared runner,
  and first Nuclear adapter.
- `TASK-0507` runs the first Nuclear residual-law factory sprint on
  `NMD-0002`: 73 candidates generated, 72 executed, 0 shortlisted. The result
  is strong negative / underpowered memory, not a formula discovery.
- `TASK-0516` lands `NMD-0003`, a source-gated AME2020 measured-row training
  surface with 2309 committed training rows, a pinned source checksum, and a
  frozen split manifest that keeps primary post-AME2020 holdout nuclides out of
  training.
- `TASK-0517` runs the first large `NMD-0003` Research Factory sprint and
  records control-dominated negative memory: 73 generated candidates, 72
  executed, 0 shortlisted, and strongest apparent gains rejected by matched
  random-slice controls.
- `TASK-0518` runs the `NMD-0002` uncertainty perturbation control and keeps
  all tracked candidates `INCONCLUSIVE`; perturbation survival is not promotion
  evidence.
- `TASK-0531` freezes the first broad-surface `NMD-0003` baseline refit and
  records an `INCONCLUSIVE` benchmark result: train/full-surface MAE improves,
  but validation-holdout MAE regresses, so it is not a promotable baseline
  improvement.
- `TASK-0552` freezes the current stratified NMD-0003 readiness gate:
  1617 train rows, 692 validation rows, and region-stratified diagnostic
  validation MAE `1.899279` MeV. This is now the validation contract for
  bounded follow-up scoring, not a discovery result.
- `TASK-0569` packages the first NMD-0003 factory sprint as negative/control
  memory: 72 executed candidates, no shortlist, and apparent gains blocked by
  controls.

Historical context:

- `TASK-0091` scoped a narrower magic-number correction idea.
- the broader campaign now supersedes that narrower framing by making dataset
  semantics, baselines, holdouts, and negative-result handling first-class
  surfaces instead of optional extras.

Current campaign state in one sentence:
the scientific direction is now explicit, baseline-backed, holdout-defined,
factory-supported, and prospectively frozen through selected registry entries,
but it has not yet reached a future-measurement reveal. The safest Nuclear
follow-up is now a baseline-family and split/domain gate over `NMD-0003`
before more expressive factory families. The `NMD-0002` and `NMD-0003` factory
sprints are preserved as negative/control memory in `AGENT-RUN-0052` and
`AGENT-RUN-0053`; the first broad-surface refit is preserved as inconclusive
sandbox benchmark evidence in `AGENT-RUN-0055`; the stratified gate is frozen
for bounded follow-up; reveal scoring remains blocked.

Current next Nuclear posture:

- Treat `TASK-0517` as completed control-dominated negative memory. Do not run
  the same `NMD-0003` factory sprint again without a new baseline or a new
  maintainer-approved feature family.
- Treat `TASK-0518` as completed `NMD-0002` control evidence. Uncertainty
  perturbations of the same 11 rows are not independent evidence for a residual
  law.
- Treat `TASK-0552` as the current NMD-0003 gate. `TASK-0583` has independently
  replayed it with matching metrics, so bounded residual-feature scoring can
  proceed against that gate rather than selecting a validation policy after
  seeing candidate behavior.
- F2 finer-taxonomy controls-first scoring, replay, component ablation, and
  diagnostic publication have now run. Treat `RESULT-0018` as validated
  diagnostic/negative memory, not as a reason for another F2 loop.
- `TASK-0585` found no admissible post-freeze reveal source. Keep reveal
  scoring blocked until a source postdating the 2026-05-20 freeze is pinned
  without exposing target values.
- `TASK-0428` should run the result-promotion preflight mainly to preserve the
  `LOCAL-CURVATURE-001` no-leakage falsification and block positive promotion
  unless the scorecard exposes a very narrow, reviewed negative-result
  publication artifact.
- `TASK-0449` has now tested the first residual-free high-error cluster
  taxonomy and landed `INCONCLUSIVE` because the current training slice is too
  sparse for per-cluster leave-one-out evaluation. Do not repeat the same
  taxonomy as another near-miss; `RESULT-0018` now keeps the current F2
  contract diagnostic-only unless a future maintainer-approved source or
  baseline contract changes the scientific question.
- `TASK-0396` should keep reveal-source readiness separate from every
  retrospective audit. No real reveal scoring is allowed until a source-grade
  post-freeze release passes the no-peek source gate.
- `TASK-0448` through `TASK-0451` reopened Nuclear hypothesis testing in a
  controls-first form: one reusable hypothesis gauntlet plus three bounded
  parallel lanes. `TASK-0449` is preserved as inconclusive evidence,
  `TASK-0450` as negative transfer/matched-control evidence, and `TASK-0451`
  as control-dominated magic-distance evidence. `TASK-0474` and `TASK-0475`
  extend that negative/control memory, while `TASK-0476` makes shell-axis
  transfer explicitly mixed and chain-local. These are not broad formula-search
  tasks and they did not create prediction entries, reveal scores, claims, or
  canonical results.
  The gauntlet template lives at
  [`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`](../notes/nuclear-controls-first-hypothesis-gauntlet.md);
  future Nuclear lanes should reuse it only when the proposed feature family
  is materially disjoint from the completed negative/control-dominated lanes.

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
- TASK-0272
- TASK-0273
- TASK-0274
- TASK-0278
- TASK-0279
- TASK-0280
- TASK-0285

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
- After `TASK-0394`, what is the cleanest negative/inconclusive artifact for
  the local-curvature lane, and what wording prevents future agents from
  repeating it as a positive candidate?
- Can a finer residual-free high-error cluster taxonomy or larger curated
  training slice ever make F2 testable, or should the current inconclusive
  `TASK-0449` result keep that lane diagnostic-only?
- Can a broad-surface `NMD-0003` baseline freeze/refit reduce the baseline
  mismatch enough to make later residual-feature testing scientifically
  interpretable?
- Should Nuclear pause new fitting until `TASK-0477`, `TASK-0478`, and
  `TASK-0479` package the latest negative memory, define a finer F2 taxonomy,
  and decide whether the current training slice is large enough for another
  high-error-family test?
- Can any fresh Nuclear hypothesis family survive if the failure condition,
  negative controls, leakage audit, and output routing are declared before
  candidate fitting starts?

## Recommended Tasks

- Run `TASK-0428` before any local-curvature publication or follow-up wording:
  the expected path is negative/inconclusive memory, not positive promotion.
- Treat `TASK-0449` as completed inconclusive sandbox evidence, not as a
  reason to run the same cluster taxonomy again.
- Use the `TASK-0448` gauntlet for every remaining Nuclear hypothesis lane:
  controls, forbidden inputs, leakage checks, and stop conditions must be
  explicit before fitting.
- Treat `TASK-0450` and `TASK-0451` as completed negative/control-dominated
  sandbox memory. Do not offer them as READY work or repeat their feature
  families without a new maintainer-approved rationale.
- Treat `TASK-0474` and `TASK-0475` as additional negative/control memory, and
  `TASK-0476` as mixed chain-local transfer evidence.
- Treat `TASK-0517` as completed control-dominated negative memory; the next
  Nuclear science task should compare baseline families and split/domain
  behavior on `NMD-0003` before another large factory sprint.
- Run `TASK-0583` and `TASK-0584` as the current source-safe Nuclear follow-up
  pair: replay the frozen stratified gate, then test exactly one materially new
  residual-feature family under controls.
- Use `TASK-0746` as the next Nuclear hypothesis-planning step: select exactly
  one materially non-F2 no-leakage lane, with source/data prerequisites,
  negative controls, survival margin, and stop conditions fixed before any
  execution sprint.
- Use `TASK-0585` to scout post-AME2020 reveal source manifests without target
  values. It is reveal-readiness work, not reveal scoring.
- Keep `TASK-0477` and `TASK-0478` useful as negative-result packaging and F2
  taxonomy preflight; do not let them delay the first `NMD-0003` sprint.
- Treat `TASK-0518` as completed sensitivity-control memory on `NMD-0002`; do
  not treat perturbation stability as independent validation data.
- Run `TASK-0396` for reveal-source readiness; keep it independent from
  retrospective model audits and do not score live measurements.
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
the maintainer-facing go/no-go for the recent Nuclear hypothesis wave, but its
local-curvature positive path has now been consumed by the later no-leakage
prototype in `TASK-0394`. Updated summary:

- **SUPERSEDED/FAILED** for the no-leakage local-curvature implementation
  path: `TASK-0394` falsified `LOCAL-CURVATURE-001` under the bounded
  no-leakage/control panel;
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
- Do not say `LOCAL-CURVATURE-001` survived no-leakage validation.
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
