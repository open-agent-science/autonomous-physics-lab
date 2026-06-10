# Exoplanet Second-Snapshot Acquisition Runbook

**Task:** `TASK-0554`
**Campaign:** Exoplanet Mass-Radius
**Status:** metadata-only acquisition package; no live fetch performed

## Purpose

This runbook prepares the maintainer-approved acquisition step for a future
second NASA Exoplanet Archive Planetary Systems (`ps`, `default_flag = 1`)
snapshot. It records the exact source surface, query contract, fields, row-class
rules, checksum policy, and no-peek attestation requirements before any new
catalog rows are fetched or inspected.

This runbook does not authorize an ordinary agent to fetch live archive data.
The future acquisition step must be explicitly approved under
`docs/source-acquisition-lane.md`.

## Source Surface

- Source family: `EXO-SRC-CLASS-001`
- Source: NASA Exoplanet Archive Planetary Systems (`ps`) table, default
  solution per planet (`default_flag = 1`). This is **not** the composite
  `PSCompPars` table; the `pscomppars_*` filenames are legacy labels for this
  `ps default_flag = 1` contract (see
  `docs/reviews/exoplanet-ps-pscomppars-query-boundary-review.md`).
- TAP endpoint: `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`
- Query contract: `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- Query SHA-256:
  `28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8`
- Response format for acquisition: CSV or VOTable, recorded before the run
- First snapshot reference:
  `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`

The query contract must remain byte-identical to the committed query file. Any
query change requires a pre-acquisition amendment PR before fetching.

## Exact Selected Fields

The acquisition must request exactly these fields from the committed query:

```text
pl_name, hostname, default_flag, soltype, disc_year, discoverymethod,
pl_orbper, pl_orbsmax, pl_orbeccen, pl_eqt, pl_insol,
pl_rade, pl_radeerr1, pl_radeerr2, pl_radj,
pl_bmasse, pl_bmasseerr1, pl_bmasseerr2, pl_bmassj, pl_bmassprov,
pl_dens, st_spectype, st_teff, st_tefferr1, st_tefferr2, st_rad,
st_mass, st_met, st_meterr1, st_meterr2, st_age, st_logg, sy_dist,
pl_refname, st_refname, disc_refname
```

No habitability, biosignature, target-prioritization, or composition-label
fields may be added in the acquisition run.

## Acquisition Command Shape

The future approved actor may run an equivalent TAP request after maintainer
approval. The run must record the final URL, timestamp, and response format in
`data/exoplanets/second_snapshot_manifest.yaml`.

```text
GET https://exoplanetarchive.ipac.caltech.edu/TAP/sync
  ?query=<url-encoded contents of data/exoplanets/snapshot_plans/pscomppars_query.adql>
  &format=csv
```

Do not paste API responses, row previews, or target values into chat, issue
comments, PR bodies, or logs before the manifest and no-peek attestation are
filled.

## Required Acquisition Manifest Fields

The acquisition manifest must record:

- source URL / TAP endpoint;
- exact query path and query SHA-256;
- selected fields;
- acquisition actor;
- approval reference;
- retrieval timestamp in UTC;
- raw artifact path;
- normalized artifact path, if committed;
- raw row count;
- included/excluded counts after deterministic normalization, if normalization
  is performed;
- raw SHA-256 checksum;
- normalized SHA-256 checksum, if normalized artifact is committed;
- redistribution decision;
- no-peek attestation.

If any checksum, timestamp, row count, or no-peek attestation is missing, the
future acquisition is incomplete and must not feed row curation or scoring.

## Checksum Portability Policy

Exoplanet source acquisition uses two checksum classes:

| Artifact class | Examples | Checksum rule |
| --- | --- | --- |
| Raw value-bearing source | TAP CSV snapshots under `data/exoplanets/raw/` | **Raw byte SHA-256** over the file as retrieved |
| Committed text artifacts | ADQL query contracts, normalized YAML snapshots, acquisition manifests | **LF-canonical SHA-256**: decode UTF-8, normalize `\r\n` to `\n`, hash the resulting bytes |

Implementation: `physics_lab/checksums.py` (`sha256_file`, `sha256_lf_canonical_file`).

Rules:

- Never compare raw-byte and LF-canonical digests against each other.
- Windows checkouts must not change LF-canonical digests for committed text
  artifacts when Git checks them out with normalized line endings.
- Recompute LF-canonical digests before acquisition if a text artifact's
  logical content changes; raw CSV digests always reflect the retrieved bytes.

Maintainer review helpers pass per-invocation `safe.directory` flags for
disposable PR review worktrees (`physics_lab/registry/review_git.py`) so Codex
and other container agents can run `git worktree` without mutating global git
config.

## Row-Class Rules

Normalization must preserve these row states separately:

- `direct_mass_radius_measurement` / true-mass transit-radius rows;
- `transit_radius_with_rv_minimum_mass` / `M sin i` minimum-mass rows;
- `model_inferred` rows;
- excluded rows with explicit `exclusion_reason`;
- radius-only or mass-only rows that do not satisfy a scored axis.

True-mass and minimum-mass axes must remain separate. No aggregate metric may
pool them.

## No-Peek Attestation

Before row inspection or scoring, the approved actor must attest that:

- the committed query contract was used unchanged, or a pre-acquisition
  amendment was merged before the run;
- no metric, residual hypothesis, target axis, slice definition, threshold, or
  exclusion rule was changed after seeing second-snapshot rows;
- raw and normalized artifacts were checksummed before any benchmark scoring;
- new rows are not copied into a benchmark result until a later row-curation or
  reveal task explicitly authorizes that step.

## Stop Conditions

Stop and record a blocker if:

- the endpoint, schema, or required fields changed;
- the query differs from the committed query contract;
- a checksum cannot be recorded;
- the response row count is missing or inconsistent;
- row-class mapping cannot distinguish true mass, minimum mass, model-derived,
  and excluded rows;
- any analysis tries to score target planets or inspect residuals during
  acquisition.

## Output Boundary

This runbook prepares an acquisition lane. It does not fetch rows, normalize a
new snapshot, run mass-radius residual metrics, create predictions, create
results, or promote claims.
