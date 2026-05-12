# Post-AME2020 Nuclear-Mass Source Manifest

`TASK-0187` pins reviewed source surfaces for a retrospective post-AME2020
time-split benchmark. `TASK-0196` adds the reviewed row-level holdout dataset
and extraction checksums. `TASK-0197` consumes those committed rows for active
retrospective metrics.

The source manifest remains separate from the row-level dataset. The committed
dataset lives at `data/nuclear_masses/post_ame2020_holdout.yaml`; checksums are
recorded in `data/nuclear_masses/post_ame2020_checksums.md`.

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
- records that reviewed row-level values are now committed;
- records that TASK-0197 activates benchmark metrics from committed rows only.

`TASK-0197` consumes `post_ame2020_holdout.yaml` as a retrospective benchmark.
It still does not promote claims, canonical results, or strict blind-prediction
language.
