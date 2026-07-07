# MD-0002 Zenodo Archive Noise Cleanup

Task: `TASK-0932`

Related task: `TASK-0924`

Decision: clean the v0.1.0 Zenodo archive before first publication.

## Context

The TASK-0900/TASK-0908 deterministic archive allowlist was useful as an
internal release dry run, but it carried repository-governance artifacts into
the standalone dataset payload. Before Zenodo publication, the archive should be
optimized for an external dataset reader: MD-0002 data, source provenance,
license attribution, schema, split contract, and the scoped benchmark record.

The cleanup happens before DOI publication, so changing the archive SHA is not a
record-breaking event.

## File Audit

Kept in the archive:

- `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`:
  primary normalized dataset.
- `data/materials/md0002_holdout_manifest.yaml`: frozen no-peek split contract.
- `data/materials/materials_md0002_snapshot_manifest.yaml`: source, checksum,
  and release metadata.
- `data/materials/snapshots/materials_project_md0002_2026.04.13.json`: pinned
  raw source snapshot behind the normalized rows.
- `data/materials/materials_md0002_release_readme.md`: standalone archive README.
- `data/materials/materials_md0002_schema.md`: MD-0002-specific release schema.
- `data/materials/materials_md0002_license.yaml`: MD-0002-only CC BY 4.0 source
  license and attribution record.
- `results/EXP-0014/RUN-0001/report.md` and
  `results/EXP-0014/RUN-0001/result.yaml`: scoped benchmark/reproducibility
  context.

Removed from the archive:

- `data/DATA_LICENSES.yaml`: repository-wide registry; includes unrelated
  source-license entries and creates avoidable standalone-package confusion.
- `data/materials/README.md`: repository-area README, not release-specific.
- `data/materials/schema.md`: broader MD-0001/future-ingestion guidance, not the
  MD-0002 release schema.
- `data/materials/fixtures/md0002_schema_fixture.yaml`: synthetic validation
  fixture; useful for repository tests but noisy in a dataset release archive.
- `docs/reviews/materials-md0002-release-metadata-closeout.md` and
  `docs/reviews/materials-md0002-external-release-decision-packet.md`: internal
  governance notes; important in the repository but not needed inside the
  Zenodo data payload.

## Rights Boundary

The applicable source license remains Materials Project CC BY 4.0. The cleanup
does not weaken attribution: the MD-0002 snapshot manifest, release README,
license record, upload pack, and Zenodo metadata all carry the Materials Project
and Jain et al. citation boundary.

No NC, NC-ND, permission-restricted, or unrelated source-license entry applies
to the MD-0002 archive payload.

## Clean Archive Facts

Command:

```bash
python3 scripts/package_materials_md0002_archive.py --output-dir <local-temp-dir>/apl-md0002-clean --archive-name md0002-v0.1.0.zip --force
```

Result:

- filename: `md0002-v0.1.0.zip`
- size: `795018` bytes
- SHA-256: `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22`
- file count: `9`

## Output Routing

- Task verdict: `ARCHIVE_PAYLOAD_CLEANED_BEFORE_ZENODO_PUBLICATION`.
- Canonical destination: deterministic MD-0002 archive helper, upload pack, and
  MD-0002-specific release metadata files.
- Review tier: none; dataset packaging metadata only.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Result impact: none; `RESULT-0021` is referenced unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Publication impact: safer, lower-noise Zenodo v0.1.0 archive before first DOI.
