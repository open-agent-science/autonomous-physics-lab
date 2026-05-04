# Project Status

## Current Stage

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

## Current Goal

Validate APL as verification-first scientific infrastructure through active
campaigns, reproducible benchmark results, and a private contributor workflow
before any public launch decision.

## Current Major Results

- `EXP-0001/RUN-0003` (`RESULT-0004`) — [Pendulum Gauntlet 100](./results/pendulum-gauntlet-100-summary.md):
  100 deterministic candidate formulas tested against the exact pendulum
  reference with explicit leaderboard, diagnostics, and precision audit.
- `EXP-0004/RUN-0004` (`RESULT-0005`) — [Koide charged-lepton reproduction](./results/koide-charged-lepton-reproduction.md):
  a scoped charged-lepton reproduction benchmark using explicit dataset inputs
  and uncertainty-aware comparison.
- `EXP-0005/RUN-0005` (`RESULT-0006`) — [Koide tau holdout](./results/koide-tau-holdout.md):
  a historical holdout-style tau prediction benchmark kept narrow and
  non-explanatory.

These are benchmark results with stored limitations. They are not evidence of
discovery-level physics, complete particle-mass explanation, universal scope,
or symbolic exactness.

## Current Benchmarks / Experiments

- `EXP-0001` — Pendulum Formula Discovery
- `EXP-0002` — Damped Oscillator Regime Verification
- `EXP-0004` — Charged-Lepton Koide Reproduction
- `EXP-0005` — Historical Tau Holdout Prediction

Together these now support two active benchmark surfaces:

- classical-mechanics verification through the pendulum and damped-oscillator
  slices;
- a falsification-first particle-mass relation track with narrow
  charged-lepton benchmarks only.

## Active Scientific Campaigns

- [Pendulum Formula Falsification](./campaigns/pendulum-formula-falsification.md)
  — strongest current measurable result package and the clearest benchmark for
  systematic approximation testing.
- [Particle Mass Relations](./campaigns/particle-mass-relations.md) — active
  falsification-first track with charged-lepton reproduction and tau holdout
  benchmarks, both kept scope-limited.
- [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md)
  — planning-complete quality-floor campaign, implementation pending.
- [Thought-Experiment Consistency](./campaigns/thought-experiment-consistency.md)
  — planning-first analytical consistency campaign with no canonical run yet.

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
- a public narrative that stays verification-first and avoids overclaim.

Current evidence is stronger than before, but the repository is still in gate
validation rather than public-release mode.

## Current Risks

- Pendulum results remain range-limited benchmark evidence, not exact symbolic
  formulas or globally valid claims.
- Koide-track results are numerically interesting but should stay
  falsification-first and non-explanatory.
- The contributor workflow is more mature, but the private pilot still needs
  continued use before public rollout.
- Status, roadmap, and mission-control docs can drift unless task files and
  active-board sync stay current.
- Visual result summaries are still uneven across campaigns, which can make the
  current evidence harder to scan than it should be.
- Public launch pressure could outrun review discipline if result wording and
  release gates are not kept aligned.

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
  and [results/koide-tau-holdout.md](./results/koide-tau-holdout.md) for the
  clearest current result summaries.
