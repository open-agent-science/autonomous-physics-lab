# GWTC-5 O4b Selection-Control Reconciliation

Task: `TASK-1100`
Review date: 2026-07-27
Source retrieval cutoff: 2026-07-27T10:32:13Z
Scope: official metadata and deterministic selection-control proof only

## Verdict

`STOP_NO_AUDITABLE_O4B_CONTROL`

One bounded reconciliation pass did not establish an auditable O4b-only
selection control. The official GWOSC run page and the versioned GWTC-5
catalog record agree that O4b began at GPS `1396796418`, while the pinned
O4a+O4b sensitivity README labels GPS `1396969218` as the same UTC start.
Those values differ by exactly 172800 seconds. The same README exposes only
aggregate O4a+O4b analysis-time and generated-count normalization and does not
document a deterministic partial-month split or weight renormalization for an
O4b-only subset.

The gravitational-wave campaign remains parked. No event row, posterior
sample, strain sample, search trigger, or astrophysical value was inspected or
ingested. No source manifest, benchmark, result, prediction, claim, or
knowledge artifact is authorized by this review.

## Inputs And Method

Input references:

- `tasks/TASK-1100-resolve-gwtc5-o4b-selection-control.yaml`
- `tasks/TASK-1085-gwtc5-source-version-incubator.yaml`
- `docs/reviews/gravitational_waves/gwtc5-o4b-source-version-incubator.md`
- `docs/blind-holdout-benchmark-protocol.md`
- `docs/notes/fresh-data-source-policy.md`

Method:

1. Retrieve the official GWOSC O4b page, the versioned GWTC-5 DCC page, the
   pinned Zenodo landing page and API record, and the small sensitivity README.
2. Verify the README bytes against Zenodo's published size and MD5, then
   compute local SHA-256 checksums for every retrieved source.
3. Compare the observing-run boundaries exactly in integer GPS seconds.
4. Audit only the README fields needed to reconstruct an O4b-only selection
   normalization: injection time, analysis time, generated count, accepted
   count, monthly mixture weights, and monthly generated counts.
5. Stop without downloading the 2.94 GB injection HDF because the published
   schema already proves that the missing aggregate normalization cannot be
   recovered from retained injection rows alone.

Code reference: no repository runtime or scientific analysis code was added.
The integer arithmetic is recorded below, and repository validation is
defined by the task YAML.

## Frozen Official Sources

All retrieved bytes were kept in the task's non-repository local-artifact
workspace. Machine-local paths and source bytes are not committed.

| Source | Frozen identity | Retrieved bytes | SHA-256 | Audit role |
| --- | --- | ---: | --- | --- |
| [GWOSC O4b release](https://gwosc.org/O4/O4b/) | Dataset DOI `10.7935/8emv-ag54`; revision history says first release 2026-05-26 | 19,896 | `be4a2403cbb9acefd2cb479dc4f41970624fd10df92b5bdb55679df6a747c5d6` | Authoritative observing-run interval, engineering-run separation, release history, and CC BY 4.0 notice |
| [GWTC-5 catalog record](https://dcc.ligo.org/LIGO-P2600152-v6/public) | DCC `LIGO-P2600152-v6` | 8,423 | `c67cc17ce89840e36818bd7a63724f89124dafdd5a79389ba235d9d3dc4ce05b` | Independent versioned statement of the O4b UTC interval and preceding engineering interval |
| [Zenodo sensitivity record](https://zenodo.org/records/19500064) | Version `v1`; DOI `10.5281/zenodo.19500064`; publication date 2026-04-10; updated 2026-05-26 | 78,446 | `1dce81912f8ffcaa766feacd03fe1018ce86a49e59fe3a9ad7a193edbc3b2cb6` | Public version label, file identities, checksums, creators, and license |
| [Zenodo API record](https://zenodo.org/api/records/19500064) | Record `19500064`; revision id `4`; concept DOI `10.5281/zenodo.19500063` | 5,259 | `d0eea4f3a4cfcc7d17d6ec4a0964d354e866bb517e5932467a946fe656fc3564` | Machine-readable file size and MD5 cross-check |
| [Sensitivity README](https://zenodo.org/records/19500064/files/gwtc-5_o4ab_sensitivity-estimates.md?download=1) | `gwtc-5_o4ab_sensitivity-estimates.md` | 16,876 | `b03eda3a058f2f6100effc3766f92ec6d44deca9b0f1017a013d1384bd04c82e` | Boundary text, HDF schema, monthly counts, normalization formulas, and weight semantics |

The README's locally computed MD5 is
`457b02eca6088eb8cc23a97f37b01f8b`, exactly matching Zenodo. Zenodo also
publishes the undownloaded injection HDF identity:

- filename: `samples-rpo4ab-1366933504-55469568-clipped.hdf`;
- size: 2,941,792,668 bytes;
- upstream MD5: `a1106c27ec6cfd906231613523f7b174`.

The HDF and the 21.6 MB PSD archive were not downloaded. The source record is
CC BY 4.0 and names the LIGO Scientific Collaboration, Virgo Collaboration,
and KAGRA Collaboration as creators.

## Documentation Hierarchy

The bounded pass applies this precedence:

1. The GWOSC observing-run release defines the public O4b run boundary.
2. The versioned GWTC-5 DCC record independently confirms the UTC interval and
   distinguishes four preceding engineering days from O4b.
3. The pinned Zenodo record defines the sensitivity artifact identity, while
   its README defines that artifact's schema and documented normalization.

The sensitivity README cannot silently redefine the observing-run boundary.
Conversely, replacing its GPS value locally with the GWOSC value would not
prove that the injection campaign, generated-count denominator, analysis time,
and monthly weights were constructed for the replacement boundary.

The GWOSC revision history exposed only the first release, the DCC source was
checked at explicit version `v6`, and the Zenodo sensitivity record exposed
only `v1`. No correction, erratum, replacement file, or documented
normalization amendment was present on those inspected official surfaces by
the retrieval cutoff.

## Exact Boundary Arithmetic

| Quantity | GPS seconds | Source |
| --- | ---: | --- |
| Official O4b start | `1396796418` | GWOSC O4b release |
| DCC O4b start | `1396796418` equivalent UTC | `LIGO-P2600152-v6` |
| Sensitivity README O4b start | `1396969218` | Zenodo README `v1` |
| Shared O4b end | `1422118818` | GWOSC and sensitivity README |

Deterministic differences:

```text
1396969218 - 1396796418 = 172800 seconds = 2 days
1422118818 - 1396796418 = 25322400 seconds
1422118818 - 1396969218 = 25149600 seconds
```

The README pairs GPS `1396969218` with the text "15:00 UTC 10 Apr 2024."
GWOSC pairs that UTC instant with GPS `1396796418`. The conflict is therefore
internal to the published boundary representation, not a difference between
two declared UTC start dates.

Both starts fall inside the README's April 2024 generation bin:

```text
April bin: 1395963904 .. 1398556672
April generated count: 38060841

official start offset from bin start = 832514 seconds
README start offset from bin start   = 1005314 seconds
official start to bin end            = 1760254 seconds
README start to bin end              = 1587454 seconds
```

Neither candidate start is a documented monthly generation boundary. A
time-proportional allocation of April's 38,060,841 generated draws would be a
new modeling assumption, not an exact count supplied by the source.

## Normalization Proof

The README describes one HDF spanning O4a and O4b. Its root contains singular,
aggregate attributes:

- `gps_start` and `gps_end`;
- `total_analysis_time`;
- `total_generated`;
- `num_accepted`;
- `searches`;
- `date`.

The detection-probability example divides an importance-sampling sum by the
root `total_generated`. The sensitive volume-time example additionally
multiplies by the root `total_analysis_time`. The event table supplies
`time_geocenter`, a constant `lnpdraw_time_geocenter`, and `weights` described
as wall-time weights within each month.

These fields do not close an O4b-only reconstruction:

| Required control | Published evidence | Deterministic finding |
| --- | --- | --- |
| Authoritative O4b start | GWOSC/DCC start and README GPS start differ by 172800 seconds | Unresolved producer-side conflict |
| O4b time filter | Retained rows expose `time_geocenter` | Rows can be filtered, but the correct start cannot be selected from current official metadata |
| O4b generated denominator | Root `total_generated` is for the combined artifact; monthly counts are whole-month totals | No exact count is supplied for the partial April bin at either candidate start |
| O4b analysis time | Root `total_analysis_time` is singular for the combined artifact | No O4b-only value or documented derivation is supplied |
| O4b mixture normalization | `weights` use wall-time within each month | No documented rule renormalizes the mixture after removing O4a and part of April |
| Recovery from stored rows | Only injections that might be detected are recorded; `num_accepted` counts those passing the hopeless-SNR cut | Stored rows cannot reconstruct all generated draws represented by `total_generated` |

Filtering the HDF by `time_geocenter` would therefore change the numerator
without supplying the matching generated denominator, analysis time, or
mixture normalization. The monthly counts do not repair that problem because
the critical April interval is partial and the source does not assert uniform
generated counts over wall time. The constant time draw density also does not
recover omitted generated draws from a file that intentionally stores only
potentially detectable injections.

The proof stops at schema and normalization. It does not inspect the HDF,
evaluate a search threshold, calculate a detection probability or
volume-time, or test a population model.

## Limitations

- This is a bounded audit of the listed official public surfaces as of the
  retrieval cutoff, not a claim that no correction exists in private LVK
  systems.
- The HDF root attributes were not read directly because the multi-gigabyte
  file was outside scope. The proof relies on the pinned producer README's
  explicit schema and storage semantics.
- No proportional allocation, inferred livetime, or locally chosen boundary
  was substituted for missing official normalization.
- This infrastructure verdict says nothing about compact-binary populations,
  catalog completeness, cosmology, anomalies, or new physics.

## Terminal Reopen Trigger

This one-attempt route may reopen only after LVK, GWOSC, or the sensitivity
artifact publisher releases a versioned official correction or replacement
artifact that supplies all of the following:

1. one unambiguous GPS/UTC O4b start and an explanation or supersession of the
   current 172800-second conflict;
2. an O4b-only `total_generated` value tied to that exact boundary;
3. an O4b-only `total_analysis_time` tied to the same boundary;
4. a documented mixture-weight or renormalization rule valid for the exact
   O4b subset, including its partial first month;
5. versioned filenames, byte lengths, and checksums for the corrected control.

A code-only workaround, time-proportional split, event-row filter, or
maintainer preference does not satisfy this trigger. Until all five items are
officially available, no further reconciliation task, event ingestion, or
benchmark execution should be opened for this route.

## Output Routing

- Canonical destination:
  `docs/reviews/gravitational_waves/gwtc5-o4b-selection-control-task1100.md`
- Campaign state: STOP and parked pending the terminal official-source trigger.
- Source-manifest impact: none; no amendment is allowed on this outcome.
- Gate A / Gate B: not applicable because no benchmark or result was run.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: unresolved official boundary plus missing O4b-only
  generated-count, analysis-time, and mixture-weight normalization.
