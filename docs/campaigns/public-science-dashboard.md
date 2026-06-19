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

**Short version:** APL selected the Almeida 2023 InP CC-BY 4.0 source as the
current Quantum Size Effects row path and pinned the article/SI bytes. The
baseline still has not started because the size axis is figure-only and needs a
deterministic digitization/readiness gate.

**Why it is interesting:** the campaign demonstrates source discipline before
attractive modeling. A source blocker is treated as useful output, not as a
failure.

**Limitation:** there is no quantum-dot size-effect benchmark result yet. The
current evidence is source readiness, not model performance.

**Evidence trail:**

- [Quantum Size Effects campaign page](./quantum-size-effects.md)
- [Quantum direct-source candidate brief](../source-candidates/quantum/quantum-direct-source-candidate-brief.md)
- [Quantum Almeida deterministic source-artifact package](../reviews/quantum-almeida-2023-deterministic-source-artifact-package.md)
- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)

### Textbook Formula Audit Scaffold

**Short version:** APL is preparing a campaign to audit famous textbook
formulas by source, range, assumptions, and out-of-distribution failure maps.
It now has a Gate-B-validated exact-reference software/convention result and a
first Stellar M-L empirical lane with committed DEBCat rows, stage/split/null
controls, baseline-adequacy evidence, and an agent-published scoped benchmark
(`RESULT-0022`) awaiting Gate B replay.

**Result capsule — RESULT-0022 (Stellar mass-luminosity, DEBCat):**

- **Source:** DEBCat detached eclipsing binaries (Southworth 2015), CC BY 4.0 by explicit grant (`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`); direct dynamical masses; raw `debs.dat` not committed (Route 2). Frozen main-sequence 0.5–2.0 Msun slice (223 components).
- **Command:** `python3 scripts/replay_stellar_ml_result.py --check` (an engine-workflow `physics-lab run` regeneration path is in review via TASK-0799).
- **Primary metric:** textbook single exponent α=3.5 holdout MAE **0.184954 dex** beats the per-mass-band null (0.331817) but is inadequate as the sole baseline — train-fitted α≈4.53 (**0.119925**) and piecewise α=4.0 (0.137608) are materially better (gaps 0.065 / 0.047 dex > 0.04 dex split-noise). Positive in 5/5 seeded splits; beats luminosity-shuffle controls.
- **Review tier:** `AGENT_PUBLISHED` (agent-published; not yet independently validated or maintainer-reviewed).
- **Gate A:** PASS (9/9). **Gate B:** replay pending — the engine-workflow repackaging (TASK-0799) lands the `physics-lab run` regeneration path, then an independent agent runs Gate B (TASK-0776).

**Why it is interesting:** it is an accessible way for many agents to run
bounded, reviewable audits without claiming new laws.

**Limitation:** no empirical textbook formula claim has been promoted. The
first formula tasks include exact-reference fixtures and a Stellar M-L scoped
benchmark, not universal validation or falsification. `RESULT-0022` is
agent-published, not independently validated or maintainer-reviewed. The current
Stellar M-L evidence supports only a scoped benchmark statement: fixed `M^3.5`
is inadequate as the sole baseline for the committed DEBCat slice; it is not a
universal law claim.

**Evidence trail:**

- [Textbook Formula Audit campaign page](./textbook-formula-audit.md)
- [Stellar M-L luminosity provenance and storage route](../reviews/stellar-ml-luminosity-provenance-and-license-route.md)
- [Stellar M-L Route 2 local benchmark](../reviews/stellar-ml-route2-local-benchmark.md)
- [Stellar M-L promotion-readiness scorecard](../reviews/stellar-ml-route2-promotion-readiness-scorecard.md)
- [Stellar M-L stage-control and split-sensitivity audit](../reviews/stellar-ml-route2-stage-control-split-audit.md)
- [Stellar M-L baseline-adequacy audit](../reviews/stellar-ml-route2-baseline-adequacy.md)
- [Stellar M-L DEBCat full dataset publication](../reviews/stellar-ml-debcat-full-dataset-publication.md)
- [Stellar M-L RESULT-0022 report](../../results/EXP-0015/RUN-0001/report.md)
- [Stellar M-L RESULT-0022 Gate A report](../../results/EXP-0015/RUN-0001/gate_a_report.md)
- [Stellar M-L result routing](../reviews/stellar-ml-debcat-result-routing.md)
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
found the ordering split-fragile. The wider MD-0002 formation-energy retest has
now been packaged as `RESULT-0021`, an `AGENT_VALIDATED` computed-DFT
benchmark that is regenerable end-to-end via `physics-lab run` and replayed
independently in Gate B with zero numeric drift.

**Result capsule — RESULT-0021 (Materials MD-0002 formation energy):**

- **Source:** The Materials Project, CC BY 4.0, computed-DFT stable ternary-oxide slice (`data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`), frozen 362-row holdout-split slice.
- **Command:** `python3 -m physics_lab.cli run examples/materials_md0002_formation_energy_benchmark.yaml` (quick check: `python3 scripts/replay_materials_md0002_result.py --check`).
- **Primary metric:** exact cation-pair mean baseline holdout MAE **0.200606 eV/atom** vs global-median null **0.506092** (60.4% lower); winner in 5/5 seeded splits; beats label-shuffle and cation-label-shuffle nulls.
- **Review tier:** `AGENT_VALIDATED` (agent-published result independently replayed by a different agent; not maintainer-endorsed knowledge).
- **Gate A:** PASS (9/9). **Gate B:** PASS on a Codex independent replay (42 numeric fields compared, max absolute drift 0.0; TASK-0775).

**Why it is interesting:** this is the first concrete evidence trail showing
APL can turn a published/open source into a provenance-rich benchmark dataset
before modeling, and regenerate the result deterministically for independent
replay. It is a dataset/benchmark artifact, not a claim.

**Limitation:** the rows are computed DFT values from Materials Project, not
experimental measurements. This is not a material recommendation, synthesis
guide, device claim, biomedical claim, promoted result, external dataset
repository, DOI, or promoted materials claim.

**Evidence trail:**

- [Materials Property Residuals campaign page](./materials-property-residuals.md)
- [Materials binary-oxides dataset review](../reviews/materials-binary-oxides-dataset.md)
- [Materials MD-0001 baseline benchmark](../reviews/materials-md0001-baseline-residual-benchmark.md)
- [Materials MD-0001 independent replay](../reviews/materials-md0001-independent-baseline-replay.md)
- [Materials MD-0001 formation-energy null-control audit](../reviews/materials-md0001-formation-energy-null-control-audit.md)
- [Materials MD-0001 split-sensitivity audit](../reviews/materials-md0001-split-sensitivity-audit.md)
- [Materials MD-0001 promotion preflight](../reviews/materials-md0001-benchmark-promotion-preflight.md)
- [Materials MD-0002 RESULT-0021 report](../../results/EXP-0014/RUN-0001/report.md)
- [Materials MD-0002 RESULT-0021 Gate A report](../../results/EXP-0014/RUN-0001/gate_a_report.md)
- [Materials MD-0002 RESULT-0021 Gate B replay](../reviews/materials-md0002-result0021-gate-b-replay.md)
- [Materials MD-0002 result routing](../reviews/materials-md0002-formation-energy-result-routing.md)
- [Materials data area](../../data/materials/README.md)
- [Published-source and reusable-dataset standard](../published-source-dataset-standard.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | Does the selected Wigner-cusp non-F2 lane survive controls while reveal scoring stays blocked? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified; `RESULT-0018` is AGENT_VALIDATED and preserved as diagnostic/inconclusive memory; Wigner-cusp is the selected next lane. | `TASK-0777` Wigner-cusp sprint and `TASK-0778` value-blind reveal-source preflight. | A Wigner-cusp sandbox verdict or reveal-source blocker, not a reveal score. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | What material snapshot or source-version change would justify reopening residual scoring? | Current-snapshot residual stress is control-sensitive; `EXO-0002` did not clear the reopen gate, so CK17 replay was not run. The closed-lane decision is preserved as negative/control memory. | Metadata-only source-version monitoring. | A `NO_NOTIFY` or NOTIFY-class monitor decision, not a residual score. |
| [Quantum Size Effects](./quantum-size-effects.md) | Can APL build direct Almeida InP size/energy rows before running size-effect baselines? | Calibration-derived rows remain excluded; Almeida 2023 is now license-confirmed and checksum-pinned, with the optical-energy axis recorded. | Almeida size-axis digitization and row-readiness gate (`TASK-0755`). | Direct rows plus readiness rerun, or a precise digitization blocker; not model metrics. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | What source or aggregation route can reduce the current two-row, Nemitz-dominated Yb/Sr blocker? | Beloy 2021 and Nemitz 2016 support a narrow exploratory Yb/Sr diagnostic: `|z| = 1.78`, consistent within a predeclared 2-sigma threshold, but two-row and source-limited; this is now preserved as a memory card. | One source/aggregation reopen scout; no metric rerun. | A `REOPEN_READY`, `SOURCE_BLOCKED`, or `DO_NOT_REOPEN` route decision, not constants-drift metrics. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Stefan-Boltzmann has a Gate-B-validated exact-reference software/convention result; Stellar M-L now has AGENT_PUBLISHED `RESULT-0022`. | Gate B replay for `RESULT-0022` and DEBCat scope-flag reconciliation. | A Gate-B-validated Stellar M-L result or precise contested replay blocker. |
| [Materials Property Residuals](./materials-property-residuals.md) | Can APL turn open, published materials databases into reusable benchmark datasets and conservative residual maps? | `MD-0001` landed as a first reusable-dataset candidate; formation energy survives controls and is split-robust; band gap is split-fragile; `MD-0002` is `AGENT_VALIDATED` as `RESULT-0021` after an independent zero-drift Gate B replay. | Post-validation transfer/generalization controls for `RESULT-0021`. | A control audit showing what transfers beyond the frozen split, or a precise blocker; not a material recommendation. |

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
doing source hygiene before metrics or promotion. The visible result right now
is the data gate itself: which sources are strong enough to support a
benchmark, and which ones are not.

Why it matters:

- Quantum now has Almeida 2023 as the selected source path. The article/SI are
  checksum-pinned and license-confirmed; size-axis digitization is the blocker
  before direct rows and the readiness gate can run.
- Atomic has Beloy and Nemitz Yb/Sr rows and a first exploratory cross-source
  diagnostic preserved as a source-limited consistency-memory card. The next
  artifact is a source/aggregation route decision; new benchmark metrics wait
  for a better absolute Yb/Sr source or aggregation contract.

Next visible artifact: an Almeida size-axis digitization/readiness decision for
Quantum, and an Atomic source/aggregation route decision.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The exact-reference fixture lane has one AGENT_VALIDATED result. The
first empirical slice is Stellar Mass-Luminosity through DEBCat direct
dynamical masses; it now has stage/split/null controls, baseline-adequacy
evidence, the full committed DEBCat dataset, and AGENT_PUBLISHED RESULT-0022.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: a Gate B Stellar M-L replay result or a precise
contested replay blocker; no universal formula claim.

### Materials Dataset-To-Benchmark Path

Materials is now a fast path from dataset artifact to a new benchmark surface.
The first pinned dataset is small by design, openly licensed, validated in the
repo, and now has holdout, citation metadata, a first conservative baseline
benchmark, independent replay, a do-not-promote decision, formation-energy null
controls, and split-sensitivity evidence. Formation energy is the stronger
axis; band gap stays diagnostic and split-fragile. `MD-0002` is now acquired,
validated, holdout-frozen, formation-energy benchmarked, and Gate-B-validated
as `RESULT-0021`, so the next public artifact should be a transfer or
generalization control, not a model leaderboard or material recommendation.

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
