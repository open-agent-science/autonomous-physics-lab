# Norris-Bawendi 1996 Source Artifact Package

Task: `TASK-0489`
Source ID: `norris-bawendi-1996-prb-cdse-band-edge`
Package status: `METADATA_ONLY_BLOCKER`
Review date: 2026-06-02

## Purpose

This directory records the deterministic source-artifact plan for the
Norris-Bawendi 1996 CdSe band-edge / first-exciton source path. It is not a
row-level dataset and does not authorize `qd-*.yaml` entries.

It complements the row-level digitization preflight recorded under
`docs/reviews/quantum-norris-bawendi-1996-digitization-preflight.md`
(`TASK-0398`) and the fuller source-artifact review under
`docs/reviews/quantum-norris-bawendi-source-artifact-review.md` (`TASK-0489`).

## Intake Metadata (13 required fields)

Per `docs/quantum-direct-source-artifact-intake.md` Section 2.2:

| Field | Value |
|---|---|
| `source_id` | `norris-bawendi-1996-prb-cdse-band-edge` |
| `title` | Measurement and Assignment of the Size-Dependent Optical Spectrum in CdSe Quantum Dots |
| `authors` | Norris, D. J.; Bawendi, M. G. |
| `year` | 1996 |
| `doi` | `10.1103/PhysRevB.53.16338` |
| `access_path` | `https://doi.org/10.1103/PhysRevB.53.16338` (APS article landing page) |
| `retrieval_date` | not retrieved in this task (no live fetch) |
| `checksum_sha256` | `PENDING` |
| `license` | APS Physical Review B publication; DOI-pinned metadata only. APS public-access policy may permit free reading of articles older than one year, but redistribution of tables or figures requires compliance with APS copyright terms. |
| `artifact_type` | `metadata_only` |
| `property_kind` | `absorption_peak_eV`, `bandgap_eV` |
| `material_family` | CdSe |
| `row_type_expected` | `digitization_required` (verified by `TASK-0364`; see below) |

## Source Locator

- Article DOI: `10.1103/PhysRevB.53.16338`
- DOI URL: `https://doi.org/10.1103/PhysRevB.53.16338`
- Journal: Physical Review B 53, 16338-16346 (1996)
- Material: CdSe quantum dots
- Size axis: radius_nm (per manifest candidate metadata)

## Verified Evidence Class

Unlike the Jasieniak 2011 path (where tabulated Supporting Information was
indicated but not retrieved), the Norris-Bawendi 1996 source has already been
inspected by `TASK-0364` via a maintainer-provided sandbox PDF copy (no
publisher PDF was committed to this repository):

- printed `Table N` headers recovered: 0
- inline body-text (size -> energy) value pairs recovered: 0
- verified provenance class: `figure_derived`
- outcome: `not_admissible_for_table_derived_curation`

See `docs/reviews/quantum-pmc-arxiv-direct-table-source-attempt.md` and the
`attempted_verifications` block (round `TASK-0364-2026-05-25`) in
`data/quantum_dots/source_manifest.yaml`.

This package therefore does **not** plan a table extraction. The only
admissible future artifact form is a deterministic WebPlotDigitizer-class
figure-digitization package.

Accepted future artifact form:

- deterministic figure-digitization package following
  `docs/quantum-direct-measurement-digitization-protocol.md`, committed under
  `data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`.

Rejected provenance forms:

- LLM-estimated graph coordinates;
- values recalled from memory;
- values generated from a sizing polynomial or calibration curve;
- table reconstruction back-computed from a calibration formula;
- generic optical absorption peaks relabeled as band-edge rows.

## Checksum And Archive Plan

If a maintainer or tool-equipped curator retrieves the article for a
digitization pass, record the following before any row curation:

```text
source_file: norris-bawendi-1996-cdse-band-edge.pdf
retrieved_from: https://doi.org/10.1103/PhysRevB.53.16338
retrieved_at_utc: <ISO-8601 timestamp>
sha256: <sha256 digest of retrieved file>
archival_status: doi_pinned | url_archived | maintainer_supplied
redistribution_decision: metadata_only | file_committed_with_permission
```

Default posture is `metadata_only`: commit the checksum, the figure-panel
reference, and the digitization artifact (axis calibration + extracted points),
not the publisher PDF or rasterized figure, unless a maintainer confirms the
APS license and repository policy allow redistribution.

## Figure Identifiers To Verify

Before any future row-curation task uses this source, a tool-equipped curator
must verify:

- the specific figure/panel that plots discrete (size, first-exciton-energy)
  points (PLE-spectroscopy / size-series surface);
- the size convention and units (radius vs diameter, nm);
- at least four axis-calibration anchors, preferably two per axis;
- at least six discrete points after exclusions;
- uncertainty semantics (per-point, per-method, or absent);
- whether any plotted point is attributed to a cited prior source that must be
  registered separately in `source_manifest.yaml`;
- that assignment-derived or model values are kept separate from direct
  spectroscopic measurements.

## Current Blocker

No deterministic source artifact is committed in this directory. This package
records the locator, verified evidence class, and acquisition plan only.

Do not curate rows from this directory until a deterministic digitization
artifact with axis calibration, extracted points, tool/version notes, and
coordinate uncertainty exists under
`data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`.

## Guardrails

- Do not commit APS PDFs, figures, or rasterized figure assets unless
  redistribution is explicitly allowed.
- Do not add `qd-*.yaml` rows from this metadata-only package.
- Do not run `TASK-0225`, `TASK-0293`, or `TASK-0336` from this package alone.
- Do not promote scientific claims, device claims, synthesis guidance, or
  biomedical claims from this source-artifact blocker.
