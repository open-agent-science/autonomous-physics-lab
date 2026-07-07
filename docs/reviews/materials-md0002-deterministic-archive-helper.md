# MD-0002 Deterministic Archive Package Helper

Task: `TASK-0908`
Cleanup update: `TASK-0932`
Dataset: `MD-0002-materials-project-stable-ternary-oxides`
Helper: `scripts/package_materials_md0002_archive.py`
Verdict: `DETERMINISTIC_ARCHIVE_HELPER_READY_MAINTAINER_GATED`
Review date: 2026-07-02

## Scope

This task turns the TASK-0900 dry-run allowlist into a deterministic,
cross-platform local helper. The helper verifies package file byte sizes and
SHA-256 hashes, writes a ZIP archive only to an explicit local output directory,
and writes a JSON package manifest beside the archive.

No release tag was created. No external upload was attempted. No DOI was minted
or declined. No MD-0002 rows, holdout membership, source snapshot content,
`RESULT-0021` metrics, claims, predictions, or knowledge artifacts were changed.

## Helper Behavior

Example maintainer/local command:

```powershell
.\.venv\Scripts\python.exe scripts\package_materials_md0002_archive.py `
  --output-dir C:\tmp\apl-task-0908-md0002-package `
  --force
```

Safety and determinism properties:

- verifies the explicit 9-file MD-0002 release-facing allowlist before archive
  write;
- preserves repository-relative `/` paths inside the archive;
- uses deterministic ZIP entry ordering from the allowlist;
- uses stored ZIP entries, fixed timestamp `1980-01-01T00:00:00`, and mode
  `0644` for each file;
- refuses repository-local output directories by default so generated ZIP and
  manifest files stay untracked;
- records `release_tag_created: false`, `external_upload_attempted: false`,
  `doi_minted_or_declined: false`, `md0002_rows_changed: false`,
  `holdout_membership_changed: false`, and `result_0021_changed: false` in the
  generated manifest.

## Current Clean Build Result

Disposable output path: `<local-temp-dir>/apl-md0002-clean`.

| Field | Value |
| --- | --- |
| Archive filename | `md0002-v0.1.0.zip` |
| Archive byte size | `795018` |
| Archive SHA-256 | `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22` |
| Packaged files | `9` |
| Generated manifest | `<local-temp-dir>/apl-md0002-clean/MD-0002-materials-project-stable-ternary-oxides-v0.1.0.manifest.json` |

A repeat build to `<local-temp-dir>/apl-md0002-clean-repeat` must produce the same
archive byte size and SHA-256.

## Current Package Manifest

TASK-0932 cleaned the package path list before first Zenodo publication. The
standalone archive now carries only release-facing MD-0002 payload files:
dataset, split contract, source/snapshot metadata, raw snapshot, MD-0002 README,
MD-0002 schema, MD-0002 license record, and the scoped `RESULT-0021` benchmark
record. The repository-wide license registry, generic materials README/schema,
synthetic schema fixture, and internal review packets remain in the repository
but are intentionally excluded from the ZIP.

| Order | Path | Bytes | SHA-256 |
| ---: | --- | ---: | --- |
| 1 | `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml` | 515699 | `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1` |
| 2 | `data/materials/md0002_holdout_manifest.yaml` | 7627 | `c98c6e699d5fd0146f3456c4726bf71adbd5aeea2cff6aada9190671095e5451` |
| 3 | `data/materials/materials_md0002_snapshot_manifest.yaml` | 6109 | `0e42fa98f7e9731818217ae8e8db6288c3873f2dbce17ebe206497dd3f21e019` |
| 4 | `data/materials/snapshots/materials_project_md0002_2026.04.13.json` | 249272 | `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567` |
| 5 | `data/materials/materials_md0002_release_readme.md` | 2598 | `44712b330985d7f251fa79fb9e41c568022cae19dbf9ec7351aca9103344d2f1` |
| 6 | `data/materials/materials_md0002_schema.md` | 2100 | `8ccd7efef9e5c14373bf7302ae7c1f471ac641e01fd666c034ba439011d47c5e` |
| 7 | `data/materials/materials_md0002_license.yaml` | 1861 | `e1e68a7a031760704ec0715740fcc36a225e1848e9caeadfca516d47f168db7f` |
| 8 | `results/EXP-0014/RUN-0001/report.md` | 603 | `accf7f33e77a8bf1003e1e086e0b54291b3371aba8e625f8b81de8d220ec5e81` |
| 9 | `results/EXP-0014/RUN-0001/result.yaml` | 7573 | `9765a4d07792dbcca02267fd59170c6a51ab028a9fdfd499ce721eb1689c1bf2` |

## Maintainer Actions Still Required

1. Choose release route and DOI posture.
2. Approve a release tag such as `dataset-md0002-v0.1.0`.
3. Confirm creator metadata and Materials Project attribution text.
4. Run the helper in a clean checkout at the approved tag and preserve the
   generated manifest.
5. Record final archive filename, byte size, SHA-256, external URL, and DOI or
   DOI-declined state in a later maintainer-approved update.
6. Keep all public text inside the computed-DFT and no-claim boundary.

## Stop Conditions

Stop before external release if any of these occur:

- package contents diverge from the helper allowlist without a new review;
- any package file hash differs at the approved release tag;
- Materials Project CC BY 4.0 attribution cannot be preserved;
- creator/license/DOI metadata is incomplete;
- the archive-level SHA-256 is not recorded;
- the release description frames MD-0002 as experimental measurement data,
  material recommendation, synthesis guidance, device-performance evidence,
  biomedical evidence, or a universal materials-law result.

## Output Routing

- Task verdict: `DETERMINISTIC_ARCHIVE_HELPER_READY_MAINTAINER_GATED`.
- Canonical destination: this dataset-publication readiness note and helper.
- Review tier: none; this is dataset-publication readiness, not a RESULT.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Result impact: none; `RESULT-0021` is unchanged.
- Dataset impact: helper and review note only; no row, holdout, source snapshot,
  DOI, release tag, or external archive mutation.
- Remaining blocker: maintainer decision and external repository action are
  required before any upload, DOI, or public release.
