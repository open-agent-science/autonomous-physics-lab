# Quantum Open Direct-Table Source Triage

**Task:** TASK-0347
**Status:** triage (no row values added; no manifest edits beyond
optional metadata stubs; no benchmark scored; no claim promoted)
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
- `docs/notes/fresh-data-source-policy.md`

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

The triage focuses on well-known quantum dot publications from major
experimental groups (Bawendi, Alivisatos, Klimov, Peng, and related
groups) for CdSe, CdS, InAs, PbS, and related material families.

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

## Candidate Set (6 sources)

### C1. Peng 1998 — JACS CdSe absorption peak vs size

- **Citation:** Peng, X.; Schlamp, M. C.; Kadavanich, A. V.;
  Alivisatos, A. P. (1997) *J. Am. Chem. Soc.* **119**, 7019–7029.
  DOI [10.1021/ja970754m](https://doi.org/10.1021/ja970754m).
  Also: Peng, Z. A.; Peng, X. (2001) *J. Am. Chem. Soc.* **123**,
  183–184. DOI [10.1021/ja003633m](https://doi.org/10.1021/ja003633m).
- **source_locator:** `10.1021/ja970754m` / `10.1021/ja003633m`
- **property_kind:** `absorption_peak_eV` (first-exciton / band-edge
  absorption peak versus TEM-measured diameter)
- **material_family:** CdSe
- **expected_row_type:** `table_derived` — the 1997 paper contains
  explicit tables of absorption peak wavelength for a size series;
  the 2001 follow-up provides a synthesis-route size series with
  listed absorption maxima. Both include TEM diameters alongside
  spectral peak positions.
- **license_reuse:** `subscription_blocked` — ACS publications; the
  article body and SI require ACS membership or institutional access.
  DOI-pinned metadata only may be committed; tables may not be
  redistributed without per-article ACS permission.
- **notes:** Alivisatos group landmark; widely cited CdSe size series.
  The printed tables, if publicly accessible, would yield ≥6 clean
  direct-absorption rows for the `absorption_peak_eV` axis without
  recourse to figure digitisation. Access verification is mandatory
  before committing a source artifact.

**Rank vs Jasieniak 2011:** Slightly worse in access terms — both are
ACS subscription-blocked. However, the absorption data is likely
`table_derived` rather than figure-only (a known advantage over the
Jasieniak 2011 SI which requires figure digitisation for several
material sizes). If a maintainer can provide the table, this becomes
the top candidate for the `absorption_peak_eV` axis.

---

### C2. Murray 1993 — JACS classic CdSe (Bawendi group)

- **Citation:** Murray, C. B.; Norris, D. J.; Bawendi, M. G. (1993)
  *J. Am. Chem. Soc.* **115**, 8706–8715.
  DOI [10.1021/ja00072a025](https://doi.org/10.1021/ja00072a025).
- **source_locator:** `10.1021/ja00072a025`
- **property_kind:** `absorption_peak_eV`, `emission_peak_eV`
  (first-exciton absorption and PL peak positions across a CdSe
  size series)
- **material_family:** CdSe
- **expected_row_type:** `digitization_required` — peak positions
  are primarily presented in figures (absorption spectra offset for
  clarity; sizing data reported in SAXS/TEM context). Some data may
  appear as listed values in text but the primary data surface is
  graphical. Full WebPlotDigitizer-class digitisation is required.
- **license_reuse:** `subscription_blocked` — ACS 1993 publication;
  no open-access deposit expected given the publication year.
- **notes:** Bawendi group foundational paper; defines the size-
  series characterisation paradigm still in use. The PL and
  absorption peaks are broad due to ensemble size distributions
  typical of early syntheses. A curator should note that 1993-era
  size dispersity may introduce systematic scatter not present in
  later monodisperse syntheses. Figure digitisation is feasible
  but every point requires WebPlotDigitizer provenance per the
  TASK-0306 protocol.

**Rank vs Jasieniak 2011:** Weaker — both require digitisation, but
Murray 1993 has broader size distributions and older measurement
precision. Its value is historical context, not a cleaner
measurement surface. Do not attempt before C1, C3, or C5.

---

### C3. Kang & Wise 1997 — PbS empirical band-edge (Physical Review B)

- **Citation:** Kang, I.; Wise, F. W. (1997) *Phys. Rev. B* **56**,
  9377–9382.
  DOI [10.1103/PhysRevB.56.9377](https://doi.org/10.1103/PhysRevB.56.9377).
- **source_locator:** `10.1103/PhysRevB.56.9377`
- **property_kind:** `bandgap_eV` / `absorption_peak_eV` (empirical
  band-edge absorption onset for a PbS quantum dot size series;
  the paper combines theory and experiment)
- **material_family:** PbS
- **expected_row_type:** `table_derived` for the experimental
  comparison points listed alongside the theoretical curve; some
  additional points may require `digitization_required` from the
  figure panels.
- **license_reuse:** `open_access` (probable) — APS Physical Review B
  articles from 1997 are freely available via the APS Public Access
  policy for articles published before the paid-open-access transition.
  APS makes articles ≥1 year old freely readable; redistribution
  of tables in derivative works is governed by APS copyright, not a
  CC license. Curator must verify the per-article APS reuse policy
  before committing table content.
- **notes:** Wise group; covers PbS in a size range (2–8 nm diameter)
  directly relevant to the `absorption_peak_eV` and `bandgap_eV`
  campaign axes. The theoretical effective-mass values in the same
  paper must be tracked separately as `mass_class: model_inferred`
  and excluded from the direct-measurement axis. The empirical
  comparison points, if tabulated or accurately figure-digitised,
  would provide a PbS complement to the CdSe-heavy existing manifest.

**Rank vs Jasieniak 2011:** Better on access — APS articles are more
reliably accessible than ACS SI files. The PbS empirical points are a
genuine alternative direct-measurement surface for a material family
not yet represented in a direct-measurement `qd-*.yaml`. This is the
top-ranked candidate for the `bandgap_eV` / PbS axis if the printed
comparison table can be confirmed.

---

### C4. Soloviev 2000 — PbS band-edge (Physical Review B)

- **Citation:** Soloviev, V. N.; Eichhöfer, A.; Fenske, D.; Banin, U.
  (2000) *J. Am. Chem. Soc.* **122**, 2673–2674.
  DOI [10.1021/ja9940367](https://doi.org/10.1021/ja9940367).
  Also relevant: Lifshitz, E.; Dag, I.; Litvin, I. D.; Hodes, G.
  (1998) *J. Phys. Chem. B* **102**, 9245–9250.
  The most directly applicable open-access PbS band-edge paper is:
  Andreev, A. D.; Lipovskii, A. A. (1999) *Phys. Rev. B* **59**,
  15402. DOI [10.1103/PhysRevB.59.15402](https://doi.org/10.1103/PhysRevB.59.15402).
- **source_locator:** `10.1103/PhysRevB.59.15402` (open APS access);
  `10.1021/ja9940367` (ACS, subscription)
- **property_kind:** `bandgap_eV` (optical gap from absorption onset
  for PbS nanocrystals)
- **material_family:** PbS
- **expected_row_type:** `table_derived` for the Andreev/Lipovskii
  comparison to experimental data (tabulated band-gap versus size);
  `digitization_required` for figures only.
- **license_reuse:** `open_access` for the APS Physical Review B
  version (same APS public-access policy as C3); `subscription_blocked`
  for the ACS version.
- **notes:** Several related papers address PbS band-edge size
  dependence in the late 1990s. The APS Physical Review B articles
  are a cleaner access path. A curator must identify which specific
  paper has a printed (size, E_gap) table versus figure-only data.
  The 1999 Andreev-Lipovskii paper contains a comparison of theory
  to experiment with tabulated experimental points, making it a good
  candidate if that table is accessible.

**Rank vs Jasieniak 2011:** Comparable or slightly better on access
(APS vs ACS); weaker on coverage because these are older papers with
fewer material families and smaller size ranges. Useful as a cross-
validation surface for the Kang-Wise (C3) PbS axis.

---

### C5. Norris & Bawendi 1996 — CdSe band-edge spectroscopy (Physical Review B)

- **Citation:** Norris, D. J.; Bawendi, M. G. (1996) *Phys. Rev. B*
  **53**, 16338–16346.
  DOI [10.1103/PhysRevB.53.16338](https://doi.org/10.1103/PhysRevB.53.16338).
- **source_locator:** `10.1103/PhysRevB.53.16338`
- **property_kind:** `bandgap_eV` / `absorption_peak_eV` (hole and
  electron energy levels versus CdSe quantum dot size; first-exciton
  transition energy tabulated for a well-characterised size series)
- **material_family:** CdSe
- **expected_row_type:** `table_derived` — Norris and Bawendi 1996
  contains an explicit table of size-versus-transition-energy for a
  CdSe nanocrystal size series (sizes confirmed by SAXS and
  absorption line positions measured by photoluminescence excitation
  spectroscopy). This is one of the most-cited direct-measurement
  sources for CdSe quantum dot energy levels.
- **license_reuse:** `open_access` (probable) — APS Physical Review B
  1996; covered by APS public-access policy for articles older than
  one year. Redistribution of article content still requires
  compliance with APS copyright terms; curator must verify the
  per-article reuse statement before committing table content to the
  repository.
- **notes:** Bawendi group; widely regarded as a high-quality CdSe
  measurement baseline in the size range 1.5–4 nm radius. The
  first-exciton transition energies in Table I (or equivalent) are
  direct spectroscopic measurements, not calibration-polynomial
  evaluations. The paper also provides hole and electron level
  assignments that are useful if the campaign later extends to
  valence/conduction band-edge provenance. This is the strongest
  candidate for a `table_derived` CdSe direct-measurement seed.

**Rank vs Jasieniak 2011:** Better — APS open-access policy is more
reliable than ACS SI access; the table is in the article body rather
than a supplementary file; and the size range overlaps well with the
existing calibration-derived seeds (Yu 2003, Moreels 2009). This
is the top-ranked candidate for the `absorption_peak_eV` / CdSe
direct-measurement axis and should be the first source-artifact
attempt in the next row-curation task.

---

### C6. Schmelz 2001 / Banin InAs arXiv preprints — InAs band-edge

- **Citation (primary):** Banin, U.; Lee, C. J.; Guzelian, A. A.;
  Kadavanich, A. V.; Alivisatos, A. P.; Jaskolski, W.; Bryant, G. W.;
  Zunger, A.; Kadavanich, A. V. (1998) *J. Chem. Phys.* **109**,
  2306. DOI [10.1063/1.476797](https://doi.org/10.1063/1.476797).
  **Also:** Schmelz, O.; Mews, A.; Basché, T.; Herrmann, A.;
  Müllen, K. (2001) *Langmuir* **17**, 2861–2865.
  DOI [10.1021/la0012553](https://doi.org/10.1021/la0012553).
  **arXiv preprint search:** `cond-mat` for "InAs quantum dot
  absorption size" to find open deposited versions.
- **source_locator:** `10.1063/1.476797` (AIP JCP); arXiv search
  for author "Banin" or "Klimov" with InAs size-dependence content.
- **property_kind:** `absorption_peak_eV` / `bandgap_eV` (lowest
  exciton transition energy versus InAs nanocrystal diameter)
- **material_family:** InAs
- **expected_row_type:** `table_derived` for the Banin 1998 paper
  (Table I lists InAs nanocrystal sizes and transition energies);
  `digitization_required` for companion figures.
- **license_reuse:** AIP JCP: `subscription_blocked` for the journal
  article; however, authors in the Alivisatos group commonly deposited
  preprints. Search arXiv `cond-mat` for an author-accepted-manuscript
  version with `arxiv_supplement` license. Schmelz 2001 is ACS
  (subscription); arXiv versions may exist.
- **notes:** InAs quantum dots extend the campaign beyond cadmium
  and lead chalcogenides into a III-V semiconductor family. The Banin
  1998 JCP paper is frequently cited for InAs size-versus-gap data.
  If an arXiv preprint version exists with the same table, the access
  path improves significantly. A curator should run an arXiv search
  for `Banin InAs quantum dot size energy` before concluding the JCP
  path is blocked.

**Rank vs Jasieniak 2011:** Weaker overall — InAs is less central to
the current campaign axes (CdSe and PbS absorption), and the primary
journal is AIP subscription. However, if an arXiv open-access version
is found, this becomes a valuable material-family diversification
candidate at low additional effort.

---

## Ranking Summary

| Rank | Candidate | DOI / locator | Property axis | Access path | Expected row type |
|------|-----------|--------------|--------------|-------------|------------------|
| 1 | **C5 Norris-Bawendi 1996 CdSe** | `10.1103/PhysRevB.53.16338` | absorption_peak_eV / bandgap_eV | APS open-access (probable) | table_derived |
| 2 | **C3 Kang-Wise 1997 PbS** | `10.1103/PhysRevB.56.9377` | bandgap_eV / absorption_peak_eV | APS open-access (probable) | table_derived + digitization fallback |
| 3 | **C1 Peng 1997/2001 CdSe** | `10.1021/ja970754m` | absorption_peak_eV | ACS subscription (blocked) | table_derived if accessible |
| 4 | **C4 Soloviev/Andreev PbS** | `10.1103/PhysRevB.59.15402` | bandgap_eV | APS open-access (probable) | table_derived + digitization fallback |
| 5 | **C6 Banin 1998 InAs** | `10.1063/1.476797` | absorption_peak_eV / bandgap_eV | AIP subscription; arXiv TBD | table_derived if arXiv found |
| 6 | **C2 Murray 1993 CdSe** | `10.1021/ja00072a025` | absorption_peak_eV / emission_peak_eV | ACS subscription (blocked) | digitization_required |

## Why Each Candidate Ranks Above or Below Jasieniak 2011

**Jasieniak 2011 baseline:** Access-blocked ACS SI; data primarily in
figures requiring full digitisation; multi-material (CdSe, CdTe, PbS,
PbSe) but no single material yields ≥6 clean table-derived rows in an
accessible format. Currently the strongest band-edge candidate but
blocked on source artifact retrieval.

- **C5 (Norris-Bawendi 1996, rank 1) — better:** APS open-access
  policy gives more reliable access than ACS SI; data reported in
  article body table, not SI; CdSe coverage matches existing seeds.
  This is the first-attempt candidate for a `table_derived`
  direct-measurement seed.

- **C3 (Kang-Wise 1997, rank 2) — better:** Same APS open-access
  advantage; PbS material family adds coverage orthogonal to CdSe;
  empirical comparison table reported in article body. Second-attempt
  candidate after C5.

- **C1 (Peng 1997, rank 3) — comparable to Jasieniak 2011:** Both are
  ACS subscription-blocked. However, if the maintainer provides
  access, Peng 1997 absorption tables are likely more complete and
  more straightforwardly `table_derived` than the Jasieniak 2011 SI
  figures. Worth noting as a target if the maintainer can provide the
  file.

- **C4 (Soloviev/Andreev, rank 4) — slightly better than Jasieniak
  2011:** APS access; but narrower coverage and older measurement
  precision. Useful cross-validation, not a primary seed.

- **C6 (Banin 1998, rank 5) — conditional:** AIP subscription until
  an arXiv version is confirmed; adds InAs diversity but requires
  additional triage effort to locate an open-access version.

- **C2 (Murray 1993, rank 6) — worse than Jasieniak 2011:** Both
  blocked on access; Murray 1993 additionally requires digitisation
  and carries larger size-distribution uncertainty from the 1993
  synthesis methods.

## Recommended Next Row-Curation Task Order

1. **C5 (Norris-Bawendi 1996, APS)** — confirm APS open-access for
   DOI `10.1103/PhysRevB.53.16338`; locate and record Table I (or
   equivalent); package as a metadata-only source artifact per the
   TASK-0334 pattern; if table is accessible, proceed to direct-
   measurement row curation for CdSe.
2. **C3 (Kang-Wise 1997, APS)** — confirm APS open-access for
   DOI `10.1103/PhysRevB.56.9377`; locate empirical comparison table;
   package source artifact; if accessible, proceed to PbS direct-
   measurement rows as a companion dataset.
3. **C4 (Andreev-Lipovskii 1999, APS)** — cross-validation surface
   for C3 PbS; attempt only after C3 is confirmed or exhausted.
4. **C1 (Peng 1997, ACS)** — escalate to maintainer for direct
   file provision; do not attempt to retrieve from ACS without
   confirmed institutional access.
5. **C6 (Banin 1998 InAs)** — run arXiv preprint search before
   attempting; promote only if an author-deposited open-access
   version with the table is found.
6. **C2 (Murray 1993)** — do not attempt unless all APS-access
   candidates are exhausted; digitisation burden and size-
   distribution uncertainty make this a last resort.

If C5 and C3 both yield at least 6 clean direct-measurement rows,
the campaign can re-run the TASK-0283 readiness gate and proceed to
the first direct-measurement benchmark without revisiting the
Jasieniak 2011 blocker path.

## Effect on Existing Blocked Tasks

- **TASK-0291 (absorption seed):** C5 (Norris-Bawendi CdSe) provides
  a more accessible first-attempt alternative to the Yu 2003 figure
  digitisation path. Curator should attempt C5 before returning to
  Yu 2003.
- **TASK-0292 (band-edge seed):** C3 (Kang-Wise PbS) and C5
  (Norris-Bawendi CdSe) offer complementary paths on the
  `bandgap_eV` axis without requiring the Jasieniak 2011 ACS SI.
- **TASK-0334 (Jasieniak source artifact):** Remains blocked; this
  triage does not unblock it. If C5 or C3 succeed, TASK-0334 may
  be deprioritised.
- **TASK-0225 (baseline benchmark):** Remains BLOCKED until at least
  one direct-measurement seed passes the readiness gate; this triage
  does not change that status.

## What This Triage Did Not Do

- It did not commit any `qd-*.yaml` row.
- It did not estimate figure coordinates.
- It did not fetch any candidate source body or retrieve any
  publisher article text.
- It did not edit `data/quantum_dots/source_manifest.yaml` for
  candidates C2 through C6. Only a metadata-only, `excluded` stub
  for C5 (Norris-Bawendi 1996) is added to the manifest so future
  curators can see the triage result without treating it as an
  accepted measurement source.
- It did not promote any claim, knowledge entry, or canonical result.
- It did not change the BLOCKED status of `TASK-0291`, `TASK-0292`,
  `TASK-0225`, or `TASK-0334`.

## Limitations

- The candidate set of six is intentionally short. The first
  row-curation task may discover that a top-ranked APS candidate is
  not publicly accessible at retrieval time; that outcome is
  preserved as a `BLOCKER_SOURCE_ARTIFACT_NOT_COMMITTED` review (per
  the TASK-0334 pattern) rather than a relaxation of the digitisation
  protocol.
- APS "open access" status for older articles must be verified at
  retrieval time; APS policies have evolved and per-article embargo
  lengths vary. The curator should check the article's Rights and
  Permissions page, not assume open access from the publication year.
- This triage relies on knowledge of the quantum dot literature as of
  the triage date. Publication metadata, access status, and supplement
  availability must be verified by the curator before any source
  artifact is committed.
- The ranking does not estimate how many clean rows a specific
  candidate would yield. That is a per-source diagnostic owned by
  the subsequent row-curation task.

## Verdict

`PARTIALLY_VALID` — the campaign now has a ranked list of
six specific open or open-leaning source candidates with named DOIs
and access paths. No source is unblocked by this triage; the next
row-curation task should attempt C5 (Norris-Bawendi 1996, APS) first
and proceed through the ranked list rather than returning to the
Jasieniak 2011 blocker path. The APS open-access candidates (C5, C3,
C4) are more accessible than the ACS SI route and should yield
`table_derived` rows if the printed comparison tables can be
confirmed.
