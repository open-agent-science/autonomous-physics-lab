# DEBCat Source Artifact Package

Task: `TASK-0628`
Source ID: `debcat-detached-eclipsing-binaries`
Package status: `METADATA_ONLY_BLOCKER`
Review date: 2026-06-06

## Purpose

This package pins the DEBCat detached-eclipsing-binary source locator,
retrieval metadata, checksum, citation posture, and row-curation blockers for
the Stellar Mass-Luminosity lane of the Textbook Formula Audit campaign.

It does not commit the DEBCat ASCII table, curate stellar rows, compute
luminosities, fit mass-luminosity exponents, run audit metrics, or promote
formula verdicts.

## Source Locator

- Catalogue page: `https://astro.keele.ac.uk/jkt/debcat/`
- Machine-readable ASCII table: `https://astro.keele.ac.uk/jkt/debcat/debs.dat`
- Publication/preprint: `https://arxiv.org/abs/1411.1219`
- Citation requested by source page: Southworth, J. (2015),
  "The DEBCat detached eclipsing binary catalogue", ASP Conference Series,
  496, 164.

## Retrieval Metadata

- Retrieval date UTC: `2026-06-06`
- HTTP Last-Modified for `debs.dat`: `Sat, 16 May 2026 11:14:34 GMT`
- HTTP ETag for `debs.dat`: `"17441-651ed6f2a15a0"`
- Content-Length: `95297` bytes
- Temporary sandbox path used for checksum only:
  `D:\Python\APLab\tmp\TASK-0628\debs.dat`
- SHA-256:
  `326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`

The temporary checksum file is value-bearing source data and is not committed.

## Current Decision

The source is suitable for a later row-curation task because it supplies
detached-binary component masses, radii, effective temperatures, and source
references in a maintained public catalogue. However, no explicit
redistribution license was found on the consulted catalogue page beyond the
request to cite the DEBCat paper. Therefore this package records the locator
and checksum but keeps raw table redistribution blocked.

## Required Follow-Up Before Rows

- Confirm whether repository redistribution of the ASCII table is permitted,
  or keep using metadata-only checksum pinning with maintainer approval.
- Define the normalized component schema before copying any values.
- Preserve binary-system identifiers and never split components from the same
  physical binary across train/test or holdout lanes.
- Preserve mass uncertainty semantics separately from radius, temperature, and
  luminosity fields.
- Define admissible luminosity provenance without using Gaia model-derived
  mass fields as benchmark truth.

## Guardrails

- Do not add `data/textbook_formula_audit/stellar_ml/*.yaml` rows from this
  package alone.
- Do not use Gaia `mass_flame`, isochrone-derived masses, or other
  model-derived masses as benchmark truth.
- Do not compute luminosities, fit an exponent, run residual metrics, create
  results, create predictions, promote claims, or promote knowledge from this
  package.
