# MD-0002 v0.1.0 Zenodo Release Integrity And Public No-Claim Readiness

- Task: `TASK-0937`
- Domain: materials science (release/readiness verification only)
- Run date: `2026-07-06`
- Builds on: `TASK-0924`
  ([materials-md0002-zenodo-upload-pack.md](materials-md0002-zenodo-upload-pack.md)),
  `TASK-0932` (release-tree cleanup)
- Verdict: **`RELEASE_INTEGRITY_CONFIRMED`**

## Scope

Post-publication verification that the externally published MD-0002 v0.1.0
release record is internally consistent across the public Zenodo record, the
repository release tag, the committed manifest, the committed archive
checksums, the data README, the campaign page, and the RESULT-0021 references
— and that the public wording keeps the computed-DFT, slice-limited, no-claim
boundary.

This task did **not** rebuild the archive, republish Zenodo, change dataset
rows, change holdout membership, rerun metrics, alter RESULT-0021, create a
new RESULT, or promote any claim. The only bytes fetched were the public
Zenodo record metadata (JSON API) and one read-only download of the released
795 KB archive into a disposable local path for checksum verification; the
download was deleted after hashing and nothing was committed.

## Integrity Table

Expected values come from the committed repository state
(`data/materials/materials_md0002_snapshot_manifest.yaml` record-back block,
`docs/reviews/materials-md0002-zenodo-upload-pack.md`, `data/materials/README.md`);
observed values come from the live public surfaces on 2026-07-06.

| Check | Expected (repository) | Observed (live) | Agree |
| --- | --- | --- | --- |
| Version DOI | `10.5281/zenodo.21207072` | Zenodo record DOI `10.5281/zenodo.21207072` | yes |
| Concept DOI | `10.5281/zenodo.21207071` | Zenodo `conceptdoi` `10.5281/zenodo.21207071` | yes |
| Record URL | `https://zenodo.org/records/21207072` | live record at that URL | yes |
| Title | `MD-0002: Frozen benchmark slice of Materials Project stable ternary oxides` (v0.1.0) | same title, version string `0.1.0` | yes |
| Resource type | Dataset | Dataset | yes |
| License | CC BY 4.0 | `cc-by-4.0` | yes |
| Creators | Hladun, Roman (ORCID `0009-0004-4853-5212`); Kutenyov, Andrii — both `Open Agent Science / Autonomous Physics Lab` | same two creators with same affiliation and ORCID | yes |
| Archive filename | `md0002-v0.1.0.zip` | `md0002-v0.1.0.zip` (single file on the record) | yes |
| Archive size | `795,018` bytes | Zenodo-reported `795,018`; fresh download measured `795,018` | yes |
| Archive SHA-256 | `19ec02cc0b64146357b14251065460d0af6b7f8cf234e20528c53ab977867b22` | fresh download hashes to the same SHA-256 | yes |
| Archive MD5 | `7cb2979574f7d39945793e1874b5d918` (manifest record-back) | Zenodo-reported MD5 and fresh-download MD5 both identical | yes |
| Release tag | `dataset-md0002-v0.1.0` at commit `8be74696` | `git ls-remote` shows the annotated tag; dereferenced target `8be7469616fb8957d4f967124720ee30db20f6e9` | yes |
| Publication date | 2026-07-05 (record-back wording) | Zenodo publication date `2026-07-05` | yes |
| Materials Project attribution | CC BY 4.0 source attribution with Jain et al. citation (`materials_md0002_license.yaml`) | Zenodo description states the data are "derived from the Materials Project (CC BY 4.0)" | yes |
| Benchmark numbers quoted publicly | RESULT-0021: holdout MAE `0.200606`; shuffle-control minima `0.474316` (cation-label) and `0.530919` (label) | Zenodo description quotes "holdout MAE 0.2006 eV/atom versus shuffle controls at 0.474-0.531 eV/atom" — correct rounding of the committed values | yes |

Supporting wording checks:

- **Zenodo description no-claim sentence (verbatim):** "This is computed DFT
  data derived from the Materials Project (CC BY 4.0), not experimental
  measurements, and it is not materials-design guidance." Present.
- **`data/materials/README.md`:** records the same version/concept DOIs and
  record URL, and keeps the boundary: MD-0002 supports "scoped benchmark
  reproducibility inside APL and as a citable dataset, not a standalone
  materials-design or experimental-validation claim."
- **`docs/campaigns/materials-property-residuals.md`:** records the same DOIs
  and explicitly says the DOI "is a dataset citation, not" a stronger claim.
- **`results/EXP-0014/RUN-0001/result.yaml` (RESULT-0021):** contains no
  Zenodo/DOI references (it predates the release) and nothing contradicting
  the release record; the manifest's record-back block carries the linkage.
- **Known intentional nuance (not a defect):** the packaged snapshot manifest
  inside the archive reads `external_dataset_doi: not_minted` because the
  archive froze the pre-DOI state; the minted DOI lives on the Zenodo record
  and in the repository record-back. The manifest documents this explicitly,
  and any rebuild would be a v0.1.1 with a new version DOI.

## Verdict

**`RELEASE_INTEGRITY_CONFIRMED`.** Version DOI, concept DOI, record URL,
release tag, archive filename/bytes/SHA-256/MD5, license, citation,
Materials Project attribution, version markers, and public no-claim wording
are mutually consistent across the Zenodo record, the repository tag, the
committed manifest, the README, the campaign page, and RESULT-0021. No
metadata correction list is needed.

**Recommendation:** no further action for MD-0002 v0.1.0 until a future
versioned source change or an explicit release reason exists; any rebuild goes
through a v0.1.1 with refreshed pins and a new version DOI rather than
mutation of this record.

## Limitations

- The verification is metadata- and checksum-level on one date (2026-07-06);
  it does not re-audit the scientific content of the dataset rows or re-run
  benchmark metrics.
- Zenodo metadata remains editable post-publication without changing the DOI;
  a later metadata edit on the record would require a fresh consistency pass.
- The archive-content allowlist was verified at packaging time (`TASK-0924` /
  `TASK-0932`); this task verified the published bytes match the pinned
  archive identity, not each inner file again.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (release-integrity verification; the
  verification verdict is `RELEASE_INTEGRITY_CONFIRMED`).
- **Canonical destination:** this review note,
  `docs/reviews/materials-md0002-zenodo-release-integrity.md`.
- **Review tier:** none (no tiered artifact produced or changed).
- **Gate A / Gate B:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Result artifact impact:** none; RESULT-0021 and all dataset rows,
  manifests, and holdout membership are byte-unchanged.
- **Publication blocker:** none for MD-0002 v0.1.0.
