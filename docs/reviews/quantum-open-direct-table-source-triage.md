# Quantum Open Direct-Table Source Triage

**Task:** TASK-0347
**Status:** triage (no row values added; no manifest edits beyond
optional metadata; no benchmark scored; no claim promoted)
**Campaign:** Quantum Size Effects
**Inputs reviewed:**

- `docs/campaigns/quantum-size-effects.md`
- `docs/reviews/quantum-jasieniak-2011-source-artifact-package.md`
  (TASK-0334, BLOCKER state)
- `docs/reviews/quantum-direct-measurement-source-triage.md`
  (TASK-0298, the original triage)
- `docs/reviews/quantum-size-direct-absorption-seed-review.md`
  (TASK-0291, BLOCKED on Yu 2003 figure digitisation)
- `docs/quantum-direct-measurement-digitization-protocol.md`
  (TASK-0306, defines acceptable digitisation workflow)
- `data/quantum_dots/source_manifest.yaml`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`

## Scope

The Jasieniak 2011 band-edge source remains the best direct candidate
for `bandgap_eV` curation but is access-blocked: the ACS Supporting
Information requires a subscription, and committing the raw PDF or
its parsed tables to the repository would breach the publisher's
redistribution terms. TASK-0291 (Yu 2003 direct absorption seed)
remains BLOCKED for the same pattern (figure-only data plus
non-redistributable tables).

This triage finds alternative quantum-dot direct-measurement source
candidates that may bypass the ACS-SI blocker via open access, an
institutional repository, PMC, an arXiv supplement, a publisher SI
with clear public access, or a maintainer-provided file path. It
does not curate any row, does not edit `qd-*.yaml`, does not estimate
figure coordinates, and does not run a benchmark.

## Decision Vocabulary

Each candidate is classified with the same vocabulary used in
TASK-0298:

- **Provenance class** — `likely_direct_measurement`,
  `calibration_derived`, `theory_or_model_only`,
  `core_shell_or_confounded`, `unsuitable`.
- **Expected row type** — `table_derived` (rows live in a printed
  table; the digitisation protocol's Step 1 alone is sufficient),
  `digitization_required` (rows live in figures and need the full
  Step 2 WebPlotDigitizer workflow before they may be committed), or
  `blocked` (neither table nor figure data is accessible without
  breaching reuse).
- **Access status** — `open_access`,
  `publisher_si_public`, `pmc_open_access`, `arxiv_supplement`,
  `institutional_repository`, `maintainer_file_path`, or
  `subscription_blocked`.

Per the digitisation protocol, an LLM agent must not estimate figure
coordinates by eye. Every `digitization_required` candidate must run
through the committed digitisation workflow before any row is
committed.

## Candidate Set (5 sources)

### C1. Hens & Moreels 2012 — RSC *J. Mater. Chem.* 22, 10406

- **Citation:** Hens, Z.; Moreels, I. (2012) *J. Mater. Chem.* **22**, 10406.
  DOI [10.1039/c2jm30760j](https://doi.org/10.1039/c2jm30760j).
- **Property coverage:** `absorption_peak_eV` (first-exciton peak),
  optical bandgap; primarily PbS and CdSe.
- **Material family:** PbS, CdSe, with secondary mention of PbSe.
- **Provenance class:** `likely_direct_measurement` (review article
  but presents tabulated source values, with per-row primary-source
  attribution that the curator must preserve when a row is committed).
- **Expected row type:** `table_derived` for the rows the review
  retabulates; `digitization_required` for the figure-only points.
- **Access status:** RSC publishes its supporting information
  separately; the article PDF behind paywall but the SI page is
  often publicly accessible. **Curator must verify SI access before
  committing source artifacts.** Status: `publisher_si_public`
  (probable).
- **Reuse notes:** RSC SI is **not** open access by default. Curator
  must check the per-article license and the SI footer for reuse
  terms; commit only metadata locators unless the SI is explicitly
  CC-licensed.
- **Rank vs Jasieniak 2011:** **Better as a first-attempt source.**
  Hens-Moreels is a curated cross-source compilation; its
  per-row primary-source attribution makes it easier to commit a
  small `qd-*.yaml` slice with clean provenance back to the
  underlying primary publications. Jasieniak 2011 is access-blocked
  on a single ACS publication.

### C2. Mulvaney group open-access compilations (Allan & Delerue 2010 etc.)

- **Citation example:** Allan, G.; Delerue, C. (2010) *J. Phys.
  Chem. C* **114**, 9027 (or later open-access tight-binding
  treatments). Use whichever the maintainer can access cleanly.
- **Property coverage:** `bandgap_eV` from tight-binding plus matching
  experimental compilations for CdSe, PbS, PbSe, InAs.
- **Material family:** CdSe, PbS, PbSe, InAs.
- **Provenance class:** `theory_or_model_only` for the tight-binding
  values themselves; `likely_direct_measurement` for the experimental
  rows the paper cites and retabulates from primary publications.
- **Expected row type:** `table_derived` for the experimental
  comparison tables when present; `digitization_required` for figure
  comparisons.
- **Access status:** mixed — early Mulvaney/Allan/Delerue papers are
  often available via institutional repositories or PMC if NIH-
  funded; the underlying primary measurement papers vary.
- **Reuse notes:** rows derived from theory must enter `qd-*.yaml`
  only as `mass_class: model_inferred` / `radius_class: model_inferred`
  and stay excluded from the true-measurement axis per the TASK-0345
  ingestion-plan mass-provenance rule.
- **Rank vs Jasieniak 2011:** **Equal or slightly weaker.** Useful
  as a *comparison surface* (model-inferred axis), not as a
  measurement seed. Should not be the first candidate the curator
  attempts.

### C3. NanoMine / Materials Project / NOMAD open databases

- **Source locator:** `https://nanomine.org/`,
  `https://nomad-lab.eu/`, `https://www.materialsproject.org/`
  (each curated separately; not a single source).
- **Property coverage:** mixed; varies per database. NanoMine has
  experimental data; Materials Project leans computational; NOMAD
  aggregates published computations and some experimental records.
- **Material family:** broad inorganic materials including
  semiconductor nanocrystals where contributed.
- **Provenance class:** `likely_direct_measurement` for the
  experimental records that cite a primary publication;
  `theory_or_model_only` otherwise.
- **Expected row type:** `table_derived` (records exposed via API
  or downloadable CSV with documented schemas).
- **Access status:** `open_access` with documented license terms (CC
  variants typically); explicit per-record license metadata.
- **Reuse notes:** check each record's license and primary-source
  attribution before committing. Use the database identifier in the
  source manifest, not the underlying publication, only after
  verifying the database itself retains primary attribution.
- **Rank vs Jasieniak 2011:** **Promising secondary candidate.**
  Lower friction than chasing publisher SIs but requires per-record
  curation discipline. The curator must not let database normalisation
  silently fold `Msini`-style mass class semantics into a single
  `true_mass` axis (the analogous discipline-failure mode for the
  quantum-dot campaign is mixing absorption peak with bandgap).

### C4. arXiv condensed-matter preprints with supplementary tables

- **Source locator:** `https://arxiv.org/list/cond-mat.mes-hall/`
  search for "quantum dot mass radius" or "exciton energy size
  table".
- **Property coverage:** depends on candidate paper; commonly
  absorption peak, emission peak, exciton fine structure, sometimes
  band-edge.
- **Material family:** varies by paper.
- **Provenance class:** `likely_direct_measurement` for experimental
  preprints; `theory_or_model_only` for theory preprints.
- **Expected row type:** `table_derived` when the preprint's
  supplement is a CSV or LaTeX `tabular`; `digitization_required`
  when only a figure is provided.
- **Access status:** `arxiv_supplement` — author's accepted manuscript
  with attached supplementary files; explicit author-grants-arXiv
  license; verify per-paper license before committing.
- **Reuse notes:** arXiv's perpetual-license terms allow archival
  redistribution; per-paper licences may add additional permissions.
  Commit derived `qd-*.yaml` rows only when the preprint's data
  policy is explicit.
- **Rank vs Jasieniak 2011:** **Best route for new data** when a
  specific preprint has a CSV supplement covering one material
  family. Curator must avoid mixing preprint values with the
  Jasieniak 2011 axis until both pass the readiness gate
  independently.

### C5. PMC open-access reprints of NIH-funded quantum-dot characterisation papers

- **Source locator:** PubMed Central search
  `https://www.ncbi.nlm.nih.gov/pmc/?term=cdse+quantum+dot+absorption+peak+size`
  and analogous searches for PbS/PbSe.
- **Property coverage:** mix of absorption peak, emission peak,
  bandgap, depending on paper.
- **Material family:** varies; commonly CdSe, CdS, PbS where the
  funding source mandated PMC deposit.
- **Provenance class:** `likely_direct_measurement` (papers that
  reach PMC are the published version-of-record).
- **Expected row type:** mixed — PMC reprints carry the same
  tables and figures as the original publication; access to the
  Supporting Information depends on whether the PMC deposit included
  SI files.
- **Access status:** `pmc_open_access` (article body) plus
  per-paper variability for SI; check each candidate before
  committing source artifacts.
- **Reuse notes:** PMC open-access articles are public under their
  recorded licence (most NIH-funded papers carry an author manuscript
  licence that allows reuse with attribution). Commit derived
  `qd-*.yaml` rows only after recording the per-article licence.
- **Rank vs Jasieniak 2011:** **Genuinely promising route** because
  PMC deposit is a hard public-access policy. Curator should run a
  targeted PMC search before the next row-curation task and prefer
  any PMC reprint whose article body contains a printed (size,
  energy) table.

## Ranking Summary

| Rank | Candidate | Why | Caveats |
| --- | --- | --- | --- |
| 1 | **C5 (PMC open-access reprints)** | Hard public-access policy; no publisher gate; printed tables when present | Each candidate needs per-paper licence verification |
| 2 | **C4 (arXiv preprints with CSV supplements)** | arXiv perpetual licence makes redistribution clean | Quality of supplement varies; preprints may differ from final paper |
| 3 | **C1 (Hens-Moreels 2012 RSC review)** | Cross-source compilation with per-row primary attribution; SI may be public | RSC SI not open by default; curator must verify access per article |
| 4 | **C3 (NanoMine / Materials Project / NOMAD)** | Open-access databases with documented licences | Schema mapping risk: easy to silently fold mass classes; per-record provenance discipline required |
| 5 | **C2 (Mulvaney / Allan-Delerue compilations)** | Useful as model-inferred comparison surface | Most rows are theory; cannot enter the true-measurement axis |

## Recommended Next Row-Curation Task

A future row-curation task should attempt the candidates in this
order:

1. **C5** — run a focused PMC search for CdSe and PbS direct
   absorption-peak or bandgap papers; pick **one** with a printed
   (size, energy) table; package it as a source artifact per the
   TASK-0334 pattern.
2. If C5 yields no clean candidate within a small triage window,
   fall back to **C4** (arXiv supplement) for one preprint with a
   CSV or LaTeX supplement.
3. If both C5 and C4 are exhausted, escalate to maintainer with the
   list of attempted candidates rather than relaxing the
   digitisation protocol.

This ordering keeps the campaign moving without breaching the
**three forbidden provenance modes** the digitisation protocol locks
in: LLM visual estimates, memory-derived values, and
polynomial-derived values.

## Decision: Does TASK-0291 / TASK-0292 Path Change?

**Not yet.** The triage finds promising alternatives but does not
commit a new source. `TASK-0291` (Yu 2003 absorption seed) and
`TASK-0292` (Jasieniak 2011 band-edge seed) remain BLOCKED until a
future row-curation task lands a usable artifact from one of the
ranked candidates. The unblock paths recorded in those task files
remain valid.

## What This Triage Did Not Do

- It did not commit any `qd-*.yaml` row.
- It did not estimate figure coordinates.
- It did not fetch any candidate source body.
- It did not edit `data/quantum_dots/source_manifest.yaml` to add
  any of the five candidates as accepted source families. The manifest
  records only a metadata-only, `excluded` Hens-Moreels 2012 candidate
  seed so future curators can see the triage result without treating it
  as an accepted measurement source.
- It did not promote any claim, knowledge entry, or canonical
  result.
- It did not change the BLOCKED status of `TASK-0291`, `TASK-0292`,
  or `TASK-0225`.

## Limitations

- The candidate set is intentionally short (five). The first
  row-curation task may discover that the highest-ranked candidate
  is not actually open after retrieval; that outcome is preserved
  as a `BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED` review (per the
  TASK-0334 pattern) rather than a relaxation of the digitisation
  protocol.
- The triage relies on publicly known database and repository
  conventions (PMC deposit policy, arXiv licence, NanoMine /
  Materials Project licences). The next curator must verify the
  current state of each candidate at retrieval time; conventions
  change.
- The ranking does not estimate how many rows a specific candidate
  would yield. That is a per-snapshot diagnostic owned by the row-
  curation task.
- This triage does not authorise live data fetches or commits of
  raw publisher PDFs.

## Verdict

`PARTIALLY_VALID` — the campaign now has a ranked list of
alternative open or open-leaning source candidates. No source is
unblocked by this triage; the next row-curation task should attempt
C5 (PMC) first and fall back through the ranked list rather than
returning to the Jasieniak 2011 blocker path.
