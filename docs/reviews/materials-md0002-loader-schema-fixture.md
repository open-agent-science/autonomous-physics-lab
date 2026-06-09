# Materials MD-0002 Loader Schema Fixture

**Task:** `TASK-0645`
**Campaign:** Materials Property Residuals
**Status:** planning-only fixture preflight (no live data fetched, no metrics computed)
**Verdict:** `schema_ready_for_later_acquisition_preflight`

## Scope

This task adds a tiny synthetic MD-0002 fixture at
`data/materials/fixtures/md0002_schema_fixture.yaml` and a deterministic test at
`tests/test_materials_md0002_schema_fixture.py`. The fixture checks that the
Materials row path can represent the planned stable-ternary-oxide slice before any
Materials Project acquisition occurs.

The fixture uses fake values and fake `mp-fixture-*` locators only. It does not
fetch Materials Project rows, commit value-bearing MD-0002 source rows, compute
residuals, score a baseline, or make material-property claims.

## Represented Row Shape

The fixture covers:

- two-cation oxide composition (`A/B/O` and `C/D/O`) with explicit cation lists;
- `materials-project` source family with source version and checksum placeholders;
- computed DFT provenance and `GGA_or_GGA+U` functional metadata;
- the two planned MD-0002 axes kept separate:
  `formation_energy_per_atom` in `eV_per_atom` and `band_gap` in `eV`;
- stable-row fields (`is_stable: true`, `energy_above_hull: 0.0`);
- an explicit `band_gap` axis-only excluded row with `value: null` and
  `exclusion_reason`.

## Guardrails

`tests/test_materials_md0002_schema_fixture.py` verifies that:

- the file is marked `fixture_only` and blocks live fetches;
- source version and snapshot checksum remain acquisition placeholders;
- row count matches the fixture rows;
- top-level metric, residual, prediction, and claim keys are absent;
- included rows are stable computed DFT fixture values;
- excluded rows stay visible with an explicit axis-specific exclusion reason;
- no row uses a real Materials Project locator.

## Limitations

- The fixture does not validate a real loader implementation against a pinned
  Materials Project snapshot.
- The fake values are schema sentinels only and must never be copied into a
  dataset, benchmark, result, claim, or publication.
- A later acquisition task still has to pin database version, checksum, row counts,
  attribution, and final dataset files.

## Output Routing Summary

- Task verdict: `schema_ready_for_later_acquisition_preflight`.
- Canonical destination: this review plus the synthetic fixture and test.
- Review tier: `none`.
- Gate A status: `not_applicable`; no source rows were ingested.
- Gate B status: `not_applicable`; no metrics or result promotion attempted.
- Claim impact: `none`.
- Knowledge impact: low-risk reusable schema guard for a future MD-0002
  acquisition task.
- Publication blocker: still requires maintainer-authorized acquisition with a
  pinned Materials Project version, checksum, attribution, and no-peek manifest
  binding before any benchmark task can run.
