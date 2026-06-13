# Exoplanet PSCompPars Snapshot De-duplication Plan

**Task:** `TASK-0735`
**Type:** repository hardening / size-and-reproducibility hygiene (P2)
**Mode:** analysis + recommendation only — no payload deleted, no path-list change
**Verdict:** `KEEP_BOTH_RAW_CSV_AND_NORMALIZED_YAML` — the two artifacts serve
different roles and neither is safely removable now.

## Scope

The NASA Exoplanet Archive PSCompPars snapshots are committed as both raw CSV and
normalized YAML. They are redistributable with acknowledgement and per-row
citations (`data/DATA_LICENSES.yaml`, `nasa-exoplanet-archive-pscomppars`), so
this is **not** a licence question — it is repository size/reproducibility
hygiene. This note compares field coverage and recommends a canonical storage
policy. It deletes nothing and changes no canonical path list.

## Field-coverage analysis (snapshot exo-0001)

| Representation | Shape | Size |
| --- | --- | --- |
| Raw CSV (`exo-pscomppars-20260523T171549Z.csv`) | 36 columns, 6291 rows | ~4.0 MB |
| Normalized YAML (`exo-0001-pscomppars-snapshot.yaml`) | 18 structured per-row fields, 6291 entries | ~11.5 MB |

- The YAML is **derived from the raw CSV** by the committed deterministic ingest
  script `scripts/ingest_exoplanet_pscomppars_snapshot.py` (raw → YAML, not the
  reverse).
- The YAML **renames and structures** the raw columns rather than dropping their
  information: e.g. `pl_bmasse`/`pl_bmasseerr1/2` → `mass` object with
  `value`/`uncertainty_upper`/`uncertainty_lower`/`uncertainty_semantics`/`mass_class`;
  `pl_rade`/errors → `radius` object; `st_*` → `host_star` object
  (Teff, mass, radius, metallicity, age, logg-in-notes); `pl_refname`/`disc_refname`/`st_refname`
  → `source_table_ref` / `host_star.notes`.
- **The YAML preserves all scientifically load-bearing fields** for the
  mass-radius campaign: mass + asymmetric uncertainties, radius + uncertainties,
  stellar parameters, detection method, period, semi-major axis, equilibrium
  temperature, insolation, discovery year, and per-row literature references.
- **Raw columns the YAML does not carry:** `pl_orbeccen` (eccentricity),
  `pl_dens` (density; derivable from mass+radius), and the Jupiter-unit duplicates
  `pl_bmassj`/`pl_radj` (derivable from Earth units). Of these, only eccentricity
  is genuinely unique and non-derivable; it is not a mass-radius variable but is
  preserved **only** in the raw CSV.

## Downstream references (cost of removing each)

- **Normalized YAML — heavily referenced (campaign-facing surface):**
  `campaign_profiles/exoplanet-mass-radius.yaml`, `campaign_profiles/_catalog.yaml`,
  several active tasks (`TASK-0580`, `TASK-0581`, `TASK-0582`, `TASK-0598`), and
  `tests/test_exoplanet_mass_radius_dataset_schema.py`. Dropping it would break the
  campaign profile and multiple consumers.
- **Raw CSV — source-of-truth and reproducibility anchor:** `TASK-0353`
  (ingestion), `tests/test_exoplanet_mass_radius_dataset_schema.py`,
  `data/exoplanets/source_manifest.yaml`, the ingestion review note, and the
  external-reviewer replication capsule. Dropping it removes the pinned source
  artifact and weakens the external-replication path.

## Why neither is safely removable now

- **Cannot drop the YAML:** it is the heavily-referenced, uncertainty-rich
  campaign surface; removing it requires migrating every consumer to read raw or
  rebuild on demand — a substantial change beyond this P2 plan.
- **Cannot drop the raw CSV:** it is the pinned source of truth and the only
  committed record of `pl_orbeccen`/`pl_dens`; it backs the external-replication
  capsule; and it is **not identically re-fetchable** from the live NASA archive
  (the composite table drifts over time, so a re-query would not reproduce the
  pinned checksum).

The two files are therefore **complementary** (source-of-truth vs curated
derived surface), not a wasteful duplicate. The ~31 MB across both snapshots is
justified by their distinct roles and reference bases.

## Recommendation

1. **Canonical policy: keep both** the raw CSV and the normalized YAML, with the
   raw CSV documented as the pinned source of truth and the YAML as its
   deterministic, campaign-facing derived view (rebuildable via the ingest
   script). No payload is deleted; no `data/DATA_LICENSES.yaml` or
   `data/exoplanets/source_manifest.yaml` path-list change is needed (this note
   documents the decision only).
2. **Deferred forward option (only if repo-size pressure later justifies it):**
   the sole information-safe de-duplication direction is to keep the raw CSV +
   ingest script and **rebuild the YAML on demand**, dropping the committed YAML.
   That requires (a) migrating the ~6 YAML consumers above to a rebuild-or-read
   path, (b) confirming no consumer needs the dropped raw fields beyond what the
   ingest produces, and (c) routing any history-blob removal through the
   maintainer-approved Phase B rewrite (`TASK-0732`) rather than a separate
   force-push. This is a separate consumer-migration task, not part of this plan.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` (planning/hygiene analysis); decision
  `KEEP_BOTH_RAW_CSV_AND_NORMALIZED_YAML`.
- **Canonical destination:** this review note only. No data payload deleted, no
  registry/manifest path-list change, no `results/`/`claims/`/`knowledge/` change.
- **Review tier:** `none`. **Gate A / Gate B:** not applicable.
- **Claim impact:** none. **Knowledge impact:** none.
- **Limitations / blockers:** field-coverage compared on snapshot exo-0001;
  exo-0002 has the same schema (second retrieval used for delta/drift audits). No
  de-duplication is executed; the deferred forward option is documented for a
  future maintainer-approved consumer-migration task.
