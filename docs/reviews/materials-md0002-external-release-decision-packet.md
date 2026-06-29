# MD-0002 External Dataset Release And DOI Decision Packet

Task: `TASK-0887`
Dataset: `MD-0002-materials-project-stable-ternary-oxides`
Primary manifest: `data/materials/materials_md0002_snapshot_manifest.yaml`
Verdict: `EXTERNAL_RELEASE_DECISION_PACKET_READY_MAINTAINER_GATED`

## Executive Decision

MD-0002 is internally reusable and content-pinned, but it is not yet an external dataset publication. The safest recommended path is a maintainer-gated external archive release only after a release tag, deterministic archive checksum, creator metadata, and final repository choice are frozen. Until then, MD-0002 should remain citable internally through the repository manifest and commit hash with `external_dataset_doi: not_minted`.

This packet does not change MD-0002 rows, holdout membership, `RESULT-0021` metrics, claims, predictions, or knowledge artifacts. It records the release choices and exact maintainer actions needed if external publication is approved.

## Current Readiness

| Item | Current state | Release implication |
| --- | --- | --- |
| Dataset id/version | `MD-0002-materials-project-stable-ternary-oxides`, version `0.1.0` | Stable enough for a named archive package. |
| Source license | Materials Project CC BY 4.0 | External release is plausible if attribution is preserved. |
| Source version | Materials Project database version `2026.04.13` | Release must pin this exact version. |
| Normalized checksum | `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1` | Already frozen for repository file integrity. |
| Raw snapshot checksum | `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567` | Can be included only with CC BY attribution and release checksum. |
| Rows | 724 normalized axis rows over 362 materials | Computed DFT rows, not experimental measurements. |
| Axes | formation energy per atom; band gap diagnostic only | Do not pool property axes or promote band gap metrics. |
| RESULT link | `RESULT-0021` is `AGENT_VALIDATED` | Benchmark evidence exists, but external dataset release is not claim endorsement. |
| External DOI/tag | not minted / not created | Maintainer action required. |

## Release Options

| Option | Package shape | DOI posture | Pros | Blocker / stop condition |
| --- | --- | --- | --- | --- |
| GitHub release artifact | Attach deterministic archive to a repository release tag such as `dataset-md0002-v0.1.0` | DOI declined unless paired with an external archive | Lowest operational friction; keeps release near code, tests, and result context | Stop if the release tag cannot be protected, archive checksum cannot be frozen, or GitHub release is not acceptable as a citable dataset endpoint. |
| Zenodo-like archive | Upload the deterministic archive with metadata, creators, license, source attribution, and related identifiers | Mint DOI if maintainer approves | Best citable dataset route; DOI can point to the exact archive package | Stop until maintainer confirms repository account, creators/ORCIDs, license field, upload metadata, and final archive checksum. |
| OSF-like archive | Upload the deterministic archive or a mirrored package with project metadata | DOI optional or declined | Useful if the maintainer wants project/context pages before DOI minting | Stop if OSF-style metadata cannot preserve Materials Project attribution, exact version, checksum, and no-claim boundary. |
| No external release yet | Keep repository-local manifest and internal citation only | DOI remains `not_minted` | Safest default; no external action or accidental overclaim | This is the current state; stop here if maintainer does not need a citable standalone dataset now. |
| DOI-declined internal citation | Explicitly record that v0.1.0 is not DOI-minted but cite by repository commit/tag | DOI declined for this version | Avoids premature archive work while keeping citation wording stable | Stop if downstream users require a DOI or if a later public release changes package contents. |

## Recommended Path

Choose **Zenodo-like DOI archive after a maintainer-approved release tag** if the immediate goal is a citable reusable dataset. Otherwise choose **DOI-declined internal citation** and keep MD-0002 inside the repository until a user or collaborator needs a standalone archive.

The recommended archive path should be two-step:

1. Create a repository release tag that freezes the exact MD-0002 package source paths.
2. Upload a deterministic archive to the chosen external repository and record the external DOI, archive checksum, and release URL in a later maintainer-approved update.

Do not mint a DOI directly from this task. The maintainer must decide the external repository account, creator metadata, and whether MD-0002 v0.1.0 is mature enough to cite as a standalone dataset.

## Proposed Package Contents

Include only committed, license-cleared, provenance-bearing files:

- `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`
- `data/materials/md0002_holdout_manifest.yaml`
- `data/materials/materials_md0002_snapshot_manifest.yaml`
- `data/materials/snapshots/materials_project_md0002_2026.04.13.json`
- `data/materials/README.md`
- `data/materials/schema.md`
- `data/materials/fixtures/md0002_schema_fixture.yaml`
- `data/DATA_LICENSES.yaml`
- `results/EXP-0014/RUN-0001/report.md`
- `results/EXP-0014/RUN-0001/result.yaml`
- `docs/reviews/materials-md0002-release-metadata-closeout.md`
- this decision packet

Exclude generated board views, agent scratch directories, live API credentials, notebooks, cache files, and any uncommitted local replay output.

## Archive Checksum Plan

- Use a maintainer-run packaging command in a clean checkout at the selected release tag.
- Build the archive from an explicit allowlist of package contents with deterministic file ordering.
- Record SHA-256 for the final archive file, not only for the normalized dataset.
- Verify that the normalized dataset checksum remains `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1` inside the archive.
- Record the external repository record URL, release tag, archive filename, archive byte size, and archive SHA-256 in a follow-up manifest update.

A later implementation task may add a small cross-platform package script, but this decision packet does not add tooling or create an archive.

## Citation And Attribution Text

Public-safe dataset citation draft, if the maintainer later approves external release:

> Autonomous Physics Lab, MD-0002 Materials Project stable ternary oxides dataset, version 0.1.0, derived from Materials Project database version 2026.04.13 under CC BY 4.0 attribution. Cite Jain et al., APL Materials 1, 011002 (2013), doi:10.1063/1.4812323, and the selected APL release tag / external archive DOI.

Required source attribution:

> Data from The Materials Project (materialsproject.org), licensed CC BY 4.0; cite Jain et al., APL Materials 1, 011002 (2013), doi:10.1063/1.4812323.

Creator metadata placeholders:

- Dataset package creator / maintainer: Roman Hladun, ORCID `https://orcid.org/0009-0004-4853-5212`.
- Additional APL contributors: maintainer to add only if they contributed to MD-0002 curation or release packaging.
- Source attribution: Materials Project / Jain et al. are source attribution, not APL dataset creators.

## No-Claim Wording

Use this wording in any release description:

> MD-0002 is a source-pinned computed-DFT benchmark dataset derived from Materials Project stable ternary oxides. It is not experimental measurement data, a materials-design recommendation set, a synthesis guide, a device-performance dataset, biomedical evidence, or support for a universal materials law. `RESULT-0021` is a scoped formation-energy benchmark on the frozen MD-0002 slice; band-gap rows remain diagnostic-only.

## Maintainer Actions If Release Is Approved

1. Choose the release route: GitHub release only, Zenodo-like DOI archive, OSF-like archive, or DOI-declined internal citation.
2. Confirm creator names, affiliations if any, and ORCID metadata.
3. Confirm license metadata for the archive package: source data CC BY 4.0 with Materials Project attribution; APL curation metadata under the repository license.
4. Create or approve a release tag such as `dataset-md0002-v0.1.0`.
5. Build the deterministic archive from the proposed allowlist and record its SHA-256.
6. If using an external repository, upload the archive, mint or decline DOI, and record the external URL/DOI/checksum in a follow-up task.
7. Keep any public description within the no-claim wording above.

## Stop Conditions

Stop without release if any of these hold:

- The archive contents differ from the committed allowlist and no new review occurs.
- The final archive SHA-256 is not recorded.
- Creator/ORCID/license metadata is incomplete.
- The external repository cannot preserve Materials Project CC BY 4.0 attribution.
- A release description frames MD-0002 as experimental measurement data or materials-design guidance.
- The maintainer has not approved DOI minting or external upload.

## Output Routing

- Task verdict: `EXTERNAL_RELEASE_DECISION_PACKET_READY_MAINTAINER_GATED`.
- Canonical destination: `docs/reviews/materials-md0002-external-release-decision-packet.md`.
- Review tier: none; this is dataset-publication readiness, not a RESULT artifact.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: none; `RESULT-0021` is unchanged.
- Prediction impact: none.
- Dataset impact: decision packet only; no row, holdout, checksum, DOI, release tag, or external archive mutation.
- Remaining blocker: maintainer decision and external repository action are required before any DOI or external release.
