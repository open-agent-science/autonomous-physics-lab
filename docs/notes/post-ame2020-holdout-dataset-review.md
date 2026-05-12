# Post-AME2020 Holdout Dataset Review

Task: `TASK-0196`

## Review Verdict

`data/nuclear_masses/post_ame2020_holdout.yaml` is a reviewed row-level
holdout dataset for the post-AME2020 nuclear-mass campaign. It is suitable for
a later benchmark task, but it does not itself compute benchmark metrics or
promote any scientific claim.

## Source Artifact

Primary source:

- Xiao-Ying Qu, Kang-Min Chen, Cong Pan, Yang-Yang Yu, and Kai-Yuan Zhang,
  "Benchmarking nuclear energy density functionals with new mass data",
  Nuclear Science and Techniques 36, 231 (2025),
  DOI `10.1007/s41365-025-01821-1`.

Rows were extracted from the NST publisher JATS XML embedded in the publisher
HTML. The downloaded HTML and extracted XML checksums are pinned in
`data/nuclear_masses/post_ame2020_checksums.md`.

The ChinaXiv machine-translation PDF was downloaded only as an audit attempt.
Its Table A1 nuclide superscripts disagree with the NST publisher XML, so it
was not used for row extraction.

## Row Semantics

The committed dataset preserves all 296 Table 2 rows:

- `Z`, `N`, and `A` are derived from the published nuclide label.
- `new_measurement.value_mev` and uncertainty preserve the published `New`
  column in MeV.
- `ame2020_comparison.value_mev` and uncertainty preserve the published
  `AME2020` comparison column in MeV.
- `ame2020_comparison.was_extrapolated` preserves the source `#` marker.
- `new_minus_ame2020_binding_energy_mev` preserves the source difference
  column.
- Table 3 reference-to-method assignments are represented by
  `measurement_method_ids`.

The dataset records 55 AME2020 extrapolated comparison values, matching the
publisher source summary. One row, `U-238`, overlaps the frozen `NMD-0002`
baseline slice and is retained only as an audit row, not primary scoring input.

## Claim Boundary

This task commits data and provenance only. It does not:

- run `TASK-0197`;
- evaluate `HYP-PROPOSAL-0021`;
- compare model residuals;
- update canonical results or claims;
- describe the time split as prospective prediction.

Any later benchmark must consume this file without live fetching and must keep
retrospective time-split evidence separate from discovery claims.
