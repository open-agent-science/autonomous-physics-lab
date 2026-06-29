# Campaign Autonomy Profiles

Campaign profiles are machine-readable contracts for bounded autonomous
research lanes.

Each profile defines:

- campaign id and source documentation;
- autonomy status;
- portfolio metadata for curator sessions (`domain`, `surface_type`,
  `lifecycle_stage`, `activity_status`, and `curator.primary_pool`);
- allowed hypothesis and experiment families;
- required inputs and references;
- required quality gates;
- forbidden claims;
- optional Research Factory fields (`allowed_factory_families`,
  `required_factory_controls`, and `factory_stop_rules`) when a campaign has
  an adapter contract;
- validation commands;
- PR handoff requirements.

Profiles do not authorize claim promotion. They may authorize canonical
`RESULT-*` or `PRED-*` creation only when the selected task explicitly allows
that artifact class and the result-promotion gates in
`docs/result-promotion-protocol.md` pass. Otherwise, they authorize bounded
proposal, source-readiness, replay, audit, and sandbox work under the task
contract.

## Current Profiles

| Profile | Status | Summary |
| --- | --- | --- |
| `pendulum-formula-falsification.yaml` | `WHITELISTED_PILOT` | First pilot for range-aware candidate formula falsification |
| `dimensional-analysis-validator.yaml` | `WHITELISTED_LIMITED` | Limited classification and challenge-entry proposal work |
| `nuclear-mass-surface.yaml` | `WHITELISTED_LIMITED` | Bounded residual diagnostics, replay, and result-promotion preflights against frozen baselines and structured holdout/reveal protocols |
| `exoplanet-mass-radius.yaml` | `WHITELISTED_LIMITED` | Pinned-snapshot residual maps, matched controls, and source/baseline discipline for the active secondary campaign |
| `quantum-size-effects.yaml` | `SOURCE_READINESS` | Direct-row/source-artifact readiness before baseline or hypothesis batches |
| `atomic-clock-residuals.yaml` | `SOURCE_READINESS` | Pinned atomic-clock rows, covariance semantics, second-source ingestion, and holdout/no-peek readiness before benchmark metrics |
| `particle-mass-relations.yaml` | `GUARDRAIL_ONLY` | Falsification-first and provenance-focused proposal work |
| `textbook-formula-audit.yaml` | `SCAFFOLD` | Per-formula sandbox audits of textbook formulas against pinned public datasets; first slice queued is the Stellar Mass-Luminosity OOD audit |
| `thermophysical-property-residuals.yaml` | `WHITELISTED_LIMITED` | ThermoML Tb / Joback source-pinned benchmark lane with replay, source-readiness, and negative-memory gates |

Profiles may also include a `portfolio` block. That block is the editable
source for the generated `campaign_profiles/_catalog.yaml` portfolio index;
edit profiles, then run `python3 scripts/generate_campaign_catalog.py --write`.

The portfolio block separates physics domain from curator ownership:

- `domain` describes the science area;
- `surface_type` describes the type of research surface;
- `lifecycle_stage` describes maturity/readiness;
- `activity_status` describes whether the campaign is active, limited,
  support-only, planning, or watchlist;
- `curator.primary_pool` selects the focused Scientific Campaign Director
  session that owns the campaign;
- `curator.secondary_pools` lists adjacent pools for context only.

See [Campaign Curator Pools](../docs/campaign-curator-pools.md). Do not use
letter-coded groups as canonical metadata.

`_catalog.yaml` is a service-style generated aggregate, not an editable campaign
profile. Profile discovery ignores `_*.yaml` files so generated helpers can live
next to the source profiles without being mistaken for campaign contracts.

## Review Rule

If a profile is missing or says `EXCLUDED`, autonomous agents must stop and ask
for a canonical task or proposal path.
