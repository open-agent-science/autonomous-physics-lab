# Materials MD-0002 Benchmark Control Plan

**Task:** `TASK-0701`
**Campaign:** Materials Property Residuals
**Mode:** planning only (no rows, no metrics, no residual inspection)
**Decision:** `FORMATION_ENERGY_PRIMARY_BAND_GAP_DIAGNOSTIC_PREDECLARED`

## Scope

This note freezes the MD-0002 benchmark and control plan before value-bearing
MD-0002 rows or residuals exist. It uses the already reviewed MD-0002 acquisition
contract, holdout scaffold, and MD-0001 negative memory only. It does not fetch
Materials Project rows, inspect residuals, compute metrics, create `RESULT-*` or
`PRED-*` artifacts, promote claims, or recommend materials.

The plan binds the later benchmark to one primary axis:
`formation_energy_per_atom` for stable ternary oxides. The `band_gap` axis stays
visible but diagnostic-only unless it independently clears the same null,
control, and split-robustness gates on the acquired slice.

## Frozen Benchmark Inputs

| Field | Predeclared value |
| --- | --- |
| Dataset family | `MD-0002` |
| Source | `materials-project` |
| Slice | stable ternary oxides: exactly two non-oxygen cations plus oxygen |
| Provenance class | computed DFT only |
| Primary axis | `formation_energy_per_atom`, units `eV_per_atom` |
| Diagnostic axis | `band_gap`, units `eV` |
| Holdout binding | `data/materials/md0002_holdout_manifest.yaml` |
| Row cap | stop and report if the bounded acquisition exceeds 1500 included rows per axis |
| No-peek rule | split rules, controls, and success margins are frozen before residuals are inspected |

The acquisition task must pin the Materials Project `database_version`, raw
snapshot checksum, normalized dataset checksums, row counts, and final split
assignments before any benchmark score is computed.

## Formation-Energy Baseline Family

The later MD-0002 benchmark must compare the following predeclared baseline
families on `formation_energy_per_atom` only:

1. `global_mean`: train-set mean formation energy, applied to every holdout row.
2. `global_median`: train-set median formation energy, applied to every holdout row.
3. `cation_group_mean`: composition-aware comparator using predeclared cation
   family buckets where available.
4. `cation_pair_mean`: unordered non-oxygen cation-pair comparator, the primary
   MD-0002 extension of the MD-0001 cation-group baseline.
5. `structure_or_prototype_mean`: optional diagnostic comparator keyed by exact
   `spacegroup_symbol` or a predeclared prototype bucket. It must fall back to the
   global train statistic when the bucket is unseen.

No fitted model family may be added after holdout residuals are inspected. Any
later learned model, tuned grouping rule, or feature search requires a separate
task and cannot be used to decide whether this predeclared benchmark succeeded.

## Null Controls

The formation-energy benchmark succeeds only if the primary composition-aware
comparator beats both global nulls and survives deterministic controls:

- label-shuffle control: permute train labels with fixed seeds and refit the same
  comparator;
- cation-pair shuffle control: permute cation-pair labels with fixed seeds while
  preserving the train/holdout split;
- train-only statistic control: compute all grouping statistics from train rows
  only, with explicit fallback for unseen groups;
- row-order control: prove scores are invariant to input row ordering by sorting
  on stable `material_id` before split-dependent operations.

Recommended fixed control seeds: `0`, `1`, `2`, `7`, and `11`. If the benchmark
implementation uses additional seeds, the added seeds must be declared in code
before scoring and reported alongside the original five.

## Split-Sensitivity Plan

The benchmark must report the primary frozen split from
`data/materials/md0002_holdout_manifest.yaml` plus these predeclared robustness
views when row counts permit:

- `seeded_random_70_30` with fixed seeds `0`, `1`, `2`, `3`, and `4`;
- leave-one-cation-pair-family-out as an extrapolation stress test;
- leave-one-structure-or-prototype-out when prototype labels are available;
- property-range bins declared before residual inspection, reported separately
  for formation energy and band gap.

The same split-sensitive rule from MD-0001 carries forward: a comparator is
`split_robust` only if it wins at least `4 / 5` seeded holdouts and its
seeded-mean margin over the runner-up exceeds the larger of the two comparators'
across-seed standard deviations.

## Success Margins

Formation-energy promotion to a later benchmark result remains blocked unless
all of the following predeclared conditions hold:

- the cation-pair or cation-family comparator has lower holdout MAE than both
  `global_mean` and `global_median`;
- relative MAE improvement versus the best global null is at least `10%`;
- absolute MAE improvement versus the best global null is at least
  `0.05 eV_per_atom`;
- deterministic label-shuffle and cation-pair-shuffle controls do not match or
  beat the real comparator under the reported permutation rule;
- the comparator is `split_robust` under the seeded random rule above;
- no stop condition fires for license, version, provenance, row schema, row cap,
  mixed measured/computed values, or no-peek violation.

If the comparator beats nulls but misses a control or split-robustness condition,
the correct verdict is diagnostic memory, not a promoted `RESULT-*`.

## Band-Gap Diagnostic Boundary

`band_gap` must remain diagnostic-only for MD-0002 unless it independently clears
the same gates on the acquired slice:

- beats both global nulls on the frozen split;
- survives label-shuffle and cation/group shuffle controls;
- is `split_robust` under the seeded rule;
- stays separate from formation energy throughout reporting;
- uses computed DFT rows only.

Band-gap behavior cannot promote, weaken, or reinterpret formation-energy
behavior. A band-gap failure should be recorded as negative memory rather than a
failure of the formation-energy benchmark.

## Do-Not-Promote Conditions

Do not create a `RESULT-*`, `PRED-*`, `CLAIM`, `KNOW`, material ranking, or public
discovery claim if any of these conditions holds:

- MD-0002 acquisition metadata are incomplete or placeholder-valued;
- row counts exceed the cap or fall below the planned lower target without a
  reviewed route decision;
- rows mix computed DFT with measured or model-only values;
- formation energy and band gap are pooled into one score;
- split rules, grouping definitions, or success margins are tuned after residual
  inspection;
- the winning comparator fails deterministic null controls or split robustness;
- license/version/checksum provenance is unclear.

## Later Implementation Checklist

A later benchmark implementation should record:

- exact input dataset files and their checksums;
- train/validation/holdout counts by axis;
- baseline definitions and fallback behavior;
- MAE and median absolute error for every comparator;
- relative and absolute skill versus the best global null;
- control-seed results;
- split-sensitivity table and verdict;
- explicit statement that no material-design or discovery claim is implied.

## Limitations

- This task is a pre-score control plan only. It cannot establish whether MD-0002
  formation energy generalizes the MD-0001 signal.
- Row-count and split feasibility depend on the later maintainer-run acquisition.
- All rows remain computed DFT values, so even a successful benchmark would not
  support measured-property, synthesis, device, biomedical, or material-selection
  guidance.

## Output Routing Summary

- **Task verdict:** `not_applicable` (planning gate); decision
  `FORMATION_ENERGY_PRIMARY_BAND_GAP_DIAGNOSTIC_PREDECLARED`.
- **Canonical destination:** this review note,
  `docs/reviews/materials-md0002-benchmark-control-plan.md`.
- **Review tier:** none; no `RESULT-*` / `PRED-*` artifact.
- **Gate A status:** not applicable because no rows or metrics were produced.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none; this freezes a later benchmark contract only.
- **Publication blocker:** result publication remains blocked until MD-0002 rows,
  checksums, split assignments, benchmark metrics, null controls, and
  split-sensitivity results exist and pass the declared gates.
