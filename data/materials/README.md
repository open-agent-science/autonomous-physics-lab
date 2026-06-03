# Materials Property Residuals — Data Area

This directory holds source manifests and pinned datasets for the Materials
Property Residuals campaign (`docs/campaigns/materials-property-residuals.md`,
`campaign_profiles/materials-property-residuals.yaml`).

The first pinned dataset is a compact Materials Project pilot:

- `md-0001-materials-project-formation-energy.yaml`
- `md-0001-materials-project-band-gap.yaml`
- `snapshots/materials_project_binary_oxides_2025-09-25.json`
- `materials_snapshot_manifest.yaml`

It covers stable binary oxides from Materials Project `database_version`
`2025.09.25` under CC BY 4.0 attribution. It is a reusable source dataset, not a
benchmark result, model, prediction, or scientific claim.

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
  snapshots/
  md-*.yaml
```
