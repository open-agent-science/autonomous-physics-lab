# Materials Pinned-Snapshot Acquisition (Materials Project)

**Task:** `TASK-0547`
**Campaign:** Materials Property Residuals
**Source:** Materials Project (CC BY 4.0)
**Lane:** `T4_snapshot_approval` (maintainer-run; API key required)
**Decision:** `RUNBOOK_READY_PENDING_MAINTAINER_FETCH`

## Scope

This task runs the source acquisition lane (`TASK-0545`) for the Materials
campaign scaffold (`TASK-0439`) to produce APL's first new reusable dataset from
an open-licensed source. It registers the source, defines the row schema, and
prepares a deterministic maintainer-run acquisition runbook plus the expected
snapshot manifest. It does **not** fetch data, commit secrets, run benchmarks,
or curate rows.

## Source Decision

- **Primary:** Materials Project (CC BY 4.0). Chosen because the license
  explicitly allows redistribution of curated rows **with attribution**, so the
  resulting dataset is fully committable and citable — the cleanest path to a
  reusable public dataset.
- **Fallback:** JARVIS-DFT (NIST). Held for a later task after a separate
  license/source note; not used here.

Materials Project requires a personal API key, so per the acquisition lane the
fetch is **maintainer-run**; the agent prepared the runbook and schema but did
not fetch.

## Artifacts Added

- `data/materials/schema.md` — row schema sketch (provenance classes, units,
  computed-vs-measured separation, required validation ideas).
- `data/materials/source_manifest.yaml` — Materials Project entry (CC BY 4.0,
  attribution text, version `PENDING` at fetch, `sha256_file` checksum policy,
  `access: api_key_required_maintainer_run`).
- `docs/runbooks/materials-snapshot-acquisition-runbook.md` — the exact
  maintainer-run fetch (mp-api query, fields, database-version pin, checksum,
  manifest fill, no-secret rules).
- `data/materials/materials_snapshot_manifest.yaml` — expected manifest shape,
  value-free, `PENDING` fields filled at fetch.

No measurement values, API keys, or copyrighted artifacts are committed.

## Frozen Acquisition Choices (no-peek)

- Property axes: `formation_energy_per_atom` (eV/atom) and `band_gap` (eV),
  scored on separate residual axes; never pooled.
- Scope filter for the first snapshot: `num_elements <= 3` AND `is_stable = true`
  (bounded, stable subset). Widen only via a pre-fetch amendment, never after
  seeing rows.
- Provenance: `computed_dft`; the DFT functional and the Materials Project
  `database_version` are recorded per snapshot.

## What The Maintainer Does Next

1. Set `MP_API_KEY` in the local environment (never commit it).
2. Run the runbook fetch script; record `database_version`,
   `retrieval_timestamp_utc`, `row_count`, `checksum_sha256`.
3. Normalize rows into `data/materials/md-0001-materials-project-<axis>.yaml`
   (one property axis per file) under the schema, keeping the CC BY attribution.
4. Fill `materials_snapshot_manifest.yaml` `PENDING` fields and commit the
   normalized snapshot + manifest (no key, no large raw dump).
5. Hand off to a separate row-curation / baseline task.

## Optionally Publishing The Dataset

Once committed, the snapshot is a candidate APL **reusable dataset** under the
publication standard. A Zenodo release (GitHub→Zenodo) can mint a citable DOI;
the dataset stays CC BY with Materials Project attribution. This is optional and
not part of this task.

## Output Routing Summary

- Task verdict: `RUNBOOK_READY_PENDING_MAINTAINER_FETCH` (no scientific claim).
- Canonical destination: this review, `data/materials/schema.md`,
  `data/materials/source_manifest.yaml`, `data/materials/materials_snapshot_manifest.yaml`,
  `docs/runbooks/materials-snapshot-acquisition-runbook.md`.
- Review tier: `none` (no RESULT/PRED artifact; no rows yet).
- Gate A/B: not attempted.
- Claim impact: no claim change. Knowledge impact: no knowledge change.
- Limitations / blockers: Materials Project needs a personal API key, so the
  actual snapshot is maintainer-run; until then no rows are committed. JARVIS-DFT
  fallback deferred. No live fetch performed; no secrets committed.

## Limitations

- This task produces a runbook and scaffolding, not the dataset itself; the
  pinned rows land after the maintainer-run fetch.
- The scope filter is a conservative first cut; the maintainer may amend it
  before fetch (pre-fetch only, to preserve no-peek).
- No baseline, residual metric, or claim is produced.
