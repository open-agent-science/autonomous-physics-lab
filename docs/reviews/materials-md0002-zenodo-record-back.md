# MD-0002 Zenodo Record Back

Task: `TASK-0924`
Date: 2026-07-05

## Verdict

`PASS` - the maintainer-published Zenodo record matches the approved MD-0002
v0.1.0 release packet and the downloaded ZIP matches the pre-upload archive
checksum.

## Published Record

| Field | Value |
| --- | --- |
| Zenodo record | <https://zenodo.org/records/21207072> |
| Version DOI | `10.5281/zenodo.21207072` |
| Concept DOI | `10.5281/zenodo.21207071` |
| Publication date | 2026-07-05 |
| Version | `0.1.0` |
| Resource type | Dataset |
| License | Creative Commons Attribution 4.0 International (`cc-by-4.0`) |

Creators on the published record:

- `Hladun, Roman`, ORCID `0009-0004-4853-5212`, affiliation
  `Open Agent Science / Autonomous Physics Lab`
- `Kutenyov, Andrii`, affiliation `Open Agent Science / Autonomous Physics Lab`

Related work:

- `10.1063/1.4812323`, relation `isDerivedFrom`, resource type
  `publication-article`

## File Verification

| Field | Value |
| --- | --- |
| Filename | `md0002-v0.1.0.zip` |
| Published size | 795,018 bytes |
| Published MD5 | `7cb2979574f7d39945793e1874b5d918` |
| Downloaded SHA-256 | `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22` |

The downloaded file size and MD5 match Zenodo's file metadata. The downloaded
SHA-256 matches the deterministic release archive recorded before upload.

## Repository Record Back

This PR records the published DOI and archive facts in:

- `data/materials/materials_md0002_snapshot_manifest.yaml`
- `data/materials/materials_md0002_release_readme.md`
- `docs/reviews/materials-md0002-zenodo-upload-pack.md`

The published archive was built from release tag `dataset-md0002-v0.1.0` before
Zenodo assigned the DOI. Therefore the archived manifest inside
`md0002-v0.1.0.zip` intentionally records `external_dataset_doi: not_minted`;
the live repository manifest records the post-publication DOI without changing
published bytes.

## Scientific And Rights Boundary

- No dataset rows changed.
- No holdout membership changed.
- No RESULT-0021 metrics changed.
- No new scientific claim was promoted.
- Materials Project CC BY 4.0 attribution remains visible in the Zenodo record
  and repository release metadata.
