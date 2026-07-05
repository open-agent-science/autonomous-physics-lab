# MD-0002 Zenodo Upload Pack (v0.1.0)

Task: `TASK-0924`
Cleanup task: `TASK-0932`
Decision basis: D5 in
[maintainer-decision-day-2026-07-02.md](./maintainer-decision-day-2026-07-02.md)
(Zenodo DOI archive route approved).

This pack records the built archive facts and gives the maintainer a
copy-paste Zenodo submission. The upload and the Publish click are maintainer
actions; the DOI record-back is a follow-up commit under the same task.

## Archive Facts (built, verified, deterministic)

| Field | Value |
| --- | --- |
| Filename | `md0002-v0.1.0.zip` |
| Size | 795,018 bytes |
| SHA-256 | `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22` |
| Contents | 9 release-facing files, exactly the TASK-0932 cleaned allowlist (verified per-file hash + size) |
| Content basis | cleaned PR #1353 release tree; create `dataset-md0002-v0.1.0` on the merged content commit before upload |
| Build command | `python3 scripts/package_materials_md0002_archive.py --output-dir <local-dir> --archive-name md0002-v0.1.0.zip` |
| Determinism | rebuild produces a byte-identical archive (fixed zip timestamps, stored entries, fixed ordering) |

TASK-0932 intentionally removed repository-governance files from the standalone
payload before first publication: the repo-wide license registry, generic
materials README/schema, synthetic schema fixture, and internal review packets
are not inside the ZIP. Their applicable MD-0002 information is represented by
release-facing README, schema, license, snapshot manifest, and benchmark
artifacts.

The packaged snapshot manifest honestly reads
`external_dataset_doi: not_minted` — the minted DOI lives on the Zenodo record
and in the repository record-back commit, not inside the v0.1.0 archive bytes.

## Maintainer Steps (~10 minutes)

1. Create a Zenodo account at zenodo.org (log in with GitHub or ORCID).
2. "New upload" -> upload `md0002-v0.1.0.zip` (the agent hands you the built
   file; verify its SHA-256 matches the value above).
3. Resource type: **Dataset**. Fill the metadata from the block below.
4. Click **Publish**. Zenodo mints the DOI (`10.5281/zenodo.XXXXXXX`).
5. Send the DOI + record URL back; the record-back commit updates
   `data/materials/materials_md0002_snapshot_manifest.yaml`
   (`external_repository_record`, `external_dataset_doi`, `release_tag`) and
   the dataset docs.
6. Create the release tag on the merged content commit used for the archive:
   `git tag -a dataset-md0002-v0.1.0 <merged-release-commit> -m "MD-0002 v0.1.0 external dataset release" && git push origin dataset-md0002-v0.1.0`

## Copy-Paste Zenodo Metadata

**Title:**
`MD-0002: Frozen benchmark slice of Materials Project stable ternary oxides (v0.1.0)`

**Creators** (affiliation for both: `Open Agent Science / Autonomous Physics Lab`):
1. `Hladun, Roman` — ORCID `0009-0004-4853-5212`
2. `Kutenyov, Andrii` — GitHub `akutenyov` (created the MD-0002 holdout
   manifest packaged in this archive; confirm his preferred Latin spelling and
   ORCID, if any, before Publish — Zenodo metadata remains editable after
   publication without changing the DOI)

Contributor-identity note: `romanhladun24-dot` is a second account of Roman
Hladun, not a third creator.

**Description:**

> A frozen, checksummed benchmark slice of 362 stable ternary oxides (exactly
> three elements: oxygen plus two distinct cations) extracted from the
> Materials Project database, version 2026.04.13. Each material carries two
> computed properties (formation energy per atom, band gap), a frozen per-row
> train/validation/holdout split (253/55/54), and a cation-pair-disjoint
> holdout contract designed for honest extrapolation testing of
> formation-energy models. The package includes the normalized dataset
> (SHA-256 pinned), the raw pinned snapshot, the holdout and release
> manifests, release-facing schema and license declarations, and a validated baseline
> benchmark record (holdout MAE 0.2006 eV/atom versus shuffle controls at
> 0.474-0.531 eV/atom; independently replayed with zero metric drift).
>
> This is computed DFT data derived from the Materials Project (CC BY 4.0),
> not experimental measurements, and it is not materials-design guidance. It
> is published as a reproducible benchmark artifact: a version-frozen slice
> with a predeclared split and null controls. Built deterministically from the
> open repository `open-agent-science/autonomous-physics-lab` at release tag
> `dataset-md0002-v0.1.0` with `scripts/package_materials_md0002_archive.py`;
> the archive SHA-256 is recorded in the repository.
>
> Please also credit the upstream source: A. Jain et al., "Commentary: The
> Materials Project: A materials genome approach to accelerating materials
> innovation", APL Materials 1, 011002 (2013), doi:10.1063/1.4812323.
>
> Two provenance notes. (1) The standalone archive carries an MD-0002-specific
> license record instead of the repository-wide `data/DATA_LICENSES.yaml`
> registry, so unrelated source-license entries do not appear in the dataset
> payload. The applicable source license is Materials Project CC BY 4.0, with
> Jain et al. attribution preserved in the license record, snapshot manifest,
> README, and Zenodo metadata. (2) The packaged snapshot manifest records
> `external_dataset_doi: not_minted` because the DOI is assigned by this
> Zenodo record; the repository records the final DOI in a follow-up commit.

**License:** `Creative Commons Attribution 4.0 International (CC BY 4.0)`

**Version:** `0.1.0`

**Keywords:**
`materials science; density functional theory; formation energy; band gap;
benchmark dataset; Materials Project; ternary oxides; machine learning;
reproducibility; holdout evaluation; open agent science`

**Related identifiers:**
- `IsDerivedFrom` -> `10.1063/1.4812323` (Materials Project commentary, Jain et al.)
- `IsSupplementTo` -> `https://github.com/open-agent-science/autonomous-physics-lab`

## Wording Discipline (per the release packet stop conditions)

- The record must not present MD-0002 as experimental measurement data or as
  materials-design guidance.
- No discovery, materials-law, or model-superiority claim; the baseline is a
  benchmark reference value, not a scientific claim.
- CC BY 4.0 and the Materials Project attribution must remain visible on the
  Zenodo record.

## Record-Back Checklist (after Publish)

- [ ] DOI recorded in `materials_md0002_snapshot_manifest.yaml`
      (`external_dataset_doi`), record URL in `external_repository_record`,
      tag in `release_tag`.
- [ ] Release tag `dataset-md0002-v0.1.0` pushed at the merged release commit.
- [ ] Dataset docs updated to cite the DOI as the canonical external citation.
- [ ] Note: the archived snapshot-manifest bytes intentionally predate the
      DOI; a future v0.1.1 rebuild would need allowlist pin refreshes and a
      new version DOI.
