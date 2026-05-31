# Agent Capacity Board

A lightweight planning surface showing how many agents can safely work in
parallel across campaign, review, and support lanes. It answers "how many agents
fit here right now, and which lanes are saturated or blocked?" before heavier
claiming infrastructure is needed.

This is a **planning snapshot**, not a live dashboard or database. The
authoritative per-campaign source is the generated
[`campaigns/catalog.yaml`](../campaigns/catalog.yaml) (each campaign's
`agent_capacity.recommended_parallel_agents`, `status`, `coordination_notes`,
and `curator_review`). Refresh this board from the catalog after a campaign
profile changes; do not hand-edit campaign numbers here.

## Campaign lanes (snapshot from `campaigns/catalog.yaml`, updated 2026-05-29)

| Lane (campaign) | Portfolio status | Recommended parallel agents | Curator review | Coordination note |
| --- | --- | --- | --- | --- |
| nuclear-mass-surface | flagship_validation | 3 | current | Disjoint lanes only: negative/preflight packaging, reveal-readiness, future maintainer tasks. |
| atomic-clock-residuals | pinned_dataset | 2 | current | Second-source ingestion, loader work, and holdout/no-peek manifest in separate branches. |
| exoplanet-mass-radius | active_secondary | 2 | current | Parallel-safe for replay, checksum cleanup, evidence-card packaging, second-snapshot protocol on separate files. |
| anharmonic-oscillator | quality_floor | 1 | current | Bounded replay/follow-up benchmark; avoid broad candidate expansion without a task. |
| dimensional-analysis-validator | quality_floor | 1 | current | Small challenge-entry or limitation-probe work; avoid concurrent edits to one challenge set. |
| particle-mass-relations | guardrail | 1 | current | Provenance, uncertainty, or negative-result memory only unless a maintainer opens a narrow task. |
| pendulum-formula-falsification | quality_floor | 1 | current | Replay, validation hardening, examples; not the default expansion lane. |
| quantum-size-effects | source_readiness | 1 | current | Sequential until a direct table or digitization source unblocks row curation. |
| textbook-formula-audit | scaffold | 1 | current | One formula slice at a time until source, schema, baseline, and holdout conventions are proven. |

**Total recommended campaign agents: ~13** (within the 10–15 planning target).

### Reading the campaign capacity

- A lane's recommended agent count is a **safe parallelism ceiling**, not a
  quota to fill. Prefer fewer agents on disjoint write surfaces over more agents
  contending for the same files.
- `source_readiness` and `scaffold` lanes are deliberately capped at 1 until
  their data/source conventions are proven; adding agents there creates rework,
  not throughput.
- A lane is **blocked** when its READY tasks are exhausted or its work depends on
  an unresolved source/decision; route spare agents to another lane rather than
  forcing parallel work.

## Review and support lanes

These are cross-campaign lanes (query the on-demand task-to-campaign index with
`python3 scripts/apl_task_campaign_index.py --format markdown` when you need
the current `support` task list):

| Lane | Recommended parallel agents | Notes |
| --- | --- | --- |
| Review / closeout | 1–2 | Maintainer-run review agent plus optional closeout assistant. Review and merge authority stays with the maintainer. |
| Support / infra / workflow | 1–2 | Protocol, tooling, and coordination tasks (`maintainer_workflow`, `workflow_protocol`). Keep write surfaces disjoint from active science lanes. |

## How this board relates to the rest of the system

- **Task claiming** ([`agent-task-claiming.md`](agent-task-claiming.md)): the
  board says *how many* agents fit a lane; the claiming ledger records *which*
  agent took *which* task so two agents do not collide. Use both.
- **Task-to-campaign index** ([`notes/task-to-campaign-lane-index.md`](notes/task-to-campaign-lane-index.md),
  TASK-0460/TASK-0509): maps each active task to a lane and flags
  parallel-safety and write-path conflicts on demand — the per-task companion
  to this per-lane board, without committing another generated board file.
- **Mission recommendations** ([`current-missions.md`](current-missions.md),
  `missions/current.yaml`): remain the authority on *what to work on next*. The
  board does not override mission guardrails or task status.
- **Campaign curator cycles** ([`campaign-curator-protocol.md`](campaign-curator-protocol.md)):
  the `curator_review` column shows freshness; a lane whose review is stale
  should be re-reviewed before adding agents.

## Boundaries

- No live dashboard, database, or external service.
- The board does not change canonical task status, mission guardrails, or
  campaign metadata; it is a read-only planning view derived from the catalog.
