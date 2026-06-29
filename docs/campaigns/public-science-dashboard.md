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

**Closed-lane capsule:** mass-quartile localization is underpowered, no
compact-radius host-context axis clears the declared bin floor, `EXO-0002`
failed the frozen reopen gate, and the latest `EXO-0003` monitor returned
`NO_NOTIFY`. Residual scoring remains closed on the unchanged snapshot.

**Reopen condition:** require a materially changed, checksum-pinned snapshot
that clears the per-axis row-count and growth floors, supports any proposed
host-context axis, and beats the nearest-radius null baseline under a
predeclared comparison. A monitor notification triggers review, not automatic
scoring.

**Evidence trail:**

- [External-reviewer replication capsule](../results/exoplanet-external-reviewer-replication-capsule.md)
- [Compact-radius benchmark evidence card](../results/exoplanet-compact-radius-benchmark-card.md)
- [Exoplanet failure-map result-promotion scorecard](../reviews/exoplanet-failure-map-result-promotion-scorecard.md)
- [Exoplanet null-baseline family audit](../reviews/exoplanet-null-baseline-family-audit.md)
- [Compact/sub-Neptune matched-control audit](../reviews/exoplanet-compact-subneptune-matched-control-audit.md)
- [Independent compact-radius replay](../reviews/exoplanet-compact-radius-independent-replay.md)
- [Control-aware no-go synthesis](../reviews/exoplanet-control-aware-go-no-go-synthesis.md)
- [Source-version monitor check 2](../reviews/exoplanet-source-version-monitor-check-2.md)
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
current Quantum Size Effects row path, pinned the article/SI bytes, and
digitized six direct `(edge length, E1s)` rows. `TASK-0225` then produced a
source-scoped sandbox baseline with controls and a one-point holdout.

**Why it is interesting:** the campaign demonstrates source discipline before
attractive modeling. A source blocker is treated as useful output, not as a
failure.

**Limitation:** this is a single-source InP sandbox baseline, not a universal
size-effect law, material recommendation, device-performance result, or
validated cross-material model. The current blocker is baseline-readiness
review plus an independent transfer-source scout.

**Evidence trail:**

- [Quantum Size Effects campaign page](./quantum-size-effects.md)
- [Quantum direct-source candidate brief](../source-candidates/quantum/quantum-direct-source-candidate-brief.md)
- [Quantum Almeida deterministic source-artifact package](../reviews/quantum-almeida-2023-deterministic-source-artifact-package.md)
- [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md)

### Atomic Yb/Sr Consistency Negative Memory

**Short version:** APL pinned two independent direct Yb/Sr frequency-ratio
rows, Beloy 2021 / BACON and Nemitz 2016 / RIKEN, and ran the single
authorized exploratory cross-source diagnostic. The two rows agree at
`|z| = 1.78`, inside the predeclared 2-sigma no-tension threshold.

**Why it is interesting:** this is useful negative/no-tension memory. It says
the first two committed Yb/Sr source rows are consistent within the declared
diagonal-only uncertainty model at the probed precision, so agents should not
rerun the same Beloy/Nemitz two-row metric as a new benchmark task.

**Limitation:** this is a two-row, source-limited diagnostic dominated by the
Nemitz uncertainty. It is not a constants-drift result, a new-constant result,
an anomaly, a prediction, a promoted `RESULT-*`, a `CLAIM-*`, or a `KNOW-*`.
It does not test Beloy's finer precision.

**Reopen condition:** a new independent absolute Yb/Sr source row, or a
maintainer-approved Pizzocaro aggregation/observable-harmonization contract.

**Evidence trail:**

- [Atomic Yb/Sr source-limited consistency memory card](../reviews/atomic-yb-sr-source-limited-consistency-memory-card.md)
- [Atomic Yb/Sr cross-source consistency benchmark](../reviews/atomic-yb-sr-cross-source-consistency-benchmark.md)
- [Atomic Yb/Sr result-path decision](../reviews/atomic-yb-sr-benchmark-result-path-decision.md)
- [Atomic Yb/Sr reopen source-route scout](../reviews/atomic-ybsr-reopen-source-route-scout.md)
- [Atomic-Clock Residuals campaign page](./atomic-clock-residuals.md)

### Anharmonic Oscillator Weak-Regime Evidence

**Short version:** `CLAIM-0009` is maintainer-reviewed as
`PARTIALLY_SUPPORTED` for the configured conservative one-dimensional quartic
oscillator `V(x) = 1/2 k x^2 + lambda x^4` with `lambda >= 0`. The strongest
evidence, `RESULT-0016`, passed an independent Gate B replay with all 36 tracked
metrics reproduced and maximum absolute drift `0.0` at tolerance `1e-9`.

**What the evidence supports:** on the predeclared weak-regime benchmark, the
train-fitted empirical quadratic period correction reached holdout mean
relative error `1.10e-3`, compared with `1.85e-2` for the leading perturbative
baseline. This is bounded benchmark evidence, not an exact formula.

**Limitation:** support is restricted to the configured potential, non-negative
`lambda`, and the tested train/holdout range. The stress slice degrades from
anharmonicity ratio `0.1014`; softening or double-well potentials, damping,
driving, chaos, strong anharmonicity, broad-range validity, and a universal
anharmonic formula are outside scope. `PARTIALLY_SUPPORTED` is the current
ceiling, not `SUPPORTED`.

**Strengthen condition:** stronger wording requires an external replay or a
separate reviewed benchmark covering broader potentials or ranges. Neither
condition is satisfied by the current repository evidence.

**Evidence trail:**

- [CLAIM-0009](../../claims/CLAIM-0009-anharmonic-oscillator-period.md)
- [RESULT-0016 report](../../results/EXP-0011/RUN-0002/report.md)
- [Gate C ratification packet](../reviews/claim-0009-anharmonic-gatec-ratification-packet.md)
- [Anharmonic benchmark summary](../results/anharmonic-oscillator-summary.md)

### Textbook Formula Audit Scaffold

**Short version:** APL is preparing a campaign to audit famous textbook
formulas by source, range, assumptions, and out-of-distribution failure maps.
It now has a Gate-B-validated exact-reference software/convention result and a
first Stellar M-L empirical lane with committed DEBCat rows, stage/split/null
controls, baseline-adequacy evidence, and an `AGENT_VALIDATED` scoped
benchmark (`RESULT-0022`). FIRAS/Wien `RESULT-0023` is now an
AGENT_PUBLISHED spectral-domain self-consistency slice packaged for independent
replay, and Stellar high-mass transfer `RESULT-0024` has independent replay
memory with metadata caveats.

**Result capsule — RESULT-0022 (Stellar mass-luminosity, DEBCat):**

- **Source:** DEBCat detached eclipsing binaries (Southworth 2015), CC BY 4.0 by explicit grant (`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`); direct dynamical masses; raw `debs.dat` not committed (Route 2). Frozen main-sequence 0.5–2.0 Msun slice (223 components).
- **Command:** `python3 -m physics_lab.cli run examples/stellar_ml_debcat_baseline_benchmark.yaml` (quick check: `python3 scripts/replay_stellar_ml_result.py --check`).
- **Primary metric:** textbook single exponent α=3.5 holdout MAE **0.184954 dex** beats the per-mass-band null (0.331817) but is inadequate as the sole baseline — train-fitted α≈4.53 (**0.119925**) and piecewise α=4.0 (0.137608) are materially better (gaps 0.065 / 0.047 dex > 0.04 dex split-noise). Positive in 5/5 seeded splits; beats luminosity-shuffle controls.
- **Review tier:** `AGENT_VALIDATED` (independently replayed; not maintainer-reviewed).
- **Gate A:** PASS (9/9). **Gate B:** PASS. Follow-up controls found the conclusion stable across a small alternate-split slate, while a piecewise baseline is not justified after complexity penalty.

**Why it is interesting:** it is an accessible way for many agents to run
bounded, reviewable audits without claiming new laws.

**Limitation:** no empirical textbook formula claim has been promoted. The
formula tasks include exact-reference fixtures, Stellar M-L scoped benchmarks,
and a FIRAS/Wien self-consistency slice, not universal validation or
falsification. `RESULT-0022` is independently replayed but not
maintainer-reviewed. `RESULT-0023` still needs Gate B replay. `RESULT-0024`
keeps a same-source DEBCat and small-holdout transfer boundary. The current
Stellar M-L evidence supports only scoped benchmark statements; it is not a
universal law claim.

**Result capsule — RESULT-0024 (Stellar high-mass transfer):**

- **Source:** the same committed DEBCat Route 2 component rows used by
  `RESULT-0022`; high-mass holdout is disjoint in mass regime but not an
  independent external catalogue.
- **Primary metric:** frozen `RESULT-0022` relation holdout MAE **0.334564
  dex** versus best control **0.483879 dex**, clearing the predeclared `0.04`
  dex margin by **0.149315 dex** on the stage-matched high-mass holdout.
- **Review status:** AGENT_PUBLISHED result with independent numeric replay
  memory; a metadata caveat remains before stronger tier wording.
- **No-claim wording:** same-source transfer under controls, not a universal
  stellar mass-luminosity law, stellar-structure conclusion, or discovery.

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
- [FIRAS/Wien RESULT-0023 report](../../results/EXP-0016/RUN-0001/report.md)
- [Stellar high-mass transfer RESULT-0024 report](../../results/EXP-0017/RUN-0001/report.md)
- [Stellar high-mass transfer RESULT-0024 replay](../reviews/stellar-result0024-high-mass-transfer-gate-b-replay.md)
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
before modeling, regenerate the result deterministically for independent
replay, and then preserve failed transfer as useful scope memory. It is a
dataset/benchmark artifact, not a claim.

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

### Thermophysical Property Residuals

**Short version:** APL now has a newly active thermophysical-property benchmark
lane. The first slice is ThermoML normal boiling temperature (`Tb`) with a
frozen Joback and Reid group-contribution baseline. `RESULT-0026` is
AGENT_PUBLISHED on a bounded 40-row family-stratified fixture; it is not yet
Gate-B replayed or maintainer-reviewed.

**Result capsule - RESULT-0026 (ThermoML Tb / Joback):**

- **Source:** NIST TRC ThermoML Archive, DOI `10.18434/mds2-2422`, with archive
  checksum and rights boundary recorded in
  `data/thermophysical/source_manifest.yaml`. Raw archive bytes and a
  substantial normalized corpus are not committed.
- **Primary metric:** frozen Joback aggregate MAE **14.925825 K** versus best
  non-oracle aggregate control **43.427943 K**, a **28.502118 K** margin against
  the predeclared `5 K` aggregate threshold.
- **Family survival:** 7 of 8 held-out families clear the survival margin.
  `esters/lactones` fails the family margin and should be treated as
  negative/control memory.
- **Review status:** AGENT_PUBLISHED, Gate A PASS, Gate B not attempted.
- **No-claim wording:** bounded `Tb` transfer on a 40-row fixture, not universal
  Joback validation, thermophysical law, chemical design, process design, or
  support for `Tc` / other property estimates.

**Why it is interesting:** it adds a public-friendly data-and-baseline surface
outside astronomy and materials DFT, while keeping source rights, identity
mapping, property leakage, and family failures visible.

**Evidence trail:**

- [Thermophysical Property Residuals campaign page](./thermophysical-property-residuals.md)
- [ThermoML source manifest](../../data/thermophysical/source_manifest.yaml)
- [ThermoML bounded Tb audit fixture](../../data/thermophysical/thermoml_tb_audit_fixture.yaml)
- [ThermoML family-stratified benchmark review](../reviews/thermoml-tb-family-stratified-transfer-benchmark.md)
- [RESULT-0026 report](../../results/EXP-0020/RUN-0001/report.md)
- [RESULT-0026 Gate A report](../../results/EXP-0020/RUN-0001/gate_a_report.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | How should validated negative/diagnostic memory be preserved while reveal scoring stays source-blocked? | Baseline and sandbox evidence exist; shell-axis is diagnostic-only; `LOCAL-CURVATURE-001` is falsified; `RESULT-0018` is AGENT_VALIDATED; Wigner-cusp is rejected in scope; no admissible reveal source manifest is currently pinned. | Negative/diagnostic memory capsule plus source-blocker preservation. | A public-safe negative-memory capsule, not a reveal score. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | What material snapshot or source-version change would justify reopening residual scoring? | Current-snapshot residual stress is control-sensitive; `EXO-0002` did not clear the reopen gate, so CK17 replay was not run. The closed-lane decision is preserved as negative/control memory. | Metadata-only source-version monitoring. | A `NO_NOTIFY` or NOTIFY-class monitor decision, not a residual score. |
| [Quantum Size Effects](./quantum-size-effects.md) | Is the single-source Almeida InP sandbox baseline strong enough for a narrowed pilot, and can an independent transfer source be found? | Calibration-derived rows remain excluded; Almeida 2023 yielded six direct InP rows and a source-scoped sandbox baseline. | Baseline-readiness review and one independent transfer-source scout. | A readiness verdict or source blocker, not a broad model claim. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | How should the current two-row, Nemitz-dominated Yb/Sr blocker be communicated safely? | Beloy 2021 and Nemitz 2016 support a narrow exploratory Yb/Sr diagnostic: `|z| = 1.78`, consistent within a predeclared 2-sigma threshold, but two-row and source-limited; Pizzocaro still needs an aggregation contract. | Public-safe consistency memory packaging; no metric rerun. | A memory-card summary, not constants-drift metrics. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can APL audit famous formulas by source, range, assumptions, and OOD failure maps? | Stefan-Boltzmann has a Gate-B-validated exact-reference software/convention result; Stellar M-L now has AGENT_VALIDATED `RESULT-0022`, AGENT_PUBLISHED FIRAS/Wien `RESULT-0023`, and replayed high-mass transfer memory for `RESULT-0024`. | RESULT-0023 Gate B replay and safe RESULT-0024 maintainer wording. | A replay verdict or maintainer-review packet, not universal formula wording. |
| [Materials Property Residuals](./materials-property-residuals.md) | Can APL turn open, published materials databases into reusable benchmark datasets and conservative residual maps? | `MD-0001` landed as a first reusable-dataset candidate; formation energy survives controls and is split-robust; band gap is split-fragile; `MD-0002` is `AGENT_VALIDATED` as `RESULT-0021`; family-holdout and descriptor-ablation audits bound the signal, and transfer-negative memory prevents overbroad wording. | External archive/DOI decision for MD-0002 after internal metadata closeout. | A release decision packet, not a material recommendation. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | Can a frozen published thermophysical estimator survive source-pinned family-stratified controls? | ThermoML `Tb` `RESULT-0026` is AGENT_PUBLISHED on a bounded 40-row fixture: Joback wins in aggregate and 7/8 families, while esters/lactones fails and must stay visible. | Gate B replay, value-free corpus-expansion preflight, and failed-family negative memory. | A replay verdict or source-readiness/negative-memory note, not a broad property-estimation claim. |

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
  checksum-pinned and license-confirmed; six direct rows and a source-scoped
  sandbox baseline exist. Baseline-readiness review and an independent transfer
  source are the blockers before any autonomous pilot.
- Atomic has Beloy and Nemitz Yb/Sr rows and a first exploratory cross-source
  diagnostic preserved as a source-limited consistency-memory card. Pizzocaro
  still needs an aggregation/observable-harmonization contract; new benchmark
  metrics wait for a better absolute Yb/Sr source or approved aggregation route.

Next visible artifact: a Quantum baseline-readiness or transfer-source decision,
and an Atomic public-safe consistency-memory summary.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The exact-reference fixture lane has one AGENT_VALIDATED result and one
AGENT_PUBLISHED replay-ready FIRAS/Wien result. The first empirical slice is
Stellar Mass-Luminosity through DEBCat direct dynamical masses; it now has
stage/split/null controls, baseline-adequacy evidence, the full committed
DEBCat dataset, AGENT_VALIDATED `RESULT-0022`, and AGENT_PUBLISHED
`RESULT-0024` as a bounded high-mass transfer result with a retained metadata
caveat.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: Gate B replay for `RESULT-0023` or a maintainer-review
packet for safe `RESULT-0024` wording; no universal formula claim.

### Materials Dataset-To-Benchmark Path

Materials is now a fast path from dataset artifact to a new benchmark surface.
The first pinned dataset is small by design, openly licensed, validated in the
repo, and now has holdout, citation metadata, a first conservative baseline
benchmark, independent replay, a do-not-promote decision, formation-energy null
controls, and split-sensitivity evidence. Formation energy is the stronger
axis; band gap stays diagnostic and split-fragile. `MD-0002` is now acquired,
validated, holdout-frozen, formation-energy benchmarked, and Gate-B-validated
as `RESULT-0021`. Family-holdout and descriptor-ablation audits now bound the
signal. Repository-local release metadata is closed; the next public decision is
whether `MD-0002` is useful and stable enough for an external archive/DOI
release, not a model leaderboard or material recommendation.

Why it matters:

- APL can produce reusable, provenance-rich scientific datasets, not only
  benchmark reports.
- The dataset can later become externally citable once it has a stable version,
  citation/DOI plan, and enough usefulness for other projects.
- Keeping axes separate (formation energy vs band gap, computed DFT vs future
  measured rows) makes future residual maps scientifically reviewable.

Scope:

External release remains blocked on maintainer choice of archive target,
version tag/checksum, DOI posture, public citation wording, and no-claim
dataset caveat. The main repo remains the home for small curated seed datasets,
schemas, loaders, tests, examples, and benchmark configs until that release
posture is decided.
