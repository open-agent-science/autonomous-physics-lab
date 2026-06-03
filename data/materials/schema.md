# Materials Property Residuals — Row Schema Sketch

**Task:** `TASK-0547`
**Status:** planning schema sketch (no measurement values committed)

This defines the minimum fields a future Materials property row must carry before
any `md-*.yaml` dataset or residual benchmark is built. It is a sketch, not an
active loader schema yet; a loader/validator lands with the first committed
snapshot. It sits under the
[Published-Source and Reusable-Dataset Standard](../../docs/published-source-dataset-standard.md)
and the
[Source Acquisition, Pinning, and Extraction Lane](../../docs/source-acquisition-lane.md).

## Provenance Classes

Every row declares exactly one:

| Provenance class | Meaning | Ingestion rule |
| --- | --- | --- |
| `computed_dft` | DFT-computed property (functional + database version recorded). | Allowed after source-manifest review; keep functional explicit. |
| `measured` | Experimentally measured property with a primary-source citation. | Separate residual axis from `computed_dft`; never merge. |
| `model_only` | Descriptor or model output, not a measurement. | Excluded context only; never a measured/computed row. |
| `excluded` | Row deliberately excluded (duplicate, out of scope, missing fields). | Kept visible with `exclusion_reason`. |

Computed and measured properties are **separate residual axes** and must never be
pooled under one metric. Property kinds (formation energy, band gap, elastic
moduli) are also never merged.

## Minimal Fields

```yaml
row_id: MD-0001-0001
source_id: materials-project-2024
provenance_class: computed_dft          # computed_dft | measured | model_only | excluded
material:
  material_id: mp-XXXX                  # source record id (stable locator)
  formula_pretty: "SiO2"
  composition: {Si: 1, O: 2}
  spacegroup_symbol: null               # symmetry context if available
  nsites: null
property:
  property_kind: formation_energy_per_atom   # formation_energy_per_atom | band_gap | bulk_modulus | shear_modulus
  value: null
  units: eV_per_atom                    # eV_per_atom | eV | GPa
  method: GGA_or_GGA+U                  # DFT functional for computed_dft; instrument for measured
uncertainty:
  value: null                           # per-row if available
  basis: null                           # measured | method | absent
provenance:
  database_version: null                # pinned MP/JARVIS release; required for computed_dft
  record_locator: null                  # API record id or citation
  retrieval_date: null                  # ISO-8601
  checksum_sha256: null                 # of the pinned raw/normalized artifact
inclusion_status: included              # included | excluded
exclusion_reason: null                  # required when inclusion_status == excluded
limitations:
  - "Planning placeholder; no value ingested."
```

## Required Validation Ideas (future loader)

- every non-excluded row has property_kind, units, value, source_id, provenance_class;
- `computed_dft` rows record DFT functional and database_version;
- `measured` and `computed_dft` rows are never mixed on one residual axis;
- different property_kinds are never merged into one metric;
- excluded rows keep an explicit `exclusion_reason`;
- every committed snapshot has a checksum and a license/attribution note.

## Stop Conditions

Stop before ingestion when: the source license/ToS is unclear; the DFT functional
or database version is unknown; property units are ambiguous; computed and
measured provenance cannot be separated; or a row lacks a stable record locator.
