# Quantum ZnSe Source Artifact + Extraction Ledger (Toufanian 2021)

**Task:** `TASK-0840`
**Campaign:** `quantum-size-effects`
**Source:** Toufanian, R.; Zhong, X.; Kays, J. C.; Saeboe, A. M.; Dennis, A. M.,
"Correlating ZnSe Quantum Dot Absorption with Particle Size and Concentration,"
*Chemistry of Materials* 2021, 33 (18), 7527-7536.
DOI `10.1021/acs.chemmater.1c02501`.
**Dataset produced:** `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`
**Verdict:** `ROWS_CURATED_LICENSE_LIMITED_FACTUAL_EXTRACT`

## Why this source

It is the strongest available open second-material transfer route for the
size-effect campaign and resolves the `NEEDS_MAINTAINER_SOURCE_DECISION` from the
open-tabular scout (TASK-0829):

- **Direct size axis:** particle diameter is measured by small-angle X-ray
  scattering (SAXS), modelled with a spherical log-normal form factor -- a direct
  structural measurement, NOT an optical-inversion sizing curve. This makes the
  rows non-circular for a size-energy transfer holdout (unlike Yu 2003 CdSe and
  Moreels 2009 PbS, whose diameters are calibration-derived).
- **Independent material:** ZnSe, distinct from the committed InP (Almeida
  qd-0003), CdSe (Yu qd-0001), and PbS (Moreels qd-0002) sets.
- **Machine-readable:** the per-sample values are a printed table (Table 1),
  read directly -- no figure digitization.

## License audit (the maintainer-confirmed gate)

| Version | License | Notes |
| --- | --- | --- |
| ACS version-of-record | **CC BY-NC-ND 4.0** (Open Access) | pubs.acs.org/doi/10.1021/acs.chemmater.1c02501; "Copyright 2021 The Authors ... licensed under CC-BY-NC-ND 4.0". |
| ChemRxiv preprint v4 | **CC BY-NC-ND 4.0** | doi:10.26434/chemrxiv-2021-m8kbg-v4; CC BY-NC-ND badge confirmed (22 Aug 2021, latest version). |
| PMC mirror | NIHPA author manuscript | PMC8872037; free-to-read, not a CC grant. |

The maintainer manually confirmed the displayed CC BY-NC-ND 4.0 license on the
ChemRxiv and ACS pages.

### Source-rights framework (per-source, not a blanket facts-only policy)

```yaml
rights:
  local_analysis_allowed: true
  source_bytes_redistribution:
    allowed: false
    basis: none
  derived_rows_publication:
    status: allowed
    basis: limited_factual_extract
  substantial_extraction_review_required: true   # 10 rows is ~all of Table 1
  covered_by_repo_license: false
```

Basis for `limited_factual_extract`: the committed values are individual numeric
measurements (SAXS diameters, 1S peak positions) -- facts, which are not
copyrightable. They are re-expressed in APL's own schema (not a copy of Table 1's
selection/arrangement), with attribution and DOI, for non-commercial research,
which preserves the BY (attribution), NC (non-commercial), and ND (no derivative
of the protected expression) terms. The publisher PDF, figures, Supporting
Information, and the Table 1 image are NOT vendored; only a locator + SHA-256 of
the version-of-record PDF are recorded
(`9963096332e4fc37b389fe72f839e347cba9dc92f402634b30c8a17a30302b51`).

## Extraction ledger (deterministic, table read)

- **Source surface:** Table 1, "Summary of MP-AES Data" (p. 7530 of the VoR).
- **Size axis:** the `diameter (nm)` column = SAXS mean +/- SD (footnote b).
  Copied verbatim per sample.
- **Energy axis:** each sample is named for its 1S absorption-peak position in nm
  (footnote a; "the 1S peak ... shifted from 361 nm to 422 nm"). `value_eV` =
  `1239.84 / lambda1s_nm`, rounded to 3 decimals. The peak carries nm precision
  (sample-id-encoded); no separate eV uncertainty is reported, so `uncertainty_eV`
  is omitted and the diameter SD is recorded in `notes` (the schema has no
  diameter-uncertainty field).
- **10 rows:** QD361..QD422, all `inclusion_status: included`,
  `property_kind: absorption_peak_eV`, `measurement_type: optical_absorption`,
  `morphology: spherical`.
- **Cross-check:** QD422 SAXS diameter 5.75 +/- 0.87 nm matches the purified-aliquot
  SAXS 5.74 +/- 0.98 nm (Figure S3), consistent within SD.

| Sample | diameter_nm (+/- SD) | 1S peak (nm) | value_eV |
| --- | --- | --- | --- |
| QD361 | 2.04 +/- 0.57 | 361 | 3.435 |
| QD364 | 2.21 +/- 0.58 | 364 | 3.406 |
| QD375 | 2.48 +/- 0.62 | 375 | 3.306 |
| QD383 | 2.86 +/- 0.67 | 383 | 3.237 |
| QD390 | 3.02 +/- 0.83 | 390 | 3.179 |
| QD397 | 3.46 +/- 0.48 | 397 | 3.123 |
| QD405 | 4.31 +/- 0.69 | 405 | 3.061 |
| QD410 | 4.42 +/- 0.70 | 410 | 3.024 |
| QD419 | 5.36 +/- 1.00 | 419 | 2.959 |
| QD422 | 5.75 +/- 0.87 | 422 | 2.938 |

## Leakage boundary

These ZnSe rows must never be mixed with the Yu 2003 CdSe or Moreels 2009 PbS
calibration-curve sizing equations, nor with any back-computed sizing relation.
They are independent direct measurements for a cross-material transfer holdout.

## Output routing

- **Canonical destination:** `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`
  (rows), `data/quantum_dots/source_manifest.yaml` (source entry),
  `data/DATA_LICENSES.yaml` (license), this note (ledger).
- **Review tier:** none; no RESULT/PRED/CLAIM/KNOW created. No benchmark metric run.
- **Next gate:** a separate transfer benchmark task may now test the frozen
  InP-validated size-energy model on this ZnSe holdout under controls (no refit).
- **No-claim wording:** this records a curated second-material dataset; it does
  not assert transfer success, a universal size law, or any discovery.
