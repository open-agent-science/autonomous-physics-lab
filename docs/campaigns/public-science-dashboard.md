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

### Materials Reusable Dataset Seed

**Short version:** APL now has a first reusable-dataset candidate:
`MD-0001`, a Materials Project stable-binary-oxides pilot with 169 rows, CC BY
4.0 attribution, checksum, dataset version, schema guidance, and validator
coverage.

**Why it is interesting:** this is the first concrete evidence trail showing
APL can turn a published/open source into a provenance-rich benchmark dataset
before modeling. It is a dataset artifact, not a claim.

**Limitation:** the rows are computed DFT values from Materials Project, not
experimental measurements. No baseline, residual map, model, material
recommendation, external dataset repository, or DOI exists yet.

**Evidence trail:**

- [Materials Property Residuals campaign page](./materials-property-residuals.md)
- [Materials binary-oxides dataset review](../reviews/materials-binary-oxides-dataset.md)
- [Materials data area](../../data/materials/README.md)
- [Published-source and reusable-dataset standard](../published-source-dataset-standard.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Can a broad-surface `NMD-0003` baseline-family and validation policy make later residual-feature tests interpretable after the first large factory sprint produced no shortlist? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified; residual-free F2 is inconclusive; pairing-asymmetry and magic-parity controls are negative/control-dominated; isotope-chain transfer is mixed and chain-local; `TASK-0517` ran 72 `NMD-0003` candidates with 0 shortlisted; `TASK-0531` showed simple broad-surface refit improves train/full metrics but regresses on validation holdout. | Baseline-family gate, F2 finer-taxonomy preflight, and reveal-source readiness | A source-safe `NMD-0003` baseline-family decision or a pause on same-family factory reruns. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | What materially changed pinned snapshot or coverage gate would justify reopening a bounded residual audit? | Compact-radius was the strongest earlier matched-control diagnostic, but `TASK-0483` found nearest-radius nulls match or beat CK17-style residuals in the highlighted true-mass slices, `TASK-0481` found no benchmark-usable compact-radius host-context axis under the current coarse-bin floor, and `TASK-0515` records `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`. `TASK-0554` packaged the second-snapshot acquisition path. | Execute the second-snapshot source-acquisition gate without residual scoring. | A checksummed second snapshot or a precise acquisition blocker. |
| [Quantum Size Effects](./quantum-size-effects.md) | Can APL build a direct-measurement row dataset before running size-effect baselines? | Calibration-derived rows and source triage exist; `TASK-0490` landed a synthetic digitization fixture, `TASK-0491` records `NEEDS_MAINTAINER_DECISION` before any weaker sandbox benchmark, and `TASK-0556` selects Norris-Bawendi 1996 as the strongest direct-source path. | Deterministic Norris-Bawendi digitization preflight. | A source-safe extraction package/blocker, not model metrics. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Can high-precision frequency-ratio data become a benchmark surface without hiding covariance or source-version risk? | Beloy 2021 is pinned as sandbox-only `ACR-0001`; a PSD source-derived covariance approximation exists; the real-row loader and synthetic cross-source dry-run have landed; Beloy row roles are assigned; Nemitz remains row-blocked. | Pin or reject Pizzocaro as a second Yb/Sr source, then run row-admissibility if it clears. | A source/covariance readiness package that says whether a first narrow Yb/Sr consistency benchmark can become legitimate later. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Campaign scaffold and ranked candidate slate exist; Stefan-Boltzmann and Wien have exact-reference fixtures; Stellar M-L has a source/baseline plan, but empirical audits have not run yet. | Exact-reference result preflight plus Stellar M-L pinned-source package. | Either a scoped exact-reference software result preflight or a Stellar M-L source package. |
| [Materials Property Residuals](./materials-property-residuals.md) | Can APL turn open, published materials databases into reusable benchmark datasets and conservative residual maps? | `MD-0001` landed as a first reusable-dataset candidate: 169 stable binary oxides from Materials Project `2025.09.25`, with formation-energy and band-gap axes kept separate, CC BY attribution, checksum, version, validator coverage, holdout manifest, and citation metadata. | First conservative baseline benchmark, then benchmark promotion preflight. | A Materials baseline/residual benchmark over `MD-0001`, not a materials-discovery claim. |

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
  calibration-consistency scope, even though a synthetic digitization fixture
  now exercises the future ledger shape and Norris-Bawendi 1996 has been
  selected as the strongest current direct-source path.
- Atomic has one pinned direct-row seed and a deterministic real-row loader,
  but benchmark readiness is still blocked on a second source or waiver,
  with Pizzocaro currently serving as the next source-artifact gate. Beloy
  row-role assignments and the first-benchmark covariance policy are no longer
  the main blockers.

Next visible artifact: a Norris-Bawendi digitization preflight or blocker for
Quantum, and a Pizzocaro source/admissibility package or blocker for Atomic.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The first recommended empirical slice is Stellar Mass-Luminosity OOD on
Gaia DR3; its source/baseline plan has landed, but it is not an audit run yet.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: a Stellar M-L pinned-source package or an exact-reference
fixture result preflight before any empirical metrics.

### Materials Dataset-To-Benchmark Path

Materials is now the fastest path from dataset artifact to a new benchmark
surface. The first pinned dataset is small by design, openly licensed, validated
in the repo, and now has holdout plus citation metadata. The next public
artifact should be a conservative baseline/residual map, not a model
leaderboard or material recommendation.

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
