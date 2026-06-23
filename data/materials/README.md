# Materials Property Residuals — Data Area

This directory holds source manifests and pinned datasets for the Materials
Property Residuals campaign (`docs/campaigns/materials-property-residuals.md`,
`campaign_profiles/materials-property-residuals.yaml`).

The first pinned dataset is a compact Materials Project pilot:

- `md-0001-materials-project-formation-energy.yaml`
- `md-0001-materials-project-band-gap.yaml`
- `md-0001-citation.yaml`
- `snapshots/materials_project_binary_oxides_2025-09-25.json`
- `materials_snapshot_manifest.yaml`

It covers stable binary oxides from Materials Project `database_version`
`2025.09.25` under CC BY 4.0 attribution. It is a reusable source dataset, not a
benchmark result, model, prediction, or scientific claim.

The second pinned dataset is `MD-0002`, a wider computed-DFT stable ternary
oxide slice:

- `md-0002-materials-project-stable-ternary-oxides.yaml`
- `md0002_holdout_manifest.yaml`
- `materials_md0002_snapshot_manifest.yaml`
- `snapshots/materials_project_md0002_2026.04.13.json`

It covers Materials Project `database_version` `2026.04.13` stable ternary
oxides under the narrowed `md0002_alkali_alkaline_earth_3d_transition_oxide`
predicate. The normalized file contains 724 axis rows over 362 materials:
formation energy per atom and band gap, both computed DFT values. The
formation-energy axis is used by `RESULT-0021`; band gap remains diagnostic-only.

`MD-0002` is internally reusable and content-pinned, but it is not an external
dataset publication. No DOI, release tag, external archive record, material
recommendation, synthesis guidance, device-performance statement, biomedical
claim, or universal materials-law claim is created by these files.

## Citation And Reuse Boundary

`md-0001-citation.yaml` records internal citation and reuse metadata for the
MD-0001 dataset family. It preserves Materials Project CC BY 4.0 attribution,
the recommended source citation, the maintainer citation-planning identity
(Roman Hladun, ORCID `https://orcid.org/0009-0004-4853-5212`), and the current
external organization boundary (`https://github.com/open-agent-science`).

MD-0001 remains an internal repository artifact. This metadata does not publish
the dataset, mint a DOI, create a Zenodo or GitHub release, move files into an
external repository, or grant permission to make benchmark, material-discovery,
device, synthesis, or biomedical claims. Any external publication path requires
a separate maintainer-approved publication task.

`materials_md0002_snapshot_manifest.yaml` records the equivalent MD-0002
release/source metadata: source citation, CC BY 4.0 reuse status, raw and
normalized checksums, computed-DFT uncertainty semantics, changelog, and
explicit DOI/external-release status. It preserves the same no-claim boundary:
MD-0002 supports scoped benchmark reproducibility inside APL, not a standalone
materials-design or experimental-validation claim.

## Source Policy

- A source must be registered in `source_manifest.yaml` with database/version,
  license, and checksum policy **before** any dataset file may reference it.
- No live external fetching inside benchmark code or ordinary agent tasks.
  Sources must be pinned via the acquisition lane with version, checksum,
  attribution, and no-secret guardrails.
- Keep computed (DFT) and measured properties on separate residual axes with
  explicit provenance; never merge them or merge different property kinds under
  one residual metric.
- Do not commit non-redistributable database dumps; record locators, versions,
  and checksums per the pinned-snapshot policy.

## Guardrails

- Do not add material-property values without a reviewed source-manifest entry,
  pinned snapshot, checksum, license/attribution note, and validation test.
- Do not treat `source_manifest.yaml` as benchmark data.
- Do not add synthesis recipes, device-fabrication steps, chemical-handling
  guidance, or biomedical content.
- Do not promote scientific, material-discovery, design, or device claims from
  this directory.

## Expected Future Layout

```text
data/materials/
  README.md
  source_manifest.yaml
  materials_snapshot_manifest.yaml
  materials_md0002_snapshot_manifest.yaml
  md-0001-citation.yaml
  snapshots/
  md-*.yaml
```
