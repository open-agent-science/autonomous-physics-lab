# MD-0002 Deterministic Archive Package Dry Run

Task: `TASK-0900`
Dataset: `MD-0002-materials-project-stable-ternary-oxides`
Primary manifest: `data/materials/materials_md0002_snapshot_manifest.yaml`
Verdict: `DETERMINISTIC_ARCHIVE_DRY_RUN_READY_MAINTAINER_GATED`

## Scope

This dry run turns the TASK-0887 external-release decision packet into an
inspectable deterministic package plan. It verifies the allowlisted repository
files, records their byte sizes and SHA-256 hashes, and defines the archive
ordering/checksum procedure a maintainer can run at a later release tag.

No external upload was attempted. No release tag was created. No DOI was minted
or declined. No MD-0002 rows, holdout membership, source snapshot, or
RESULT-0021 metrics were changed.

## Package Boundary

Package identity:

- dataset id: `MD-0002-materials-project-stable-ternary-oxides`
- dataset version: `0.1.0`
- source provider: Materials Project
- source database version: `2026.04.13`
- source license: `CC BY 4.0`
- normalized dataset checksum: `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1`
- raw snapshot checksum: `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567`
- external dataset DOI: `not_minted`
- release tag: `not_created`

The package remains computed-DFT benchmark data and curation metadata. It is
not experimental measurement data, material recommendation, synthesis guidance,
device-performance evidence, biomedical evidence, or support for a universal
materials law.

## Deterministic Ordering Rule

A release package should use this explicit allowlist in the exact order shown
below. The archive builder should normalize path separators to `/`, preserve
file bytes exactly as committed at the selected release tag, and record the
final archive filename, byte size, and archive-level SHA-256 after packaging.

No generated board views, agent scratch directories, live API credentials,
notebooks, caches, uncommitted replay output, or external-upload metadata should
enter the archive.

## Dry-Run File Manifest

| Order | Path | Bytes | SHA-256 |
| ---: | --- | ---: | --- |
| 1 | `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml` | 515699 | `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1` |
| 2 | `data/materials/md0002_holdout_manifest.yaml` | 7627 | `c98c6e699d5fd0146f3456c4726bf71adbd5aeea2cff6aada9190671095e5451` |
| 3 | `data/materials/materials_md0002_snapshot_manifest.yaml` | 5392 | `a5644ad51128cf94097ffd1f4673346bdf003a7cc6cbbaeea9a2a3d645f9a691` |
| 4 | `data/materials/snapshots/materials_project_md0002_2026.04.13.json` | 249272 | `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567` |
| 5 | `data/materials/README.md` | 4256 | `343880f2cc2971af79758b44dc27c352cee808f7b2d40d8dc48701787db55fe2` |
| 6 | `data/materials/schema.md` | 5366 | `75031c10aaeece15e1eba569478dbd16c2ccc2b3d17d5cd597fcbea6f715b6ed` |
| 7 | `data/materials/fixtures/md0002_schema_fixture.yaml` | 3678 | `a02d19553888ecd65d5e89de295b052580733b4d6830ed930185b305716b50f8` |
| 8 | `data/DATA_LICENSES.yaml` | 15630 | `83cca13ee600ca5b3d1326a87a18374df0b9cfb06aae53e6054a8d5ebed208b7` |
| 9 | `results/EXP-0014/RUN-0001/report.md` | 603 | `accf7f33e77a8bf1003e1e086e0b54291b3371aba8e625f8b81de8d220ec5e81` |
| 10 | `results/EXP-0014/RUN-0001/result.yaml` | 7573 | `9765a4d07792dbcca02267fd59170c6a51ab028a9fdfd499ce721eb1689c1bf2` |
| 11 | `docs/reviews/materials-md0002-release-metadata-closeout.md` | 3553 | `c02b2676f729771487a97152cbc7fe8f714e769114aebe88b863a14d472e1b1f` |
| 12 | `docs/reviews/materials-md0002-external-release-decision-packet.md` | 9758 | `02207f3d956170f6021a145a5c68f2fd093d04e3838ff835ea4ce0f463d1c967` |

The allowlist preserves the Materials Project attribution surface, the
normalized dataset, the raw pinned snapshot already committed under CC BY 4.0,
the holdout split, schema/fixture documentation, license registry, RESULT-0021
context, metadata closeout, and the TASK-0887 maintainer decision packet.

## Local Dry-Run Result

A package archive was not created in this PR. The dry run therefore has no local
archive path, archive byte size, archive SHA-256, release URL, release tag, or
DOI. That boundary is intentional: the task prepares the deterministic package
surface only, and external publication remains maintainer-gated.

The maintainer-ready package command can be implemented later as a small
cross-platform helper that consumes the ordered allowlist above in a clean
checkout at an approved release tag. The helper should fail if any file is
missing, if any file hash differs from the table, if extra files are present, or
if the archive-level checksum is not recorded.

## Release-Route Impact

- GitHub release route: ready for a deterministic package helper after the
  maintainer approves the release tag and archive filename.
- Zenodo-like DOI route: still blocked on maintainer approval of repository
  account, creators/ORCIDs, metadata, DOI posture, and final archive checksum.
- OSF-like route: same blocker set as any external repository; attribution and
  no-claim wording must survive the upload form.
- No external release route: remains the safest default until a citable dataset
  endpoint is needed.

## Maintainer Actions Still Required

1. Choose release route and DOI posture.
2. Approve a release tag such as `dataset-md0002-v0.1.0`.
3. Confirm creator metadata and Materials Project attribution text.
4. Run or approve a deterministic archive helper in a clean checkout at the tag.
5. Record final archive filename, byte size, SHA-256, external URL, and DOI or
   DOI-declined state in a later maintainer-approved update.
6. Keep public text within the computed-DFT and no-claim boundary.

## Stop Conditions

Stop before external release if any of these occur:

- package contents diverge from the allowlist without a new review;
- any file hash differs unexpectedly at the release tag;
- Materials Project CC BY 4.0 attribution cannot be preserved;
- creator/license/DOI metadata is incomplete;
- the archive-level SHA-256 is not recorded;
- the release description frames MD-0002 as experimental measurement data,
  material recommendation, synthesis guidance, device-performance evidence, or
  a universal materials-law result.

## Output Routing

- Task verdict: `DETERMINISTIC_ARCHIVE_DRY_RUN_READY_MAINTAINER_GATED`.
- Canonical destination: `docs/reviews/` package-readiness dry-run note.
- Review tier: none; this is dataset-publication readiness, not a RESULT.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Prediction impact: none.
- Result impact: none; RESULT-0021 is unchanged.
- Dataset impact: no row, holdout, checksum, DOI, release tag, or external
  archive mutation.
- Remaining blocker: maintainer decision and external repository action are
  required before any upload, DOI, or public release.