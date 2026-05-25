# Quantum PMC/arXiv Direct-Table Source Attempt

**Task:** `TASK-0364`
**Predecessor triage:** `TASK-0347` (`docs/reviews/quantum-open-direct-table-source-triage.md`)
**Campaign:** Quantum Size Effects
**Outcome:** `BLOCKER_NO_PRINTED_TABLES_FOUND` (no rows curated; no `qd-*.yaml` added; no benchmark; no claim)

## Boundary

This task attempted to convert one of the TASK-0347 ranked open-access /
arXiv candidates into a `table_derived` direct-measurement seed row for the
Quantum Size Effects campaign. It does **not** curate any row, does **not**
edit existing `qd-*.yaml` files, does **not** estimate figure coordinates,
does **not** apply calibration polynomials or sizing equations, does **not**
run any benchmark, and does **not** promote any claim or knowledge file.

Per the TASK-0364 contract, this review records the verification outcome
when no candidate from the TASK-0347 ranking yields a clean printed
table acceptable for direct-row curation.

## Candidates verified (5 of 6 from the TASK-0347 ranking)

The maintainer supplied PDF copies of five of the six TASK-0347 candidate
papers via the local sandbox path (`/tmp/`), explicitly not redistributable.
None of the PDFs were committed to this repository. The sixth candidate (C3
Kang-Wise 1997 PbS, DOI `10.1103/PhysRevB.56.9377`) was not provided, but
the verification result for the other five is informative enough on its own
to conclude this task.

| TASK-0347 rank | Candidate | DOI | Material | Page count | Printed `Table N` headers | Inline (size → energy) value pairs |
| ---: | --- | --- | --- | ---: | ---: | --- |
| 1 | Norris & Bawendi 1996 (C5) | `10.1103/PhysRevB.53.16338` | CdSe | 9 | 0 | none recovered from body text |
| 2 | Kang & Wise 1997 (C3) | `10.1103/PhysRevB.56.9377` | PbS | n/a (not provided) | n/a | n/a |
| 3 | Peng / Alivisatos 1997 (C1) | `10.1021/ja970754m` | CdSe / CdS core/shell | 11 | 0 | none recovered |
| 4 | Andreev & Lipovskii 1999 (C4) | `10.1103/PhysRevB.59.15402` | PbS / PbSe | 3 | 0 | none recovered |
| 5 | Banin 1998 (C6) | `10.1063/1.476797` | InAs | 5 | 0 (only "Table of Contents" header from the AIP journal masthead) | descriptive ranges only (e.g. "10 - 35 Å radii", "0.8 eV shift") |
| 6 | Murray, Norris, Bawendi 1993 (C2) | `10.1021/ja00072a025` | CdSe | 10 | 0 | none recovered |

Verification method per candidate:

- `pdftotext` extraction of every page;
- case-insensitive grep for `tabl[eE]` to find any printed table label;
- pattern-based grep for inline numerical pairs of the form
  `<size> Å . . . <energy> eV` (or the reverse) in the body text;
- inspection of figure captions to confirm the data-bearing surface is a
  figure rather than a table.

## Provenance-class assessment

Per the TASK-0306 digitization protocol vocabulary and the TASK-0298 /
TASK-0347 decision vocabulary:

- All five verified papers carry their size-vs-energy data in
  **figures only** (e.g. PLE spectra, energy-vs-`1/a²` plots, absorption
  spectra). The Banin 1998 paper, for example, presents the level structure
  as `FIG. 3: Map of levels plotted versus 1/a²` rather than as a printed
  table.
- None of the five papers exposes the underlying numerical sample-by-sample
  size + transition-energy pairs in either a printed table or as inline
  body-text values that can be parsed without estimating figure coordinates.
- Consequently the provenance class for all five is **`figure_derived`**,
  not `table_derived`. The TASK-0364 contract explicitly forbids LLM-
  estimated figure coordinates, calibration polynomials, sizing equations,
  memory-derived values, and non-redistributable publisher tables.

The TASK-0347 ranking labelled C5 and C3 as "table_derived (probable)" and
C4 as "table_derived + digitization fallback" based on publication-pattern
priors. Direct PDF inspection on this round did not confirm those priors
for any of the five verified candidates.

## Why no row is committed

The TASK-0364 accepted-outputs explicitly permit a blocker-only outcome:

> "If the selected source has clean direct table rows, curate a small seed
> set with schema-valid provenance; if not, produce a blocker review and no
> rows."

The blocker conditions met here are:

- **No printed table** found in any of the five verified candidates.
- **No inline body-text data values** found that could be parsed without
  figure coordinate estimation.
- **No arXiv or PMC open-access version** of any of these candidates was
  located via the arXiv API (`au:<lastname> AND ti:<topic>` searches
  returned no hits for the 1996–1999 vintage of these papers; the few
  Banin / Bawendi arXiv preprints that exist are from 2021 onward, not
  the 1996–1999 papers).
- **Publisher PDFs themselves are not redistributable** — APS (Phys. Rev. B),
  ACS (JACS), and AIP (JCP) all require subscription access; the
  maintainer-provided copies are held locally only and are not committed.

## What this attempt did not do

- It did not commit any publisher PDF (APS, ACS, or AIP) to the
  repository. None of the five sandbox-held PDFs are redistributable.
- It did not edit any existing `qd-*.yaml` row (the existing
  `qd-0001-yu-2003-absorption.yaml` and `qd-0002-moreels-2009-pbs-absorption.yaml`
  seed files remain unchanged).
- It did not add any new `qd-*.yaml` row.
- It did not estimate figure coordinates, apply a sizing equation, apply a
  calibration polynomial, or copy values from memory.
- It did not edit `data/quantum_dots/source_manifest.yaml`. A follow-up
  task that wants to record the figure-derived classification per
  source_id in the manifest may do so under a separate scope.
- It did not run the Quantum Size Effects baseline benchmark or any
  autonomous pilot.
- It did not promote any claim or knowledge update.

## Recommended next steps (not authorized by this PR)

These recommendations are documented here as visible follow-ups; **none are
authorized by this PR**:

1. **Run the TASK-0306 digitization protocol on Norris-Bawendi 1996 (C5).**
   The PLE-spectra figures in that paper are the strongest direct
   measurement surface among the five verified candidates and align with
   the existing CdSe seed (`qd-0001-yu-2003-absorption.yaml`). The TASK-0306
   protocol is the proper home for figure-coordinate extraction work, not
   TASK-0364.
2. **Re-target the search to QD papers with machine-readable supplements.**
   Newer (≈ 2015-onward) quantum-dot papers often publish CSV / Excel
   supplements through PMC or institutional repositories. A new triage task
   in the spirit of TASK-0347 — but scoped to post-2015 publications with
   explicit machine-readable SI — would have a higher probability of
   surfacing `table_derived` candidates without an ACS/APS/AIP paywall.
3. **Update the TASK-0347 triage ranking with the verified findings.** The
   "table_derived (probable)" labels on C5, C3, and C4 should be downgraded
   to "figure_derived" once this review is merged. This is a maintainer-side
   triage update, not an automatic agent edit.
4. **Do not re-attempt the verified five candidates in another row-curation
   task** without first satisfying TASK-0306 (figure digitization) or
   obtaining a publisher-licensed redistributable table (unlikely for these
   subscription venues).

## Limitations

- Verification used `pdftotext` for table detection. PDFs that encode tables
  as embedded images would not be detected by this method; however, all
  five papers verified here are standard typeset journal PDFs from PRB /
  JACS / JCP, where printed tables are typeset (not raster), so
  `pdftotext` is reliable for distinguishing "printed table" from
  "figure-only data" on these documents.
- One TASK-0347 candidate (C3 Kang-Wise 1997 PbS) was not provided by the
  maintainer for this round. Its verification is deferred; a future task may
  attempt it, but the publication-pattern prior is the same as C4
  (Andreev 1999, also APS PRB on PbS) which also turned out to be
  figure-only.
- The arXiv API searches were limited to author + title-term queries; deeper
  full-text search via INSPIRE-HEP / Google Scholar was not attempted in
  this round.
- The maintainer-provided Dupuis 1997 PDF was an unrelated PRB 56 paper
  ("Dimensional crossover and metal-insulator transition in
  quasi-two-dimensional disordered conductors", by N. Dupuis) — not the
  intended C3 Kang-Wise PbS candidate. It was excluded from this
  verification round.

## Verdict

`BLOCKER_NO_PRINTED_TABLES_FOUND`

Verified 5 of 6 TASK-0347 ranked candidates. None expose printed tables or
inline (size → energy) value pairs suitable for `table_derived` direct-row
curation under the TASK-0364 contract. No `qd-*.yaml` seed is committed.
The TASK-0306 digitization protocol or a new post-2015 machine-readable
supplement triage are the recommended next paths.
