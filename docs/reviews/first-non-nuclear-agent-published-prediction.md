# First Non-Nuclear AGENT_PUBLISHED Prediction

**Task:** `TASK-0417`
**Prediction:** `prediction_registry/exoplanet_mass_radius/PRED-0001.yaml`
**Campaign:** `exoplanet-mass-radius`
**Review tier:** `AGENT_PUBLISHED`
**Status:** no live fetch, no future rows inspected, no scoring

## Scope

This task registers the first non-nuclear prediction entry under the generic
prediction schema. The selected domain is `exoplanet_mass_radius` because the
repository already has a pre-reveal source protocol and target-freeze artifact:

- `docs/exoplanet-second-snapshot-no-live-fetch-protocol.md`;
- `data/exoplanets/second_snapshot_target_freeze.yaml`;
- `docs/reviews/exoplanet-second-snapshot-target-freeze.md`;
- `data/exoplanets/snapshot_plans/pscomppars_query.adql`;
- `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`.

The registry entry does not fetch, browse, ingest, summarize, or score a newer
NASA Exoplanet Archive PSCompPars snapshot. It does not change nuclear
prediction entries.

## Pre-Claim Search

Before implementation, GitHub PR search found no open implementation PR for:

- `TASK-0417`;
- `first-non-nuclear-agent-published-prediction`;
- `prediction_registry exoplanet_mass_radius PRED`.

Claim surface for this PR:

- `tasks/TASK-0417-register-first-non-nuclear-agent-published-prediction.yaml`;
- `prediction_registry/exoplanet_mass_radius/README.md`;
- `prediction_registry/exoplanet_mass_radius/PRED-0001.yaml`;
- `docs/reviews/first-non-nuclear-agent-published-prediction.md`.

Artifact tier: `AGENT_PUBLISHED`.

## Prediction Shape

The registered forecast is a categorical protocol-outcome forecast, not a
planet-level measurement. It names exactly two future reveal axes:

| target_id | predicted_value |
| --- | --- |
| `true_mass_transit_radius_axis` | `NULL_OR_BLOCKER` |
| `minimum_mass_transit_radius_axis` | `NULL_OR_BLOCKER` |

This keeps the prediction aligned with the existing campaign memory: true-mass
and minimum-mass rows must stay separate, null-baseline controls remain
mandatory, and any future positive route requires a separate
maintainer-reviewed reveal task that clears source, checksum, row-count,
sample-size, and no-peek requirements.

## Gate A Summary

Gate A fields populated in `PRED-0001.yaml`:

- no-peek state: committed-only source state and `live_external_fetch_allowed: false`;
- frozen model/reference: `data/exoplanets/second_snapshot_target_freeze.yaml`;
- named target set: the two frozen reveal axes;
- reveal conditions: future maintainer-approved PSCompPars second snapshot;
- non-claim ceiling: explicit no-claim boundary;
- overclaim wording: no discovery, confirmation, broader physical, habitability,
  biosignature, or target-priority wording.

## Limitations

- This is an agent-published registry entry, not independently validated or
  maintainer-reviewed.
- The forecast is categorical and protocol-facing; it does not register new
  measured planet values.
- Later comparison must leave the registry entry unchanged and write a separate
  reviewed reveal artifact.
- The normalized EXO-0001 checksum gap remains outside this task and may block
  future reveal scoring.

## Output Routing Summary

- Task verdict: `not_applicable` - pre-registration only.
- Canonical destination:
  `prediction_registry/exoplanet_mass_radius/PRED-0001.yaml`.
- Review tier: `AGENT_PUBLISHED`.
- Gate A status: pass, pending command validation in this PR.
- Gate B status: not applicable.
- Claim impact: no claim status transition.
- Knowledge impact: no knowledge promotion.
- Result artifact impact: no `results/` artifact modified.
