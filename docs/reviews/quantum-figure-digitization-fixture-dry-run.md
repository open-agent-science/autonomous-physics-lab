# Quantum Figure-Digitization Fixture Dry Run

**Task:** `TASK-0490`  
**Campaign:** `quantum_size_effects`  
**Fixture:** `data/quantum_dots/digitization_fixture.yaml`  
**Status:** synthetic fixture only; no real measurement rows

## Scope

This dry run creates a synthetic ledger for future WebPlotDigitizer-class
quantum-dot figure extraction. It does not digitize a real publication figure,
commit raw figure assets, create `qd-*.yaml` measurement rows, run size-effect
baseline metrics, or promote claims.

## Fixture Coverage

The fixture exercises the fields required by the direct-measurement
digitization protocol:

- axis calibration for diameter (`nm`) and absorption peak (`eV`);
- at least four calibration anchors;
- extraction-tool metadata;
- per-point raw pixel coordinates;
- per-point material, property kind, and primary-source identifiers;
- coordinate uncertainty in diameter and energy;
- residual-vs-formula cross-check fields;
- included and excluded point states;
- exclusion reasons for excluded points;
- explicit statement that no `qd-*.yaml` rows are authorized by the fixture.

## Tests

`tests/test_quantum_dot_digitization_fixture.py` verifies that:

- the fixture is synthetic-only and does not authorize baseline metrics;
- the axis calibration has at least four anchors with units;
- every extracted point has provenance, uncertainty, and cross-check fields;
- excluded points carry an exclusion reason;
- the fixture cannot itself authorize real quantum-dot measurement rows.

## Mapping To Future Real Digitization Artifacts

A future real digitization task should replace this synthetic YAML with the
protocol layout:

- `data/quantum_dots/digitization/<source_id>/README.md`;
- `axis_calibration.csv`;
- `extracted_points.csv`;
- `notes.md`.

The future task must also register the source in `source_manifest.yaml`, record
tool version and reviewer attribution, and preserve digitized values rather
than overwriting them with calibration-polynomial outputs.

## Verdict

`VALID_IN_RANGE`

The fixture validates the ledger shape needed for future figure-derived
quantum-dot rows while keeping the direct-measurement benchmark blocked until
real source artifacts, digitization exports, and row-level provenance exist.

## Output Routing Summary

- task verdict: `VALID_IN_RANGE`;
- canonical destination: synthetic fixture, targeted tests, and this review
  note;
- review tier: `none`;
- Gate A status: not attempted;
- Gate B status: not attempted;
- claim impact: no claim change;
- knowledge impact: no knowledge change;
- result artifact impact: no `results/` artifacts modified;
- limitations / blockers: no real figure was digitized; source quality,
  copyright status, and real axis readability remain future curator work.
