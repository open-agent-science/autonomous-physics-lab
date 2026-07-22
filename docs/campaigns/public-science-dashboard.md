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

### NMD-0003 Retrospective Point-Estimator Card

**Review tier:** `RESULT-0025` is `AGENT_VALIDATED`; Gate B point metrics were
independently replayed exactly.

> On one frozen NMD-0003 residual surface, a single RBF Gaussian-process model on
> `[Z, N]` lowers the retrospective post-AME2020 holdout nuclear-mass MAE from a
> frozen baseline of `2.979273` MeV to `0.462129` MeV — a `2.517144` MeV
> improvement — and beats the best predeclared control (`smooth_a_gp`) by
> `1.869312` MeV against a `0.25` MeV survival margin. An independent Gate B
> replay reproduced these point metrics exactly (maximum absolute drift `0.0`).
> This is point-estimator evidence on a retrospective time-split holdout, not a
> blind prediction reveal. Its predictive uncertainty envelope is heavy-tailed
> and miscalibrated, so it provides no calibrated prediction intervals. The
> later tier-1 prospective registry freezes point-only central values only; it
> is not a reveal result, interval claim, or success verdict. It establishes no
> nuclear-mass law, no broad mass formula, and no discovery; it is an
> AGENT_VALIDATED retrospective point-estimator result
> plus a guarded point-only prediction-registration follow-up.

**Replay bookkeeping:** the committed `RESULT-0025` package preserves the
originally published `TASK-0843` input task file, while the Gate B replay
recorded an expected lifecycle drift in the copied task-YAML hash and replay
git commit; this is bookkeeping drift, not a scientific input change.

**Evidence trail:**

- [NMD-0003 RESULT-0025 public review packet](../reviews/nmd0003-result0025-public-review-packet.md)
- [Nuclear Mass Surface campaign page](./nuclear-mass-surface.md)

### Quantum Direct-Measurement Data Gate

**Short version:** APL selected the Almeida 2023 InP CC-BY 4.0 source as the
current Quantum Size Effects row path, pinned the article/SI bytes, and
digitized six direct `(edge length, E1s)` rows. `TASK-0225` then produced a
source-scoped sandbox baseline with controls and a one-point holdout. The later
ZnSe/InP no-refit transfer is now packaged as `RESULT-0029`: the transferred
model beats the best control but misses the frozen `0.05 eV` survival margin by
`0.00341632 eV`, so the result is `INCONCLUSIVE`, not positive. A separate
Kim-2020 route contributes eight source-stated CdSe observations: four
absorption and four emission rows, kept on distinct axes. A frozen adequacy
review found both axes underpowered, and a five-candidate source scout found no
qualifying independent direct-row route.

**Why it is interesting:** the campaign demonstrates source discipline before
attractive modeling. A source blocker is treated as useful output, not as a
failure.

**Limitation:** this is a single-source InP sandbox baseline plus one bounded
two-material transfer-control result, not a universal size-effect law, material
recommendation, device-performance result, or validated cross-material model.
The current blocker is new evidence: four rows per axis leave zero residual
degrees of freedom for the frozen two-parameter stability check, and no
independent source cleared the row-count, semantics, rights, uncertainty, and
stable-byte gates. Rerunning the same ZnSe/InP surface or another generic scout
would be methodology shopping.

**Evidence trail:**

- [Quantum Size Effects campaign page](./quantum-size-effects.md)
- [Quantum direct-source candidate brief](../source-candidates/quantum/quantum-direct-source-candidate-brief.md)
- [Quantum Almeida deterministic source-artifact package](../reviews/quantum-almeida-2023-deterministic-source-artifact-package.md)
- [RESULT-0029 report](../../results/EXP-0022/RUN-0001/report.md)
- [RESULT-0029 result metadata](../../results/EXP-0022/RUN-0001/result.yaml)
- [Kim-2020 small-surface adequacy decision](../reviews/quantum/kim-2020-cdse-small-surface-contract-task1077.md)
- [Independent CdSe source verdict](../source-candidates/quantum/cdse-independent-source-task1078.md)
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
AGENT_VALIDATED spectral-domain self-consistency slice after Gate B replay,
and Stellar high-mass transfer `RESULT-0024` is now an AGENT_VALIDATED bounded
same-source transfer result after formal workflow Gate B replay. Their strongest
recorded validation identity remains `same_owner_different_account`.
The external CHARA transfer is now `AGENT_PUBLISHED` `RESULT-0031`: it beats the
best eligible control, but misses the predeclared survival margin and is
therefore `INCONCLUSIVE`. A first replay attempt confirmed all five frozen
input hashes but stopped before metrics because original-publisher provenance
was absent; that metadata must be repaired before an independent replay.

**Result capsule — RESULT-0022 (Stellar mass-luminosity, DEBCat):**

**Review tier:** `AGENT_VALIDATED`; Gate A and Gate B both pass. The strongest
recorded validation independence is `same_owner_different_account`.

> On a frozen, CC BY 4.0 DEBCat slice of 223 main-sequence-compatible binary
> components spanning `0.5-2.0 M_sun`, the fixed `L proportional to M^3.5`
> baseline beats a per-mass-band median null but has higher holdout error
> (`0.184954 dex`) than a train-fitted single exponent near `4.53`
> (`0.119925 dex`). The direction is stable across the committed controls and
> three additional value-blind system-level splits, although the alternate-
> split margin is modest. A two-segment fit is not justified after the
> predeclared complexity penalty. This Gate-B-replayed result shows
> only that `alpha=3.5` is inadequate as the sole baseline on this frozen
> slice; it does not falsify the textbook relation universally or establish a
> universal mass-luminosity or stellar-evolution law.

- **Source:** DEBCat detached eclipsing binaries (Southworth 2015), CC BY 4.0 by explicit grant (`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`); direct dynamical masses; raw `debs.dat` not committed (Route 2). Frozen main-sequence 0.5–2.0 Msun slice (223 components).
- **Command:** `python3 -m physics_lab.cli run examples/stellar_ml_debcat_baseline_benchmark.yaml` (quick check: `python3 scripts/replay_stellar_ml_result.py --check`).
- **Primary metric:** textbook single exponent α=3.5 holdout MAE **0.184954 dex** beats the per-mass-band null (0.331817) but is inadequate as the sole baseline — train-fitted α≈4.53 (**0.119925**) and piecewise α=4.0 (0.137608) are materially better (gaps 0.065 / 0.047 dex > 0.04 dex split-noise). Positive in 5/5 seeded splits; beats luminosity-shuffle controls.
- **Review tier:** `AGENT_VALIDATED` (Gate B replayed under
  `same_owner_different_account`; not maintainer-reviewed).
- **Gate A:** PASS (9/9). **Gate B:** PASS. Follow-up controls found the conclusion stable across a small alternate-split slate, while a piecewise baseline is not justified after complexity penalty.

**Why it is interesting:** it is an accessible way for many agents to run
bounded, reviewable audits without claiming new laws.

**Limitation:** no empirical textbook formula claim has been promoted. The
formula tasks include exact-reference fixtures, Stellar M-L scoped benchmarks,
and a FIRAS/Wien self-consistency slice, not universal validation or
falsification. `RESULT-0022` and `RESULT-0023` have passed Gate B but retain
`same_owner_different_account` validation identity and are not
maintainer-reviewed. `RESULT-0023` remains calibration/known-physics
verifier memory, not a discovery claim. `RESULT-0024` keeps a same-source
DEBCat and small-holdout transfer boundary; the formal workflow replay removes
the earlier helper blocker but does not make the evidence external to DEBCat.
The current Stellar M-L evidence supports only scoped benchmark statements; it
is not a universal law claim.

**Result capsule — RESULT-0024 (Stellar high-mass transfer):**

- **Source:** the same committed DEBCat Route 2 component rows used by
  `RESULT-0022`; high-mass holdout is disjoint in mass regime but not an
  independent external catalogue.
- **Primary metric:** frozen `RESULT-0022` relation holdout MAE **0.334564
  dex** versus best control **0.483879 dex**, clearing the predeclared `0.04`
  dex margin by **0.149315 dex** on the stage-matched high-mass holdout.
- **Review status:** `AGENT_VALIDATED` after formal workflow Gate B replay;
  still not maintainer-reviewed and still same-source DEBCat evidence.
- **No-claim wording:** same-source transfer under controls, not a universal
  stellar mass-luminosity law, stellar-structure conclusion, or discovery.

**Result capsule — RESULT-0031 (CHARA fixed-relation transfer):**

- **Source:** twelve components from six source-curated CHARA systems, with
  independent source replay and physical-system grouping.
- **Primary metric:** frozen-relation MAE **0.060530 dex** versus best eligible
  control **0.097317 dex**. The **0.036787 dex** margin misses the predeclared
  **0.04 dex** survival threshold by **0.003213 dex**.
- **Review status:** `AGENT_PUBLISHED`, `INCONCLUSIVE`; a first replay attempt
  was environment-blocked before metrics by missing publisher provenance.
- **No-claim wording:** bounded six-system transfer test, not a validated
  universal stellar law and not a positive near-miss to be rescued by refit.

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
- [FIRAS/Wien RESULT-0023 Gate B replay](../reviews/firas-wien-result0023-gate-b-replay.md)
- [Stellar high-mass transfer RESULT-0024 report](../../results/EXP-0017/RUN-0001/report.md)
- [Stellar high-mass transfer RESULT-0024 replay](../reviews/stellar-result0024-high-mass-transfer-gate-b-replay.md)
- [CHARA fixed-relation RESULT-0031 report](../../results/EXP-0023/RUN-0001/report.md)
- [CHARA fixed-relation transfer review](../reviews/stellar/chara-fixed-relation-transfer-task1050.md)
- [CHARA Gate B replay blocker](../reviews/stellar/result0031-chara-gate-b-replay-task1075.md)
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
benchmark that is regenerable end-to-end via `physics-lab run` and replayed in
Gate B with zero numeric drift.

The separate OQMD lane now has 172 source-pinned rows, a frozen 120/26/26
composition-grouped split, value-blind controls, and an independent source
replay PASS. A proposed one-shot result remains under review in PR #1634; its
metrics are not canonical repository evidence until merge.

**Result capsule — RESULT-0021 (Materials MD-0002 formation energy):**

- **Source:** The Materials Project, CC BY 4.0, computed-DFT stable ternary-oxide slice (`data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`), frozen 362-row holdout-split slice.
- **Command:** `python3 -m physics_lab.cli run examples/materials_md0002_formation_energy_benchmark.yaml` (quick check: `python3 scripts/replay_materials_md0002_result.py --check`).
- **Primary metric:** exact cation-pair mean baseline holdout MAE **0.200606 eV/atom** vs global-median null **0.506092** (60.4% lower); winner in 5/5 seeded splits; beats label-shuffle and cation-label-shuffle nulls.
- **Review tier:** `AGENT_VALIDATED` (Gate B replayed by a different agent under
  `same_owner_different_account`; not maintainer-endorsed knowledge).
- **Gate A:** PASS (9/9). **Gate B:** PASS on 42 compared numeric fields with
  maximum absolute drift `0.0` (TASK-0775).

**Why it is interesting:** this is the first concrete evidence trail showing
APL can turn a published/open source into a provenance-rich benchmark dataset
before modeling, regenerate the result deterministically for replay, and then
preserve failed transfer as useful scope memory. It is a
dataset/benchmark artifact, not a claim.

**Limitation:** the rows are computed DFT values from Materials Project, not
experimental measurements. This is not a material recommendation, synthesis
guide, device claim, biomedical claim, or promoted materials claim. The
dataset is externally published at DOI `10.5281/zenodo.21207072`, but that
citation does not broaden the result's scientific scope.

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
- [OQMD independent source replay](../reviews/materials/oqmd-bounded-snapshot-independent-source-replay.md)
- [Materials data area](../../data/materials/README.md)
- [Published-source and reusable-dataset standard](../published-source-dataset-standard.md)

### Thermophysical Property Residuals

**Short version:** APL now has a newly active thermophysical-property benchmark
lane. The first slice is ThermoML normal boiling temperature (`Tb`) with a
frozen Joback and Reid group-contribution baseline. `RESULT-0026` is
AGENT_VALIDATED on a bounded 40-row family-stratified fixture. `RESULT-0028`
separately packages the esters/lactones failed-family slice as AGENT_VALIDATED
negative/control memory.

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
- **Review status:** `RESULT-0026` and `RESULT-0028` are AGENT_VALIDATED after
  zero-drift formal workflow Gate B replay.
- **No-claim wording:** bounded `Tb` transfer on a 40-row fixture, not universal
  Joback validation, thermophysical law, chemical design, process design, or
  support for `Tc` / other property estimates.

**Why it is interesting:** it adds a public-friendly data-and-baseline surface
outside astronomy and materials DFT, while keeping source rights, identity
mapping, property leakage, and family failures visible.

**Expansion state:** the exact 80-row design is stopped because acids provide
6/10 and ketones 8/10 admissible identities. A later value-blind decision froze
an availability-capped, family-equal contract of at most 74 rows. No expanded
fixture or score exists yet; extraction is blocked until the exact archive is
supplied and the five-row article cap and information floor pass.

**Evidence trail:**

- [Thermophysical Property Residuals campaign page](./thermophysical-property-residuals.md)
- [ThermoML source manifest](../../data/thermophysical/source_manifest.yaml)
- [ThermoML bounded Tb audit fixture](../../data/thermophysical/thermoml_tb_audit_fixture.yaml)
- [ThermoML family-stratified benchmark review](../reviews/thermoml-tb-family-stratified-transfer-benchmark.md)
- [RESULT-0026 report](../../results/EXP-0020/RUN-0001/report.md)
- [RESULT-0026 Gate A report](../../results/EXP-0020/RUN-0001/gate_a_report.md)
- [RESULT-0026 result metadata](../../results/EXP-0020/RUN-0001/result.yaml)
- [RESULT-0028 report](../../results/EXP-0020/RUN-0002/report.md)
- [RESULT-0028 result metadata](../../results/EXP-0020/RUN-0002/result.yaml)
- [ThermoML feasible expansion contract](../../data/thermophysical/thermoml_tb_feasible_expansion_contract.yaml)
- [ThermoML contract review](../reviews/thermoml/thermoml-tb-feasible-expansion-contract-task1084.md)

## Campaign Snapshot

| Campaign | Current question | What we have learned | Current focus | Next visible artifact |
| --- | --- | --- | --- | --- |
| [Nuclear Mass Surface](./nuclear-mass-surface.md) | What official post-registration event could legitimately reopen the frozen shell-axis reveal route? | `RESULT-0025` has exact replayed point-estimator improvement; intervals remain uncalibrated; point-only PRED entries are frozen; a clean scout found only pre-registration AME2020/NUBASE2020 sources with zero target exposure. | Ratify event-triggered monitoring; do not repeat no-signal scouts or inspect targets. | A trigger ledger now, then a source-manifest decision only after a qualifying official release. |
| [Exoplanet Mass-Radius](./exoplanet-mass-radius.md) | What material snapshot or source-version trigger would justify reopening residual scoring? | Current-snapshot residual stress is control-sensitive; `EXO-0002` did not clear the reopen gate; monitor check 3 returned `NO_NOTIFY`; `RESULT-0027` is AGENT_VALIDATED negative/control memory with fair-null transparency. | Monitor-only trigger discipline. | A source-version/coverage trigger verdict, not a residual score. |
| FRB / Radio Transients | Can a time-truncated exposure surface support a sealed repeater-propensity prediction without label leakage? | The Catalog-1 interval exposure pair passed checksum/schema gates, `TASK-0963` built a 479-row pre-T exposure feature surface, `TASK-0964` froze the exposure-only model surface, `PRED-0001` was registered as a 479-source point-score/rank prediction, the full anchor is sealed by GitHub Release tag `pred-frb-pret-repeater-propensity-20260710`, and `TASK-1024` completed a reduced rights-bounded capsule without external upload. | Keep any reduced-capsule publication maintainer-only; activate reveal-source work only on a concrete official release signal. | An optional citable reduced checksum anchor or a later trigger-based reveal-source decision; no current success verdict. |
| [Quantum Size Effects](./quantum-size-effects.md) | What genuinely new source could reopen the stopped CdSe route? | AGENT_VALIDATED `RESULT-0029` preserves the strict ZnSe/InP miss; both four-row Kim-2020 axes are underpowered and no independent direct-row source cleared the frozen gates. | Monitor/source-trigger-only; no score, pooling, or repeated generic scout. | A trigger-specific source-readiness decision, not a metric on the current rows. |
| [Atomic-Clock Residuals](./atomic-clock-residuals.md) | What future source event would justify reopening the two-row `171Yb/87Sr` surface? | Beloy and Nemitz support a narrow no-tension memory card; other routes are blocked or isotope-mismatched; the multi-species route returned `KEEP_MONITOR_ONLY`. | Follow the ratified reopen-trigger ledger; no standing executor task or metric rerun. | A future trigger decision, not constants-drift metrics. |
| [Textbook Formula Audit](./textbook-formula-audit.md) | Can the bounded CHARA transfer receive a valid independent replay, and can one supplemental system clear source gates without rescuing it? | `RESULT-0031` is AGENT_PUBLISHED INCONCLUSIVE; all five frozen hashes match, but the first replay stopped before metrics on missing publisher provenance. | Repair provenance, then replay with an independent identity; assess HD 284163 only as a separate extension. | A Gate-B-validated bounded inconclusive result or a precise replay contest, not universal stellar-law wording. |
| [Materials Property Residuals](./materials-property-residuals.md) | Can the frozen OQMD surface produce a durable within-source computed-DFT benchmark? | `MD-0002` is AGENT_VALIDATED and externally citable; OQMD has 172 normalized rows, a 120/26/26 grouped split, frozen controls, and independent source replay PASS. | Review proposed result PR #1634; do not publish its metrics before merge. | After merge, an independent replay of the unchanged bounded result, not a cross-database claim. |
| [Thermophysical Property Residuals](./thermophysical-property-residuals.md) | Can the revised at-most-74-row contract be extracted without violating its source and information gates? | `RESULT-0026` and failed-family `RESULT-0028` are AGENT_VALIDATED; exact-80 is stopped, while a value-blind family-equal 74-row ceiling is frozen. | Supply the exact archive and enforce the five-row article cap and information floor; keep scoring separate. | One complete rights-bounded fixture or a hard extraction stop, not a partial fixture or metric. |
| Lattice-QCD Aggregated Consistency | Can primary evidence resolve dependency structure before any central values are admitted? | An eleven-publication `f_K/f_pi` manifest and graph exist, but all 49 pairwise dependency relations remain `UNKNOWN`. | Split the dependency audit by flavor family and freeze value-admissibility policy in parallel. | Resolved conservative components or a durable covariance HOLD; no Lattice-QCD physics claim. |
| [Dimensional Analysis Validator](./dimensional-analysis-validator.md) | Can reproducible calibration be separated from a genuinely external test of generalization? | AGENT_VALIDATED `RESULT-0030` reproduced with zero drift but remains calibration-only; the first external-freeze attempt stopped before rows because of prior result exposure. | Retry only with a clean external controller and independently scout third-party labelled corpora. | A frozen external benchmark route or a precise source/independence blocker; no automatic `CLAIM-0005` promotion. |

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
- Reveal scoring remains blocked until uncertainty calibration and a future
  source-grade no-peek release pass.

Next visible artifact: a blocker/negative-memory preflight for the failed
uncertainty-calibration audit, plus a rights-safe DZ10 parity check if local
AMDC bytes are available. The residual-free high-error cluster audit,
neutron-rich boundary transfer, and magic-distance interaction lanes have all
landed as non-positive sandbox memory and should not be treated as positive
near-misses.

### FRB Sealed-Prediction Pipeline

The FRB campaign has moved from source scouting into an activated prediction
chain. The Catalog-1 interval exposure pair passed checksum/schema gates,
`TASK-0963` built a compact pre-T exposure feature surface with 479 source rows,
`TASK-0964` froze the exposure-only model surface without label contact, and the
maintainer approved registration of `PRED-0001` as a point-score/rank-only
prediction. The deterministic nine-member anchor capsule is sealed by GitHub
Release tag `pred-frb-pret-repeater-propensity-20260710`.

Why it matters:

- It is now a sealed, third-party-verifiable prediction pack outside nuclear
  masses.
- The chain has explicit sequencing: frozen exposure-only model surface,
  registration pack, maintainer-approved PRED entry, GitHub Release anchor, and
  a separate reveal-source contract before any scoring.

Scope:

No FRB result, claim, population model, or repeater-success verdict exists yet.
`PRED-0001` is a pre-reveal prediction registry artifact, not post-reveal
evidence.

Next visible artifacts: a reveal-source manifest and maintainer-reviewed reveal
scoring packet if an admissible post-T source appears.

### Quantum And Atomic Fresh-Data Gates

Quantum Size Effects and Atomic-Clock Residuals are slower because they are
doing source hygiene before metrics or promotion. The visible result right now
is the data gate itself: which sources are strong enough to support a
benchmark, and which ones are not.

Why it matters:

- Quantum now has Almeida 2023 as the selected source path. The article/SI are
  checksum-pinned and license-confirmed; six direct rows and a source-scoped
  sandbox baseline exist. ZnSe/Toufanian rows are frozen as limited factual
  extracts, and `RESULT-0029` packages the strict no-refit transfer miss as
  bounded inconclusive/control memory. Kim-2020 figure digitization stopped at
  its frozen two-axis calibration gate, but a separately pinned body-text route
  has now admitted four absorption and four emission rows without scoring.
- Atomic has Beloy and Nemitz Yb/Sr rows and a first exploratory cross-source
  diagnostic preserved as a source-limited consistency-memory card. Pizzocaro
  still needs an aggregation/observable-harmonization contract; McGrew/NIST is
  blocked as not a direct independent Yb/Sr route.

Next visible artifact: a future Atomic trigger decision or a Quantum
benchmark-adequacy/source-breadth verdict; neither is a physics result.

### Textbook Formula Audit As A Public Entry Surface

Textbook Formula Audit is the most accessible future campaign for new
contributors: each task can audit one famous formula in one source-pinned
range. The exact-reference fixture lane and FIRAS/Wien result are
AGENT_VALIDATED. The first empirical slice is
Stellar Mass-Luminosity through DEBCat direct dynamical masses; it now has
stage/split/null controls, baseline-adequacy evidence, the full committed
DEBCat dataset, AGENT_VALIDATED `RESULT-0022`, AGENT_VALIDATED `RESULT-0023`
as calibration/known-physics verifier memory, and AGENT_VALIDATED
`RESULT-0024` as a bounded high-mass transfer result with same-source DEBCat
caveats.

Why it matters:

- APL will audit textbook formulas by range and assumptions.
- Each audit produces per-slice verdicts, not universal truth/falsity.

Next visible artifact: independent Gate B replay of INCONCLUSIVE `RESULT-0031`,
plus a separate source decision for HD 284163; no universal formula claim.

### Materials Dataset-To-Benchmark Path

Materials is now a fast path from dataset artifact to a new benchmark surface.
The first pinned dataset is small by design, openly licensed, validated in the
repo, and now has holdout, citation metadata, a first conservative baseline
benchmark, independent replay, a do-not-promote decision, formation-energy null
controls, and split-sensitivity evidence. Formation energy is the stronger
axis; band gap stays diagnostic and split-fragile. `MD-0002` is now acquired,
validated, holdout-frozen, formation-energy benchmarked, Gate-B-validated as
`RESULT-0021`, and externally citable as Zenodo DOI `10.5281/zenodo.21207072`.
Family-holdout and descriptor-ablation audits now bound the signal. Release
integrity and no-claim record-back are complete, so the current posture is fixed
dataset memory, not a rebuild, metric rerun, or model leaderboard.

Why it matters:

- APL can produce reusable, provenance-rich scientific datasets, not only
  benchmark reports.
- The dataset is externally citable now, with DOI, release tag, checksum,
  license, attribution, and no-claim wording tied back into the repository.
- Keeping axes separate (formation energy vs band gap, computed DFT vs future
  measured rows) makes future residual maps scientifically reviewable.

Scope:

External release is now complete for `MD-0002` v0.1.0, including DOI,
checksum, release tag, license, attribution, and no-claim wording. Future
Materials work should not rebuild that archive without a versioned release
reason; the next dataset question belongs to a separately gated surface.
