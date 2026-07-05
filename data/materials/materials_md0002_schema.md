# MD-0002 Release Schema

Dataset: `MD-0002-materials-project-stable-ternary-oxides`

Version: `0.1.0`

This file describes the release-facing row shape for the MD-0002 archive. It is
intended for archive readers and avoids the broader repository guidance that
also covers earlier and future Materials datasets.

## Dataset Shape

The normalized dataset file is:

`data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`

It contains 724 axis rows over 362 distinct Materials Project material ids:

- 362 `formation_energy_per_atom` rows;
- 362 `band_gap` rows.

The frozen split is material-level, so both property axes share the same
train/validation/holdout assignment for a given material.

## Required Row Fields

Each included normalized row carries:

- `row_id`
- `material_id`
- `formula_pretty`
- `composition`
- `nsites`
- `spacegroup_symbol`
- `property_kind`
- `value`
- `units`
- `method`
- `energy_above_hull`
- `is_stable`
- `provenance_class`
- `inclusion_status`
- split metadata inherited from the MD-0002 holdout manifest

The supported property kinds in v0.1.0 are:

| Property kind | Units | Provenance |
| --- | --- | --- |
| `formation_energy_per_atom` | `eV_per_atom` | Materials Project computed DFT |
| `band_gap` | `eV` | Materials Project computed DFT |

## Provenance And Uncertainty

All value-bearing rows in this release are Materials Project computed DFT rows.
They are not experimental measurements. The source snapshot does not provide
per-row experimental uncertainty, covariance, or method-specific uncertainty
estimates for these normalized rows.

Formation energy and band gap must be treated as separate benchmark axes and
must not be pooled into one residual metric.

## Validation Boundary

The repository loader contract is implemented in
`physics_lab/datasets/materials_md0002.py`. The standalone archive includes
data and metadata, not the full executable repository environment. Consumers
who want exact loader behavior should use the corresponding
`open-agent-science/autonomous-physics-lab` repository revision named by the
Zenodo record.
