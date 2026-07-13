# Kim 2020 CdSe Optical Source Artifact Metadata (TASK-1027)

Source ID: `kim-2020-nanomaterials-cdse-optical`

Value-blind source-artifact package for Kim et al. 2020, "Influence of Size
and Shape Anisotropy on Optical Properties of CdSe Quantum Dots". No article
PDF, figure raster, supplementary file, digitized point, or measurement row is
committed here; retrieved bytes stay in a temporary uncommitted cache and are
pinned by SHA-256 only. See
`docs/reviews/quantum/kim-2020-cdse-source-artifact.md` for the full intake
review and verdict.

## Required intake fields (docs/quantum-direct-source-artifact-intake.md §2.2)

| Field | Value |
| --- | --- |
| `source_id` | `kim-2020-nanomaterials-cdse-optical` |
| `title` | Influence of Size and Shape Anisotropy on Optical Properties of CdSe Quantum Dots |
| `authors` | Kim, Sung Hun; Man, Minh Tan; Lee, Joong Wook; Park, Kyoung-Duck; Lee, Hong Seok |
| `year` | 2020 |
| `doi` | `10.3390/nano10081589` |
| `access_path` | `https://mdpi-res.com/d_attachment/nanomaterials/nanomaterials-10-01589/article_deploy/nanomaterials-10-01589.pdf` (publisher CDN copy of the version of record) |
| `retrieval_date` | 2026-07-13 |
| `checksum_sha256` | `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb` (1,368,239 bytes; PDF 1.7; not committed) |
| `license` | CC BY 4.0 on the version of record (Crossref `license.content-version: vor`, effective 2020-08-12; PMC OA record `license="CC BY"`, `retracted="no"`; JATS license block names Creative Commons Attribution) |
| `artifact_type` | `pdf` (retrieved and hash-pinned; redistribution decision `metadata_only`, PDF not vendored) |
| `property_kind` | `absorption_peak_eV` (primary candidate axis; `emission_peak_eV` and any bandgap interpretation are separate axes and must not be inferred from one another) |
| `material_family` | CdSe |
| `row_type_expected` | `digitization_required` (no printed row table and no supplementary material exist; see figure inventory) |

Additional intake metadata (§1.3):

- expected upstream filename: `nanomaterials-10-01589.pdf`
- archival status: `doi_pinned`
- redistribution decision: `metadata_only` (default posture; CC BY 4.0 would
  permit vendoring, but committing publisher bytes still requires an explicit
  maintainer decision per the intake protocol)
- table or figure identifiers to verify before row curation: Figure 1(a–d)
  HRTEM images, Figure 1(e–h) size histograms, Figure 3a absorption and
  fluorescence spectra, Figure 4(a–d) differential-absorption transitions,
  Figure 5 size-level plot; no table-wrap and no supplementary-material
  elements exist in the JATS full text
- accepted evidence class: `digitization_required`
- current blocker: none for source identity/rights; deterministic extraction
  preflight (axis calibration, per-point provenance, uncertainty ledger,
  geometry rule for anisotropy) is required before any row curation

## Pinned metadata artifacts (retrieved 2026-07-13; not committed)

| Artifact | Locator | SHA-256 |
| --- | --- | --- |
| Version-of-record PDF | publisher CDN path above | `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb` |
| Europe PMC JATS full text (62,029 bytes) | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7466547/fullTextXML` | `6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244` |
| Crossref work metadata (12,087 bytes; live-index snapshot of the access date) | `https://api.crossref.org/works/10.3390/nano10081589` | `6b3a36ba7160d7c3d12a54bc64b846ec358d569ee562e778e8ac64eca6526e9c` |
| PMC OA service record | `https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id=PMC7466547` | `sha256 not asserted (dated stateless API response; license and tgz locator recorded in the review note)` |

Access notes: `www.mdpi.com` article pages refuse scripted retrieval (Akamai
"Access Denied") and the `pmc.ncbi.nlm.nih.gov` article page sits behind a
browser-verification wall, so identity and license were pinned through the
publisher CDN PDF, Crossref, the PMC OA service, and Europe PMC instead. The
official PMC OA package `ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/f1/56/PMC7466547.tar.gz`
is recorded as a locator only (FTP egress is blocked in the task sandbox; no
checksum is asserted for an un-fetched artifact).

## Sample identifiers (identifier-level metadata only)

Four growth-time samples: `CdSe-1` (5 s), `CdSe-2` (1 min), `CdSe-3` (5 min),
`CdSe-4` (60 min). Per-sample mean diameter and per-sample size dispersion are
stated in the article text and Figure 1 caption as HRTEM Gaussian-fit
statistics in nm; those values are deliberately not transcribed here.
