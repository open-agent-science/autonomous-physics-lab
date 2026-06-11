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
- [Quantum Vossmeyer source verification](../reviews/quantum-cds-vossmeyer-source-artifact-verification.md)
- [Quantum Almeida checksum source-artifact blocker](../reviews/quantum-almeida-checksum-source-artifact-package.md)
- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)

### Textbook Formula Audit Scaffold

**Short version:** APL is preparing a campaign to audit famous textbook
formulas by source, range, assumptions, and out-of-distribution failure maps.

**Why it is interesting:** it is an accessible way for many agents to run
bounded, reviewable audits without claiming new laws.

**Limitation:** no empirical textbook formula audit has run yet. The first
formula tasks are exact-reference fixtures and source/baseline planning, not
universal validation or falsification. Stellar M-L now has a luminosity-
provenance policy, but still needs DEBCat storage routing and rows before
metrics.

**Evidence trail:**

- [Textbook Formula Audit campaign page](./textbook-formula-audit.md)
- [Stellar M-L luminosity provenance and storage route](../reviews/stellar-ml-luminosity-provenance-and-license-route.md)
- [Candidate slate](../notes/textbook-formula-audit-candidate-list.md)

### Materials Reusable Dataset And First Baseline

**Short version:** APL now has a first reusable-dataset candidate and first
baseline benchmark: `MD-0001`, a Materials Project stable-binary-oxides pilot
with 169 computed-DFT rows, CC BY 4.0 attribution, checksum, dataset version,
schema guidance, and validator coverage. The first conservative benchmark was
replayed exactly. Formation energy is the clearer diagnostic axis: the
composition-aware cation-group baseline beats global baselines, survives
deterministic null controls, and is split-robust. Band gap is weaker: it
survived the first null-control audit only modestly, and later split-sensitivity
found the ordering split-fragile.

**Why it is interesting:** this is the first concrete evidence trail showing
APL can turn a published/open source into a provenance-rich benchmark dataset
before modeling. It is a dataset artifact, not a claim.

**Limitation:** the rows are computed DFT values from Materials Project, not
experimental measurements. This is not a material recommendation, synthesis
guide, device claim, biomedical claim, promoted result, external dataset
repository, or DOI.

**Evidence trail:**

- [Materials Property Residuals campaign page](./materials-property-residuals.md)
- [Materials binary-oxides dataset review](../reviews/materials-binary-oxides-dataset.md)
- [Materials MD-0001 baseline benchmark](../reviews/materials-md0001-baseline-residual-benchmark.md)
- [Materials MD-0001 independent replay](../reviews/materials-md0001-independent-baseline-replay.md)
- [Materials MD-0001 formation-energy null-control audit](../reviews/materials-md0001-formation-energy-null-control-audit.md)
- [Materials MD-0001 split-sensitivity audit](../reviews/materials-md0001-split-sensitivity-audit.md)
- [Materials MD-0001 promotion preflight](../reviews/materials-md0001-benchmark-promotion-preflight.md)
- [Materials data area](../../data/materials/README.md)
- [Published-source and reusable-dataset standard](../published-source-dataset-standard.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Can bounded residual-feature work produce a robust result after the first large `NMD-0003` factory sprint produced no shortlist? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified; `TASK-0517` ran 72 `NMD-0003` candidates with 0 shortlisted; `TASK-0531` improved train/full metrics but regressed on validation holdout; F2 is diagnostic/inconclusive rather than promoted. | Reveal-readiness reporting, F2/factory result routing, and only tightly bounded controls-first follow-up. | A reveal-readiness matrix or scoped negative/diagnostic result, not a reveal score. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | What material snapshot or source-version change would justify reopening residual scoring? | Current-snapshot residual stress is control-sensitive; `EXO-0002` did not clear the reopen gate, so CK17 replay was not run. The closed-lane decision is preserved as negative/control memory. | Negative/control publication preflight and source-version / `EXO-0003` trigger discipline. | A source-version or negative-memory artifact, not a residual score. |
| [Quantum Size Effects](./quantum-size-effects.md) | Can APL build a direct-measurement row dataset before running size-effect baselines? | Calibration-derived rows and source triage exist; Almeida is source-copy/checksum gated; Vossmeyer 1994 is a promising CdS direct-table candidate but has no committable source artifact yet. | Vossmeyer source-copy handoff and Almeida checksum/reuse decision. | A legal source-artifact package or blocker, not model metrics. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | Can high-precision frequency-ratio data become a benchmark surface without hiding covariance or source-version risk? | Beloy 2021 is pinned as sandbox-only `ACR-0001`; Pizzocaro PSD covariance is useful but row admissibility preserved the aggregation blocker. | Nemitz `ACR-0002` row curation as the primary benchmark-unblock path; Pizzocaro harmonization only as diagnostic fallback. | A second Yb/Sr row gate or baseline-readiness decision, not constants-drift metrics. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Campaign scaffold and ranked candidate slate exist; Stefan-Boltzmann has a Gate-B-validated exact-reference software/convention result; Stellar M-L now has a luminosity-provenance policy and Route 2 storage recommendation. | DEBCat storage route, normalized rows, and then first empirical M-L audit. | A row package or precise blocker before empirical metrics. |
| [Materials Property Residuals](./materials-property-residuals.md) | Can APL turn open, published materials databases into reusable benchmark datasets and conservative residual maps? | `MD-0001` landed as a first reusable-dataset candidate; formation energy survives controls and is split-robust; band gap is split-fragile; `MD-0002` acquisition is now authorized. | Maintainer-gated MD-0002 acquisition, holdout binding, and first formation-energy benchmark. | A pinned MD-0002 dataset and benchmark, not a material recommendation. |

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
  calibration-consistency scope. Almeida 2023 and Vossmeyer 1994 are the most
  useful current source-artifact paths, but neither is row-ready.
- Atomic has one pinned direct-row seed and a deterministic real-row loader,
  but benchmark readiness is still blocked on a second source row. Pizzocaro is
  diagnostic-only after the PSD covariance/readiness pass; Nemitz `ACR-0002`
  is the primary route to a benchmark.

Next visible artifact: an Almeida or Vossmeyer source-artifact package/blocker
for Quantum, and a Nemitz row-curation or baseline-readiness decision for
Atomic.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The first recommended empirical slice is Stellar Mass-Luminosity through
DEBCat direct dynamical masses; its source/baseline and luminosity policy have
landed, but it is not an audit run yet.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: DEBCat storage-route confirmation, a normalized row
package, or a precise blocker before any empirical Stellar M-L metrics.

### Materials Dataset-To-Benchmark Path

Materials is now a fast path from dataset artifact to a new benchmark surface.
The first pinned dataset is small by design, openly licensed, validated in the
repo, and now has holdout, citation metadata, a first conservative baseline
benchmark, independent replay, a do-not-promote decision, formation-energy null
controls, and split-sensitivity evidence. Formation energy is the stronger
axis; band gap stays diagnostic and split-fragile. `MD-0002` acquisition is now
authorized, so the next public artifact should be a pinned wider dataset and
formation-energy benchmark, not a model leaderboard or material recommendation.

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
