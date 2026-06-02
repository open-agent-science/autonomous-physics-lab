# Materials Property Residuals — Data Area (Source Policy Placeholder)

This directory is the **value-free** data area for the Materials Property
Residuals campaign (`docs/campaigns/materials-property-residuals.md`,
`campaign_profiles/materials-property-residuals.yaml`).

**No measurement or computed property values are committed here yet.** No live
materials-database data has been fetched or ingested. This is a source-policy
placeholder created by the campaign scaffold (TASK-0439).

## Source Policy

- A source must be registered in `source_manifest.yaml` with database/version,
  license, and checksum policy **before** any dataset file may reference it.
- No live external fetching inside agent tasks. Sources must be pinned at commit
  time via a deterministic, version-pinned, checksum-recorded snapshot policy
  defined by a future task.
- Keep computed (DFT) and measured properties on separate residual axes with
  explicit provenance; never merge them or merge different property kinds under
  one residual metric.
- Do not commit non-redistributable database dumps; record locators, versions,
  and checksums per the future pinned-snapshot policy.

## Guardrails

- Do not add real material-property values without a reviewed source-manifest
  entry and pinned snapshot policy.
- Do not treat `source_manifest.yaml` as benchmark data.
- Do not add synthesis recipes, device-fabrication steps, chemical-handling
  guidance, or biomedical content.
- Do not promote scientific, material-discovery, design, or device claims from
  this directory.

## Expected Future Layout

```text
data/materials/
  README.md            # this source-policy placeholder
  source_manifest.yaml # registered sources (no values until reviewed)
  <future> md-*.yaml   # pinned, schema-valid property rows once a snapshot and
                       # schema task land
```
