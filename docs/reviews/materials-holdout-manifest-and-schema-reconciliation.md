# Materials Holdout Manifest And Schema Reconciliation

**Task:** `TASK-0541`
**Campaign:** Materials Property Residuals
**Status:** review-ready manifest/schema reconciliation; no benchmark scoring
**Verdict:** `MD0001_HOLDOUT_MANIFEST_DEFINED`

## Scope

This task reconciles the committed `MD-0001` Materials Project pilot dataset
with the Materials row schema and creates a no-peek holdout manifest for future
benchmark tasks.

Reviewed committed inputs:

- `data/materials/md-0001-materials-project-formation-energy.yaml`
- `data/materials/md-0001-materials-project-band-gap.yaml`
- `data/materials/materials_snapshot_manifest.yaml`
- `data/materials/source_manifest.yaml`
- `data/materials/schema.md`
- `docs/campaigns/materials-property-residuals.md`

No new Materials Project rows were fetched, generated, or ingested.

## Dataset Reconciliation

`MD-0001` is a pinned Materials Project stable-binary-oxides pilot at database
version `2025.09.25`. It contains 169 materials represented on two separate
computed DFT property axes:

| Dataset file | Axis | Units | Provenance |
| --- | --- | --- | --- |
| `md-0001-materials-project-formation-energy.yaml` | `formation_energy_per_atom` | `eV_per_atom` | `computed_dft` |
| `md-0001-materials-project-band-gap.yaml` | `band_gap` | `eV` | `computed_dft` |

The row schema was updated from a pre-ingestion sketch into active guidance for
the committed dataset. It now records the flat MD-0001 row shape
(`material_id`, `formula_pretty`, `composition`, `nsites`,
`spacegroup_symbol`, `property_kind`, `value`, `units`, `method`,
`energy_above_hull`, `is_stable`, `provenance_class`, and
`inclusion_status`) and keeps future measured, model-only, and excluded rows as
distinct provenance/row-class states.

## Holdout Manifest

`data/materials/holdout_manifest.yaml` now freezes the pre-score split surface
for future MD-0001 benchmark work:

- allowed split values: `train`, `validation`, `holdout`, `stress`, `excluded`;
- property axes must remain separate;
- computed DFT, measured, model-only, and excluded rows are distinct row-class
  lanes;
- admissible pre-score split axes include composition family, cation group,
  structure prototype / `spacegroup_symbol`, property-range bins, and source
  version / checksum;
- no row-level split assignment is made in this task.

The manifest is intentionally a benchmark-binding artifact, not a benchmark
run. A later baseline task must bind to this manifest and declare concrete row
split rules before scoring.

## Boundaries Preserved

- No live fetch was performed.
- No dataset rows or property values were changed.
- No baseline metric, residual map, model comparison, prediction, result, claim,
  or knowledge artifact was created.
- Formation energy and band gap remain separate axes.
- Computed DFT rows are not mixed with measured or model-only rows.
- Property-range bins are allowed only when a future benchmark task freezes
  numeric thresholds before residual inspection.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `MD0001_HOLDOUT_MANIFEST_DEFINED`; not a scientific claim or
  benchmark result.
- **Canonical destination:** `data/materials/holdout_manifest.yaml`,
  `data/materials/schema.md`, and this review note.
- **Review tier:** `none`.
- **Gate A status:** not attempted.
- **Gate B status:** not attempted.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge promotion.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** future Materials baseline work still needs a
  separate task that binds to this manifest, assigns row-level splits before
  scoring, and reports metrics per property axis. This is advisory next-work
  context only; this task does not create a new task proposal.
