# MD-0002 Deterministic Archive Package Helper

Task: `TASK-0908`
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

- verifies the explicit 12-file MD-0002 package allowlist before archive write;
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

## Local Dry-Run Result

Disposable output path: `C:\tmp\apl-task-0908-md0002-package`.

| Field | Value |
| --- | --- |
| Archive filename | `MD-0002-materials-project-stable-ternary-oxides-v0.1.0.zip` |
| Archive byte size | `832514` |
| Archive SHA-256 | `5023175a33f5050a35d435e9cba23ccee111734fec0b9987f09311ae919b1e85` |
| Packaged files | `12` |
| Generated manifest | `C:\tmp\apl-task-0908-md0002-package\MD-0002-materials-project-stable-ternary-oxides-v0.1.0.manifest.json` |

A repeat build to `C:\tmp\apl-task-0908-md0002-package-repeat` produced the
same archive byte size and SHA-256.

## Current Package Manifest

The package path list is unchanged from TASK-0900. One checksum changed since
TASK-0900 because `data/DATA_LICENSES.yaml` has accumulated later repository
license-registry entries on `main`; MD-0002 rows, the MD-0002 holdout manifest,
source snapshot, and `RESULT-0021` artifacts are unchanged.

| Order | Path | Bytes | SHA-256 |
| ---: | --- | ---: | --- |
| 1 | `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml` | 515699 | `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1` |
| 2 | `data/materials/md0002_holdout_manifest.yaml` | 7627 | `c98c6e699d5fd0146f3456c4726bf71adbd5aeea2cff6aada9190671095e5451` |
| 3 | `data/materials/materials_md0002_snapshot_manifest.yaml` | 5392 | `a5644ad51128cf94097ffd1f4673346bdf003a7cc6cbbaeea9a2a3d645f9a691` |
| 4 | `data/materials/snapshots/materials_project_md0002_2026.04.13.json` | 249272 | `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567` |
| 5 | `data/materials/README.md` | 4256 | `343880f2cc2971af79758b44dc27c352cee808f7b2d40d8dc48701787db55fe2` |
| 6 | `data/materials/schema.md` | 5366 | `75031c10aaeece15e1eba569478dbd16c2ccc2b3d17d5cd597fcbea6f715b6ed` |
| 7 | `data/materials/fixtures/md0002_schema_fixture.yaml` | 3678 | `a02d19553888ecd65d5e89de295b052580733b4d6830ed930185b305716b50f8` |
| 8 | `data/DATA_LICENSES.yaml` | 17713 | `75bbd5230d83c037bb64b39e2b4b35c154c56551bc9b99d48747c81a36da813f` |
| 9 | `results/EXP-0014/RUN-0001/report.md` | 603 | `accf7f33e77a8bf1003e1e086e0b54291b3371aba8e625f8b81de8d220ec5e81` |
| 10 | `results/EXP-0014/RUN-0001/result.yaml` | 7573 | `9765a4d07792dbcca02267fd59170c6a51ab028a9fdfd499ce721eb1689c1bf2` |
| 11 | `docs/reviews/materials-md0002-release-metadata-closeout.md` | 3553 | `c02b2676f729771487a97152cbc7fe8f714e769114aebe88b863a14d472e1b1f` |
| 12 | `docs/reviews/materials-md0002-external-release-decision-packet.md` | 9758 | `02207f3d956170f6021a145a5c68f2fd093d04e3838ff835ea4ce0f463d1c967` |

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