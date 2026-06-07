# Exoplanet PS vs PSCompPars Query Boundary Review

- Task: `TASK-0647`
- Campaign: Exoplanet Mass-Radius
- Verdict: `PRESERVE_CURRENT_PS_DEFAULT_ROW_CONTRACT`
- Decision: keep the committed `ps` + `default_flag = 1` query contract as the
  active source boundary. Treat `PSCompPars` in artifact names and campaign
  shorthand as a legacy/composite-source-family label, not as permission to
  silently switch the TAP table to literal `pscomppars`.

## Scope

This review resolves the query-family ambiguity surfaced by
`docs/reviews/exoplanet-exo0003-metadata-trigger-scout.md`. It compares the
committed query, acquisition runbook, source manifests, normalized snapshot
metadata, and campaign wording. It does not fetch NASA Exoplanet Archive rows,
preview value-bearing data, run residual metrics, alter the query text, create
predictions, publish results, or promote claims.

Reviewed inputs:

- `data/exoplanets/snapshot_plans/pscomppars_query.adql`
- `docs/runbooks/exoplanet-second-snapshot-acquisition-runbook.md`
- `docs/reviews/exoplanet-exo0003-metadata-trigger-scout.md`
- `docs/reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md`
- `data/exoplanets/source_manifest.yaml`
- `data/exoplanets/second_snapshot_manifest.yaml`
- `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- `data/exoplanets/exo-0002-pscomppars-snapshot.yaml`
- `docs/campaigns/exoplanet-mass-radius.md`

## Query Contract Found

The committed query file is named:

```text
data/exoplanets/snapshot_plans/pscomppars_query.adql
```

Its executable ADQL source surface is unambiguous:

```sql
FROM ps
WHERE default_flag = 1
```

The query comments also state that it selects the canonical default solution per
planet from the NASA Exoplanet Archive Planetary Systems (`ps`) table and omits
habitability, biosignature, target-prioritization, composition-label, and
similar out-of-scope fields.

The ingestion plan already documents the original boundary: `default_flag = 1`
selects the single canonical row per planet from `ps`, while `pscomppars` is a
related composite flat view; a snapshot must choose one route and must not mix
both in the same acquisition.

## Metadata And Wording Check

The normalized snapshots are internally consistent with the executable query:

- `exo-0001-pscomppars-snapshot.yaml` describes the artifact as a Planetary
  Systems default-row snapshot and records per-row provenance notes such as
  `Normalized from NASA Exoplanet Archive ps table with default_flag=1`.
- `exo-0002-pscomppars-snapshot.yaml` uses the same `ps` provenance wording.
- `data/exoplanets/source_manifest.yaml` names the source family as the NASA
  Exoplanet Archive Planetary Systems table while retaining a PSCompPars-style
  artifact title.
- `data/exoplanets/second_snapshot_manifest.yaml` records the committed query
  path and checksum, which bind the acquisition to the existing `ps`
  default-row query text.

The remaining ambiguity is wording-level, not data-level: many documents and
artifact names use `PSCompPars` as campaign shorthand for the composite
mass-radius source family even though the committed query table is `ps`.

## Decision

Preserve the current query family.

The active contract for future Exoplanet acquisition remains:

1. use `data/exoplanets/snapshot_plans/pscomppars_query.adql` byte-for-byte;
2. query the NASA Exoplanet Archive TAP service;
3. select from `ps`;
4. require `default_flag = 1`;
5. preserve true-mass, minimum-mass, model-derived, excluded, and
   radius-only/mass-only row classes separately;
6. do not add habitability, biosignature, target-prioritization, composition,
   or atmosphere fields.

Do not switch a future acquisition to literal `pscomppars` under the existing
runbook. A table-family switch would be a query-amendment task because it could
change row semantics, row counts, field availability, and comparison with the
two pinned snapshots.

## Documentation Update

This PR clarifies the second-snapshot runbook source-surface section so future
agents read `PSCompPars` as the legacy artifact/source-family label and `ps`
as the executable table contract. No query text, manifest checksum, source
data, normalized row, metric, result, prediction, claim, or knowledge file is
changed.

No broader rewrite of historical artifact names is recommended. Renaming the
existing `exo-0001-pscomppars-*`, `exo-0002-pscomppars-*`, and
`pscomppars_query.adql` paths would create more churn than clarity. The stable
boundary should instead be documented as:

```text
PSCompPars-named artifact family, implemented by the committed ps/default_flag=1 query.
```

## Allowed Future Routes

- Continue using the committed `ps` default-row query for metadata checks and
  any maintainer-approved future acquisition.
- Create a later query-amendment task only if a future source trigger or
  maintainer decision explicitly requires comparing or switching to literal
  `pscomppars`.
- Keep EXO-0003 closed until the existing coverage gate or a reviewed
  materially changed snapshot condition is met.

## Output Routing

- Task verdict: `PRESERVE_CURRENT_PS_DEFAULT_ROW_CONTRACT`.
- Canonical destination:
  `docs/reviews/exoplanet-ps-pscomppars-query-boundary-review.md`.
- Review tier: `none`; this is source-protocol planning, not a result artifact.
- Gate A status: not attempted; no dataset, residual metric, prediction, or
  result was produced.
- Gate B status: not applicable.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no `results/` artifact created or modified.
- Limitations: no live archive fetch, no external source-row comparison, and no
  decision about whether literal `pscomppars` would be scientifically better in
  a future amended acquisition.
