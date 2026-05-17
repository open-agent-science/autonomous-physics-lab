# Quantum Dot Size-Effect Datasets

This directory stores pinned input datasets for the Quantum Size Effects
campaign.

The purpose of these files is to make future baseline residual benchmarks,
holdout splits, and sandbox-only correction tests source-aware and reviewable
before any size-effect interpretation is attempted.

## Scope

These files are input data only. They cover size-dependent optical and
electronic properties of semiconductor quantum dots.

They do not, by themselves:

- establish a benchmark result or validated correction model;
- justify a specific effective-mass parametrisation;
- support a broad physical conclusion about any material family;
- authorize mixing absorption peak, emission peak, and bandgap values under
  a single residual metric;
- support synthesis, fabrication, device-performance, or biomedical claims.

## Source Policy

Primary source policy:

- use pinned publication sources with explicit DOI, year, and table reference;
- store a pinned copy or record a SHA-256 checksum for any redistributable
  dataset file;
- record access date, redistribution terms, and license notes;
- preserve whether a value is a directly measured result, an extrapolated
  fit, or an explicitly theoretical value from the source layer.

Adding a live-fetched or unreviewed dataset file is not permitted.
Each new source must be registered in `source_manifest.yaml` before dataset
entries referencing it may be committed.

## Field-Semantics Policy

Every dataset entry must record:

- `material`: canonical chemical symbol or formula (e.g. `CdSe`, `InP`,
  `PbS`, `CdS`, `ZnSe`).
- `size_nm`: particle size. Record as `diameter_nm` for spherical particles
  or `radius_nm` when the source reports radius. Both fields may not be
  present on the same entry. Derive the missing form only when the source
  explicitly states the geometry.
- `property_kind`: one of `absorption_peak_eV`, `emission_peak_eV`,
  `bandgap_eV`. Do not use a generic `energy_eV` field; keep semantics
  explicit.
- `value_eV`: the measured or derived energy value in electron-volts.
- `source_id`: must match a registered entry in `source_manifest.yaml`.
- `inclusion_status`: `included` or `excluded`.

Optional but encouraged fields:

- `uncertainty_eV`: measurement uncertainty in eV if reported by source.
- `temperature_K`: measurement temperature if reported.
- `composition_note`: alloy fraction or doping notes when relevant.
- `measurement_type`: one of `optical_absorption`, `photoluminescence`,
  `electrical_transport`, `theoretical_calculation`.
- `exclusion_reason`: required when `inclusion_status` is `excluded`.

Mixing absorption peak, emission peak, and bandgap values on the same
residual axis is a leakage risk and is explicitly forbidden by the campaign
holdout protocol.

## Directory Layout

```text
data/quantum_dots/
  README.md               — this file
  source_manifest.yaml    — pinned source registry
  qd-XXXX-*.yaml          — versioned dataset files (added after curation)
```

Dataset files follow the schema defined in
`physics_lab/schemas/quantum_dot_size_effect.schema.json`.

## Validation

Dataset YAML files in this directory are validated by
`tests/test_quantum_dot_dataset_schema.py` and by
`python3 -m physics_lab.cli validate-repo .`.

## Campaign Context

This dataset layer supports the Quantum Size Effects campaign described in
`docs/notes/quantum-size-effects-campaign-plan.md`. Dataset work is a
prerequisite for `TASK-0225` (baseline residual benchmark).
