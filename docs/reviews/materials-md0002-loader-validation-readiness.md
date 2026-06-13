# Materials MD-0002 Loader Validation Readiness

**Task:** `TASK-0700`
**Campaign:** Materials Property Residuals
**Status:** loader validation ready for fixture and later acquisition files
**Verdict:** `VALID_IN_RANGE`

## Scope

This task adds a deterministic MD-0002 normalized dataset loader at
`physics_lab/datasets/materials_md0002.py` and extends
`tests/test_materials_md0002_schema_fixture.py` so the committed synthetic
fixture is validated through the same loader path expected for later acquisition
files.

The loader reads committed YAML only. It does not fetch Materials Project rows,
compute residuals, score benchmark metrics, recommend materials, create result
artifacts, or promote claims.

## Loader Checks

The loader validates:

- MD-0002 dataset family and `materials-project` source family;
- `live_external_fetch_allowed: false`;
- source-version and checksum placeholder rules for fixture payloads;
- pinned source-version and checksum requirements for non-fixture payloads;
- axis policy coverage for `formation_energy_per_atom` and `band_gap`;
- axis-specific units: `eV_per_atom` and `eV`;
- required normalized row fields;
- computed DFT provenance for included rows;
- explicit `excluded` provenance plus `exclusion_reason` for excluded rows;
- row-id uniqueness;
- material-id uniqueness within each property axis;
- two-cation ternary-oxide composition shape;
- record locator/source/provenance consistency.

Formation energy and band gap are grouped and summarized as separate axes. A
material may appear once per axis, but duplicate `material_id` values inside the
same axis fail validation.

## Fixture Coverage

The focused fixture tests now cover:

- synthetic/pre-acquisition guardrails;
- axis-policy separation;
- two-cation oxide row shape;
- included computed-DFT fixture rows;
- explicit axis-specific exclusions;
- loader summary counts by axis;
- duplicate material-id rejection within one axis;
- unresolved placeholder rejection for non-fixture payloads.

## Limitations

- The committed fixture still contains fake values only.
- No real MD-0002 acquisition rows are present in this task.
- The loader does not validate the eventual Materials Project API response shape
  before normalization.
- Checksum validation currently enforces presence/pinning rules; it does not
  recompute a source snapshot checksum because no real snapshot is committed by
  this task.

## Output Routing Summary

- Task verdict: `VALID_IN_RANGE`.
- Canonical destination: `physics_lab/datasets/materials_md0002.py`,
  `tests/test_materials_md0002_schema_fixture.py`, and this review note.
- Review tier: `none`.
- Gate A status: `not_applicable`; no value-bearing source rows were ingested.
- Gate B status: `not_applicable`; no benchmark metrics or result promotion were
  attempted.
- Claim impact: no claim change.
- Knowledge impact: reusable loader/schema guard only.
- Publication blocker: MD-0002 remains unfetched; acquisition still needs a
  maintainer-authorized source run with pinned database version, checksum,
  attribution, row counts, and holdout binding before benchmark work can proceed.
