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
  md-0001-citation.yaml
  snapshots/
  md-*.yaml
```
