# Materials Project Binary-Oxides Dataset (first pinned snapshot)

**Task:** `TASK-0548` (row curation; follows `TASK-0547` acquisition runbook)
**Campaign:** Materials Property Residuals
**Source:** Materials Project, `database_version` 2025.09.25 (CC BY 4.0)
**Decision:** `DATASET_PINNED` — APL's first new reusable, provenance-rich dataset

## What landed

The maintainer ran the acquisition runbook
([materials-snapshot-acquisition-runbook.md](../runbooks/materials-snapshot-acquisition-runbook.md))
locally with their own `MP_API_KEY` (never committed) for a bounded pilot scope.
This task commits the result:

- `data/materials/snapshots/materials_project_binary_oxides_2025-09-25.json` —
  pinned raw snapshot (SHA-256 `bdcd57f0…f7101`).
- `data/materials/md-0001-materials-project-formation-energy.yaml` — 169 rows,
  `formation_energy_per_atom` (eV/atom), `computed_dft`.
- `data/materials/md-0001-materials-project-band-gap.yaml` — 169 rows,
  `band_gap` (eV), `computed_dft`.
- `data/materials/materials_snapshot_manifest.yaml` — filled (db version,
  timestamp, row count, checksum, `no_peek_attestation: true`).
- `data/materials/source_manifest.yaml` — version pinned to 2025.09.25.
- `tests/test_materials_dataset.py` — checksum + schema guard.

## Scope (frozen before fetch, no-peek)

- Query: `elements ⊇ {O}`, `num_elements = 2`, `is_stable = true`
  (stable binary oxides).
- Two property axes kept **separate** (one file each); never pooled into one
  metric. Both axes are computed DFT, never mixed with experimental data.
- 169 materials; every row has both properties.

## Provenance and license

- Provenance: `computed_dft` (Materials Project GGA/GGA+U convention), pinned to
  `database_version` 2025.09.25 with a stable `material_id` per row.
- License: CC BY 4.0 — redistribution of curated rows is allowed **with
  attribution**, which is recorded on every dataset file:
  "Data from The Materials Project (materialsproject.org), licensed CC BY 4.0;
  cite Jain et al., APL Materials 1, 011002 (2013)."

## Reproducibility

Re-running the runbook against the same `database_version` and query reproduces
the snapshot; the committed SHA-256 detects drift. The test asserts the dataset
and manifest checksums match the committed snapshot file.

## Output Routing Summary

- Task verdict: `DATASET_PINNED` (data artifact; no scientific claim).
- Canonical destination: `data/materials/` dataset + snapshot + manifest, guarded
  by `tests/test_materials_dataset.py`.
- Review tier: `AGENT_PUBLISHED` (pinned source data; not a benchmark result).
- Gate A/B: not applicable (no RESULT/PRED metric).
- Claim impact: none. Knowledge impact: none.
- Limitations / blockers: computed DFT only; bounded pilot scope; no baseline,
  residual metric, or claim. Secret never committed; key should be rotated by the
  maintainer since it was shared out-of-band.

## Suggested next steps (separate tasks)

- Optionally widen scope (ternary oxides / other chemistries) via a new
  pre-fetch-amended snapshot task.
- Build a residual baseline task over `formation_energy_per_atom` (e.g., a simple
  composition model) — separate from this data task.
- Optionally mint a citable DOI (GitHub→Zenodo) for the pinned dataset.

## Limitations

- DFT-computed values, not experimental measurements.
- Pilot scope (stable binary oxides) is deliberately small and well-understood.
- No model, metric, or claim is produced here.
