# Quantum Open-Tabular Transfer Source Scout

**Task:** `TASK-0829`
**Campaign:** `quantum-size-effects`
**Scope:** open-licensed-first Tier-1/2 tabular transfer-source admissibility scout.
**Pinned candidate route:** Toufanian et al. 2021, "Correlating ZnSe Quantum Dot
Absorption with Particle Size and Concentration," *Chemistry of Materials*
33(18), 7527-7536, DOI `10.1021/acs.chemmater.1c02501` (ZnSe).
**Verdict:** `SOURCE_LIMITED`

## Scope And Non-Goals

This is a source-admissibility scout for the campaign's transfer validity gate.
It assesses exactly ONE open, machine-readable, license-clear route with DIRECT
(size, energy) row-level measurements for a SECOND quantum-dot material (not InP).
It executes the open-licensed-first preference adopted in `TASK-0751` and never
run as an actual open-tabular scout (the prior transfer scout `TASK-0810` blocked
on a closed, figure-derived CdSe route, Norris-Bawendi 1996).

This scout records a verdict only. It does **not**:

- curate any `qd-*.yaml` row, edit `qd-0003`, or add a manifest source entry;
- run baseline metrics, holdout splits, or any benchmark;
- fetch, download, or vendor external data, figures, tables, or PDFs;
- compute or fabricate a SHA-256 (no license-clear fetch occurred in this pass);
- unblock correction search (`TASK-0226` stays blocked) or change any
  RESULT / PRED / CLAIM / KNOW artifact.

## Why InP And The Two Committed Sets Do Not Count

- **InP / Almeida 2023** is already the single DIRECT source on the campaign's
  benchmark slice (six rows; holdout 0.048 eV vs 0.376 / 0.420 eV null/shuffled
  controls). A transfer holdout must be a SECOND, independent material.
- **Yu 2003 CdSe** (`qd-0001`) and **Moreels 2009 PbS** (`qd-0002`) are
  calibration-DERIVED: their diameters are produced by inverting a published
  sizing polynomial from the same optical property, so using either as a
  transfer holdout would be circular. They are excluded by construction.

The leakage boundary for any future ZnSe (or other) transfer rows: the candidate
must be an independent DIRECT measurement (SAXS / TEM / XRD size, optically
independent of the size axis) and must not be mixed with the Yu 2003 or
Moreels 2009 calibration curves or any back-computed sizing equation.

## Search Performed (Open-Licensed-First, Tier 1 then Tier 2)

Per the `TASK-0751` preference order, the scout searched open surfaces first
and treated a fitted sizing equation alone as non-qualifying (calibration-derived):

- **Tier 1 (open-data repositories):** Zenodo and Figshare keyword sweeps for a
  per-sample (size, first-exciton-energy or bandgap) table as CSV/XLSX with a
  CC license. No admissible quantum-dot size-energy dataset surfaced. This is
  consistent with the prior `TASK-0399` finding that machine-readable
  size-energy supplements are not a productive discovery surface for this
  campaign (arXiv ancillary, PMC OA package, Europe PMC supplementaryFiles,
  Zenodo, and Figshare all returned PDF-only or non-measurement assets).
- **Tier 2 (open-access / CC-BY journals and preprints):** targeted sweeps for
  CdSe, PbS, PbSe, ZnSe, CuInS2, and CsPbBr3 size-series papers in CC-BY venues
  (Nature Communications, Scientific Reports, RSC Advances, Nanoscale Advances,
  MDPI Nanomaterials), plus PMC mirrors and ChemRxiv preprints, looking for a
  printed per-sample table pairing a DIRECT size with an optical transition
  energy.

The most promising DIRECT + machine-readable per-sample table found is the
Toufanian 2021 ZnSe paper; the most promising clean-CC-BY paper found
(MDPI CuInS2 2023) is emission/temperature-series rather than a clean direct
absorption table. Neither cleared all three qualification gates simultaneously.

## Admissibility Table

Gates: open license on the data-bearing version; machine-readable/tabular
per-sample rows; DIRECT (not calibration/figure/theory) size axis; clean
size-semantics; second-material independence; no duplication of committed sets.

| Candidate (material) | License on data-bearing version | Machine-readable per-sample table | **Direct vs derived (size axis)** | Size semantics | Second material vs committed sets | Admissibility |
| --- | --- | --- | --- | --- | --- | --- |
| **Toufanian et al. 2021, ZnSe** (Chem. Mater., DOI `10.1021/acs.chemmater.1c02501`) | Version-of-record CLOSED (ACS subscription). PMC mirror `PMC8872037` is an **NIHPA author manuscript** (free to read under NIH Public Access; **not** a CC-BY grant, no redistribution/derivative license). ChemRxiv preprint `10.26434/chemrxiv-2021-m8kbg-v4` exists but its license (CC BY vs CC BY-NC vs CC BY-NC-ND) is **UNCONFIRMED** — ChemRxiv blocked automated access (HTTP 403) and offers all three options with no single default. | YES. Table 1 ("Summary of MP-AES Data") lists 10 samples (QD361-QD422), each with a SAXS diameter (e.g. 2.04 +/- 0.57 nm) and a 1S absorption-peak position encoded in the sample id (nm). | **DIRECT.** Size measured directly by **SAXS** (TEM cross-check); authors explicitly use SAXS for the size axis, not an optical inversion. The 1S peak is an independent optical measurement. | `diameter_nm`; nearly spherical ZnSe; clean spherical semantics (no non-spherical coercion needed). Exact per-sample 1S peak in eV must be read from Table 1 / SI at curation time (encoded in nm in sample ids). | ZnSe; independent of InP (Almeida), Yu 2003 CdSe, and Moreels 2009 PbS. No overlap, no calibration-curve reuse. | **BLOCKED on license clarity.** Direct + tabular + independent, but no confirmed redistributable (CC-BY/CC0) version. |
| CuInS2 (ACS Nano 2018, DOI `10.1021/acsnano.8b03641`, `PMC6117745`) | **CC-BY-NC-ND** (verbatim header: "Creative Commons Non-Commercial No Derivative Works (CC-BY-NC-ND) Attribution License"). ND prohibits derivative redistribution (a curated rows dataset is a derivative). | NO consolidated per-sample (size, energy) table; size-energy exposed as a sizing curve plus TEM histograms. | DIRECT TEM/XRD sizing, but the row-bearing surface is FIGURE-derived. | `diameter_nm`. | CuInS2; independent material. | **BLOCKED:** ND license + figure-derived (no printed per-sample table). |
| CuInS2 (MDPI Nanomaterials 2023, DOI `10.3390/nano13212892`, `PMC10650527`) | **CC-BY** (MDPI; "© the authors", Creative Commons Attribution). Clean reuse license. | WEAK: size-selected fractions with temperature-dependent **PL/emission** spectra; no clean single-temperature per-sample (size, absorption-peak) table; emission maximum shifts with temperature. | DIRECT TEM/XRD sizing per fraction. | `diameter_nm`. | CuInS2; independent material; but property is emission/PL (keep separate from absorption per the property-kind policy). | **NOT READY:** CC-BY is clean, but the data surface is a temperature/emission study, not a clean direct (size, absorption-energy) table; not confirmable as a row-ready transfer set in this pass. |
| Lead-bromide perovskite (arXiv `2004.08310`; VoR JPCL `10.1021/acs.jpclett.0c00266`) | arXiv **non-exclusive** license (not a CC reuse grant); VoR CLOSED (ACS). | Not confirmable from metadata; primary surface is T-dependent PL. | Mixed; size semantics (edge length) need review. | edge_length (non-spherical) would need `edge_length_nm` + morphology. | CsPbBr3-family; independent material. | **NOT READY:** no license-clear reuse grant; surface not confirmed as a direct (size, energy) table. |
| Open-data repositories (Zenodo / Figshare) | n/a | NONE found (no admissible size-energy dataset). | n/a | n/a | n/a | **NOT FOUND** (corroborates `TASK-0399`). |

## Risk Flags

- **Licensing.** The single direct + tabular candidate (ZnSe) has no confirmed
  redistributable license: VoR is closed ACS; the PMC copy is an NIHPA author
  manuscript (read-only NIH Public Access, not CC-BY); the ChemRxiv preprint's
  license could not be verified (server blocked). The cleanest CC-BY paper
  (MDPI CuInS2) is not a clean direct-absorption table. Committing curated rows
  from a non-CC-BY / ND source would breach reuse terms.
- **Machine-readability.** ZnSe Table 1 is a printed article-body table (with an
  SI PDF), not a CSV; the per-sample 1S peak is encoded in sample ids and would
  need transcription with explicit eV semantics. CuInS2 ACS Nano exposes the
  size-energy relation only through figures.
- **Size-semantics (non-spherical).** Not a blocker for ZnSe (spherical,
  `diameter_nm`). Would be a blocker for any perovskite route (cuboidal edge
  length must use `edge_length_nm` + morphology, never coerced to diameter).
- **Duplicates.** No candidate duplicates the committed InP / Yu CdSe /
  Moreels PbS sets; ZnSe and CuInS2 are genuinely new materials.
- **Circularity.** ZnSe and CuInS2 (MDPI) use direct SAXS/TEM/XRD sizing, so they
  are not circular with their own optics. Circularity risk would only arise if a
  curator later mixed them with the Yu 2003 / Moreels 2009 calibration curves;
  the leakage boundary above forbids that.

## Verification Status (Honesty Record)

- ZnSe Table 1 contents, direct-SAXS sizing, `diameter_nm` axis, DOI, journal,
  and the NIHPA-author-manuscript nature of the PMC copy: **confirmed** via the
  PMC mirror `PMC8872037` and PubMed `35221489`.
- ZnSe ChemRxiv preprint existence and DOI `10.26434/chemrxiv-2021-m8kbg-v4`:
  **confirmed**; its Creative Commons license: **UNCONFIRMED** (ChemRxiv returned
  HTTP 403 to automated fetches; no single default license).
- CuInS2 ACS Nano CC-BY-NC-ND license and figure-derived surface: **confirmed**
  via `PMC6117745`.
- CuInS2 MDPI CC-BY and emission/temperature focus: **confirmed** via search +
  PMC metadata (`PMC10650527`); full per-sample table contents not independently
  fetched (MDPI / ResearchGate mirrors returned HTTP 403).
- No SHA-256 was computed or fabricated; no external bytes were downloaded.

## Blockers

`BLOCKER_NO_CONFIRMED_OPEN_LICENSE_DIRECT_TABULAR_SECOND_MATERIAL_ROUTE`

The strongest direct, machine-readable, second-material table (ZnSe / Toufanian
2021) lacks a confirmed redistributable license. The cleanest CC-BY routes
(MDPI CuInS2) are emission/temperature studies or figure-derived rather than a
clean direct (size, absorption-energy) table. No Tier-1 open dataset
(Zenodo / Figshare) exists. A confirmable open + tabular + direct route was not
established in this pass, so a cautious `SOURCE_LIMITED` is the correct verdict
rather than an unsupported `READY`.

## Why SOURCE_LIMITED (not READY, not SOURCE_BLOCKED)

- **Not READY:** the task forbids fabricating license text or SHAs, and prefers
  a cautious verdict over an unsupported `READY`. The one direct/tabular route
  has an unconfirmed license; a license must be verified on a redistributable
  version before any row task.
- **Not fully SOURCE_BLOCKED:** unlike `TASK-0810` (closed, figure-derived, no
  legal copy), a concrete near-ready route exists with a single, well-defined
  unblocking action (confirm a CC-BY/CC0 version of the ZnSe data) and a clean
  direct table already verified in structure.

## Pinned Candidate Route (Locator + Reuse Terms + Verify Pattern)

- **Source identity:** Toufanian, R.; Zhong, X.; Kays, J. C.; Saeboe, A. M.;
  Dennis, A. M. "Correlating ZnSe Quantum Dot Absorption with Particle Size and
  Concentration." *Chemistry of Materials* 2021, 33(18), 7527-7536.
- **Material:** ZnSe (nearly spherical, `diameter_nm`).
- **Locators:**
  - VoR (closed): DOI `10.1021/acs.chemmater.1c02501`.
  - PMC author manuscript (read-only): `PMC8872037`.
  - Preprint: ChemRxiv DOI `10.26434/chemrxiv-2021-m8kbg-v4`.
- **Data-bearing surface:** Table 1, 10 samples (QD361-QD422); per-sample SAXS
  diameter + 1S absorption-peak position. SI PDF on the ACS page.
- **Reuse terms (current):** no confirmed redistributable license. VoR closed;
  PMC is NIH Public Access read-only (not CC-BY); ChemRxiv license unverified.
  Do **not** vendor the article, SI, table, or extracted rows until a future
  task confirms a CC-BY/CC0 version.
- **Fetch/verify pattern for a future license-clear fetch** (no fetch performed
  now; SHA-256 to be computed only at first license-clear fetch — do not
  fabricate):

  ```text
  # Only after a maintainer-confirmed CC-BY/CC0 version is identified:
  # 1. Record the exact licensed URL and its license statement.
  # 2. Fetch that exact licensed file (article/SI/preprint PDF or dataset).
  # 3. Compute and pin the checksum at intake time:
  #      python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" <file>
  # 4. Store locator + license + SHA-256 in the source artifact README;
  #    do not vendor the bytes if the license forbids redistribution.
  ```

## Bounded Future Row-Curation Task Shape (Only If Later Confirmed READY)

This scout returns `SOURCE_LIMITED`, so no row task is unblocked now. If a future
maintainer-confirmed CC-BY/CC0 version of the ZnSe data is identified, a bounded
row task should:

1. Add a ZnSe `source_manifest.yaml` entry (DOI-pinned; license note recording
   the confirmed CC-BY/CC0 version; `checksum_policy`), keeping
   `inclusion_decision: excluded` until rows pass the readiness gate.
2. Transcribe Table 1 per-sample SAXS `diameter_nm` and the 1S absorption-peak
   position, converting the peak to `absorption_peak_eV` with explicit unit
   semantics; preserve each value as a direct table entry (no sizing-equation
   evaluation, no figure eyeballing).
3. Keep `absorption_peak_eV` strictly separate from emission and bandgap axes.
4. Record direct-vs-derived provenance, per-point size/energy uncertainty, and
   exclusion reasons for any sample that cannot carry full provenance; require
   at least six admissible rows.
5. Re-run the row-level readiness gate; do **not** run baseline metrics or
   unblock correction search in the row task.
6. Maintain the leakage boundary: ZnSe rows must never be combined with the
   Yu 2003 / Moreels 2009 calibration curves or back-computed sizing equations.

## No-Claim Wording

This scout makes no quantum-dot design-law, material-recommendation,
device-performance, biomedical, universal-size-law, transfer-success, or
discovery claim. It records only that one open-tabular direct-size
second-material route (ZnSe / Toufanian 2021) is the strongest candidate but is
license-limited, and that no fully admissible open route was confirmable in this
pass. Absorption, emission, and bandgap remain separate axes.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (source-admissibility scout; no scientific
  metric scored).
- **Canonical destination:** source-readiness gate (the campaign's transfer
  validity gate); this source-gate review note under `docs/reviews/`.
- **Review tier:** `none`; no RESULT / PRED / CLAIM / KNOW artifact.
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact and no `qd-*.yaml` row
  created; no manifest source entry added.
- **Rows curated:** 0. **Metrics run:** none. **Correction search:** still
  blocked.
- **Transfer-holdout blocker:** no confirmed open-licensed, machine-readable,
  DIRECT (size, energy) second-material route; the pinned ZnSe route needs a
  confirmed CC-BY/CC0 version before any row task.
- **Limitations:** ChemRxiv, MDPI, and ResearchGate mirrors returned HTTP 403 to
  automated access, so the ZnSe preprint license and the MDPI CuInS2 full table
  could not be independently fetched; both are recorded as unconfirmed. No bytes
  were fetched or vendored and no SHA-256 was fabricated.

## Sources

- ZnSe (Chem. Mater. 2021) PMC author manuscript: https://pmc.ncbi.nlm.nih.gov/articles/PMC8872037/
- ZnSe PubMed record: https://pubmed.ncbi.nlm.nih.gov/35221489/
- ZnSe version-of-record (ACS): https://pubs.acs.org/doi/10.1021/acs.chemmater.1c02501
- ZnSe ChemRxiv preprint landing: https://chemrxiv.org/engage/chemrxiv/article-details/611fb16651cfecd23196382b
- CuInS2 (ACS Nano 2018, CC-BY-NC-ND) PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC6117745/
- CuInS2 (Nanomaterials 2023, CC-BY) MDPI: https://www.mdpi.com/2079-4991/13/21/2892
- CuInS2 (Nanomaterials 2023) PMC mirror: https://pmc.ncbi.nlm.nih.gov/articles/PMC10650527/
- Lead-bromide perovskite preprint (arXiv): https://arxiv.org/abs/2004.08310
- ChemRxiv license options (FAQ): https://chemrxiv.org/engage/chemrxiv/submission-information

## Verdict

`SOURCE_LIMITED`
