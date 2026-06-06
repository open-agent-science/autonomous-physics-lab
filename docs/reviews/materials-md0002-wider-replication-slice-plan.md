# Materials MD-0002 Wider Replication Slice Plan

**Task:** `TASK-0601`-adjacent planning under `TASK-0602`
**Campaign:** Materials Property Residuals
**Status:** planning-only (no data fetched, no rows added, no metrics computed)
**Verdict:** `not_applicable` (planning task)

## Scope

This plan selects the next wider Materials slice (`MD-0002`) after the committed
`MD-0001` stable-binary-oxides pilot produced a weak-but-real benchmark signal. It
defines candidate scope, property axes, inclusion/exclusion rules, provenance,
units, and holdout/no-peek split candidates strong enough that a later acquisition
task can pin version, license, schema, and holdout rules. It does **not** fetch
source data, add rows, compute metrics, promote claims, or move datasets to a
separate repository.

It builds on the committed
[MD-0001 baseline benchmark](materials-md0001-baseline-residual-benchmark.md), the
[MD-0001 band-gap null-control audit](materials-md0001-band-gap-null-control-audit.md),
the [benchmark promotion preflight](materials-md0001-benchmark-promotion-preflight.md),
the [campaign page](../campaigns/materials-property-residuals.md), the
[materials schema](../../data/materials/schema.md), and the committed
[source manifest](../../data/materials/source_manifest.yaml) and
[holdout manifest](../../data/materials/holdout_manifest.yaml).

## Selected Candidate Scope: Materials Project Stable Ternary Oxides

`MD-0002` is selected as **stable ternary oxides from the Materials Project**, the
same provider and license family as `MD-0001`, keeping the same two property axes.

### Justification

- **Scientific value.** `MD-0001` showed a clear composition-aware formation-energy
  advantage (`cation_group_mean` holdout MAE `0.646` eV/atom versus global-median
  `0.967` eV/atom) and a weak, borderline band-gap signal. A split-sensitivity audit
  on `MD-0001` (TASK-0601, under review) found the formation-energy conclusion
  split-robust but the band-gap ordering split-fragile on the 33-row holdout. Ternary
  oxides add a second cation per formula, so they directly test whether the
  composition-aware formation-energy advantage generalizes beyond single-cation
  oxides, and they provide the row count needed to resolve the band-gap fragility
  that `MD-0001` could not settle.
- **Row count.** Stable ternary oxides are far more numerous than stable binary
  oxides in the Materials Project. The plan targets a **bounded** slice of roughly
  `600`-`1500` included rows per axis (predeclared cap; the acquisition runbook
  query must stop and report if the bounded query exceeds the cap rather than
  silently widening). This is large enough for a 70/15/15 split with a holdout of
  ~`100`-`220` rows, removing the small-holdout fragility of `MD-0001`.
- **Source availability.** Same Materials Project API as `MD-0001`; the fetch stays
  maintainer-run with a personal `MP_API_KEY` that is never committed, with the
  database version pinned and an `sha256_file` checksum recorded at commit time.
- **License.** Materials Project data are CC BY 4.0; redistribution of curated rows
  is allowed with mandatory attribution and citation, identical to `MD-0001`.
- **Overclaim risk.** Rows remain computed DFT only (GGA/GGA+U per Materials Project
  convention). No measured rows, no material-design, synthesis, device, or
  discovery wording. The slice is a benchmark surface, not a recommendation set.

### Alternatives Considered (and deferred)

- **Larger binary+ternary mixed slice.** Rejected for `MD-0002`: mixing binary and
  ternary in one slice would confound the "does the binary-oxide finding generalize"
  retest. Keep `MD-0001` (binary) and `MD-0002` (ternary) as comparable, separable
  slices.
- **Adding an elastic-moduli axis.** Deferred to a later `MD-0003`: a third property
  axis would broaden scope and complicate the direct retest of the existing two
  axes. `MD-0002` keeps formation energy and band gap only.
- **A different provider (JARVIS-DFT / OQMD).** Deferred: changing provider changes
  the DFT functional convention and license terms, which would confound the retest.
  Keep Materials Project for a clean comparison; cross-provider replication is a
  separate later task.

## Property Axes

Two axes, kept strictly separate (never pooled), matching `MD-0001` for a direct
retest:

| Axis | Property kind | Units | Provenance |
| --- | --- | --- | --- |
| Formation energy | `formation_energy_per_atom` | `eV_per_atom` | `computed_dft` |
| Band gap | `band_gap` | `eV` | `computed_dft` |

## Inclusion / Exclusion Rules

Included rows must satisfy all of:

- composition has exactly three distinct elements, one of which is oxygen
  (two distinct cations plus O);
- `is_stable` is true (`energy_above_hull == 0.0` under the pinned Materials Project
  convention);
- `provenance_class == computed_dft` with the DFT functional and database version
  recorded;
- both `formation_energy_per_atom` and `band_gap` are present for the material
  (a row missing one axis is excluded from that axis only, with an explicit
  `exclusion_reason`);
- a stable record locator (`material_id`) and a normalized `composition` are present.

Excluded (kept visible with `exclusion_reason`):

- binary oxides (already in `MD-0001`) and quaternary-or-higher oxides;
- non-oxides and oxide rows with non-O anions;
- metastable rows (`energy_above_hull > 0`);
- duplicates by `material_id`;
- rows missing functional, database version, units, or value.

## Provenance, Units, Snapshot Policy

- Provenance: `computed_dft` only; GGA/GGA+U per Materials Project convention,
  recorded per row; `measured` and `model_only` rows are never folded into the
  computed axes.
- Units: `eV_per_atom` (formation energy), `eV` (band gap).
- Snapshot: pinned Materials Project `database_version`, raw snapshot file stored
  under `data/materials/snapshots/`, `sha256_file` checksum recorded in the dataset
  header and a new `MD-0002` holdout manifest, `live_external_fetch_allowed: false`.
- The normalized row shape follows the committed
  [materials schema](../../data/materials/schema.md) "Minimal Future Row Fields".

## Holdout / No-Peek Split Candidates

Predeclared before any scoring and bound to a new `MD-0002` holdout/no-peek manifest
(mirroring `holdout_manifest.yaml`), choosing splits only from pre-score axes:

- `material_id`-modulo interpolation split (e.g. 70/15/15), the `MD-0001`-style
  primary split, now with a holdout large enough (~`100`-`220` rows) to be stable.
- `seeded_random_70_30` robustness family with fixed seeds, carried forward from the
  `MD-0001` split-sensitivity discipline (TASK-0601) so `MD-0002` reports split
  stability from the start rather than discovering fragility afterward.
- `cation_group` / cation-pair-family split, including a leave-one-cation-group-out
  extrapolation diagnostic.
- structure-prototype / `spacegroup_symbol` split.
- property-range bins defined before residual inspection.
- source version / retrieval-date split when a second snapshot exists.

Computed-vs-measured provenance and the two property kinds stay separate across all
splits.

## How MD-0002 Retests the MD-0001 Findings

- **Formation energy.** Refit `global_mean`, `global_median`, and a composition-aware
  baseline (generalized to a cation-pair grouping) on ternary oxides. Retest whether
  the composition-aware baseline still beats the null baselines and whether the
  advantage is split-robust at the larger row count. A persistent advantage would
  show the `MD-0001` formation-energy finding generalizes beyond single-cation
  oxides; a collapse would bound it to binary oxides.
- **Band gap.** With a holdout an order of magnitude larger than `MD-0001`'s 33 rows,
  retest whether the weak, split-fragile cation-group band-gap edge firms up,
  stays borderline, or collapses under the same null-control and seeded-random
  robustness discipline. `MD-0002` supplies the statistical power `MD-0001` lacked.

Both retests stay benchmark-only: no claim, prediction, material recommendation, or
discovery wording.

## Recommended Follow-up Acquisition Task

The source, version, license, and citation plan is clear, so a concrete acquisition
task is well-defined (to be formalized by the maintainer or `TASK-0614`, not assigned
a canonical id here):

```text
Scope: Materials Project stable ternary oxides (two cations + O), bounded query,
       row cap ~600-1500 per axis.
Source: materials-project (already registered, CC BY 4.0, sha256_file).
Version: pin Materials Project database_version at acquisition; record checksum.
Fetch: maintainer-run with MP_API_KEY (never committed); no live fetch in agent tasks.
Outputs: data/materials/md-0002-*-formation-energy.yaml,
         data/materials/md-0002-*-band-gap.yaml,
         data/materials/snapshots/<pinned ternary-oxide snapshot>.json,
         a new MD-0002 holdout/no-peek manifest,
         MD-0002 citation/reuse metadata.
Stop conditions (from schema.md): unclear license/version, ambiguous units,
         mixed provenance, missing record locator, or bounded query exceeding the
         row cap.
```

## Limitations

- Planning only: no data fetched, no rows added, no metrics computed, no claim made.
- Row-count and split targets are predeclared estimates; the acquisition runbook must
  report the actual bounded-query counts and stop if the cap is exceeded.
- `MD-0002` remains computed DFT only; it cannot support measured-property,
  material-design, or discovery claims.
- The split-sensitivity input from `TASK-0601` is referenced as in-review context;
  this plan does not depend on it being merged.

## Output Routing Summary

- Task verdict: `not_applicable` (planning task).
- Canonical destination: this review;
  optional minimal `docs/campaigns/materials-property-residuals.md` pointer.
- Review tier: `none`.
- Gate A status: `not_applicable`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: task-proposal recommendation only (acquisition task described,
  not assigned a canonical id).
- Result impact: `no RESULT artifact created`.
