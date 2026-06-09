# Materials MD-0002 Acquisition Preflight Package

**Task:** `TASK-0631`
**Campaign:** `materials-property-residuals`
**Mode:** planning only (no-live-fetch acquisition preflight)
**Verdict:** `MD0002_ACQUISITION_CONTRACT_DEFINED_NO_FETCH`

## Scope

`TASK-0614` selected `MD0002_WIDENING_FIRST`, authorizing an MD-0002 acquisition
preflight. This package turns the `TASK-0602` MD-0002 wider-replication slice plan
into a concrete, frozen acquisition **contract** that a maintainer-run acquisition
task can execute deterministically: bounded query contract, row cap and
cap-exceeded stop behavior, version pin, checksum plan, citation/reuse metadata,
and the holdout/no-peek manifest plan.

It fetches no live Materials Project data, commits no MD-0002 rows or snapshot, and
makes no materials-design, synthesis, device, biomedical, prediction, claim, or
discovery statement. Formation energy and band gap stay separate axes, with band
gap treated as split-fragile until a larger slice shows otherwise.

## Inputs Reviewed

- `docs/reviews/materials-md0002-wider-replication-slice-plan.md` (`TASK-0602` scope)
- `docs/reviews/materials-md0001-result-or-dataset-publication-decision.md` (`TASK-0614`, `MD0002_WIDENING_FIRST`)
- `docs/reviews/materials-md0001-split-sensitivity-audit.md` (band-gap split fragility)
- `docs/reviews/materials-bandgap-split-fragility-negative-memory.md` (band-gap negative memory)
- `data/materials/source_manifest.yaml` (Materials Project registered, CC BY 4.0)
- `data/materials/schema.md`, `data/materials/holdout_manifest.yaml` (row + holdout shape)

## Source Pin

| Field | Value |
| --- | --- |
| `source_id` | `materials-project` (already registered, `inclusion_decision: accepted`) |
| Provider | Materials Project (LBNL) |
| Access | `api_key_required_maintainer_run` — `MP_API_KEY` never committed; no live fetch in agent tasks |
| Provenance | `computed_dft` only (GGA / GGA+U per Materials Project convention, recorded per row) |
| License | CC BY 4.0 — redistribution of curated rows allowed **with** mandatory attribution + citation |
| `database_version` | **pinned at acquisition time** and recorded in the dataset header, snapshot, and MD-0002 holdout manifest (do not reuse the MD-0001 `2025.09.25` pin implicitly — re-pin and record the actual version used) |
| `checksum_policy` | `sha256_file` over the raw snapshot and over each normalized dataset file |

## Bounded Query Contract

A single bounded mp-api summary query, executed once by the maintainer, frozen and
recorded verbatim in the acquisition runbook output.

Filter predicates (all required):

- `elements` contains `O`;
- `nelements == 3` (exactly three distinct elements → two distinct cations + O);
- `is_stable == true` (equivalently `energy_above_hull == 0.0` under the pinned
  Materials Project convention);
- both `formation_energy_per_atom` and `band_gap` requested per record.

Requested fields per record (mp-api summary):

- `material_id` (stable record locator);
- `formula_pretty` and normalized `composition`;
- `nelements`, `elements`;
- `energy_above_hull`, `is_stable`;
- `formation_energy_per_atom` (eV/atom);
- `band_gap` (eV);
- `symmetry.symbol` (spacegroup / structure prototype, for a split axis);
- the DFT functional indicator and `database_version`.

Determinism: record the exact filter dictionary, the requested field list, the
`database_version`, and the retrieval date UTC in the runbook output so the query
is reproducible against the pinned version.

## Row Cap And Stop Behavior

- Predeclared cap: **~600–1500 included rows per axis** (target band from the slice
  plan). Set the hard cap to **1500 rows per axis**.
- If the bounded query returns more than the cap, the acquisition task must **stop
  and report** the raw count and the predicate, not silently widen, sub-sample, or
  truncate. Narrowing (e.g. a tighter stability or element predicate) is a
  reviewed follow-up decision, never an in-line silent filter.
- If the query returns fewer than ~600 included rows per axis after exclusions,
  record the actual count and flag that the larger-holdout goal (resolving MD-0001
  band-gap fragility) may be only partially met; do not pad with metastable or
  binary rows.

## Inclusion / Exclusion (frozen before fetch)

Included rows satisfy all of: exactly three distinct elements incl. oxygen
(two cations + O); `is_stable`/`energy_above_hull == 0.0`; `provenance_class ==
computed_dft` with functional + `database_version` recorded; both axes present
(a row missing one axis is excluded from that axis only, with `exclusion_reason`);
`material_id` and normalized `composition` present.

Excluded, kept visible with `exclusion_reason`: binary oxides (already in MD-0001),
quaternary+ oxides, non-oxides / non-O anions, metastable (`energy_above_hull > 0`),
`material_id` duplicates, and rows missing functional, version, units, or value.

## Checksum And Snapshot Plan

- Store the raw query response under `data/materials/snapshots/<md-0002-ternary-oxide-snapshot>.json`.
- Record `sha256_file` over the raw snapshot in the dataset header and the MD-0002
  holdout manifest.
- Record `sha256_file` over each normalized dataset file
  (`data/materials/md-0002-*-formation-energy.yaml`, `md-0002-*-band-gap.yaml`).
- `live_external_fetch_allowed: false` in every committed MD-0002 artifact.

## Citation / Reuse Metadata Block

Every committed MD-0002 dataset file must carry, verbatim:

```text
attribution_text: "Data from The Materials Project (materialsproject.org),
  licensed CC BY 4.0; cite Jain et al., APL Materials 1, 011002 (2013)."
license: "CC BY 4.0"
citation: "A. Jain et al., 'Commentary: The Materials Project: A materials genome
  approach to accelerating materials innovation', APL Materials 1, 011002 (2013),
  doi:10.1063/1.4812323."
provenance_class: computed_dft
database_version: "<pinned at acquisition>"
```

## Holdout / No-Peek Manifest Plan

Create a new MD-0002 holdout/no-peek manifest mirroring
`data/materials/holdout_manifest.yaml`, frozen **before** any scoring, choosing
splits only from pre-score axes:

- primary: `material_id`-modulo interpolation split **70/15/15** (holdout ~100–220
  rows — the row count MD-0001's 33-row holdout lacked);
- `seeded_random_70_30` robustness family with fixed seeds (carry forward the
  MD-0001 split-sensitivity discipline so MD-0002 reports split stability from the
  start);
- cation-pair-family split incl. a leave-one-cation-group-out extrapolation
  diagnostic;
- structure-prototype / `spacegroup_symbol` split;
- property-range bins defined before residual inspection;
- source-version / retrieval-date split when a second snapshot exists.

The manifest must record the raw-snapshot checksum, the frozen split assignment,
and a no-peek attestation. Computed-vs-measured provenance and the two property
kinds stay separate across all splits. No threshold, exclusion rule, or split may
be tuned after holdout residuals are seen.

## Guardrails Carried Into Acquisition

- Computed DFT only; no measured rows, no material-design / synthesis / device /
  biomedical / discovery wording, no prediction or claim.
- Formation energy and band gap are separate axes, never pooled.
- Band gap is treated as **split-fragile** (see
  `materials-bandgap-split-fragility-negative-memory.md`); MD-0002 supplies the
  statistical power to retest it, but a band-gap edge is not promotable here.
- Stop conditions (from `schema.md`): unclear license/version, ambiguous units,
  mixed provenance, missing record locator, or bounded query exceeding the cap.

## Recommended Follow-up

A maintainer-run MD-0002 acquisition task (to be assigned a canonical id by the
maintainer, not here) that executes this frozen contract and commits:
`data/materials/md-0002-*-formation-energy.yaml`,
`data/materials/md-0002-*-band-gap.yaml`,
`data/materials/snapshots/<pinned ternary-oxide snapshot>.json`, and the MD-0002
holdout/no-peek manifest. No agent-side live fetch.

## Limitations

- Planning only: no data fetched, no rows added, no metrics computed, no claim.
- Row-count and split sizes are predeclared estimates; the runbook must report
  actual bounded-query counts and stop on cap exceedance.
- MD-0002 remains computed DFT only and cannot support measured-property,
  material-design, or discovery claims.
- Does not modify `data/materials/source_manifest.yaml` (the Materials Project
  source is already registered); the acquisition plan lives in this review.

## Output-Routing Summary

- **Task verdict:** `not_applicable` (planning task);
  contract state `MD0002_ACQUISITION_CONTRACT_DEFINED_NO_FETCH`.
- **Canonical destination:** this review note,
  `docs/reviews/materials-md0002-acquisition-preflight-package.md`.
- **Review tier:** `none`; no `RESULT-*`/`PRED-*` artifact.
- **Gate A status:** not applicable (no rows/metrics). **Gate B:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** task-proposal recommendation only (maintainer-run
  acquisition task described, not assigned a canonical id).
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** MD-0002 rows remain unfetched and uncommitted; value-
  bearing publication is blocked until the maintainer-run acquisition executes this
  contract with a pinned version, checksum, and frozen holdout manifest.
