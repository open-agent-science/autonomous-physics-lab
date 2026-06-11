# Curator Review Cadence Semantics

**Task:** TASK-0462
**Status:** portfolio metadata contract (no campaign verdict changes)

Each campaign profile's `portfolio.curator_review` block now carries structured
cadence fields alongside `last_reviewed`, `status`, `source`, and `notes`:

| Field | Purpose |
| --- | --- |
| `review_interval` | How often maintainers should revisit the lane |
| `next_review_due` | ISO date when the next scheduled review is due |
| `review_reason` | Why that cadence applies (stable label for capacity boards) |

## Allowed values

**`review_interval`**

| Value | Typical use |
| --- | --- |
| `quarterly_active` | Flagship or active benchmark lanes with moving evidence |
| `quarterly_blocked` | Lanes blocked on source/readiness that need periodic unblock checks |
| `quarterly_planning` | Scaffold or planning-only lanes before first pinned snapshot |
| `semiannual_quality_floor` | Guardrail, quality-floor, or hygiene tracks with slower drift |

**`review_reason`**

| Value | Typical use |
| --- | --- |
| `flagship_validation` | Primary validation lane (e.g. nuclear mass surface) |
| `benchmark_monitoring` | Active secondary benchmark with published metrics |
| `source_readiness` | Source pinning, licence, or row-class gates dominate |
| `planning_scaffold` | Campaign scaffold without pinned dataset yet |
| `quality_floor_hygiene` | Reproducibility, falsification, or guardrail tracks |

## Choosing cadence for a campaign

Match cadence to **portfolio `status`**, not to aspirational science claims:

1. **`flagship_validation` or `active_secondary`** → `quarterly_active` with
   `flagship_validation` or `benchmark_monitoring`.
2. **`source_readiness` or blocked source tracks** → `quarterly_blocked` with
   `source_readiness`.
3. **`scaffold` or early planning** → `quarterly_planning` with
   `planning_scaffold`.
4. **`quality_floor` or `guardrail`** → `semiannual_quality_floor` with
   `quality_floor_hygiene`.
5. **`pinned_dataset` with benchmark gates still open** → `quarterly_active` with
   `source_readiness` until the first benchmark slice lands.

Set `next_review_due` to the next calendar boundary after `last_reviewed`
(quarterly → ~90 days; semiannual → ~180 days). Use concrete ISO dates; do not
use relative phrases like "next quarter".

When a Director or Curator cycle completes, update `last_reviewed`, roll
`next_review_due` forward, and adjust `review_interval` / `review_reason` only
if the lane's operational class changed (for example scaffold → active
secondary).

## Validation

`scripts/generate_campaign_catalog.py --check` validates cadence fields when
building `campaign_profiles/_catalog.yaml`. The JSON schema at
`physics_lab/schemas/campaign_catalog.schema.json` enforces the same enums on
load.
