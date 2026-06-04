# Public Science Dashboard

This page is the public campaign monitor for APL. It is meant for scientists,
technical contributors, and curious readers who want to see what each active
campaign is testing, what has already been learned, what is blocked, and which
reviewable result may appear next.

APL does not use this page to announce discoveries. It uses this page to show
the research frontier in a way that is easy to inspect, reproduce, and falsify.

## Shareable Result Cards

These cards are intentionally short and linkable. They are safe for README
summaries, issue comments, social posts, or external discussion because each
card carries its limitation line with the result.

### Exoplanet Null-Baseline Control Panel

**Short version:** On a pinned NASA Exoplanet Archive PSCompPars snapshot, APL
previously highlighted the compact-radius slice (`R < 1.5 R_earth`) as the
strongest matched-control diagnostic in a frozen Chen-Kipping-style mass-
radius failure-map audit. A later null-baseline family audit found that a
simple nearest-radius null matches or beats CK17-style residuals across the
compact, sub-Neptune, Jovian-radius, and hot-Jupiter true-mass slices.

**Why it is interesting:** this is a clear, visual benchmark surface:
mass-radius baseline, residual map, matched controls, deterministic replay,
null baselines, and explicit forbidden wording.

**Limitation:** this is not a planet-composition, habitability, or new
mass-radius-law claim. The current scorecard verdict is
`BENCHMARK_SUMMARY_ONLY`. The control-aware synthesis preserves the apparent
compact-radius residual stress as negative/control memory and does not open
another residual pilot on the current snapshot.

**Evidence trail:**

- [External-reviewer replication capsule](../results/exoplanet-external-reviewer-replication-capsule.md)
- [Compact-radius benchmark evidence card](../results/exoplanet-compact-radius-benchmark-card.md)
- [Exoplanet failure-map result-promotion scorecard](../reviews/exoplanet-failure-map-result-promotion-scorecard.md)
- [Exoplanet null-baseline family audit](../reviews/exoplanet-null-baseline-family-audit.md)
- [Compact/sub-Neptune matched-control audit](../reviews/exoplanet-compact-subneptune-matched-control-audit.md)
- [Independent compact-radius replay](../reviews/exoplanet-compact-radius-independent-replay.md)
- [Exoplanet campaign page](./exoplanet-mass-radius.md)

### Nuclear Local-Curvature Falsification

**Short version:** APL tested a promising Nuclear local-curvature residual
candidate under a bounded no-leakage prototype and falsified it.

**Why it is interesting:** the negative result is useful scientific memory:
it blocks a tempting residual-feature lane from being repeated or promoted
without controls.

**Limitation:** this does not validate or falsify any broad nuclear mass law.
Reveal scoring remains blocked until a future source-grade no-peek release.

**Evidence trail:**

- [Nuclear negative-result evidence card](../reviews/nuclear-negative-result-evidence-card.md)
- [Nuclear local-curvature no-leakage prototype review](../reviews/nuclear-local-curvature-no-leakage-prototype.md)
- [Residual-free high-error cluster audit](../reviews/nuclear-residual-free-high-error-cluster-hypothesis-audit.md)
- [Nuclear residual-law factory sprint review](../reviews/nuclear-residual-factory-sprint.md)
- [Nuclear Mass Surface campaign page](./nuclear-mass-surface.md)

### Quantum Direct-Measurement Data Gate

**Short version:** APL has not started the Quantum Size Effects baseline
because the committed rows are calibration-derived rather than direct
measurement rows.

**Why it is interesting:** the campaign demonstrates source discipline before
attractive modeling. A source blocker is treated as useful output, not as a
failure.

**Limitation:** there is no quantum-dot size-effect benchmark result yet.

**Evidence trail:**

- [Quantum Size Effects campaign page](./quantum-size-effects.md)
- [Quantum direct-source candidate brief](../source-candidates/quantum/quantum-direct-source-candidate-brief.md)
- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)

### Textbook Formula Audit Scaffold

**Short version:** APL is preparing a campaign to audit famous textbook
formulas by source, range, assumptions, and out-of-distribution failure maps.

**Why it is interesting:** it is an accessible way for many agents to run
bounded, reviewable audits without claiming new laws.

**Limitation:** no empirical textbook formula audit has run yet. The first
formula tasks are exact-reference fixtures and source/baseline planning, not
universal validation or falsification.

**Evidence trail:**

- [Textbook Formula Audit campaign page](./textbook-formula-audit.md)
- [Candidate slate](../notes/textbook-formula-audit-candidate-list.md)

### Materials Reusable Dataset And First Baseline

**Short version:** APL now has a first reusable-dataset candidate and first
baseline benchmark: `MD-0001`, a Materials Project stable-binary-oxides pilot
with 169 rows, CC BY 4.0 attribution, checksum, dataset version, schema
guidance, and validator coverage. The first conservative benchmark finds that
simple composition-aware baselines help formation energy more clearly than
band gap.

**Why it is interesting:** this is the first concrete evidence trail showing
APL can turn a published/open source into a provenance-rich benchmark dataset
before modeling. It is a dataset artifact, not a claim.

**Limitation:** the rows are computed DFT values from Materials Project, not
experimental measurements. This is not a material recommendation, synthesis
guide, device claim, external dataset repository, or DOI.

**Evidence trail:**

- [Materials Property Residuals campaign page](./materials-property-residuals.md)
- [Materials binary-oxides dataset review](../reviews/materials-binary-oxides-dataset.md)
- [Materials MD-0001 baseline benchmark](../reviews/materials-md0001-baseline-residual-benchmark.md)
- [Materials data area](../../data/materials/README.md)
- [Published-source and reusable-dataset standard](../published-source-dataset-standard.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Can a frozen `NMD-0003` stratified gate make new residual-feature tests interpretable after the first large factory sprint produced no shortlist? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified; `TASK-0517` ran 72 `NMD-0003` candidates with 0 shortlisted; `TASK-0531` showed simple broad-surface refit improves train/full metrics but regresses on validation holdout; `TASK-0552` froze a stratified gate with diagnostic validation MAE `1.899279` MeV. | Independent gate replay, one bounded residual-feature sprint, F2 controls-first scoring, and reveal-source manifest scouting without values. | A replayed `NMD-0003` gate or one controls-first residual-feature verdict, not a reveal score. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | Does the pinned `EXO-0002` snapshot clear the reopen gate for a bounded second-snapshot residual replay? | Current-snapshot residual stress is control-sensitive; `TASK-0565` acquired `EXO-0002` with 6298 raw rows, 4308 post-filter included rows, 2110 true-mass rows, and 985 minimum-mass rows, but no metrics. | Reopen coverage gate, EXO-0001/EXO-0002 delta audit, then baseline replay only if the gate clears. | A second-snapshot coverage/delta decision. |
| [Quantum Size Effects](./quantum-size-effects.md) | Can APL build a direct-measurement row dataset before running size-effect baselines? | Calibration-derived rows and source triage exist; `TASK-0490` landed a synthetic digitization fixture; `TASK-0563` preserved the Norris-Bawendi source-copy/tool-run blocker rather than adding weak rows. | Norris-Bawendi source-copy handoff and Kang-Wise fallback source-artifact package. | A legal source-artifact handoff or blocker, not model metrics. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Can high-precision frequency-ratio data become a benchmark surface without hiding covariance or source-version risk? | Beloy 2021 is pinned as sandbox-only `ACR-0001`; a PSD source-derived covariance approximation exists; the real-row loader and synthetic cross-source dry-run have landed; Beloy row roles are assigned; Pizzocaro source artifacts are pinned, but rows remain blocked. | Pizzocaro row-admissibility gate. | A decision on whether Pizzocaro can become a second Yb/Sr row or remains blocker memory. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Campaign scaffold and ranked candidate slate exist; Stefan-Boltzmann and Wien have exact-reference fixtures; `TASK-0568` preflighted their scoped result route; Stellar M-L has a source/baseline plan. | Scoped exact-reference packaging or blocker, plus Stellar M-L row-readiness. | A scoped exact-reference software result or a Stellar M-L row-readiness gate. |
| [Materials Property Residuals](./materials-property-residuals.md) | Can APL turn open, published materials databases into reusable benchmark datasets and conservative residual maps? | `MD-0001` landed as a first reusable-dataset candidate, and `TASK-0550` ran the first benchmark: formation energy benefits more clearly from composition-aware baselines than band gap. | Promotion preflight, independent replay, and band-gap null-control audit. | A conservative Materials benchmark routing decision, not a materials-discovery claim. |

## What Is Interesting Right Now

### Exoplanet Null-Baseline Check

The exoplanet campaign has the clearest near-term public benchmark story right
now. A frozen Chen-Kipping-style baseline was compared against a pinned NASA
Exoplanet Archive PSCompPars snapshot. The key new result is conservative:
nearest-radius null baselines match or beat the CK17-style baseline in the
previously highlighted true-mass slices.

Why it matters:

- APL has a reproducible exoplanet mass-radius benchmark/failure-map surface.
- The compact-radius diagnostic is now explicitly control-sensitive rather
  than a promoted residual signal.
- Mass-quartile localization and host-context coarse bins are currently
  underpowered. The control-aware synthesis records no-go for another
  current-snapshot residual pilot.
- This is a benchmark-diagnostic signal, not a planet-composition claim.

Scope:

The result does not say that APL found a new exoplanet law, predicts
habitability or planet composition, or globally falsified Chen-Kipping.

Current visible artifact: a null-baseline control audit plus the older compact
evidence card, read together with the scorecard and limitations.

### Nuclear No-Leakage Falsification

The Nuclear campaign remains the flagship validation surface, but its newest
important lesson is negative: `LOCAL-CURVATURE-001` did not survive the
bounded no-leakage prototype. That is useful scientific memory because it
prevents agents from repeating a promising but leakage-sensitive path.

Why it matters:

- APL preserves negative and falsified Nuclear residual-feature lanes.
- The shell-axis lane remains diagnostic-only.
- Reveal scoring remains blocked until a future source-grade no-peek release.

Next visible artifact: a local-curvature result-promotion preflight that records
the falsification as negative/inconclusive memory, reveal-source readiness, or
a genuinely new controls-first lane. The residual-free high-error cluster
audit, neutron-rich boundary transfer, and magic-distance interaction lanes
have all landed as non-positive sandbox memory and should not be treated as
positive near-misses.

### Quantum And Atomic Fresh-Data Gates

Quantum Size Effects and Atomic-Clock Residuals are slower because they are
doing source hygiene before metrics. The visible result right now is the data
gate itself: which sources are strong enough to support a benchmark, and which
ones are not.

Why it matters:

- Quantum is blocked on direct measurement rows or an explicit weaker
  calibration-consistency scope. A synthetic digitization fixture now exercises
  the future ledger shape, and Norris-Bawendi 1996 has been selected and
  preflighted as the strongest current direct-source path, but it still needs
  a legitimate source copy and tool-run handoff before real rows.
- Atomic has one pinned direct-row seed and a deterministic real-row loader,
  but benchmark readiness is still blocked on a second source row or waiver.
  Pizzocaro source artifacts are now pinned; the open question is row-level
  admissibility, ratio orientation, campaign window, and covariance semantics.

Next visible artifact: a Norris-Bawendi source-copy handoff or Kang-Wise
fallback package for Quantum, and a Pizzocaro row-admissibility decision for
Atomic.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The first recommended empirical slice is Stellar Mass-Luminosity OOD on
Gaia DR3; its source/baseline plan has landed, but it is not an audit run yet.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: a scoped exact-reference software result or blocker, or
a Stellar M-L row-readiness gate before any empirical metrics.

### Materials Dataset-To-Benchmark Path

Materials is now the fastest path from dataset artifact to a new benchmark
surface. The first pinned dataset is small by design, openly licensed, validated
in the repo, and now has holdout, citation metadata, and a first conservative
baseline benchmark. The next public artifact should be a promotion/replay/null-
control decision, not a model leaderboard or material recommendation.

Why it matters:

- APL can produce reusable, provenance-rich scientific datasets, not only
  benchmark reports.
- The dataset can later become externally citable once it has a stable version,
  citation/DOI plan, and enough usefulness for other projects.
- Keeping axes separate (formation energy vs band gap, computed DFT vs future
  measured rows) makes future residual maps scientifically reviewable.

Scope:

No external dataset repository or DOI is planned for the current step. The main
repo remains the home for small curated seed datasets, schemas, loaders, tests,
examples, and benchmark configs.
