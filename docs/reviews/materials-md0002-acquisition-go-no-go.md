# Materials MD-0002 Acquisition Go/No-Go

**Task:** `TASK-0670`
**Campaign:** Materials Property Residuals
**Mode:** planning only (no live fetch, no rows, no metrics)
**Decision:** `GO_AUTHORIZE_MD0002_MAINTAINER_RUN_ACQUISITION`
**Task verdict:** `not_applicable` (planning gate)

## Scope

This review decides whether the MD-0002 planning wave is ready for a
maintainer-run Materials Project acquisition. It compares the three completed
preflight surfaces only. It does not fetch Materials Project rows, commit
value-bearing MD-0002 datasets, compute benchmarks, create `RESULT-*` /
`PRED-*` / `CLAIM-*` artifacts, recommend materials, or promote claims.

## Prerequisites Checked

| Task | Verdict | Status |
| --- | --- | --- |
| `TASK-0631` | `MD0002_ACQUISITION_CONTRACT_DEFINED_NO_FETCH` | `DONE` |
| `TASK-0644` | `SCAFFOLD_DEFINED_NO_ROWS_NO_METRICS` | `DONE` |
| `TASK-0645` | `schema_ready_for_later_acquisition_preflight` | `DONE` |

All three prerequisites are merged and mutually consistent on `main`.

## Consistency Review

The planning wave agrees on:

- **Slice scope:** Materials Project stable ternary oxides (exactly three distinct
  elements: two non-oxygen cations + O); computed DFT only; stable rows under
  the pinned Materials Project convention.
- **Property axes:** `formation_energy_per_atom` (`eV_per_atom`) and `band_gap`
  (`eV`) kept strictly separate; never pooled.
- **Source family:** existing `materials-project` registration in
  `data/materials/source_manifest.yaml` (CC BY 4.0); no new provider.
- **Acquisition posture:** maintainer-run with `MP_API_KEY` never committed;
  `live_external_fetch_allowed: false` in every committed MD-0002 artifact.
- **Row cap:** hard cap **1500 included rows per axis**; stop and report if the
  bounded query exceeds the cap (no silent sub-sampling or widening).
- **Version and checksum:** pin `database_version` at acquisition time (do not
  reuse MD-0001's `2025.09.25` pin implicitly); record `sha256_file` over the
  raw snapshot and each normalized dataset file.
- **Holdout/no-peek:** bind to `data/materials/md0002_holdout_manifest.yaml`;
  declare split rules and seeds before residuals or metrics are inspected; no
  post-score split tuning.
- **Loader shape:** `data/materials/fixtures/md0002_schema_fixture.yaml` and
  `tests/test_materials_md0002_schema_fixture.py` validate the planned row
  schema without real Materials Project locators.

No contract conflict requires a narrowed preflight revision.

## Route Options Considered

| Route | Assessment |
| --- | --- |
| **Authorize MD-0002 maintainer-run acquisition** | **Selected.** Planning wave is complete and aligned with `TASK-0614` `MD0002_WIDENING_FIRST`. |
| Request narrowed preflight revision | Not warranted. Query contract, holdout scaffold, and loader fixture agree. |
| Keep MD-0001 dataset-publication-first | Rejected as the primary next action. `TASK-0614` already chose widening before external dataset packaging; MD-0001 remains a reusable-dataset candidate, not the blocking next step. |
| Stop the widening lane | Rejected. MD-0001 formation energy is split-robust and null-control-surviving; a bounded ternary-oxide retest is the correct empirical next step. |

## Decision

`GO_AUTHORIZE_MD0002_MAINTAINER_RUN_ACQUISITION`

Materials should proceed to a **maintainer-run** MD-0002 acquisition task that
executes the frozen contract from `TASK-0631` and commits:

- `data/materials/snapshots/materials_project_stable_ternary_oxides_<database_version>.json`
- `data/materials/md-0002-materials-project-formation-energy.yaml`
- `data/materials/md-0002-materials-project-band-gap.yaml`
- populated `data/materials/md0002_holdout_manifest.yaml` (replace acquisition
  placeholders with pinned version, checksum, row counts, and frozen split
  assignments)

No agent-side live fetch. The maintainer assigns the canonical acquisition task
id when opening that work.

## Frozen Acquisition Parameters

| Parameter | Requirement |
| --- | --- |
| Primary retest axis | `formation_energy_per_atom` — test whether MD-0001's composition-aware formation-energy advantage generalizes beyond stable binary oxides. |
| Diagnostic-only axis | `band_gap` — remain visible and separate; treat as split-fragile per MD-0001 negative memory until a larger holdout changes the evidence. Do not use band-gap behavior to promote formation-energy conclusions or vice versa. |
| Row cap | **1500 included rows per axis**; stop and report raw count + predicate on exceedance; record actual count if below the ~600-row lower target. |
| Source / version | `materials-project`; pin `database_version` at acquisition; record retrieval date UTC and exact filter dictionary in the runbook output. |
| Checksum | `sha256_file` on raw snapshot and each normalized dataset file; record in dataset headers and holdout manifest. |
| Citation / reuse | Mandatory CC BY 4.0 attribution block per `TASK-0631` (Jain et al., APL Materials 1, 011002 (2013)). |
| Holdout / no-peek | Primary split: `material_id`-modulo **70/15/15**; carry forward seeded random, cation-pair-family, spacegroup/prototype, property-range, and source-version split candidates declared in the holdout scaffold; freeze all rules before scoring. |
| Promotion boundary | No benchmark promotion, claims, or `RESULT-*` artifacts from acquisition alone; acquisition supplies rows and manifest binding only. |

## Guardrails For The Acquisition Task

- Computed DFT only; no measured rows.
- No material-design, synthesis, device, biomedical, or discovery wording.
- No prediction, claim, or new-law statement.
- Formation energy and band gap stay separate axes across all splits and reports.
- Stop on unclear license/version, ambiguous units, mixed provenance, missing
  record locator, or cap exceedance.

## Limitations

- This decision authorizes acquisition planning execution only; it does not
  guarantee the bounded query returns the target row count.
- Band-gap split fragility may persist even after MD-0002; a larger holdout
  retests but does not pre-commit a promotable band-gap edge.
- MD-0002 rows remain computed DFT values and cannot support measured-property
  or material-design claims.
- External MD-0001 dataset publication packaging remains a separate maintainer
  decision (`TASK-0643` blockers still apply).

## Output Routing Summary

- **Task verdict:** `not_applicable` (planning gate); decision
  `GO_AUTHORIZE_MD0002_MAINTAINER_RUN_ACQUISITION`.
- **Canonical destination:** this review note,
  `docs/reviews/materials-md0002-acquisition-go-no-go.md`.
- **Review tier:** `none`; no `RESULT-*` / `PRED-*` artifact.
- **Gate A status:** not applicable (no rows ingested).
- **Gate B status:** not applicable (no metrics or replay).
- **Claim impact:** none.
- **Knowledge impact:** campaign routing only — MD-0002 acquisition authorized
  pending maintainer-run execution.
- **Publication blocker:** value-bearing MD-0002 publication and benchmark
  binding remain blocked until acquisition pins version, checksum, row counts,
  and holdout assignments.
