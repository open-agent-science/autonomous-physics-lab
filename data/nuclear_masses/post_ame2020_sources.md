# Post-AME2020 Nuclear-Mass Source Manifest

`TASK-0187` pins reviewed source surfaces for a future retrospective
post-AME2020 time-split benchmark.

This is deliberately a source manifest, not a row-level dataset. The full table
of later measurements should be imported only in a separate task that records
the exact source artifact checksum, extraction method, row filters, and unit
mapping.

## Primary Source

The candidate holdout source is:

- Xiao-Ying Qu, Kang-Min Chen, Cong Pan, Yang-Yang Yu, and Kai-Yuan Zhang,
  "Benchmarking nuclear energy density functionals with new mass data",
  Nuclear Science and Techniques 36, 231 (2025),
  DOI `10.1007/s41365-025-01821-1`.

The source reports a compilation of 296 newly measured masses from 40
references published between 2021 and 2024 after AME2020. It also compares
those values with AME2020 and records which AME2020 comparison values were
extrapolated empirical values.

## Baseline Reference

The comparison and training boundary remains AME2020:

- AME2020 Part I: DOI `10.1088/1674-1137/abddb0`
- AME2020 Part II: DOI `10.1088/1674-1137/abddaf`
- AMDC source page: <https://amdc.impcas.ac.cn/web/masseval.html>

APL's current frozen nuclear-mass baseline slice is still `NMD-0002`. Any
future row-level holdout import must exclude those nuclides from primary
time-split scoring unless a task explicitly labels them as overlap-audit rows.

## Current Boundary

This manifest:

- records source references and stable identifiers;
- records measured-versus-extrapolated policy;
- records exclusion rules for `NMD-0002` overlap;
- blocks live fetching during validation;
- does not activate `TASK-0188` benchmark execution by itself.

`TASK-0188` should start only after a reviewed row-level
`data/nuclear_masses/post_ame2020_holdout.yaml` exists or after the maintainer
explicitly chooses to treat this manifest as sufficient for a source-audit-only
benchmark dry run.
