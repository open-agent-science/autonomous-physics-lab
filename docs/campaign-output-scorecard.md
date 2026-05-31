# Campaign Output Scorecard

`scripts/apl_campaign_scorecard.py` reports **durable scientific-memory
throughput** per campaign so strategy agents and the Scientific Campaign
Director can steer by output, not by raw task or PR activity (see the
`docs/strategy.md` "Steering Metric").

It is **descriptive**: it counts committed canonical artifacts. It never
promotes claims, edits review tiers, or ranks scientific truth.

## What it reports

- **Repo-wide results** — every committed `results/**/result.yaml` grouped by
  `best_verdict` and `review_tier`.
- **Per-campaign durable output** — `RESULT` artifacts a campaign profile lists
  in `portfolio.current_results`, plus `PRED` artifacts under the campaign's
  `prediction_registry/<domain>/`, each broken down by verdict / registry
  status and review tier.
- **Sandbox separation** — `agent_runs/AGENT-RUN-*` counted per campaign via
  `campaign_profile_id`, kept distinct from durable canonical output.
- **Claims and knowledge** — repo-wide `CLAIM-*` counts by status and `KNOW-*`
  count.
- **Coverage** — committed results not referenced by any campaign profile are
  reported as a count and excluded from per-campaign attribution.

```bash
python3 scripts/apl_campaign_scorecard.py          # human-readable
python3 scripts/apl_campaign_scorecard.py --json    # machine-readable
```

## How artifact -> campaign mapping works (and its limits)

There is no single canonical artifact->campaign field in the repository, so the
scorecard reuses the signals that already exist:

- a `RESULT` belongs to a campaign when that campaign profile's
  `portfolio.current_results` references it;
- a `PRED` belongs to a campaign by its `prediction_registry/<domain>/`
  directory (`nuclear_masses` -> `nuclear-mass-surface`);
- a sandbox `AGENT-RUN-*` belongs to a campaign by its `campaign_profile_id`.

**Limitation:** profile `current_results` is a *curated* short list, not a full
census, so most results are reported only in repo-wide totals and counted under
**Coverage** rather than attributed to a campaign. `CLAIM-*` and `KNOW-*` are
reported repo-wide (their per-campaign attribution is not cleanly available).
Treat per-campaign result counts as "curated current evidence," and the
repo-wide totals as the full durable-output picture.

## How to use it

- The **Scientific Campaign Director** consumes the scorecard to see which lanes
  produce durable evidence (results, validated predictions, ratified claims)
  versus only sandbox activity, and to surface promotion or do-not-promote
  candidates.
- **Strategy agents** use repo-wide totals + claim-status counts to judge
  whether the project is converting bounded work into reviewable scientific
  memory (e.g. a backlog of `DRAFT` claims with passing evidence signals a
  claim-review cadence is due — see `docs/claim-review-cadence.md` when present).

The scorecard is a data layer for those roles; it does not replace the
`apl_campaign_curator.py` narrative brief or `campaigns/catalog.yaml`.

## Cross-references

- `docs/strategy.md` — the durable-output steering metric.
- `docs/scientific-memory-review-tiers.md` — the review-tier definitions.
- `docs/result-promotion-protocol.md` — how artifacts earn tiers.
- `campaigns/catalog.yaml` — campaign portfolio map.
- `docs/scientific-campaign-curator.md` — the Director role that consumes this.
