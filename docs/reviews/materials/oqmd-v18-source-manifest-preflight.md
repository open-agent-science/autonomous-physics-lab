# TASK-1026: OQMD v1.8 source-manifest preflight

## Scope and freeze

This preflight executes the `OPEN_SOURCE_TASK` decision from
[materials-second-dataset-stop-go-task0993.md](./materials-second-dataset-stop-go-task0993.md).
It pins the official OQMD v1.8 release identity, rights, field and unit
semantics, a reproducible retrieval-identity policy, a bounded row-cap
proposal, and a conservative MD-0002 overlap/no-peek contract — from official
OQMD metadata only.

Nothing was acquired: the 21.1 GB dump was not downloaded, no API data query
was run, no scientific row was extracted or selected, no overlap count was
computed from values, no dataset was constructed, no metric was run, and no
RESULT, CLAIM, or KNOW artifact was created or changed. MD-0002 remains
byte-stable and untouched.

## Pinned official source identity

All pages fetched directly from the official OQMD site on `2026-07-13`; raw
bytes are held in a temporary uncommitted cache and pinned by SHA-256.

| Artifact | Locator | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Download page (release list, license statement) | `https://www.oqmd.org/download/` | 7,819 | `1735b99ac2fed5cc18c9299574ad978a71b96043e77b89b35fcd00f521b47a07` |
| RESTful API documentation (field semantics) | `https://static.oqmd.org/static/docs/restful.html` | 27,263 | `17a15bd5ad21ecd590f8910757e2ce4386846373a4604d7f3bb60f012a9a839f` |
| DFT settings page (calculation provenance) | `https://www.oqmd.org/documentation/vasp` | 8,825 | `9329197d3dc888fc903d84eed7b01154929cd66272930cf845bb4a1640ad12bc` |
| Publications page (required citations) | `https://www.oqmd.org/documentation/publications` | 4,812 | `67c2ac99245c321da3ebddfa4b506354410ed763cb6363eab49c53ebe4521f5e` |

Release identity recorded from the download page:

| Property | Value |
| --- | --- |
| Release | OQMD v1.8 (incremental release; "no significant changes to the qmpy API") |
| Dump artifact | `qmdb__v1_8__022026.sql.gz` |
| Dump locator | `https://static.oqmd.org/static/downloads/qmdb__v1_8__022026.sql.gz` |
| Stated size | 21.1 GB (MySQL dump; ~100 GB imported) |
| Database updated | February 2026 |
| Compatible API | qmpy API v1.4 (per download page); RESTful `oqmdapi` responses self-report `api_version: 1.0` |
| Provider | OQMD development team (Wolverton group, Northwestern University) |
| Publisher checksum | none published on the download page (recorded honestly; see retrieval-identity policy) |

## Rights and attribution

- The download page states: "The data in OQMD is licensed under CC-BY 4.0",
  linking `https://creativecommons.org/licenses/by/4.0/`, and asks that
  results referencing the site cite the canonical papers.
- Required attribution (publications page): Saal, J. E., Kirklin, S., Aykol,
  M., Meredig, B., and Wolverton, C., JOM 65, 1501–1509 (2013),
  doi:`10.1007/s11837-013-0755-4`; and Kirklin, S., Saal, J. E., Meredig, B.,
  Thompson, A., Doak, J. W., Aykol, M., Rühl, S., and Wolverton, C., npj
  Computational Materials 1, 15010 (2015), doi:`10.1038/npjcompumats.2015.10`.
- Verdict component: rights are compatible with a future committed, attributed
  snapshot slice (same CC BY 4.0 posture as the MD-0002 Materials Project
  lane). No paywall, key, or registration is required for the API or dump.

## Field and unit semantics (official metadata only)

Candidate computed-property fields from the RESTful documentation:

| Field | Official description | Semantics notes for a future slice |
| --- | --- | --- |
| `delta_e` | "formation energy of that compound" | Computed DFT formation energy per compound; canonical definition and eV/atom convention are set by the Kirklin 2015 reference (fitted elemental chemical potentials / correction scheme). Per-field unit confirmation is a named acquisition-gate check. |
| `stability` | "hull distance of the compound" | Convex-hull distance; `stability = 0` identifies hull members (the source-side stability predicate analogous to MD-0002's `is_stable`). |
| `band_gap` | "band gap of the materials" | DFT-PBE band gap (systematic underestimate); a separate property axis, never merged with formation energy under one metric. |
| `icsd_id` | "ICSD ID of this structure, if it exists" | Provider-reference lineage field; useful for structure-source screening. |
| `duplicate_entry_id` | "OQMD ID of the preferred entry with this same crystal structure" | OQMD-internal duplicate semantics; with query flag `noduplicate`, defines the dedup contract inside the slice. |
| `spacegroup`, `prototype`, `ntypes`, `natoms`, `volume`, `composition`, `name`, `entry_id` | structure/identity fields | Identifier-level fields available for predicates, dedup, and overlap screening without touching target values. |

Calculation provenance (DFT settings page): VASP 5.3.2, GGA-PBE with PAW
potentials; four-step relaxation ending in a static calculation at 520 eV
cutoff and KPPRA = 8000 ("all the energies calculated in OQMD are
comparable"); 3d (Sc–Cu) and actinide calculations are spin-polarized with
ferromagnetic initialization (complex antiferromagnetic order is not
captured; the page itself notes 10–20 meV/atom formation-energy errors from
this); GGA+U in the Dudarev form is applied to several transition metals in
compounds with oxygen, with published U−J values (V 3.1, Cr 3.5, Mn 3.8,
Fe 4.0, Co 3.3, Ni 6.4, Cu 4.0 eV).

**Non-comparability with MD-0002 fields, recorded explicitly:** MD-0002's
`formation_energy_per_atom` comes from the Materials Project pipeline (its own
GGA/GGA+U conventions and correction scheme, recorded per record in MD-0002),
while OQMD `delta_e` comes from the OQMD pipeline above (different U−J
values, potentials policy, and fitted-reference corrections). Similarly named
fields are therefore **not** directly comparable across sources. Any future
benchmark must analyze each source internally (within-source residuals);
cross-source value mixing under one metric is forbidden, and cross-source
agreement must not be framed as a materials-design result.

Missingness semantics: the RESTful page does not document per-field
nullability. The acquisition task must probe and record missingness (nullable
`band_gap`, `delta_e`, `stability`, `icsd_id`) on its bounded slice before the
split design; missing target values route rows to exclusion with recorded
reasons, not silent drops.

## Retrieval-identity policy (proposed, not executed)

The 21.1 GB dump is the only version-stamped artifact, and it is not an
admissible first acquisition step. The bounded route is a RESTful `oqmdapi`
snapshot, which self-reports `api_version` and a response `time_stamp` but no
database-version field. The reproducible identity policy for the future
acquisition task is therefore snapshot-pinning, mirroring MD-0002:

1. record every full query URL, the UTC fetch window, and the raw paginated
   responses byte-for-byte;
2. compute SHA-256 of the concatenated raw snapshot and of the normalized
   slice at commit time;
3. capture the response `meta` fields (`api_version`, `time_stamp`,
   `data_returned`, `data_available`) into the snapshot manifest;
4. label the slice "OQMD live-API snapshot of <date>, post-v1.8 (February
   2026) release", not "exactly v1.8" — API-vs-dump equality is not provable
   without the dump and is not claimed;
5. never re-fetch silently: any repeat fetch is a new dated snapshot with its
   own hashes.

Residual risk recorded: unlike the Materials Project API (which reports
`database_version`, as used by MD-0002), OQMD's API offers no version stamp,
so version identity rests on the release calendar plus the dated, hash-pinned
snapshot. This is a documented limitation, not an absence of policy.

## Bounded row-cap and source-side predicate proposal (not executed)

- Scope mirror: ternary oxides in the MD-0002 chemistry family — element set
  {one alkali or alkaline-earth} + {one first-row transition metal} + O,
  `ntypes = 3`, hull members via `stability = 0` (source-side predicate, the
  analogue of MD-0002's `is_stable`), `noduplicate = True`.
- Fields: `name, entry_id, icsd_id, duplicate_entry_id, prototype,
  spacegroup, ntypes, natoms, volume, composition, delta_e, band_gap,
  stability`.
- Hard row cap: **2,000 rows** for the committed normalized slice. If the
  predicate matches more, narrow it by identifier-level scope only (e.g.,
  restrict the alkali/alkaline-earth subset) before reading any target
  values; never narrow by property values.
- Provenance class: `computed_dft` for every row; measured rows may never
  enter this slice or its metrics.

## MD-0002 overlap and no-peek contract (proposed, not executed)

Identity surfaces available value-blind: MD-0002 commits `material_id`,
`formula_pretty`, `composition`, `nsites`, `symmetry` (spacegroup), and
`elements` for 362 included materials; OQMD exposes `composition`/`name`,
`spacegroup`, `prototype`, and `icsd_id`.

1. **Composition-family exclusion (primary, conservative):** exclude from the
   entire OQMD benchmark slice (train and holdout) every entry whose reduced
   composition matches any MD-0002 included material's reduced composition.
   This guarantees material-level disjointness with MD-0002 regardless of
   polymorphism, using identifiers only.
2. **Structure check (secondary):** where spacegroup exists on both sides,
   log composition+spacegroup coincidences discovered during screening as an
   audit trail; they are excluded already by rule 1.
3. **OQMD-internal dedup:** `noduplicate=True` at query time plus a
   `duplicate_entry_id` null-check on the slice; duplicates route to
   exclusion with reasons.
4. **Provider-reference lineage:** MD-0002's committed fields carry no ICSD
   references, so cross-database calculation-lineage screening via `icsd_id`
   is not fully resolvable; rule 1 is the conservative cover, and this
   residual risk is recorded for the benchmark-design task.
5. **No-peek rules:** target-axis values (`delta_e`, `band_gap`) must not be
   used for row selection, predicate narrowing, dedup, overlap screening,
   split assignment, or any exploratory statistics before the split freeze;
   overlap screening runs on identifiers only; the split must be frozen and
   hash-pinned before any residual or metric is computed; any leakage found
   after the freeze fails closed (re-freeze, never patch in place).
6. **Disjoint holdout:** no reduced composition may appear in more than one
   split partition of the OQMD slice.

## Verdict

**`READY_FOR_BOUNDED_ACQUISITION_TASK`.** Rights (CC BY 4.0 with required
citations), release identity (v1.8, February 2026, exact dump locator),
field/provenance semantics (including the explicit OQMD-vs-MP
non-comparability record), a reproducible snapshot-pinning retrieval-identity
policy, a bounded predicate with a 2,000-row cap, and a conservative
MD-0002 overlap/no-peek contract are all specified from official metadata.
The acquisition itself, missingness probing, unit confirmation, snapshot
manifest, and any benchmark split remain separate future tasks; this verdict
authorizes none of them to skip their own gates.

## Limitations

- No publisher checksum exists for the v1.8 dump; dump identity is
  filename + stated size + release date until a future task hashes fetched
  bytes.
- The API lacks a database-version stamp; version identity for an API
  snapshot is calendar-anchored and hash-pinned, weaker than MD-0002's
  `database_version` record (explicitly documented above).
- Unit and missingness semantics are anchored to the canonical OQMD papers
  and must be confirmed per-field on the bounded slice at acquisition time.
- The qmpy data-model documentation index was fetched, but deep model pages
  were not crawled; the RESTful field list above is the authoritative surface
  used here.
- MD-0002 carries no ICSD lineage fields, so provider-reference overlap
  screening is composition-anchored (rule 1) rather than lineage-exact.

## Output routing

- Task verdict: `not_applicable` (source preflight; packet-level outcome is
  `READY_FOR_BOUNDED_ACQUISITION_TASK`).
- Canonical destination: this review packet plus one metadata-only source
  registry entry in `data/materials/source_manifest.yaml`; no `agent_runs/`,
  `results/`, `prediction_registry/`, `claims/`, or `knowledge/` artifact.
- Review tier: none (source readiness only).
- Gate A: not attempted (no publishable RESULT/PRED exists).
- Gate B: not attempted (nothing replayable exists at this stage).
- Claim impact: none.
- Knowledge impact: none; opening the bounded acquisition task is a
  maintainer decision.
- Publication blockers: none for this packet itself; acquisition, snapshot
  manifest, DATA_LICENSES entry, and split design remain gated future tasks.
