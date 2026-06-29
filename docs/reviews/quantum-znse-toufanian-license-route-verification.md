# Quantum ZnSe Toufanian License Route Verification

**Task:** `TASK-0870`
**Campaign:** `quantum-size-effects`
**Source:** Toufanian, R.; Zhong, X.; Kays, J. C.; Saeboe, A. M.; Dennis, A. M.,
"Correlating ZnSe Quantum Dot Absorption with Particle Size and Concentration,"
*Chemistry of Materials* 2021, 33(18), 7527-7536, DOI
`10.1021/acs.chemmater.1c02501`.
**Verdict:** `SOURCE_ROUTE_READY_LIMITED_FACTUAL_EXTRACT_SOURCE_BYTES_BLOCKED`

## Decision

The Toufanian 2021 ZnSe route is now maintainer-acceptable for committed
factual numeric rows under the existing source-rights framework, but it is not a
source-byte redistribution route.

This resolves the earlier `NEEDS_MAINTAINER_SOURCE_DECISION` state from
`TASK-0829` by incorporating the later `TASK-0840` evidence:

- the ACS version of record and ChemRxiv v4 preprint are recorded as
  `CC BY-NC-ND 4.0`;
- the PMC mirror remains an NIHPA author manuscript, free to read but not a
  Creative Commons grant;
- publisher PDF bytes, figures, supporting information, and the Table 1 image
  are not vendored;
- the repository may commit individual factual numeric measurements
  re-expressed in the APL schema with attribution under the
  `limited_factual_extract` basis;
- the current repository already contains the accepted metadata and row file, so
  this task does not create or modify any value-bearing rows.

No CC-BY or CC0 data-bearing version was identified in the committed evidence.
The route is therefore "ready" only in the narrow limited-factual-extract sense,
not as a general redistributable source package.

## Evidence Review

| Artifact | Finding |
| --- | --- |
| `docs/reviews/quantum-open-tabular-transfer-source-scout.md` | Pinned Toufanian 2021 as the strongest direct, tabular second-material ZnSe route, but stopped at `NEEDS_MAINTAINER_SOURCE_DECISION` because the license was unresolved. |
| `docs/reviews/quantum-toufanian-2021-znse-source-artifact-and-extraction.md` | Records maintainer-confirmed `CC BY-NC-ND 4.0` on ACS and ChemRxiv v4, a no-vendored-bytes policy, and a limited factual extract basis for the curated measurements. |
| `data/quantum_dots/source_manifest.yaml` | Registers `toufanian-2021-znse` as an accepted source with direct SAXS `diameter_nm`, optical absorption rows, and no source-byte redistribution. |
| `data/DATA_LICENSES.yaml` | Declares the committed ZnSe rows as `limited_factual_extract_no_artifact_redistribution_with_attribution`; raw artifact bytes are not vendored. |
| `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml` | Existing curated rows are already present and tied to the source policy. This task does not edit them. |

## Source Policy

```yaml
source_id: toufanian-2021-znse
local_analysis_allowed: true
source_bytes_redistribution:
  allowed: false
  basis: none
derived_rows_publication:
  status: allowed
  basis: limited_factual_extract
substantial_extraction_review_required: true
covered_by_repo_license: false
```

The exact locator and checksum policy remain metadata-only:

- ACS version of record DOI: `10.1021/acs.chemmater.1c02501`
- ChemRxiv v4 DOI: `10.26434/chemrxiv-2021-m8kbg-v4`
- PMC mirror: `PMC8872037`
- version-of-record PDF SHA-256 recorded by the prior ledger:
  `9963096332e4fc37b389fe72f839e347cba9dc92f402634b30c8a17a30302b51`
- source bytes: not committed

## Future Task Shape

A new row-curation task for the same Toufanian Table 1 surface is not needed
unless the maintainer wants a separate audit of the already committed `qd-0004`
file. The next executable science task should instead use the frozen existing
ZnSe rows only under a separately scoped benchmark or readiness contract.

Recommended future task shape if the maintainer wants a next quantum transfer
step:

1. Treat the existing ZnSe rows as frozen input.
2. Re-run only an approved transfer benchmark or row-readiness audit.
3. Preserve the direct SAXS `diameter_nm` and `absorption_peak_eV` semantics.
4. Do not refit, add a correction term, search formulas, or mix ZnSe with the
   Yu 2003 / Moreels 2009 calibration-derived sizing curves unless the future
   task explicitly authorizes that comparison as a control.
5. Keep the source-byte no-vendoring policy in place.

If a later CC-BY or CC0 data-bearing version appears, a separate source-cleanup
task may update the manifest and license registry. That would not by itself
change the scientific rows or authorize new metrics.

## Stop Conditions

- Stop if a proposed workflow requires committing publisher PDF bytes, SI bytes,
  figure rasters, or table images from the Toufanian source.
- Stop if a future task tries to use this license decision to promote a
  quantum-dot design law, material recommendation, biomedical claim, universal
  size law, or CLAIM/KNOW artifact.
- Stop if the task reruns transfer metrics without a separate benchmark
  contract.

## Output Routing

- **Task verdict:** `not_applicable` for numerical science; source-readiness
  verdict is
  `SOURCE_ROUTE_READY_LIMITED_FACTUAL_EXTRACT_SOURCE_BYTES_BLOCKED`.
- **Canonical destination:** this source-policy review note under
  `docs/reviews/`; existing source manifest and license registry are treated as
  prior accepted evidence.
- **Review tier:** `none`; no RESULT, PRED, CLAIM, or KNOW artifact.
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no result artifact and no benchmark metrics.
- **Rows curated:** 0 in this task.
- **Publication blocker:** source bytes remain non-redistributable; only limited
  factual numeric extraction is available.

## No-Claim Wording

This note states only the source-rights route for the existing ZnSe row surface.
It makes no assertion that the quantum size-effect benchmark transfers to ZnSe,
that a correction model is valid, or that a universal size law exists.