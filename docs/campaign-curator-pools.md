# Campaign Curator Pools

Campaign curator pools are operational ownership shards for focused Scientific
Campaign Director sessions. They are not physics domains and they are not
letter-coded groups.

Use them when the maintainer wants several curator sessions to work in
parallel without changing the role prompt. A session can say, for example,
"work as Scientific Campaign Director for `source_data_benchmark` campaigns"
and use the generated campaign catalog to find the matching campaigns.

## Metadata Model

Campaign profiles keep separate dimensions:

- `domain` — physics or science domain, such as `astrophysics` or
  `precision_metrology`;
- `surface_type` — the scientific work surface, such as
  `source_pinned_benchmark` or `prediction_reveal`;
- `lifecycle_stage` — current maturity, such as `source_readiness`,
  `reveal_blocked`, or `mature`;
- `activity_status` — whether the campaign is active, limited, support-only,
  planning, or watchlist;
- `curator.primary_pool` — the current ownership pool for focused curator
  sessions;
- `curator.secondary_pools` — relevant adjacent pools for handoff context, not
  automatic ownership.
- `next_validity_gate` — the next higher-validity route after the current
  result or blocker: `transfer`, `ratification`, `external_reveal`, or
  `source_readiness`.

The primary pool answers: which curator session owns this campaign right now?

## Pools

| Pool | Use For |
| --- | --- |
| `prediction_reveal` | Frozen predictions, no-peek/reveal gates, reopen decisions, controls-first negative memory. |
| `source_data_benchmark` | Source artifacts, checksums, row datasets, loaders, holdout manifests, first benchmark readiness. |
| `verifier_quality_floor` | Exact references, textbook audits, falsification tracks, range limits, and benchmark diagnostics. |
| `result_promotion` | Gate A/B routing, replay candidates, negative-result packaging, claim/result/knowledge backlog. |
| `frontier_planning` | Watchlist directions, new campaign scouting, source policy, and overclaim-risk planning. |

## Focused Sessions

Use the curator helper to inspect a focused scope:

```bash
python3 scripts/apl_campaign_curator.py --pool source_data_benchmark
python3 scripts/apl_campaign_curator.py --domain astrophysics
python3 scripts/apl_campaign_curator.py --stage source_readiness --active-only
python3 scripts/apl_campaign_curator.py --pool verifier_quality_floor --output agent
```

`--pool` matches `curator.primary_pool`. Secondary pools are shown as context,
but they do not pull a campaign into multiple owner sessions automatically.

## Transfer Policy

Campaigns may move between pools as their maturity changes. For example,
Quantum Size Effects may eventually move from `source_data_benchmark` to
`verifier_quality_floor` after direct rows and a baseline result exist.

Transfers are never automatic. A transfer requires a maintainer or Scientific
Campaign Director-approved PR that updates:

- the campaign profile metadata;
- the generated campaign catalog;
- any campaign page or mission wording that would otherwise become stale.

Scripts may warn or help inspect, but they must not mutate curator pool
assignment automatically.

## What Not To Do

- Do not encode Group A/B/C as canonical metadata.
- Do not use `domain` to mean curator ownership.
- Do not create manual group pages that duplicate the generated catalog.
- Do not move a campaign between pools just because one task in that campaign
  touched another pool's workflow.
- Do not widen a curator session beyond its pool/domain/stage without an
  explicit maintainer decision.
