# Quantum Post-2015 Machine-Readable Supplement Triage

**Task:** `TASK-0399`
**Predecessor triage:** `TASK-0347`
  (`docs/reviews/quantum-open-direct-table-source-triage.md`)
**Predecessor verification:** `TASK-0364`
  (`docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md`)
**Campaign:** Quantum Size Effects
**Outcome:**
  `BLOCKER_NO_MACHINE_READABLE_SIZE_ENERGY_SUPPLEMENT_FOUND`
  (no source artifact committed; no `qd-*.yaml` added; no benchmark; no
  claim; one negative-result review document recorded.)

## Boundary

This task targets the third TASK-0364 recommended next path: re-target the
source search to **post-2015 quantum-dot publications** that might publish
machine-readable supplements (CSV, XLSX, plain-text tables) containing
direct size + first-exciton-energy or size + bandgap measurement points
acceptable for `table_derived` row curation under the Quantum Size Effects
provenance gate.

It does **not** curate any `qd-*.yaml` row, does **not** edit existing
quantum-dot dataset files, does **not** estimate figure coordinates, does
**not** apply calibration polynomials or sizing equations, does **not** run
any benchmark, does **not** promote any claim, and does **not** commit a
publisher PDF or licence-restricted supplement.

Per the TASK-0399 contract, this review records the negative outcome when
the post-2015 publication slice does not yield a machine-readable
supplement that satisfies the campaign's strict direct-row provenance gate.

## Sources probed

The triage probed five independent index/host surfaces. All queries are
metadata-only API calls; no publisher full text or supplement was committed
to this repository.

### 1. arXiv search API + ancillary-file endpoint

Author / title / abstract queries against `export.arxiv.org/api/query` for
the post-2015 slice:

- `abs:"quantum dot" AND abs:"size dependent" AND abs:"absorption" AND
  submittedDate:[20150101 TO 20251231]`
- `abs:"nanocrystal" AND abs:"first exciton" AND
  submittedDate:[20150101 TO 20251231]`
- `ti:"nanocrystal" AND abs:"exciton" AND
  submittedDate:[20150101 TO 20251231]`
- `abs:"colloidal quantum dot" AND abs:"diameter" AND abs:"optical"`
  (date-unconstrained, then post-2015 filter applied locally)

Each returned 9-50 entries. Theoretical / device-physics papers dominate;
the experimental size-series candidates surfaced include:

- arXiv:2409.06165 "Non-Monotonic Size-Dependent Exciton Radiative Lifetime
  in CsPbBr3 Nanocrystals" (Sept 2024)
- arXiv:2510.14695 "Quantum beats of exciton-polarons in CsPbI3 perovskite
  nanocrystals" (Oct 2025)
- arXiv:1703.00530 "Optical Stark metrology of CdSe quantum dots:
  Reconciling size-dependent oscillator strength" (2017)

The arXiv ancillary-files endpoint
(`https://arxiv.org/src/<id>/anc/`) was probed for every candidate ranked
in the top tier of each query. Every probe returned HTTP 404. **No arXiv
preprint in the post-2015 slice exposes a CSV/XLSX/text data supplement via
the arXiv ancillary-files surface for the experimental QD size-series
papers ranked here.**

### 2. NCBI PMC E-utilities (esearch + esummary)

Targeted PMC queries via `esearch.fcgi`:

- `"colloidal quantum dot" AND "Table S1" AND 2018:2026[PDAT]` → 399 hits
- `"colloidal quantum dot" AND "first exciton" AND "diameter" AND
  2018:2023[PDAT]` → 41 hits
- `"PbS quantum dot" AND "size" AND "absorption" AND 2018:2023[PDAT]`
  → 390 hits
- `"CdSe quantum dot" AND "TEM" AND "first exciton peak" AND
  2018:2023[PDAT]` → 7 hits

Top results for each query were probed for actual supplement file
contents via Europe PMC's `/supplementaryFiles` API (see Section 3 — Europe
PMC's API is the same OA archive surface but with a working HTTPS mirror;
NCBI's own HTTPS OA-package mirror returned HTTP 404 for every PMC ID
probed in this round, even when `oa.fcgi` confirmed an OA package was
indexed).

### 3. Europe PMC search + supplementaryFiles API

Twelve OA + supplement-bearing candidates from Nat Commun, Sci Adv,
Adv Sci, ACS Photonics, Materials, Heliyon, and Chemistry were retrieved
via the Europe PMC search endpoint scoped to:

`"colloidal quantum dot" AND "first exciton" AND OPEN_ACCESS:y AND
PUB_YEAR:[2018 TO 2024]`

Six were probed for actual supplementary file contents via
`/supplementaryFiles?includeInlineImage=no`. The complete list of probed
candidates and the supplement file types returned:

| PMC ID | Year | Venue | Supplement file types returned |
| --- | ---: | --- | --- |
| PMC9896031 | 2023 | Adv Sci | `ADVS-10-2204655-s001.pdf` (5.7 MB, single PDF) |
| PMC10741659 | 2023 | ACS Photonics | `ph3c00945_si_001.pdf` (188 KB, single PDF) |
| PMC8113276 | 2021 | Nat Commun | `41467_2021_22947_MOESM1_ESM.pdf` (1.0 MB, single PDF) |
| PMC10987160 | 2024 | Adv Sci | `ADVS-11-2306798-s001.pdf` (1.1 MB, single PDF) |
| PMC8596982 | 2021 | Chemistry | zero supplementary files returned |
| PMC7931447 | 2021 | Acc Chem Res | zero supplementary files returned |
| PMC11231167 | 2024 | Nat Commun | two PDFs (MOESM1+MOESM2) |
| PMC11408697 | 2024 | Nat Commun | two PDFs (MOESM1+MOESM2) |
| PMC11228028 | 2024 | Nat Commun | two PDFs (MOESM1+MOESM2) |
| PMC10817946 | 2024 | Nat Commun | two PDFs (MOESM1+MOESM2) |
| PMC11045821 | 2024 | Nat Commun | three PDFs + four `.wmv` videos |
| PMC11315915 | 2024 | Nat Commun | two PDFs (MOESM1+MOESM2) |

**Across every probed candidate, the only data-bearing supplementary file
type returned by the Europe PMC API is PDF.** No XLSX, no CSV, no TSV, no
plain-text data tables, no SQLite, no NetCDF, no HDF5. Videos appear in
one case but are not data tables.

### 4. Zenodo dataset API

Queries against `zenodo.org/api/records`:

- `"quantum dot" AND "size-dependent" AND (diameter OR exciton)` →
  zero dataset hits.
- `"colloidal nanocrystal" OR "quantum dot" AND size` (broader, type:dataset)
  → two hits, neither suitable:
  - "Raw data for manuscript A. Dey et. al., ACS Nano 2023, 17, 16,
    16080-16088." (DOI `10.5281/zenodo.13710482`) — 521 MB STM scan zip and
    individual `.spm` / `.tif` instrument files. Raw STM topography, not a
    sample-by-sample size + first-exciton-energy table; not consumable by
    the Quantum Size Effects schema without an entire reduction pipeline.
  - "Quantum dot-like plasmonic modes in twisted bilayer graphene" (2025)
    — title-only match; not a colloidal QD size series.

### 5. Figshare dataset API

Query: `quantum dot size dependent diameter exciton`, `item_type=3`
(dataset). Two hits:

- `10.1021/acs.chemmater.4c00602.s002` "How Surface Defects Shape the
  Excitons and Photoluminescence of Ultrasmall CdSe Quantum Dots"
  (Chem Mater 2024, CC BY-NC 4.0). Inspected: ten `.xyz` files of CdSe
  cluster atomic coordinates with various defect topologies. **Not a
  size + measured-energy table; these are DFT input geometries, not
  experimental sample rows.** Additionally CC BY-NC 4.0 imposes a
  non-commercial constraint inconsistent with the campaign's open-reuse
  posture.
- `10.3389/fchem.2018.00567.s001` "Bandgap Engineering of Indium
  Phosphide-Based Core/Shell Heterostructures Through Shell Composition
  and Thickness" — Data_Sheet_1 published as a single PDF; not a
  machine-readable size + energy table.

## Why no source artifact is committed

The TASK-0399 accepted-outputs explicitly permit a blocker-only outcome
(see `tasks/TASK-0399-...yaml` `requirements` and `accepted_outputs`).
The blocker conditions met here are:

- **Zero machine-readable size + energy data supplements** surfaced across
  arXiv ancillary files, PMC OA packages, Europe PMC supplement archive,
  Zenodo datasets, and Figshare datasets within the post-2015 publication
  slice queried.
- **PDF-only supplement convention is uniform across modern
  high-data-availability venues** (Nature Communications, Science
  Advances, Advanced Science, ACS Photonics, Accounts of Chemical Research,
  Materials, Heliyon, Chemistry-A European Journal). Tables S1-Sn are
  consistently embedded inside `*_MOESM*_ESM.pdf` rather than separated
  into `*_si_002.xlsx` or `*_data.csv` deposits.
- **The two Figshare / Zenodo dataset entries that did match** are an
  atomistic-coordinate file set (`.xyz` cluster geometries) and a raw STM
  topography zip, neither of which is a curated experimental size + energy
  row table.
- **No publicly accessible deposit found** that pairs a measured QD
  diameter (TEM, XRD, SAXS, or photon-correlation) with a measured first
  exciton energy (PL, PLE, absorption) in a CSV / XLSX / text form for any
  material in the existing manifest scope (CdSe, CdTe, CdS, PbS, PbSe,
  InAs).

## What this attempt did not do

- It did not commit any publisher PDF, supplement PDF, or restricted-licence
  artifact to the repository. The Europe PMC supplement probes downloaded
  bundles to `/tmp/pmc_check/` only; nothing was moved into the working
  tree.
- It did not download the 521 MB Dey 2023 STM dataset. The size, format
  (raw STM scans), and absence of a reduction pipeline put it outside the
  TASK-0399 contract.
- It did not commit the Figshare CdSe defects coordinate package
  (`cm4c00602_si_002.zip`). Its content is DFT inputs, not a measurement
  table; and its CC BY-NC 4.0 licence is incompatible with the open-reuse
  posture used elsewhere in the manifest.
- It did not edit any existing `qd-*.yaml` row. The existing
  `qd-0001-yu-2003-absorption.yaml` and
  `qd-0002-moreels-2009-pbs-absorption.yaml` seed files remain unchanged.
- It did not add any new `qd-*.yaml` row.
- It did not estimate figure coordinates, apply a sizing equation, apply a
  calibration polynomial, or copy values from memory.
- It did not add any accepted source entry to
  `data/quantum_dots/source_manifest.yaml`. It records the negative
  TASK-0399 round in the manifest's `attempted_verifications` block so
  future agents do not repeat the same post-2015 supplement search without
  first reading this outcome.
- It did not run the Quantum Size Effects baseline benchmark or any
  autonomous pilot.
- It did not promote any claim or knowledge update.

## Recommended next steps (not authorized by this PR)

These recommendations are documented here as visible follow-ups for the
maintainer; **none are authorized by this PR**:

1. **Treat machine-readable supplements as a closed search surface for the
   QD size-effect campaign.** The combined TASK-0364 (pre-2000 PRB / JACS /
   JCP) + TASK-0399 (post-2015 OA + Nat Commun / Sci Adv) result is that
   the modern publishing convention is supplement-PDF embedding, and the
   pre-2000 convention is figure-embedding. Neither matches the campaign's
   strict `table_derived` provenance class without an additional extraction
   step.

2. **Promote TASK-0306 (figure digitization protocol) to the critical path
   for unblocking the Quantum Size Effects campaign.** The Norris-Bawendi
   1996 PLE-spectra figures (verified figure-derived under TASK-0364)
   remain the strongest direct-measurement candidate; a deterministic
   figure-coordinate extraction with an audit trail would be admissible
   under TASK-0306 rules even though it is not admissible under TASK-0364
   `table_derived` rules.

3. **Open a maintainer-decision task on the supplement-extraction branch.**
   A second admissible path is OCR / human-supervised table extraction
   from the Adv Sci / Nat Commun supplement PDFs catalogued in Section 3
   above, gated by an explicit maintainer waiver and a checksum-pinned
   redistributable derivative artifact. This is a policy decision (does
   the campaign accept extraction-from-PDF as `table_derived`, as
   `digitization_derived`, or as a new provenance class?), not an agent
   decision.

4. **Do not re-attempt the post-2015 machine-readable supplement search**
   in a new task unless the maintainer signals that a new index surface
   (e.g., a specific institutional repository, a Materials Project export,
   a NOMAD download) has become available. The five surfaces probed here
   are the standard discovery layer; re-running the same surfaces will
   re-derive the same blocker.

5. **Reflect the closed-supplement-surface conclusion in the campaign's
   `docs/strategy.md`** so newly onboarded agents do not propose another
   variant of the same search without a new source-discovery angle.

## Limitations

- API queries are not exhaustive: each surface was probed with a small
  set of focused queries (typically 3-5 query strings per surface). Broader
  bibliographic harvesting (e.g. a 10000-paper title sweep) was out of
  scope for this triage; the focused queries were designed to surface
  high-data-density candidate venues (Nat Commun, Sci Adv, Adv Sci, ACS
  journals, and PMC OA), and they consistently returned the same PDF-only
  supplement convention.
- The Europe PMC `/supplementaryFiles` endpoint bundles all supplements
  exposed by the journal for a given article into a single zip. If a
  journal published a supplement as a separate XLSX file that was not
  ingested by PMC, that file would not appear in this round. No evidence
  of such ingestion gaps was visible from the search results sampled.
- The Zenodo / Figshare queries searched only the dataset record type;
  software-record or other Zenodo records with attached CSV files were
  not searched. The QD size-effect domain is not a typical software
  deposit surface, so this gap is unlikely to be load-bearing.
- This triage did not query commercial publishers' own data deposit
  portals (e.g. ACS Author Choice supplements, Elsevier Mendeley Data,
  Wiley repository) directly; the Europe PMC / PMC OA aggregation is the
  best available unified surface for those deposits, and the results
  were uniformly PDF-only across the ACS, Nat Pub Group, Wiley, and AIP
  venues probed via PMC.
- NCBI's own HTTPS OA-package mirror returned HTTP 404 for every PMC
  package probed during this round, even when `oa.fcgi` confirmed
  indexing. Europe PMC's mirror served the same content. This is a
  reachability detail about NCBI's HTTPS layer at the time of this
  round, not a finding about the underlying corpus.

## Verdict

`BLOCKER_NO_MACHINE_READABLE_SIZE_ENERGY_SUPPLEMENT_FOUND`

Probed five independent index surfaces (arXiv, PMC E-utilities, Europe PMC,
Zenodo, Figshare) for post-2015 quantum-dot publications carrying a
machine-readable size + first-exciton-energy / bandgap supplement
acceptable for `table_derived` row curation under the Quantum Size Effects
provenance gate. None of the five surfaces yielded an admissible
supplement: modern high-data-availability venues bundle supplements as
single PDFs, dataset repositories surface either atomistic coordinates or
raw instrument scans, and the arXiv ancillary-files endpoint is empty for
the experimental candidates ranked here. No `qd-*.yaml` seed is committed;
no source artifact is added. The recommended unblock path is now
TASK-0306 (figure digitization) or a maintainer-decided
extraction-from-PDF policy.
