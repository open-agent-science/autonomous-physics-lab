# Textbook Stellar M-L DEBCat Source Artifact Package

Task: `TASK-0628`
Domain: Textbook Formula Audit / Stellar mass-luminosity
Mode: source artifact packaging
Verdict: `DEBCAT_METADATA_PINNED_ROWS_BLOCKED`

## Scope

This review packages the DEBCat source artifact path selected by the landed
TASK-0610 source review. It pins the source locator, retrieval metadata,
checksum, citation posture, and row-curation blockers before any Stellar M-L
row curation.

It does not copy value-bearing DEBCat rows into the repository, compute
luminosities, fit mass-luminosity exponents, run empirical metrics, or promote
formula verdicts.

## Source Identity

- Catalogue: DEBCat catalogue of the physical properties of well-studied
  eclipsing binaries.
- Catalogue page: `https://astro.keele.ac.uk/jkt/debcat/`
- Machine-readable artifact: `https://astro.keele.ac.uk/jkt/debcat/debs.dat`
- Citation requested by source page: Southworth, J. (2015), "The DEBCat
  detached eclipsing binary catalogue", ASP Conference Series, 496, 164.
- Preprint: `https://arxiv.org/abs/1411.1219`

The catalogue page describes DEBCat as a maintained catalogue of detached
eclipsing binaries and states that the catalogue is updated when revised
results are published. It also records that the catalogue contains 374 systems
in the consulted update log.

## Retrieval And Checksum

The value-bearing ASCII table was downloaded only to sandbox temp for checksum
verification, not committed.

```text
retrieval_date_utc: 2026-06-06
temporary_sandbox_path: D:\Python\APLab\tmp\TASK-0628\debs.dat
artifact_url: https://astro.keele.ac.uk/jkt/debcat/debs.dat
http_last_modified: Sat, 16 May 2026 11:14:34 GMT
http_etag: "17441-651ed6f2a15a0"
content_length_bytes: 95297
raw_line_count_including_header: 375
sha256: 326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da
```

The committed source package records the checksum and metadata at:

```text
data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/
```

## License And Reuse Posture

The consulted DEBCat page is public and asks users to cite the DEBCat paper.
No explicit redistribution license for committing the value-bearing ASCII
table into this repository was found on that page during TASK-0628.

Decision: keep this package metadata-only. Do not commit `debs.dat` or derived
row values until maintainer/license review approves a value-bearing route.

## Row Semantics To Preserve Later

A later row-curation task must preserve:

- physical binary system identifier;
- component role, with primary and secondary components kept linked;
- component mass and mass uncertainty semantics;
- radius, effective-temperature, luminosity/log-luminosity, and metallicity
  provenance separately;
- source reference notes from DEBCat;
- source checksum and retrieval timestamp used for extraction.

The first no-leakage rule is system-level splitting: components from the same
physical binary must not be split across train/test or holdout lanes.

## Blockers Remaining

- raw DEBCat table is not committed;
- explicit redistribution license for committing the value-bearing table was
  not found;
- normalized component row schema is not reviewed;
- luminosity provenance policy is not defined;
- system-level holdout policy is not implemented;
- no row counts after inclusion/exclusion filters exist yet.

## Manifest Update

`data/textbook_formula_audit/stellar_ml/source_manifest.yaml` now records a
DEBCat candidate-source entry with the artifact locator, checksum policy,
metadata-only storage decision, and no-leakage notes.

## Output Routing

Task verdict: `DEBCAT_METADATA_PINNED_ROWS_BLOCKED`.

Canonical destination: metadata-only source artifact package plus source
manifest entry.

Review tier: none. This is not a RESULT artifact.

Gate A status: not applicable.

Gate B status: not applicable.

Claim impact: none.

Knowledge impact: none.

Limitations: source rows remain blocked until license/storage, row schema,
luminosity provenance, and holdout/no-leakage policies are reviewed.
