# Stellar External-Source Readiness Scout

Task: `TASK-0928`
Campaign: stellar mass-luminosity (transfer/holdout lane)
Mode: planning-only source-readiness scout (no rows, no metric, value-blind)
Candidate scouted: the long-baseline **interferometric double-lined
spectroscopic binary** dynamical-mass compilation built from the CHARA Array
"Visual Orbits of Spectroscopic Binaries" programme (Fekel, Gardner, Lester,
et al., 2019+) plus the companion CHARA cluster-orbit programme (for example
the Hyades six-system orbits, Torres et al. 2024)
Verdict: `SOURCE_LIMITED`
Review date: 2026-07-02
Decision context: Decision Day 2026-07-02 D1 Option 3 (external stellar-dataset
scout commissioned alongside the scoped DEBCat capsule)

## Scope And Boundary

This scout assesses **exactly one** candidate independently curated stellar
dataset as a possible future transfer / holdout surface for the frozen,
DEBCat-calibrated baselines behind `RESULT-0022` (the `0.5-2.0 M_sun`
main-sequence-compatible slice) and `RESULT-0024` (the high-mass transfer
slice). Per the task it is **readiness only**: no rows enter the repository,
no metric is run, no stellar result is modified, and no value is transcribed.

The candidate class was chosen for **independence of measurement technique and
provenance** from DEBCat. Of the three candidate classes named in the task:

- an **asteroseismic sample** (for example the Kepler LEGACY dwarfs,
  Silva Aguirre et al. 2017) supplies main-sequence masses, but those masses
  are **model-derived** — they come from fitting stellar-evolution model grids
  to oscillation frequencies. Using model-derived masses to test a
  mass-luminosity relation re-introduces the very stellar-model dependence the
  benchmark is meant to probe, and the published-source standard forbids a
  computed/model surface from serving as the judge. Rejected as the primary
  candidate (kept only as a possible secondary cross-check).
- a **visual-binary dynamical-mass catalogue** curated as a bulk table
  (for example Malkov et al. 2012 / MORBBINCAT) mixes a genuinely dynamical
  mass column with a **photometric mass derived from an assumed
  mass-luminosity relation**, and its luminosities lean on the same relation.
  That makes the luminosity axis circular for an M-L test. Rejected.
- an **eclipsing-binary catalogue curated independently of DEBCat** is the
  obvious direct-mass option, but the strongest modern EB compilations
  (Torres, Andersen & Giménez 2010; Andersen 1991; Eker et al. dEB samples)
  **share systems and upstream provenance with DEBCat** — DEBCat is itself "an
  update of the compilation by Andersen (1991)." A second EB compilation is
  therefore the **weakest** independence choice, not the strongest.

The interferometric double-lined route is the one candidate that pairs a
**direct dynamical mass** with a **non-circular luminosity** while using a
measurement chain (long-baseline optical interferometry resolving the visual
orbit, combined with double-lined radial velocities) that is essentially
disjoint from eclipse photometry. That is why it is scouted here.

This note uses committed repository evidence plus value-blind general knowledge
of the stellar-astrophysics literature and public abstract/landing pages listed
under Sources. It did **not** fetch, transcribe, or ingest any mass,
luminosity, parallax, or radius value; it did not add or edit rows, run any
benchmark, refit any exponent, or create or change any `RESULT`, `PRED`,
`CLAIM`, or `KNOW` artifact.

## What DEBCat Is (The Independence Baseline)

To assess independence, the incumbent surface must be pinned. Per the
[RESULT-0022 review packet](stellar-ml-result0022-maintainer-review-packet.md)
and the DEBCat landing page:

- DEBCat (Southworth 2015) is a **literature compilation** of detached
  eclipsing binaries, originally based on Andersen (1991) and extended as
  revised results appear. It is one curated source, not an independent survey.
- Masses are dynamical, obtained from **double-lined radial velocities plus the
  eclipse-derived inclination** of each detached eclipsing system, to ~1-2%.
- Luminosities in the committed slice **mix catalogue-reported luminosities and
  Stefan-Boltzmann-derived luminosities** from radius and effective
  temperature, with per-row provenance (recorded in the packet's luminosity
  boundary).
- Committed under CC BY 4.0 only after an explicit permission grant
  (`TASK-0763`); the public DEBCat page itself states only "Please cite this
  paper if you use DEBCat" and declares no open license.

Independence from DEBCat therefore means: (a) systems not already in DEBCat,
and (b) a mass and luminosity chain that does not route back through the same
Andersen/Southworth reductions or the same eclipse-inclination technique.

## Candidate Identity And Locator

| Field | Value (locator-level only, value-blind) |
| --- | --- |
| Candidate class | Long-baseline interferometric visual orbit + double-lined spectroscopic orbit -> dynamical masses and orbital parallax |
| Reporting facility / group | CHARA Array (Georgia State University) plus its RV collaborators; contemporaneous VLTI/PIONIER-GRAVITY orbits are an adjacent same-class extension |
| Anchor programme of record | "Visual Orbits of Spectroscopic Binaries with the CHARA Array" series — e.g. Paper I, HD 224355 (Gardner et al. 2019, AJ 158, 73); Paper II, HD 185912 (Lester et al. 2019, AJ 158, 218) |
| Companion programme | CHARA cluster orbits, e.g. "Orbits and Dynamical Masses for Six Binary Systems in the Hyades Cluster" (Torres et al. 2024, ApJ 971, 31) |
| DOI locators (not values) | 10.3847/1538-3881/ab064d (Paper I); 10.3847/1538-4357/ad54b2 (Hyades) |
| Machine-readable data locus | Per-paper journal machine-readable tables (AAS/IOP) and VizieR mirrors; there is **no single pinnable catalogue snapshot** for the whole class |
| Intended source class | `direct_dynamical_mass_from_resolved_orbit` (masses) + `orbital_parallax` (distance) + `sed_integrated_bolometric` (luminosity) |

## Measurement Class Per Column

| Column | Measurement class | Basis and independence note |
| --- | --- | --- |
| Component mass `M` | **direct** (dynamical) | Full Keplerian solution from the interferometrically resolved visual orbit combined with a double-lined RV orbit; no mass-luminosity assumption enters. Precision is frequently <1% and can reach ~0.3% (Paper I quotes `1.626 +/- 0.005` and `1.608 +/- 0.005 M_sun`). The **inclination is astrometric**, not eclipse-derived, so the mass chain does not share DEBCat's eclipse-photometry technique. |
| Orbital parallax / distance `d` | **direct** (geometric) | Derived from the same combined orbit (angular vs physical semi-major axis), e.g. `63.98 +/- 0.26 pc`. This is **independent of Gaia**, which matters: it means the luminosity does not inherit a Gaia-parallax systematic shared with any Gaia-distance-based DEBCat luminosities. |
| Luminosity `L` | **independently-derived** | From SED-integrated bolometric flux plus the orbital parallax (or from angular diameter and `T_eff` when the components are individually resolved). It is **not** model-derived and **not** taken from an assumed M-L relation, so the luminosity axis is non-circular. It does inherit the usual bolometric-correction / SED-fitting systematics. |
| Effective temperature `T_eff` | **independently-derived** (some **direct**) | From SED/spectrophotometry fitting; direct where a limb-darkened angular diameter plus bolometric flux yields `T_eff` geometrically. |
| Radius `R` | **direct** or **independently-derived** | Direct when the component angular diameter is resolved and combined with the orbital-parallax distance; otherwise SED-derived. Not needed for a bare M-L surface but relevant if the transfer uses `L` from `R` and `T_eff`. |

There is no model-derived mass anywhere in the candidate's primary columns —
this is the key advantage over the asteroseismic and photometric-mass options.

## Overlap And Independence Risk Versus DEBCat

Independence is **strong in technique and provenance but not automatic at the
system level**, and this is the load-bearing limitation.

| Independence dimension | Assessment | Risk |
| --- | --- | --- |
| Measurement technique | Long-baseline interferometry + double-lined RV vs DEBCat's eclipse-photometry + RV. Disjoint chains; the interferometric inclination is astrometric, not eclipse-derived. | **low** — genuinely independent technique |
| Curation provenance | CHARA-team primary publications vs the Southworth/Andersen compilation lineage. No shared reduction pipeline. | **low** |
| Parallax / distance systematic | Orbital parallax is internal to each system and independent of Gaia; DEBCat luminosities that used Gaia distances do not share this systematic. | **low** |
| System-level overlap | **This is the decisive risk.** Interferometric orbits favour *bright, nearby, resolvable* binaries, and some of those are **also eclipsing** and therefore may already sit in DEBCat. Paper II of the very series (HD 185912) is an **eclipsing** system. A holdout built from this class must be **de-duplicated against DEBCat at the system level** before it can be called independent; shared systems must be excluded or moved into the same leakage lane. | **medium-high** until de-dup is done |
| Shared calibration scales | Both surfaces ultimately calibrate `T_eff` / bolometric corrections against overlapping temperature and flux scales, so the *luminosity* axis retains a common-scale correlation even when systems are disjoint. | **medium** — weakens, does not void, luminosity independence |

Net: the class clears the technique- and provenance-independence bar that a
second EB catalogue would fail, but it carries a real per-system overlap risk
that cannot be assumed away and must be resolved by de-duplication, not
asserted.

## Coverage Versus The Frozen Slices

Row counts below are **estimates** with a stated basis; no value was
transcribed, and the exact admitted count can only be fixed by a bounded
curation task that de-duplicates against DEBCat and applies the same
main-sequence, mass-range, and system-level-leakage policy as the frozen
slices.

**`0.5-2.0 M_sun` main-sequence slice (target population of `RESULT-0022`,
which admits 223 components across 102/56/65 train/val/holdout).**

- Basis: the CHARA SB series and the CHARA cluster programme each publish a
  handful of systems per paper (2 components per system; 12 components in the
  Hyades paper). The published interferometric+RV population with <1-3%
  dynamical masses in this mass range is on the order of **tens of systems**,
  i.e. a few tens of components, not hundreds.
- Estimate: **~20-60 main-sequence-compatible components** in `0.5-2.0 M_sun`
  before de-duplication, likely **fewer after** removing systems already in
  DEBCat. That is enough for a **holdout / transfer check**, but thin for an
  independent refit and clearly smaller than the incumbent 223-component slice.
- Marked as an estimate; must be confirmed by paper-by-paper assembly.

**High-mass slice (target population of `RESULT-0024`).**

- Basis: high-mass systems are dominated by *distant* O/B stars that are hard to
  resolve interferometrically; the class is biased toward nearby solar-type
  binaries. The literature is explicit about scarcity: "only ten dEBs were
  known with physical properties measured to ... 3% at the time of Torres et
  al. (2010) ... expanded by only three systems," and "less than 20 O stars
  have accurate (<=10%) dynamical mass estimates," most of them eclipsing (and
  thus DEBCat-adjacent), not interferometric.
- Estimate: **~0-5 interferometric high-mass components** independent of
  DEBCat — effectively **no usable independent high-mass coverage** from this
  class. The high-mass transfer lane cannot be served by the interferometric
  route.
- Marked as an estimate; the scarcity basis is a robust literature fact.

Coverage is therefore **adequate-at-best for a small `0.5-2.0 M_sun` transfer
holdout and essentially empty for the high-mass slice**.

## Source-Rights Framework (Three Questions)

| Question | Determination | Evidence / basis |
| --- | --- | --- |
| 1. Local analysis of the source allowed? | **Yes.** Published numeric parameters may be read and analysed locally. | Journal articles and their AAS/IOP machine-readable tables are openly readable; individual factual numbers (a mass, a parallax) are **not copyrightable** and are extractable with attribution under the published-source standard. |
| 2. Byte redistribution (vendoring the source table into the repo) allowed? | **No, by default.** | Preprints carry the arXiv **non-exclusive distribution** licence, which grants arXiv a distribution right and does **not** grant third-party redistribution. Journal machine-readable tables need a per-table licence check. Per the standard, default to **locator + expected SHA-256, not vendoring**. |
| 3. Publication of APL-derived rows allowed? | **Conditionally yes**, as facts with attribution. | Individual factual values, normalized into an APL schema with per-row provenance and per-source citation, are generally committable under the published-source standard when license/ToS allow. This is a curation-task decision per source, not a blanket grant, and it does not authorize copying the upstream tables verbatim. |

Storage posture (per the standard's "published != redistributable" rule): for
each contributing paper, record locator (DOI + machine-readable-table URL),
retrieval date, licence note, and an **expected SHA-256 computed at the first
license-clear fetch** — do NOT fabricate a checksum and do NOT vendor the
bytes here. No fetch beyond license-cleared scope was performed in this scout;
no checksum is asserted.

`blocker_type` (per the published-source standard vocabulary): **`T3_coverage`
plus a `T4_snapshot_approval` component** — the source is admissible in
principle but (a) the curated independent slice is thin/heterogeneous and
scattered across many papers, and (b) there is no single maintainer-approved,
checksum-pinnable snapshot for the class.

## Verdict

`SOURCE_LIMITED`.

The interferometric double-lined route is the **right independence choice** —
it is the one candidate class that supplies a **direct dynamical mass** and a
**non-circular, Gaia-independent luminosity** through a measurement and curation
chain disjoint from DEBCat's, and it cleanly beats the asteroseismic
(model-derived masses), photometric-visual-binary (circular luminosity), and
second-EB-catalogue (shared Andersen/Southworth provenance) alternatives.

It is **not `READY`**, for three honest reasons, any one of which is
disqualifying for an independence claim:

1. **No pinnable license-clear surface.** The class has no single catalogue
   snapshot; it must be assembled paper-by-paper, each with its own licence and
   its own expected checksum. There is nothing to pin today.
2. **Unresolved system-level overlap with DEBCat.** Bright resolvable binaries
   include eclipsing systems already in DEBCat (Paper II is one). Independence
   requires system-level de-duplication that has not been done and cannot be
   assumed.
3. **Coverage is thin where it exists and empty where it is most needed.** The
   independent `0.5-2.0 M_sun` count is an estimated few tens of components
   (likely fewer after de-dup), and the **high-mass slice has essentially no
   independent interferometric coverage**.

It is **not `BLOCKED`**: the sources are public, the masses are direct and
non-model, the rights path (facts + attribution + locator + checksum) is viable,
and a bounded curation task could produce a small independent `0.5-2.0 M_sun`
transfer holdout. The gaps are coverage, snapshot-pinning, and de-duplication —
`SOURCE_LIMITED`, not a hard block.

Because the verdict is not `READY`, **no next-task shape is authorized here.**
The maintainer-facing readiness signal, stated for planning only and not as an
authorization, is: if a second stellar surface is still wanted, the viable
shape is a bounded, metadata-first `scientific_source_curation` task that pins
the CHARA SB-series and cluster-orbit **papers** (locators, DOIs,
machine-readable-table URLs, retrieval dates, licence notes, expected SHA-256
at first license-clear fetch), de-duplicates candidate systems against DEBCat,
and only then proposes a small `0.5-2.0 M_sun` **transfer/holdout** slice — with
the explicit understanding that the high-mass slice stays unserved by this
class and would need a different source. No metric, refit, holdout scoring, or
`RESULT`/`PRED`/`CLAIM`/`KNOW` change may ride along with that curation step.

## Output Routing Summary

- Purpose: source-readiness gate for the stellar transfer/holdout lane; this
  note is the gate surface and nothing downstream.
- Task verdict: `SOURCE_LIMITED` (source-readiness scout; no data, metric, or
  claim change).
- Canonical destination:
  `docs/reviews/stellar-external-source-readiness-scout.md`.
- Review tier: `none`.
- Gate A: not attempted (no `RESULT`/`PRED` artifact produced).
- Gate B: not attempted (not applicable to a planning-only scout).
- Data impact: none — no rows, source manifests, checksums, or provenance files
  created or changed; no value transcribed; no byte vendored.
- Metric impact: none — no benchmark run, no exponent refit, no holdout scored.
- Claim impact: none — no claim created, edited, or promoted.
- Knowledge impact: none — no knowledge entry created or changed.
- Stellar result impact: none — `RESULT-0022` and `RESULT-0024` are untouched.
- Publication blocker: an independent second stellar M-L surface is **not**
  ready to pin. The interferometric route is the best candidate but is
  coverage-limited, unpinnable as a single snapshot, and carries an unresolved
  DEBCat system-level overlap. This blocks *broader generalization* of the
  stellar baselines beyond the frozen DEBCat slice; it does **not** block the
  already-approved scoped DEBCat capsule wording.

## Limitations

- This scout evaluated **exactly one** candidate class, as required; it is not a
  broad survey of all possible independent stellar M-L sources.
- It used committed repository evidence plus value-blind general knowledge and
  public abstract/landing pages. It did **not** inspect the full journal PDFs,
  machine-readable tables, VizieR row contents, or current archive state, and it
  transcribed **no** mass, luminosity, parallax, radius, or temperature value.
- All row-count figures are **estimates** with a stated basis and are labelled
  as such; the exact admitted counts, the de-duplicated system list, and the
  per-paper licences and checksums can only be fixed by a future bounded
  curation task, not by this scout.
- No checksum is asserted. Any expected SHA-256 must be computed at the first
  license-clear fetch inside an authorized curation task and must not be
  fabricated.
- Nothing here authorizes fetching beyond license-cleared scope, row curation,
  source pinning, metric runs, holdout scoring, or any
  claim/knowledge/result promotion. Asteroseismic and photometric-mass surfaces
  are noted as rejected primary candidates, not as authorized secondary rows.

## Sources

- DEBCat catalogue landing page (Southworth), scope, quantities, citation
  statement: https://www.astro.keele.ac.uk/jkt/debcat/
- DEBCat description paper (Southworth 2015), arXiv abstract:
  https://arxiv.org/abs/1411.1219
- VizieR record for the DEBCat catalogue (Southworth, 2015):
  https://ui.adsabs.harvard.edu/abs/2017yCat.5152....0S/abstract
- Torres, Andersen & Giménez (2010), "Accurate masses and radii of normal
  stars," the well-characterized EB reference population (shared Andersen
  lineage with DEBCat): https://ui.adsabs.harvard.edu/abs/2010A%26ARv..18...67T/abstract
- CHARA "Visual Orbits of Spectroscopic Binaries" Paper I, HD 224355
  (direct dynamical masses, orbital parallax): https://arxiv.org/abs/1902.05557
- CHARA "Visual Orbits of Spectroscopic Binaries" Paper II, HD 185912
  (an eclipsing system in the same interferometric series — the overlap-risk
  evidence): https://ui.adsabs.harvard.edu/abs/2019AJ....158..218L
- CHARA Hyades six-system orbits (Torres et al. 2024), interferometric
  dynamical masses and orbital parallaxes: https://arxiv.org/abs/2406.01674
- Kepler asteroseismic LEGACY dwarfs (Silva Aguirre et al. 2017), the rejected
  model-derived-mass alternative:
  https://ui.adsabs.harvard.edu/abs/2017ApJ...835..173S
- Malkov et al. (2012) orbits of visual binaries and dynamical masses
  (MORBBINCAT), the rejected circular-luminosity alternative:
  https://ui.adsabs.harvard.edu/abs/2012yCat..35460069M/abstract
- High-mass dEB scarcity evidence (V1034 Sco et al., A&A 2023), for the
  high-mass coverage estimate: https://www.aanda.org/articles/aa/full_html/2023/03/aa44980-22/aa44980-22.html
- arXiv non-exclusive distribution licence (rights question 2):
  https://arxiv.org/licenses/nonexclusive-distrib/1.0/
