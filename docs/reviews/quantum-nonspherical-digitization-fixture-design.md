# Quantum Non-Spherical Digitization Fixture Design

**Task:** `TASK-0655`  
**Campaign:** Quantum Size Effects  
**Fixture:** `data/quantum_dots/fixtures/nonspherical_digitization_fixture.yaml`  
**Status:** synthetic fixture only; no real measurement rows

## Scope

This design defines a synthetic non-spherical figure-digitization ledger for
tetrahedral InP-style sizing curves before any Almeida 2023 or other real
non-spherical figure coordinates are digitized. It does not download article or
SI files, digitize publication figures, create committed `qd-*.yaml` measurement
rows, run size-effect baseline metrics, or promote claims.

Prerequisite [TASK-0637](../tasks/TASK-0637-extend-quantum-size-schema-for-non-spherical-axes.yaml)
landed `edge_length_nm`, `volume_nm3`, `equivalent_diameter_nm`, `morphology`,
and `size_conversion` on the `quantum_dot_size_effect` schema.

## Fixture Coverage

The fixture extends the spherical dry-run ledger
(`data/quantum_dots/digitization_fixture.yaml`, TASK-0490) with non-spherical
routes required by
[docs/quantum-direct-measurement-digitization-protocol.md](../quantum-direct-measurement-digitization-protocol.md)
§ Non-Spherical Size Axes:

- primary x-axis calibration on `edge_length_nm` with `source_axis_conversion`
  metadata mapping figure quantity to schema size axis and `tetrahedral`
  morphology;
- alternate `volume_nm3` calibration block for a separate non-spherical panel;
- included points on `edge_length_nm`, `volume_nm3`, and
  `equivalent_diameter_nm` with preserved `size_conversion` metadata;
- per-point coordinate uncertainty on size and energy axes;
- residual-vs-formula cross-check fields;
- included and excluded point states with exclusion reasons;
- explicit statement that no `qd-*.yaml` rows are authorized by the fixture.

All coordinates and values are fabricated. No Almeida 2023 figure pixels or
published measurement values are committed.

## Schema Round-Trip

`tests/test_quantum_nonspherical_digitization_fixture.py` maps each included
fixture point to a `quantum_dot_size_effect` entry, validates the payload with
`validate_document`, and round-trips numeric size axes, conversion metadata,
and uncertainty fields back to fixture-shaped dictionaries.

This proves the TASK-0637 schema extension can accept digitization-ledger rows
for non-spherical sources without coercing edge length or volume into
undocumented `diameter_nm` fields.

## Mapping To Future Real Digitization

A future Almeida digitization task should replace this synthetic YAML with the
protocol artifact layout under `data/quantum_dots/digitization/<source_id>/`,
register `almeida-2023-nano-letters-inp-optical` in `source_manifest.yaml`, and
preserve per-point primary-source breakdown before any `qd-*.yaml` seed is
reviewed.

## Verdict

`VALID_IN_RANGE`

The fixture validates the non-spherical ledger shape and schema round-trip path
needed for future figure-derived InP rows while keeping the direct-measurement
benchmark blocked until real source artifacts, license review, and row-level
provenance exist.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: synthetic fixture, targeted tests, and this review note;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- limitations / blockers: no real figure was digitized; Almeida license and
  figure-surface review remain separate tasks; TASK-0225 remains blocked.
