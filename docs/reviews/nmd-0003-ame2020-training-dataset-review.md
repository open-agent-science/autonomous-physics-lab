# NMD-0003 AME2020 Training Dataset Review

**Task:** `TASK-0516`  
**Dataset:** `NMD-0003`  
**Source:** AME2020 `mass_1.mas20` unrounded atomic mass table  
**Verdict:** `SOURCE_GATED_DATASET_READY_FOR_REVIEW`  
**Claim ceiling:** Source-curated training dataset only. No residual-law
candidate, benchmark metric, prediction registry entry, reveal score, claim,
knowledge entry, or canonical result is promoted by this PR.

## Summary

This PR adds a broader AME2020 measured-row Nuclear training surface that
unblocks the next large-surface Nuclear factory work after maintainer review.
The raw AMDC ASCII file is not vendored. Instead, the PR records an immutable
retrieval manifest, the raw source checksum, a deterministic parser, a
normalized measured-row training dataset, and a frozen split manifest.

The committed dataset contains **2309 measured training rows**. It excludes:

- the `Z=0` free-neutron row;
- AME2020 rows whose mass-excess or atomic-mass value / uncertainty fields
  contain the AME2020 `#` estimated-value marker or `*` not-calculable marker;
- all **295 primary** post-AME2020 holdout nuclide ids from
  `data/nuclear_masses/post_ame2020_holdout.yaml`.

`NMD-0002` is preserved as overlap audit coverage: all 11 `NMD-0002` nuclide ids
remain present in the `NMD-0003` training split.

## Source Artifact

The source artifact used for parsing was:

- retrieval URL:
  `https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt`
- source navigation page:
  `https://amdc.impcas.ac.cn/web/masseval.html`
- access date: `2026-06-01`
- byte size: `472648`
- SHA-256:
  `e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307`

The AME2020 source page describes the file as the atomic-mass ASCII table and
the file header states that `#` in place of a decimal point marks an estimated
(non-experimental) value. That marker is the mechanical boundary used here for
measured-row eligibility.

## Committed Artifacts

- `data/nuclear_masses/nmd-0003-source-manifest.yaml`
- `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
- `data/nuclear_masses/nmd-0003-split-manifest.yaml`
- `scripts/build_nmd0003_ame2020_training.py`
- `tests/test_nuclear_mass_dataset.py`

## Parser / Extraction Method

The parser reads the fixed-width `mass_1.mas20` format documented in the source
file header:

- `N`, `Z`, and `A` are read from the integer columns;
- `symbol` and `nuclide_id` are derived from the element and mass-number fields;
- `mass_excess_keV` and `mass_excess_uncertainty_keV` are read directly;
- `atomic_mass_u` is reconstructed from the AME integer micro-u prefix plus
  fractional micro-u field;
- `atomic_mass_uncertainty_u` is converted from micro-u to u;
- `evaluation` is set to `measured` only after the `#` / `*` filter passes;
- `source_entry` records the raw source line number.

No candidate metric, residual feature, factory ranking, or benchmark score is
computed during extraction.

## Row Accounting

| Category | Count |
| --- | ---: |
| AME2020 source data rows parsed | 3558 |
| `Z=0` rows excluded | 1 |
| estimated / not-calculable rows excluded | 1008 |
| primary post-AME2020 holdout rows excluded | 240 |
| committed NMD-0003 training rows | 2309 |

The primary post-AME2020 holdout has 295 nuclide ids. Of those, 240 would have
passed the AME2020 measured-row filter and are explicitly excluded from
training. The remaining primary holdout ids are already excluded by the AME2020
estimated / missing value filter.

## Split Boundary

The frozen split manifest defines:

- training: AME2020 measured rows excluding primary post-AME2020 holdout ids;
- excluded holdout: all primary `post_ame2020_holdout.yaml` ids;
- excluded estimated rows: AME2020 rows with `#` or `*`;
- excluded `Z=0`: the free neutron row.

This keeps `post_ame2020_holdout.yaml` as a retrospective time-split validation
surface and prevents it from being silently absorbed into the training set.

## Validation / Tests

The new tests assert:

- `NMD-0003` loads through the existing `load_nuclear_mass_dataset` loader;
- row count is stable at 2309;
- source checksum metadata is pinned;
- every committed row is `measured`, has `A == Z + N`, has `Z > 0`, and has
  uncertainty fields;
- nuclide ids are unique;
- primary post-AME2020 holdout ids are disjoint from the training split;
- all `NMD-0002` nuclide ids are preserved as overlap audit rows.

## Output Routing

- **Task verdict:** `SOURCE_GATED_DATASET_READY_FOR_REVIEW`
- **Canonical destination:** source-curated dataset files under
  `data/nuclear_masses/` plus this review note.
- **Review tier:** none; no `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*`
  artifact is proposed.
- **Gate A status:** not attempted. This is not a benchmark result.
- **Gate B status:** not attempted. No independent replay artifact is proposed.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Publication blocker:** none for dataset review. Candidate metrics remain
  blocked until maintainer review / merge and `TASK-0517` is unblocked.

## Limitations

- The raw AMDC ASCII file is not committed. Reproduction requires downloading
  the pinned retrieval URL and verifying the recorded SHA-256.
- The measured-row filter uses the AME2020 `#` marker and `*` marker only; it
  does not re-audit the underlying AME experimental-input graph.
- This PR does not decide whether future candidates should use all 2309 rows,
  stratified subsets, or additional stress splits. It only freezes the initial
  source-safe training surface and primary holdout exclusion.
- This PR does not run `TASK-0517`; that remains blocked until this dataset PR
  is merged and accepted.

## Verdict

`SOURCE_GATED_DATASET_READY_FOR_REVIEW`.

`NMD-0003` provides the source-pinned, measured-row AME2020 training surface
requested by `TASK-0516` while preserving the post-AME2020 holdout boundary.
