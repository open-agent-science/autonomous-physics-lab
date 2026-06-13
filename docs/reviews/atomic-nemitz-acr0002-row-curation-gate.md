# Atomic Nemitz 2016 ACR-0002 Row Curation Gate

**Task:** `TASK-0704`
**Campaign:** Atomic-Clock Residuals
**Status:** row curated (cross-source target committed)
**Decision:** `ACR_0002_ROW_COMMITTED_NO_DRIFT_CROSS_SOURCE_TARGET`

## Scope

This task curates the second independent direct Yb/Sr frequency-ratio row for
the Atomic-Clock Residuals campaign from Nemitz et al. 2016 / RIKEN, the
cross-source partner for the Beloy 2021 / BACON reference row
(`ACR-0001-ROW-003`). It commits exactly one `direct_measurement` row,
`ACR-0002-ROW-001`, with explicit uncertainty, covariance state, and a
`cross_source_target` holdout role.

It does **not** compare Nemitz against Beloy, compute consistency metrics, fit
constants drift, create `RESULT-*` / `PRED-*` / `CLAIM-*` artifacts, or make any
fundamental-physics interpretation.

## Why This Was Previously Blocked

The prior second-source gate
([`atomic-second-source-yb-sr-row-gate.md`](atomic-second-source-yb-sr-row-gate.md),
`TASK-0525`) returned `BLOCKER_SECOND_SOURCE_ROW_NOT_COMMITTED`. The single
load-bearing blocker was the **arXiv-vs-Nature version-of-record table-level
drift cross-check**: APL requires (per `TASK-0452`, matching the Beloy 2021
posture) that a high-precision atomic-clock row be verified against the
published version of record before commit. The public Nature page does not
expose the full Table 1 uncertainty budget, and the version-of-record PDF is
copyright and was not available. The campaign window was also unlocked because
the arXiv text states only "ten measurements over four months".

## What Cleared The Gate

The maintainer supplied the **Nature Photonics version-of-record PDF locally**
(`doi:10.1038/nphoton.2016.20`, held off-repository, copyright — **not
committed**), exactly as was done for the Beloy 2021 row. A field-by-field
cross-check of the committed arXiv preprint (`arXiv:1601.04582v1`) against the
version of record was performed.

### Version-drift verdict: `NO_DRIFT`

| Field | arXiv:1601.04582v1 | Nature VOR (10.1038/nphoton.2016.20) | Match |
| --- | --- | --- | --- |
| Ratio R (abstract) | 1.207507039343337749(55) | 1.207507039343337749(55) | yes |
| Ratio R (body) | …749(43)sys(35)stat | …749(43)sys(35)stat | yes |
| Total fractional uncertainty | 4.6e-17 | 4.6e-17 | yes |
| Table 1 Yb single-clock total | 103.7 / 34.7 (x1e-18) | 103.7 / 34.7 | yes |
| Table 1 Sr single-clock total | 177.6 / 5.8 | 177.6 / 5.8 | yes |
| Table 1 Yb/Sr ratio rows | Yb 34.7, Sr 5.8, link 5.4, grav 0.2, stat 28.6, total 45.6 | identical | yes |
| Transition labels | 171Yb, 87Sr, 1S0-3P0 | identical | yes |

Every value-bearing and row-defining field matched exactly. The 2016-03-15
public Nature correction (a Table 2 column heading) does not touch the Yb/Sr
ratio value or Table 1 budget.

### Campaign-window lock

The Nature version-of-record **Figure 3** date axis shows the ten 2015
measurement dates spanning approximately **2015-02-26 to 2015-06-23**. The row
records this month-level (`2015-02` to `2015-06`) to avoid over-precise
figure-axis day reading; the exact days are noted as figure reads, not committed
values.

## Curated Row

`data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml`,
row `ACR-0002-ROW-001`:

| Field | Value |
| --- | --- |
| Observable | frequency ratio nu_Yb / nu_Sr (171Yb / 87Sr, 1S0-3P0) |
| Value | R = 1.207507039343337749(55) |
| Total uncertainty | 4.56e-17 (fractional) |
| Statistical | 2.86e-17 |
| Systematic | 3.56e-17 (Table 1: Yb 34.7, Sr 5.8, link 5.4, grav 0.2 x1e-18) |
| Epoch | 2015-02 to 2015-06 |
| Holdout split / role | `cross_source_target` / `cross_source_target` |
| Freeze manifest | `data/atomic_clocks/atomic_holdout_manifest.yaml` |

The row passes the `load_atomic_clock_direct_dataset` real-row loader
(`direct_measurement`, `frequency_ratio`, required uncertainty/source/holdout
fields present, role-split consistent). The holdout role matches the
manifest's pre-declared `nemitz_future_ratio_family` policy
(`expected_dataset_prefix: ACR-0002-NEMITZ-2016`, `Yb/Sr -> cross_source_target`).

## Covariance State

Nemitz 2016 (RIKEN) and Beloy 2021 (NIST + JILA, BACON 2018) are fully
independent: no shared clock, comb, network link, or geopotential systematic.
The cross-source pair is therefore `COV_DIAGONAL_ONLY_DECLARED` — the
off-diagonal versus `ACR-0001-ROW-003` is defensibly zero. **Consequence:** a
cross-source consistency *verdict* is not allowed; the first cross-source Yb/Sr
check (`TASK-0456`) must be an exploratory diagonal-only diagnostic carrying an
explicit independence banner.

## Limitations

- The Nature version-of-record PDF is **not committed** (copyright); the
  `NO_DRIFT` verdict rests on a local maintainer-supplied cross-check, recorded
  in `provenance.yaml` (`version_of_record_full_check_task_0704`).
- The campaign-window epoch is month-level, read from the version-of-record
  Figure 3 date axis; per-measurement calendar days are figure reads.
- This is a sandbox second-source seed. No benchmark, drift fit, constants
  constraint, Beloy comparison, or claim is produced.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `VALID` as a source/row-gate clearance and row commit;
  `not_applicable` as a scientific RESULT (no metric computed).
- **Canonical destination:** new dataset row
  `data/atomic_clocks/acr-0002-nemitz-2016-direct-ratio.yaml`, this review, plus
  source-manifest and provenance metadata updates. No `results/`,
  `prediction_registry/`, `claims/`, or `knowledge/` change.
- **Review tier:** `none` (no `RESULT-*` / `PRED-*` artifact).
- **Gate A status:** not applicable. **Gate B status:** not applicable.
- **Claim impact:** no claim change. **Knowledge impact:** campaign routing only
  — first admissible cross-source Yb/Sr target committed; `TASK-0456` unblocked
  for an exploratory diagonal-only diagnostic.
- **Limitations / blockers:** version of record verified locally but not
  committed (copyright); cross-source comparison remains diagonal-only and
  exploratory.
