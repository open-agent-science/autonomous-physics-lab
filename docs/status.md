# Project Status

## Current Stage

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

## Current Goal

Validate APL as verification-first scientific infrastructure through active
campaigns, reproducible benchmark and falsification results, v0.2 packaging
work, and a private contributor workflow before any public-opening decision.

## Current Major Results

- `EXP-0001/RUN-0003` (`RESULT-0004`) — [Pendulum Gauntlet 100](./results/pendulum-gauntlet-100-summary.md):
  100 deterministic candidate formulas tested against the exact pendulum
  reference with explicit leaderboard, diagnostics, and precision audit.
- `EXP-0006/RUN-0006` (`RESULT-0007`) — [Dimensional Analysis Validator MVP](../results/EXP-0006/RUN-0006/report.md):
  a frozen 50-item dimensional-analysis benchmark with 49/50 agreement against
  the curated MVP replay scope under explicit limitations.
- `EXP-0004/RUN-0004` (`RESULT-0005`) — [Koide charged-lepton reproduction](./results/koide-charged-lepton-reproduction.md):
  a scoped charged-lepton reproduction benchmark using explicit dataset inputs
  and uncertainty-aware comparison.
- `EXP-0005/RUN-0005` (`RESULT-0006`) — [Koide tau holdout](./results/koide-tau-holdout.md):
  a historical holdout-style tau prediction benchmark kept narrow and
  non-explanatory.
- `EXP-0007/RUN-0001` (`RESULT-0009`) — [Koide neutrino falsification](./results/koide-neutrino-falsification.md):
  the original Koide relation fails cleanly for physically admissible
  neutrino mass triplets under the encoded oscillation-data assumptions.
- `EXP-0008/RUN-0001` (`RESULT-0010`) — [Quark Koide cascade falsification](../docs/notes/koide-quark-cascade.md):
  the Brannen-style quark cascade remains outside the charged-lepton target in
  both up and down sectors under the stored dataset and scale limitations.
- `EXP-0009/RUN-0001` (`RESULT-0011`) — [Particle-Mass Relation Falsifier MVP](../results/EXP-0009/RUN-0001/report.md):
  a first falsifier workflow applies uncertainty propagation, deterministic
  random-baseline calibration, and a fixed complexity-penalty ledger to the
  standard Koide target across encoded charged-fermion family triplets.
- `EXP-0011` - Anharmonic Oscillator Period Benchmark:
  a deterministic nonlinear period benchmark with perturbative and empirical
  baselines for bounded methodology testing.
- `EXP-0012/RUN-0001` (`RESULT-0015`) - [Nuclear Mass Baseline Residual Benchmark](./results/nuclear-mass-baseline-summary.md):
  a pinned measured-slice nuclear-mass residual benchmark used as a frozen
  baseline for sandbox-only follow-up.
- `AGENT-RUN-0005` - [Nuclear Mass Pilot Summary](./results/nuclear-mass-pilot-summary.md):
  sandbox-only nuclear residual candidate evidence with no claim, knowledge, or
  canonical result promotion.
- `AGENT-RUN-0007` and `AGENT-RUN-0008` - post-AME2020 guard and retrospective
  time-split evidence: `AGENT-RUN-0007` is `INCONCLUSIVE` source-manifest-only
  guard evidence, while `AGENT-RUN-0008` is sandbox-only row-level time-split
  evidence that remains `INCONCLUSIVE`.
- `PRED-0001` through `PRED-0062` - prospective nuclear prediction registry
  entries awaiting future maintainer-reviewed reveal data. The registry now has
  coverage-audit and synthetic reveal dry-run support, but these are frozen
  forecasts, not results or claims.
- [Negative Results Registry](./negative-results-registry.md):
  repository-level index of clean falsifications that should remain visible
  alongside successful reproductions.
- [Scientific Result Quality Rubric](./result-quality-rubric.md):
  maintainer-facing assessment of reproducibility, falsifiability, baseline
  strength, uncertainty handling, and overclaim risk for the current flagship
  surface.

These are benchmark results with stored limitations. They are not evidence of
discovery-level physics, complete particle-mass explanation, universal scope,
or symbolic exactness.

## Current Benchmarks / Experiments

- `EXP-0001` — Pendulum Formula Discovery
- `EXP-0002` — Damped Oscillator Regime Verification
- `EXP-0004` — Charged-Lepton Koide Reproduction
- `EXP-0005` — Historical Tau Holdout Prediction
- `EXP-0006` — Dimensional Analysis Validator MVP
- `EXP-0007` — Neutrino Koide Falsification
- `EXP-0008` — Quark Koide Cascade Falsification
- `EXP-0009` — Particle-Mass Relation Falsifier MVP
- `EXP-0010` — Muon g-2 Formula-Search Stress Test (`INCONCLUSIVE`, kept out
  of the current public-facing success surface)
- `EXP-0011` - Anharmonic Oscillator Period Benchmark
- `EXP-0012` - Nuclear Mass Baseline Residual Benchmark

Together these now support four active benchmark surfaces:

- classical-mechanics verification through the pendulum and damped-oscillator
  slices;
- a falsification-first particle-mass relation track with narrow charged-lepton
  reproductions plus explicit neutrino, quark, and falsifier-MVP negative
  results;
- a dimensional-analysis validation track with one canonical MVP benchmark run
  and a growing challenge-set surface;
- a Nuclear Mass Surface validation track with `EXP-0012`, sandbox-only pilot
  evidence, an `INCONCLUSIVE` `AGENT-RUN-0007` source-manifest guard, and
  retrospective post-AME2020 row-level time-split evidence after `TASK-0196`
  unlocked `TASK-0197`. The prediction registry now adds prospective entries
  for later reveal comparison without treating them as current results.

## Active Scientific Campaigns

- [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md)
  — strongest current measurable result package and the clearest benchmark for
  systematic approximation testing.
- [Particle Mass Relations](./campaigns/particle-mass-relations.md) — active
  falsification-first track with scoped charged-lepton reproduction, a narrow
  tau holdout benchmark, direct neutrino and quark follow-up falsifications,
  and the first fixed-target falsifier MVP.
- [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md)
  — active quality-floor campaign with a completed frozen MVP benchmark and
  follow-on challenge-set curation work.
- [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md)
  — planning-first analytical consistency campaign with no canonical run yet.
- [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) - current
  flagship validation campaign with a frozen baseline residual benchmark,
  sandbox-only autonomous pilot evidence, prospective registry entries through
  `PRED-0062`, and post-AME2020 follow-up guardrails.

## Current Contributor Workflow

APL now has a structured private contributor flow rather than ad hoc local
experimentation.

- canonical task files plus `tasks/ACTIVE.md` as the shared execution surface;
- proposal-first task creation workflow for new ideas that do not yet have a
  maintainer-assigned canonical id;
- active-board sync via `python3 -m physics_lab.cli sync-active-board .`;
- maintainer review and closeout tooling for review bundles, PR hygiene, and
  post-merge task handling;
- private contributor pilot workflow for invited humans and coding agents using
  branch-based task execution and validation.

## Current Public Release Gates

APL remains private until the gates in [public-release-gates.md](./public-release-gates.md)
are satisfied.

Current gate categories:

- technical stability;
- multi-agent or multi-contributor pilot evidence;
- at least one honest measurable scientific result with limitation wording;
- at least one clear falsification surface preserved as first-class evidence;
- a public narrative that stays verification-first and avoids overclaim.

Current evidence is stronger than before, and the repository now has clearer
v0.2 packaging inputs. It is still in gate validation rather than
public-release mode.

Latest review verdict:

- `PUBLIC AFTER NAMED BLOCKERS` - see
  [reviews/v0.2-public-readiness.md](./reviews/v0.2-public-readiness.md)

Current named blockers before any public opening:

- keep the local path leak check clean through release signoff; the
  `TASK-0206` signoff pass found and fixed one public-path wording issue and
  reran the checker cleanly;
- verify the existing external-reviewer replication guide against the current
  flagship evidence surface during release signoff; the `TASK-0206` signoff
  confirms the bounded replay scope and reruns the core reproduction path into
  sandbox output;
- record a release-time default-branch validation and CI signoff artifact; this
  is now captured for maintainer review in
  [public-release-validation-signoff.md](./reviews/public-release-validation-signoff.md).

## Current Risks

- Pendulum results remain range-limited benchmark evidence, not exact symbolic
  formulas or universal-scope claims.
- Koide-track results are numerically interesting but should stay
  falsification-first, dataset-scoped, and non-explanatory.
- Quark and neutrino falsifications are strong within their encoded
  assumptions, but they do not justify broader "Koide is false everywhere"
  claims.
- The falsifier MVP rejects cross-family survival of one fixed standard target
  under encoded charged-fermion triplets; it does not rule out all modified
  Koide-like constructions.
- `EXP-0010` is a high-risk formula-search stress test and should not be
  presented as a public success story without stronger multiple-testing and
  alternate-target guardrails.
- The dimensional-analysis validator has a canonical MVP result, but its unit
  system and known-limit handling remain intentionally narrow.
- Nuclear Mass Surface is the current flagship validation track, but its
  candidate evidence remains sandbox-only. `AGENT-RUN-0007` is only an
  `INCONCLUSIVE` source-manifest guard, and post-AME2020 evaluation is
  retrospective time-split evidence rather than strict blind prediction.
- The contributor workflow is more mature, but the private pilot still needs
  continued use before public rollout.
- Status, roadmap, and mission-control docs can drift unless task files and
  active-board sync stay current.
- Visual result summaries are still uneven across campaigns, which can make the
  current evidence harder to scan than it should be.
- Public launch pressure could outrun review discipline if result wording and
  release gates are not kept aligned.
- Result-quality assessment should remain visible during release review so that
  strong negative results, scoped reproductions, and stress-test outputs are not
  flattened into one public-success narrative.

## Ready Now

- `./scripts/validate_quick.sh`
- `python3 -m ruff check .`
- `python3 -m pytest`
- `python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum`
- `python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped`
- `python3 -m physics_lab.cli validate-repo .`
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`
- `python3 -m physics_lab.cli sync-active-board .`
- [mission-control.md](./mission-control.md) for project-level orientation;
- [campaigns/README.md](./campaigns/README.md) for the campaign map;
- [results/pendulum-gauntlet-100-summary.md](./results/pendulum-gauntlet-100-summary.md)
  for the clearest classical benchmark summary;
- [results/koide-neutrino-falsification.md](./results/koide-neutrino-falsification.md)
  and [negative-results-registry.md](./negative-results-registry.md) for the
  falsification-first particle-mass surface;
- [../results/EXP-0009/RUN-0001/report.md](../results/EXP-0009/RUN-0001/report.md)
  for the first particle-mass relation falsifier MVP;
- [../results/EXP-0006/RUN-0006/report.md](../results/EXP-0006/RUN-0006/report.md)
  for the current dimensional-analysis benchmark result.
- [reproducibility-capsules.md](./reproducibility-capsules.md) for compact
  replay commands, expected metrics, and caveats for the current major
  canonical results.
- [external-reviewer-replication-guide.md](./external-reviewer-replication-guide.md)
  for a short outside-review path from checkout to core replay, strict
  validation, and scoped interpretation.
- [result-quality-rubric.md](./result-quality-rubric.md) for the current
  maintainer-facing assessment of which result surfaces are packaging-ready and
  which need stronger caveats.
- [results/nuclear-mass-pilot-summary.md](./results/nuclear-mass-pilot-summary.md)
  and [nuclear-mass-robustness-gate.md](./nuclear-mass-robustness-gate.md) for
  the current Nuclear Mass Surface evidence and follow-up limits.
