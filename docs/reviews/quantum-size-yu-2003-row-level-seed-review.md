# Quantum Size Yu 2003 Row-Level Seed Review

Task: `TASK-0281`

## Scope

This review records the first row-level Quantum Size Effects dataset seed for
`absorption_peak_eV`. The dataset is limited to the DOI-pinned Yu 2003 source
already registered as `yu-2003-cm-absorption`.

No baseline model comparison, holdout reveal, autonomous hypothesis search, or
claim promotion was run.

## Inputs

- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- `docs/quantum-size-effect-holdout-protocol.md`
- Yu et al. 2003, DOI `10.1021/cm034081k`

## Method

The seed uses the published Yu 2003 empirical sizing-curve polynomials for
CdTe, CdSe, and CdS nanocrystals. For each material, four first excitonic
absorption peak wavelengths were selected inside the source's calibration
surface. The row `diameter_nm` value is computed from the corresponding source
polynomial, and `value_eV` is computed from `hc/lambda` using
`1239.841984 eV nm`.

The selected rows are explicitly marked as calibration-derived outputs. No
source table rows, spectra, or digitized figure coordinates were copied into
repository memory.

## Metrics

- Dataset files added: 1
- Dataset rows added: 12
- Included rows: 12
- Excluded rows: 0
- Materials covered: CdTe, CdSe, CdS
- Property kind: `absorption_peak_eV`
- Source ids used: `yu-2003-cm-absorption`
- Baseline comparisons run: 0
- Claims promoted: 0

## Limitations

- These rows are calibration-derived from published sizing curves, not direct
  source table rows. `TASK-0283` should decide whether this is sufficient for
  the first baseline gate or whether direct table/figure-reviewed rows are
  needed first.
- The seed intentionally covers only `absorption_peak_eV`; it must not be
  combined with emission or bandgap residuals.
- Values are rounded to four decimals for diameter and six decimals for
  energy. Future benchmark code should treat the seed as a reviewable
  calibration surface, not as a high-precision metrology artifact.
- No synthesis, fabrication, biomedical, or device-performance guidance is
  included or implied.

## Verdict

`PARTIALLY_VALID`

The task produces a schema-valid, source-linked, multi-material absorption seed
that can support the row-level readiness review. It should not by itself
unblock the first baseline without the `TASK-0283` gate.
