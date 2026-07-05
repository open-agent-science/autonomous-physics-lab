# MD-0002 Release README

Dataset: `MD-0002-materials-project-stable-ternary-oxides`

Version: `0.1.0`

This archive is a frozen benchmark dataset package for the Autonomous Physics
Lab Materials Property Residuals campaign. It contains a source-pinned slice of
362 stable ternary oxides from the Materials Project database version
`2026.04.13`, plus the manifests needed to reproduce the no-peek split and the
baseline benchmark context.

## What This Archive Contains

- `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`:
  normalized MD-0002 rows.
- `data/materials/snapshots/materials_project_md0002_2026.04.13.json`:
  raw pinned Materials Project API snapshot used to build the normalized rows.
- `data/materials/materials_md0002_snapshot_manifest.yaml`: source, checksum,
  release, and no-claim metadata.
- `data/materials/md0002_holdout_manifest.yaml`: frozen train, validation, and
  holdout split contract.
- `data/materials/materials_md0002_schema.md`: release-facing row schema.
- `data/materials/materials_md0002_license.yaml`: MD-0002-only license and
  attribution record.
- `results/EXP-0014/RUN-0001/report.md` and
  `results/EXP-0014/RUN-0001/result.yaml`: the scoped formation-energy
  baseline benchmark record used as reproducibility context.

The repository-wide `data/DATA_LICENSES.yaml` registry is intentionally not
included in this standalone archive. Its applicable entry is represented by the
MD-0002-specific license record above, so unrelated repository source-license
entries do not appear in the dataset payload.

## Source And License

MD-0002 is derived from Materials Project computed DFT data. The source data are
licensed CC BY 4.0 and require attribution to the Materials Project and Jain et
al.:

A. Jain et al., "Commentary: The Materials Project: A materials genome approach
to accelerating materials innovation", APL Materials 1, 011002 (2013),
doi:10.1063/1.4812323.

## Scope Boundary

MD-0002 is computed DFT benchmark data, not experimental measurement data. It is
not materials-design guidance, a synthesis recommendation, device-performance
evidence, biomedical evidence, or support for a universal materials law.

The formation-energy benchmark is slice-limited to this frozen MD-0002 release.
Band-gap rows remain diagnostic-only for the current promoted result path.

## DOI Note

The packaged snapshot manifest may record `external_dataset_doi: not_minted`
because archive bytes are built before Zenodo assigns the DOI. The final DOI is
recorded on the Zenodo record and in a repository record-back commit after
publication.
