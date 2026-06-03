# Materials Property Residuals - Row Schema

**Task:** `TASK-0547`; reconciled for `TASK-0541`
**Status:** active committed dataset guidance for `MD-0001`

This defines the minimum fields a Materials property row must carry before any
residual benchmark is built. `MD-0001` is already committed as a pinned
Materials Project stable-binary-oxides snapshot, so this document now records
the active row shape as well as future widening semantics. It sits under the
[Published-Source and Reusable-Dataset Standard](../../docs/published-source-dataset-standard.md)
and the
[Source Acquisition, Pinning, and Extraction Lane](../../docs/source-acquisition-lane.md).

## Provenance Classes

Every row declares exactly one:

| Provenance class | Meaning | Ingestion rule |
| --- | --- | --- |
| `computed_dft` | DFT-computed property, with functional and database version recorded. | Allowed after source-manifest review; keep functional explicit. |
| `measured` | Experimentally measured property with a primary-source citation. | Separate residual axis from `computed_dft`; never merge. |
| `model_only` | Descriptor or model output, not a measurement. | Excluded context only; never a measured/computed row. |
| `excluded` | Row deliberately excluded: duplicate, out of scope, or missing fields. | Kept visible with `exclusion_reason`. |

Computed and measured properties are separate residual axes and must never be
pooled under one metric. Property kinds such as formation energy, band gap, and
elastic moduli are also never merged.

## Active MD-0001 Dataset Shape

The committed `MD-0001` pilot consists of two axis files over the same 169
stable binary oxides from Materials Project database version `2025.09.25`:

| Dataset file | Property axis | Units | Provenance class |
| --- | --- | --- | --- |
| `md-0001-materials-project-formation-energy.yaml` | `formation_energy_per_atom` | `eV_per_atom` | `computed_dft` |
| `md-0001-materials-project-band-gap.yaml` | `band_gap` | `eV` | `computed_dft` |

The two files must remain separate benchmark axes. Their rows share material
locators and snapshot provenance, but their property values, units, and future
metrics must not be pooled.

Committed MD-0001 rows use this row-level shape:

```yaml
row_id: MD-0001-FE-0001
material_id: mp-1274279
formula_pretty: FeO
composition:
  Fe: 4
  O: 4
nsites: 8
spacegroup_symbol: C2/m
property_kind: formation_energy_per_atom
value: -1.481519387499999
units: eV_per_atom
method: DFT (GGA/GGA+U, Materials Project convention)
energy_above_hull: 0.0
is_stable: true
provenance_class: computed_dft
inclusion_status: included
```

The dataset header, not each row, records snapshot-level fields such as
`database_version`, `retrieved_at_utc`, `snapshot_file`,
`snapshot_checksum_sha256`, `license`, `attribution`, `uncertainty`, and the
no-claim boundary.

## Minimal Future Row Fields

Future rows should preserve this normalized shape before they are made
available to a benchmark task:

```yaml
row_id: MD-0001-0001
source_id: materials-project
provenance_class: computed_dft  # computed_dft | measured | model_only | excluded
material:
  material_id: mp-XXXX
  formula_pretty: SiO2
  composition: {Si: 1, O: 2}
  spacegroup_symbol: null
  nsites: null
property:
  property_kind: formation_energy_per_atom
  value: null
  units: eV_per_atom
  method: GGA_or_GGA+U
uncertainty:
  value: null
  basis: null
provenance:
  database_version: null
  record_locator: null
  retrieval_date: null
  checksum_sha256: null
inclusion_status: included
exclusion_reason: null
limitations:
  - "Planning placeholder; no value ingested."
```

## Holdout / No-Peek Semantics

Before any Materials baseline or residual map can run, each benchmark task must
bind itself to `data/materials/holdout_manifest.yaml`. That manifest freezes
the allowed split vocabulary and the pre-score axes that may be used to choose
splits:

- property axis: `formation_energy_per_atom` and `band_gap`;
- composition family: `binary_oxide` for MD-0001;
- cation group;
- structure prototype or `spacegroup_symbol`;
- source version and checksum;
- property-range bins defined before residual inspection.

`MD-0001` currently has computed DFT rows only. Future measured, model-only, or
excluded rows must stay distinct through `provenance_class` and
`inclusion_status`; they must not be silently folded into the computed DFT axes.

## Required Validation Ideas For Future Loaders

Future ingestion work should add deterministic validation that checks:

- every non-excluded row has property kind, units, value, source id, and
  provenance class;
- `computed_dft` rows record DFT functional and database version;
- `measured` and `computed_dft` rows are never mixed on one residual axis;
- different property kinds are never merged into one metric;
- excluded rows keep an explicit `exclusion_reason`;
- every committed snapshot has a checksum and a license/attribution note;
- every benchmark task references the holdout/no-peek manifest before scoring.

## Stop Conditions

Stop before ingestion or benchmark execution when: the source license or terms
are unclear; the DFT functional or database version is unknown; property units
are ambiguous; computed and measured provenance cannot be separated; a row lacks
a stable record locator; or a baseline task attempts to choose split rules after
inspecting residuals.
