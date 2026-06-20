# Materials MD-0002 Dataset Publication Preflight

**Task:** `TASK-0805`
**Campaign:** Materials Property Residuals
**Mode:** repository-only publication preflight; no fetch, upload, DOI mint, or
data mutation
**Verdict:** `NOT_READY_FOR_EXTERNAL_DATASET_RELEASE__SMALL_METADATA_CLOSEOUT`

## Scope

This review checks whether the committed MD-0002 dataset is ready to become a
separately citable reusable-dataset release. It uses only repository evidence:

- `data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`;
- `data/materials/snapshots/materials_project_md0002_2026.04.13.json`;
- `data/materials/md0002_holdout_manifest.yaml`;
- `data/materials/source_manifest.yaml`;
- `data/DATA_LICENSES.yaml`;
- `data/materials/schema.md`;
- `physics_lab/datasets/materials_md0002.py`;
- the MD-0002 tests and `RESULT-0021`.

The scientific scope remains the frozen 362-material stable ternary-oxide
slice. The 724 normalized rows contain two separate computed-DFT axes:
formation energy per atom and band gap. This is not experimental data and does
not support a materials discovery, design, synthesis, device, or universal-law
claim.

## Readiness Checklist

| Publication requirement | State | Repository evidence |
| --- | --- | --- |
| Stable dataset identity and semantic version | **PASS** | Dataset id `MD-0002-materials-project-stable-ternary-oxides`; `dataset_version: 0.1.0`. |
| Source redistribution licence | **PASS** | Dataset header and `data/DATA_LICENSES.yaml` identify Materials Project data as CC BY 4.0 and require attribution to Materials Project and Jain et al. |
| Dataset-release licence statement | **PARTIAL** | The committed dataset says `license: CC BY 4.0`, but there is no MD-0002 release metadata file that distinguishes the source-data licence, APL curation attribution, and the licence applied to the release package. |
| Source citation | **PARTIAL** | Jain et al., APL Materials 1, 011002 (2013) is named. `data/materials/source_manifest.yaml` records source DOI `10.1063/1.4812323`, but the MD-0002 dataset header and a dedicated MD-0002 citation record do not include the complete citation. |
| External dataset citation / DOI | **BLOCKED** | No MD-0002 recommended citation, creator list/ORCID record, external repository record, release tag, or dataset DOI exists. No DOI was minted by this task. |
| Source version and retrieval timestamp | **PASS** | Dataset header records Materials Project source version `2026.04.13` and retrieval time `2026-06-15T03:56:20.360115+00:00`; live fetching is disabled. |
| Source manifest for the released snapshot | **BLOCKED** | The shared source manifest still describes only the `2025.09.25` MD-0001 snapshot and says `status: first_snapshot_pinned`. The MD-0002 holdout manifest points to a planned `data/materials/materials_md0002_snapshot_manifest.yaml`, but that file is absent. |
| Raw snapshot checksum | **PASS** | Recomputed SHA-256 is `5bfb3e7f86c0afcdfa7e7898a47e05e063226758eeabeae0c95c246660349567`, matching the dataset and holdout manifest. |
| Normalized release-file checksum | **BLOCKED** | The current normalized YAML hashes to `516ed06f005157da93fb30490fea2d7a5026146129a4b56ed4c6d4159d81b1d1`, but this hash is not recorded in a release manifest. The existing checksum covers the raw snapshot, not the distributable normalized file. |
| Computed-DFT provenance | **PASS** | Every included row is classified `computed_dft`; rows record source id, database version, record locator, `GGA_or_GGA+U`, method text, and snapshot checksum. |
| Property-axis and unit separation | **PASS** | Formation energy uses `eV_per_atom`; band gap uses `eV`. Loader validation and the holdout manifest prohibit pooling the axes or mixing measured and computed rows. |
| Machine-readable schema and types | **PARTIAL** | `physics_lab/datasets/materials_md0002.py` is an executable row validator with a synthetic schema fixture and tests. There is no standalone MD-0002 JSON/YAML schema for release consumers, and `data/materials/schema.md` still describes itself as active guidance for MD-0001. |
| Validator coverage | **PARTIAL** | Loader, fixture, checksum, axis, benchmark, and result tests exist. Publication-specific checks do not require MD-0002 changelog, uncertainty semantics, citation metadata, normalized-file checksum, or release manifest completeness. |
| Uncertainty semantics | **BLOCKED** | MD-0002 is clearly labelled computed DFT, but the dataset has no explicit per-row or per-method uncertainty block and no explicit `absent` uncertainty policy as required by the reusable-dataset standard. |
| Changelog | **BLOCKED** | Version `0.1.0` is present, but MD-0002 has no changelog. |
| Dataset README and intended-use boundary | **PARTIAL** | Campaign and review documentation provide limitations and no-claim wording, and the dataset header has a no-claim boundary. `data/materials/README.md` documents MD-0001 as the first pinned dataset but does not inventory MD-0002 or describe its reuse package. |
| Reproducible scientific use | **PASS** | `RESULT-0021` is `AGENT_VALIDATED`; its deterministic replay uses the committed MD-0002 data and reports no metric drift. This supports reproducibility, not external publication completeness. |

## Publication Blockers

1. **MD-0002 source/release manifest is incomplete.** The source manifest is
   pinned to the older MD-0001 version, while the planned MD-0002 snapshot
   manifest referenced by the holdout file does not exist.
2. **Citation and DOI metadata are absent.** There is no MD-0002 equivalent of
   `md-0001-citation.yaml`, no recommended dataset citation, and no explicit
   external-release or DOI status record.
3. **The release payload is not content-pinned.** The raw snapshot checksum is
   pinned, but the normalized dataset checksum is not recorded in a release
   manifest.
4. **Reusable-dataset metadata is incomplete.** MD-0002 lacks a changelog,
   explicit uncertainty semantics, and an MD-0002-specific README/intended-use
   entry.
5. **The consumer schema is only partly portable.** Repository code validates
   the row contract, but there is no standalone machine-readable schema and no
   publication-completeness validator.

These are metadata and packaging blockers, not evidence that the committed
rows are invalid. The existing source licence, raw checksum, provenance,
version pin, unit separation, and deterministic loader are sufficient for
continued internal repository reuse.

## Smallest Closing Steps

The smallest future maintainer-approved closeout is:

1. Add one MD-0002 release/source manifest that records source version and
   retrieval metadata, raw-snapshot checksum, normalized-file checksum, source
   DOI/citation, source licence, dataset-package licence, creator/ORCID fields,
   and explicit external repository/DOI status.
2. Add a short MD-0002 changelog and explicit uncertainty policy such as
   `absent_in_source_snapshot`, without changing any value-bearing row.
3. Publish or generate a standalone machine-readable MD-0002 schema from the
   existing loader contract, and add a publication-preflight test covering
   schema, citation, licence, checksums, changelog, and uncertainty metadata.
4. Extend the materials data README with MD-0002 scope, intended uses,
   computed-DFT limitation, citation instructions, and no-claim boundary.
5. After those repository changes pass review, run a separate
   maintainer-approved release task to choose an external repository, freeze
   the final archive checksum, create a release tag, and mint a DOI if desired.

No new fetch or row curation is needed to close the identified metadata gaps.
The external release and DOI remain optional maintainer decisions.

## Decision

MD-0002 is **internally reusable and close to publication-ready**, but it is
not ready for an external dataset release today. Its data integrity and
scientific provenance checks are strong; the remaining work is a bounded
release-metadata and portable-schema package.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (dataset-publication readiness preflight).
- **Readiness verdict:** `NOT_READY_FOR_EXTERNAL_DATASET_RELEASE__SMALL_METADATA_CLOSEOUT`.
- **Canonical destination:** this dataset-publication readiness review.
- **Review tier:** `none`; no canonical scientific artifact was created or
  re-tiered.
- **Gate A:** not attempted. **Gate B:** not attempted for this preflight;
  existing `RESULT-0021` replay status is unchanged.
- **Claim impact:** no `CLAIM-*` change.
- **Knowledge impact:** no `KNOW-*` change.
- **Result/prediction impact:** no `RESULT-*` or `PRED-*` change.
- **External publication:** not performed; no upload, release, fetch, or DOI
  mint occurred.
- **Publication blockers:** MD-0002 release/source manifest, citation/DOI
  metadata, normalized payload checksum, changelog, uncertainty semantics,
  portable machine-readable schema, and publication-completeness validation.
