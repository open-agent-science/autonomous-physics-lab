# Exoplanet Snapshot Plans

This directory holds **value-free** query contracts, mapping tables, and
retrieval recipes for future Exoplanet Mass-Radius ingestion tasks. It
does not contain any catalog row values.

The first source family covered is
[`EXO-SRC-CLASS-001`](../source_manifest_template.yaml) — NASA Exoplanet
Archive `PSCompPars`. The plan that produced these files is
[`docs/reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md`](../../../docs/reviews/exoplanet-pscomppars-snapshot-ingestion-plan.md)
(TASK-0345).

## Files

- [`pscomppars_query.adql`](./pscomppars_query.adql) — the exact ADQL
  query a future ingestion task must run against the NASA Exoplanet
  Archive TAP service. The query is locked at plan time; running a
  modified query produces a different snapshot and requires a new plan
  amendment.
- [`pscomppars_method_map.yaml`](./pscomppars_method_map.yaml) — the
  mapping from NASA Exoplanet Archive `discoverymethod` values to the
  schema's `detection_method` enum.
- [`pscomppars_mass_provenance_map.yaml`](./pscomppars_mass_provenance_map.yaml)
  — the mapping from `pl_bmassprov` values to the schema's `mass_class`
  enum and the per-class default `inclusion_status`. This is the single
  source of truth for whether a row contributes to the true-mass
  residual axis.

## What Belongs Here

- query contracts in a query-language file (`.adql`, `.sql`);
- mapping tables in YAML when needed for parser determinism;
- short README notes describing query intent without leaking row
  values.

## What Does Not Belong Here

- catalog rows or per-planet values (those live in
  `data/exoplanets/exo-NNNN-*.yaml` under the schema);
- raw CSV downloads from NASA Exoplanet Archive (those live under
  `data/exoplanets/raw/`);
- model outputs, baseline predictions, or residual maps;
- habitability scores, biosignature flags, or prioritization output.

## Coordination

Future ingestion tasks must keep these plan files byte-identical to the
plan version they cite. A change to the query, the method map, or the
mass-provenance map requires a separate amendment PR to TASK-0345's
plan document before the change is committed here.
