# Jasieniak 2011 Source Artifact Package

Task: `TASK-0334`
Source ID: `jasieniak-2011-acs-nano-band-edge`
Package status: `METADATA_ONLY_BLOCKER`
Review date: 2026-05-22

## Purpose

This directory records the deterministic source-artifact plan for the
Jasieniak 2011 band-edge source path. It is not a row-level dataset and does
not authorize `qd-*.yaml` entries.

## Source Locator

- Article DOI: `10.1021/nn201681s`
- DOI URL: `https://doi.org/10.1021/nn201681s`
- ACS article page: `https://pubs.acs.org/doi/abs/10.1021/nn201681s`
- Expected Supporting Information locator:
  `https://pubs.acs.org/doi/suppl/10.1021/nn201681s/suppl_file/nn201681s_si_001.pdf`
- Expected upstream file name: `nn201681s_si_001.pdf`

## Expected Evidence Class

The reviewed ACS metadata surface indicates that the Supporting Information
contains tabulated energy-point data and full-page size-dependent energy-level
diagrams. A future curator must verify the actual file before using it.

Accepted future artifact forms:

- source-table extraction from the official Supporting Information;
- checksum-pinned maintainer-provided SI file, if repository policy permits;
- deterministic figure-digitization package following
  `docs/quantum-direct-measurement-digitization-protocol.md`.

Rejected provenance forms:

- LLM-estimated graph coordinates;
- values recalled from memory;
- values generated from a sizing polynomial or calibration curve;
- generic optical absorption or emission peaks relabeled as band-edge rows.

## Checksum And Archive Plan

If the official SI is retrieved, record the following before any row curation:

```text
source_file: nn201681s_si_001.pdf
retrieved_from: https://pubs.acs.org/doi/suppl/10.1021/nn201681s/suppl_file/nn201681s_si_001.pdf
retrieved_at_utc: <ISO-8601 timestamp>
sha256: <sha256 digest of retrieved file>
archival_status: doi_pinned | url_archived | maintainer_supplied
redistribution_decision: metadata_only | file_committed_with_permission
```

Default posture is `metadata_only`: commit the checksum and extraction notes,
not the publisher PDF or full table, unless a maintainer confirms the license
and repository policy allow redistribution.

## Table And Figure Identifiers To Verify

Before `TASK-0336` or any equivalent row-curation task starts, verify:

- the SI table or section that lists all energy points;
- whether values are direct table entries or must be derived from valence and
  conduction band-edge components;
- material labels for CdSe, CdTe, PbS, and PbSe;
- diameter/radius convention and units;
- uncertainty semantics, including whether uncertainty is measured, fitted, or
  absent;
- figure panels used only if table rows are insufficient.

## Current Blocker

No deterministic source artifact is committed in this directory yet. This
package records the locator and acquisition plan only.

Do not curate rows from this directory until one of these exists:

- checksum-pinned SI/table evidence;
- a reviewed non-copyrighted table extraction;
- a deterministic digitization artifact with calibration and extracted points.

## Guardrails

- Do not commit ACS PDFs, figures, or full tables unless redistribution is
  explicitly allowed.
- Do not add `qd-*.yaml` rows from this metadata-only package.
- Do not run `TASK-0225`, `TASK-0293`, or `TASK-0336` from this package alone.
- Do not promote scientific claims, device claims, synthesis guidance, or
  biomedical claims from this source-artifact blocker.
