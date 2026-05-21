# Jasieniak 2011 Band-Edge Digitization Package

Task: `TASK-0325`
Source path selected: `jasieniak-2011-acs-nano-band-edge`
Package status: `BLOCKER_NO_COMMITTED_SOURCE_TABLE_OR_DIGITIZATION_ARTIFACT`

## Scope

This directory records the bounded TASK-0325 attempt to prepare a direct
measurement package for the Jasieniak 2011 band-edge source path.

It is a blocker package, not a digitization artifact. It contains no row-level
measurements and must not be used as evidence for a `qd-*.yaml` dataset file.

## Local Evidence Audit

The source is already registered in
[`../source_manifest.yaml`](../../source_manifest.yaml) as
`jasieniak-2011-acs-nano-band-edge`, with DOI `10.1021/nn201681s`.

The existing review notes identify this source as the correct band-edge
first-attempt path, but also record the blocker:

- the Supporting Information table was not available to the previous agent;
- no row values, uncertainty fields, or per-material table references were
  reviewed locally;
- no deterministic figure-digitization artifact exists under this directory.

For this TASK-0325 pass, the repository was searched for committed
`nn201681s` source files, source tables, and existing digitization artifacts.
Only metadata and review notes are committed. No ACS Supporting Information
file, table extraction, axis-calibration CSV, or extracted-points CSV is
present in the repository.

## Decision

No `qd-*.yaml` band-edge seed is produced in this pass.

The repository does not currently contain enough committed source/table or
digitization evidence to curate the required `>=6` compliant direct rows
without inventing data or using LLM-estimated coordinates.

## Required Unblock Evidence

A future curator may replace this blocker with a row-producing package only
after one of these evidence paths is committed or supplied for review:

- a reviewed table extraction from the Jasieniak 2011 Supporting Information,
  with at least six direct rows and source-table locators;
- a deterministic WebPlotDigitizer-class artifact with `axis_calibration.csv`,
  `extracted_points.csv`, tool/version notes, per-point uncertainty, and row
  provenance;
- maintainer-provided rows with explicit source, units, derivation semantics,
  and redistribution constraints.

Rows must preserve the band-edge derivation semantics: the source must not be
collapsed into a generic optical absorption or emission dataset, and
`bandgap_eV` rows must document how the underlying valence/conduction band
edge or optical-gap values were used.

## Guardrails

- Do not commit raw article PDFs, full-resolution figures, or ACS Supporting
  Information files unless redistribution is explicitly permitted.
- Do not use LLM-estimated graph coordinates.
- Do not run the quantum baseline benchmark from this package.
- Do not promote claims, canonical results, device claims, synthesis guidance,
  or biomedical claims from this blocker.
