# Materials Independent Transfer-Route Scout (TASK-0817)

**Task:** `TASK-0817`
**Campaign:** Materials Property Residuals
**Mode:** planning-only source/transfer scout; no fetch, no row edit, no metric run,
no claim/result change
**Verdict:** `TRANSFER_ROUTE_READY_FOR_TASK`

## Why this scout exists

`RESULT-0021` (the MD-0002 cation-pair formation-energy baseline) is
`AGENT_VALIDATED` but localized. It wins on the frozen split by memorizing the
train-mean of each exact unordered non-oxygen cation pair, and two prior
controls show the win does not generalize:

- the family-holdout stress preflight (`TASK-0789`) held out *entire* cation
  pairs under a **random** `random.Random(0)` 30%-of-pairs draw; the cation-pair
  baseline collapsed to the global-mean fallback (0.637 vs 0.654 null);
- the descriptor-ablation control audit (`TASK-0790`) showed that coarsening the
  grouping descriptor from the exact pair to the cation group removes essentially
  all lift (0.526, identical to the global mean).

The next useful scientific question is whether an **independent transfer route**
exists that changes the chemistry seen at train vs holdout time, so a future
authorized task could test transfer rather than memorization. This note scouts
exactly one such route and runs no metrics.

## Selected route (exactly one)

**Disjoint A-site cation-family holdout within the committed MD-0002
formation-energy slice.** Hold out one complete cation-family class
(alkaline-earth + first-row-transition oxides) as the transfer lane and train on
the disjoint class (alkali + first-row-transition oxides), or the reverse.

This is the **disjoint chemistry family within the committed Materials source
posture** option from the task contract. It is preferred over a new
source-snapshot class or a new computed-DFT database route because it can be
described and bounded *entirely from committed rows*, needs no live fetch, and
introduces no new provenance to verify.

### Route is distinct from prior work

`TASK-0789` used a *random* pair holdout (any cation pair can land in holdout
regardless of chemistry). The route here is a *chemically-disjoint A-site family*
holdout: the alkali (Li/Na/K/Rb/Cs) and alkaline-earth (Be/Mg/Ca/Sr/Ba)
A-site families are mutually exclusive across the slice, so train and holdout
share no A-site family. That is a stronger, chemistry-defined transfer surface
than a random pair draw and has not been scouted as a route.

### Feasibility evidence (committed rows only; deterministic, no metric run)

Grouping the 362 included formation-energy rows by the chemistry family of each
non-oxygen cation (alkali / alkaline-earth / first-row 3d transition) partitions
the slice cleanly into exactly two A-site-family classes with **zero**
unclassified rows:

| A-site family class | Rows | Example compositions |
| --- | --- | --- |
| `{alkali, transition_3d}` | 225 | Li-Ti, Na-Mn, K-V oxides |
| `{alkaline_earth, transition_3d}` | 137 | Ba-Ti, Sr-V, Mg-Cr oxides |
| total | 362 | (225 + 137, exhaustive) |

Either holdout direction clears a sensible floor (holdout >= ~40 rows): holding
out alkaline-earth-transition gives **train 225 / holdout 137**; holding out
alkali-transition gives **train 137 / holdout 225**. Leakage is **none by
construction** — the two A-site families are disjoint, so no cation-family is
shared between lanes. (Counts are read directly from the committed dataset; no
split rule was tuned and no residual or MAE was inspected for this scout.)

The frozen MD-0002 holdout manifest already pre-authorizes exactly this split
vocabulary: `pre_score_split_axes.cation_pair_family` lists
`alkali_transition_pair` and `alkaline_earth_transition_pair` as
allowed groupings, and `holdout_schema.allowed_split_values` includes `stress`.
A future task can bind a disjoint-family `stress` split without inventing new
split semantics, provided the family definitions are frozen before any scoring
(no-peek rule already stated in that manifest).

## Admissibility table

| Dimension | Assessment for the selected route |
| --- | --- |
| Source accessibility | **Ready.** Uses only the committed, content-pinned MD-0002 snapshot (`data/materials/md-0002-materials-project-stable-ternary-oxides.yaml`, snapshot checksum `5bfb3e7f...49567`). No live external fetch; `live_external_fetch_allowed: false`. |
| License / reuse posture | **Ready.** Materials Project data, CC BY 4.0, attribution to Materials Project and Jain et al. 2013 (`doi:10.1063/1.4812323`), declared in `data/DATA_LICENSES.yaml` (`materials-project-ternary-oxides-md0002`) and the dataset header. Reusing a subset of already-committed rows adds no new redistribution obligation. |
| Property-kind semantics | **Ready, single axis.** Route stays on `formation_energy_per_atom` (`eV_per_atom`) only. It does not pool with `band_gap`, which the holdout manifest and snapshot manifest mark diagnostic-only and forbid pooling. |
| Computed-vs-measured provenance | **Ready, computed-DFT only.** Every row is `provenance_class: computed_dft` (GGA / GGA+U, Materials Project convention). No measured or model-only rows enter the route; the computed-DFT vs measured boundary is preserved. Residuals would be computed-DFT benchmark diagnostics, not experimental errors. |
| Row identity | **Ready.** Each row carries `material_id` (e.g. `mp-aaaaaeit`), `formula_pretty`, `composition`, `cations`, and `record_locator`. The family bucket is derived deterministically from the existing `cations` field; no new identity is minted. |
| Uncertainty semantics | **Carried, absent-by-design.** MD-0002 snapshot manifest records `uncertainty_semantics.policy: absent_in_source_snapshot` (no per-row uncertainty). The route inherits that policy; a future task must report residuals as computed-DFT diagnostics and must not assert measurement uncertainty. |
| Holdout feasibility | **Ready.** Clean two-class partition (225 / 137, exhaustive, zero leakage); both directions clear a >=40-row holdout floor; split vocabulary pre-authorized as a `stress` family split with a no-peek freeze rule already in the manifest. |

## Compatibility with TASK-0809 metadata / release boundaries

`TASK-0809` is **`DONE`**. It closed the MD-0002 dataset-publication metadata
blockers: it added `data/materials/materials_md0002_snapshot_manifest.yaml`
(source/release manifest, raw + normalized checksums, citation/reuse metadata,
`absent_in_source_snapshot` uncertainty policy, changelog, explicit
`external_publication_status`), and extended `data/materials/README.md` and
`data/DATA_LICENSES.yaml` — all **without** changing rows, holdout membership,
or `RESULT-0021` metrics.

The selected route is **compatible** with those boundaries and is **not blocked
by TASK-0809**, because:

- it reuses the same committed snapshot and the metadata TASK-0809 finalized
  (checksum, license, uncertainty policy), changing none of it;
- it stays inside the no-claim boundary TASK-0809 reaffirmed
  (`external_publication_status: Metadata closeout only`; computed-DFT, no
  material-design / synthesis / device / biomedical / universal-law claim);
- it requires no new dataset rows and no external-release/DOI action, so it does
  not touch the parts TASK-0809 explicitly left to a separate
  maintainer-approved release task.

One boundary to respect downstream: TASK-0809 confirmed MD-0002 is **internally
reusable but not externally published** (no DOI, no release tag). A future
metric task on this route therefore stays an internal, scoped benchmark; it must
not be framed as an external dataset-release result.

## Recommended future task (no metric run here)

A future, separately authorized metric task could bind a **frozen disjoint
A-site-family `stress` split** (alkali-transition vs alkaline-earth-transition)
to the MD-0002 formation-energy axis and evaluate whether any *transfer-capable*
descriptor (for example element-property features) generalizes across the held-
out A-site family — in contrast to the cation-pair lookup baseline, which the
`TASK-0789` random-pair preflight already showed cannot transfer. That task
must: declare the family definitions and seed before inspecting residuals;
report results as computed-DFT diagnostics; keep formation energy and band gap
unpooled; and make no material-design claim. This scout opens no such metric,
descriptor search, RESULT, PRED, CLAIM, or KNOW artifact.

## Alternatives considered (and why not selected)

- **Band-gap axis of the same snapshot.** Available and committed, but it is the
  same materials under a different property, not an independent transfer surface
  for the formation-energy cation effect; it is also diagnostic-only and
  unpromoted. Not an independent *transfer* route.
- **A second Materials Project snapshot class** (e.g. a wider or different
  composition family). The holdout manifest requires "a separate manifest
  revision" and the fetch is maintainer-run and API-key-gated; describing rows
  would require live fetch or provenance speculation. Deferred to a future
  acquisition task, not scouted as ready here.
- **A new computed-DFT database route (OQMD or JARVIS-DFT).** License posture is
  favorable — OQMD publishes its data under CC BY 4.0 and offers full database
  dumps; JARVIS-DFT is a NIST product in the public domain — so either could
  found a future cross-database transfer lane. But both would need a new
  maintainer-run acquisition, a new pinned snapshot, checksum, and source-manifest
  entry, plus careful handling of cross-database DFT-functional and
  formation-energy-reference offsets. That is out of scope for a no-fetch scout
  and is recorded below as a future option, not as a ready route.

## Limitations / no-claim

Computed-DFT MD-0002 stable ternary-oxide slice only. This is a transfer-route
and source-readiness scout, not a benchmark, residual map, prediction, material
recommendation, synthesis guidance, device statement, biomedical statement,
experimental validation, materials-discovery, or universal-law statement.
`RESULT-0021` metrics and `review_tier` are unchanged; no MD-0002 row, holdout
membership, claim, or knowledge artifact is edited. All counts in this note are
read deterministically from committed rows; no MAE, residual, or model error was
inspected, so the route's transfer outcome is intentionally **not** predicted.

## Output-routing summary

- **Task verdict:** `not_applicable` (planning-only transfer/source scout; no
  benchmark verdict produced).
- **Route verdict:** `TRANSFER_ROUTE_READY_FOR_TASK`.
- **Canonical destination:** transfer/source readiness — this scout review note.
- **Review tier:** `none`; no canonical scientific artifact was created or
  re-tiered.
- **Gate A:** not attempted. **Gate B:** not attempted; existing `RESULT-0021`
  replay status is unchanged.
- **Claim impact:** no `CLAIM-*` change.
- **Knowledge impact:** no `KNOW-*` change; a future metric task is recommended
  but not opened.
- **Result / prediction impact:** no `RESULT-*` or `PRED-*` change; no
  `agent_runs/AGENT-RUN-*` and no `results/.../RUN-*` artifact created.
- **Dependency on TASK-0809:** TASK-0809 is `DONE`; the route is compatible with
  its finalized MD-0002 metadata/release boundaries and is **not** blocked by it.
- **Limitations / blockers:** no live external fetch performed; the in-snapshot
  route needs none. New-database routes (OQMD / JARVIS-DFT) remain future
  maintainer-run acquisition options, not ready routes.

## Sources

External source-posture checks consulted for the alternatives-considered
section (the selected route uses only committed rows and needs no external
fetch):

- The Open Quantum Materials Database (OQMD) — data licensed CC BY 4.0; full
  database dumps offered for download: <https://oqmd.org/download/> and the OQMD
  one-million-compounds reflection,
  <https://iopscience.iop.org/article/10.1088/2515-7639/ac7ba9>. Verified
  2026-06-25.
- JARVIS-DFT (NIST) — NIST data product, public domain under NIST terms:
  <https://www.nist.gov/programs-projects/jarvis-dft> and database index
  <https://pages.nist.gov/jarvis/databases/>. Verified 2026-06-25.
- Materials Project license/citation (already committed for MD-0002) — CC BY 4.0;
  cite Jain et al., APL Materials 1, 011002 (2013), `doi:10.1063/1.4812323`:
  <https://materialsproject.org>. License recorded in `data/DATA_LICENSES.yaml`.
