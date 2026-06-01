# Research Factory Protocol (TASK-0504)

The canonical, campaign-agnostic protocol for **bounded research factories** in
APL. A factory is a deterministic workflow that a campaign adapter calls to
generate many scoped candidates, apply locked controls, and route the output
into reviewable scientific memory **without promoting claims**. This is the v0.3
capability foundation (see [roadmap.md](roadmap.md), `v0.3 — Research Factory
Layer`, and [notes/research-factory-layer-plan.md](notes/research-factory-layer-plan.md)).

This task defines the protocol only. It does **not** implement a runner
(TASK-0506), define the summary schema (TASK-0505), or run a sprint (TASK-0507).

## What a research factory is

- A **bounded** candidate-generation workflow over a pinned dataset and a frozen
  baseline, restricted to a campaign's approved feature families.
- **Controls-first**: every candidate is evaluated against mandatory controls
  before it can be routed as anything other than negative/blocked.
- A **memory router**: outputs land as negative, inconclusive, shortlist, or
  replay-ready memory — never as a claim, prediction reveal, or discovery.
- **Reusable**: a shared callable layer plus a thin campaign adapter, so a second
  campaign reuses the layer without a framework rewrite.

## What a research factory is not

- Not a discovery engine, an auto-claim path, or a universal-law search.
- Not a place to create `PRED-*`, `CLAIM-*`, `KNOW-*`, or to reveal/score
  predictions.
- Not a live data fetcher, and not a baseline-refit unless a task authorizes it.
- Not a framework: it is a vertical slice that stays small until a real sprint
  proves it.

## Required inputs (declared before any candidate is generated)

| input | requirement |
| --- | --- |
| dataset | a pinned snapshot with source id, retrieval policy, and checksum; no live fetch |
| baseline | a frozen baseline (or an explicitly declared null baseline) |
| allowed feature families | only the campaign-approved `allowed_factory_families` |
| split definitions | train / holdout / stress (and no-leakage guards where applicable) |
| controls | the campaign `required_factory_controls` (null, matched, shuffled, complexity penalty, …) |
| candidate cap | a maximum candidate count declared up front; no post-hoc expansion after seeing metrics |
| output routing | a route verdict per candidate plus campaign-specific blockers |

## Shared callable layer contract

The reusable layer (intended home `physics_lab/factories/`, entrypoint
`scripts/run_research_factory.py`) is defined by these responsibilities. Adapters
implement the campaign-specific parts; the shared core implements the rest.

| component | responsibility | shared vs adapter |
| --- | --- | --- |
| **factory spec** | declares dataset, baseline, families, splits, controls, cap, routing for one run | adapter-supplied, shared schema |
| **campaign adapter** | maps campaign data/baseline/families/controls onto the spec | adapter |
| **candidate generator** | enumerates bounded candidates from allowed families only | shared engine, adapter-parameterized |
| **control suite** | runs mandatory controls and records outcomes | shared, adapter declares which apply |
| **ranking policy** | orders candidates with a complexity penalty; never hides adverse controls | shared |
| **artifact writer** | emits the `factory_summary` (TASK-0505) with per-candidate records | shared |
| **CLI/runner entrypoint** | runs a spec end-to-end deterministically, dry-run capable | shared |

An adapter must not bypass the control suite or artifact writer, and must not add
a campaign-only route verdict outside the canonical set below.

## Route verdicts (canonical set)

Every candidate routes to exactly one of these. No verdict creates a canonical
artifact by itself.

| verdict | meaning |
| --- | --- |
| `NEGATIVE_RESULT` | matched/beaten by a control or baseline; preserved as negative memory |
| `INCONCLUSIVE` | effect visible but underpowered, coverage-limited, or control-sensitive |
| `SHORTLIST_CANDIDATE` | survives declared controls in a sandbox run; non-claim evidence |
| `READY_FOR_REPLAY` | shortlisted with a deterministic replay target and no source/provenance blocker |
| `READY_FOR_PRED_FREEZE` | blocked by default; needs a future no-peek prediction-freeze task and maintainer approval |
| `REJECTED_BY_CONTROL` | a null/shuffled/matched/uncertainty control removes the apparent advantage |
| `LOCAL_ONLY` | useful for local diagnosis but not suitable for reviewable campaign memory |
| `DATA_QUALITY_BLOCKED` | missingness, row count, provenance, or label limits block interpretation |

This is the same set the first adapter contract (Exoplanet, TASK-0508) already
declares; adapters reuse it verbatim.

## Forbidden work

- creating `PRED-*` entries or performing reveal scoring;
- universal mass-law / discovery wording, or any claim/knowledge promotion;
- post-hoc cherry-picking or candidate-cap expansion after seeing metrics;
- live external fetch; baseline refit without an explicit authorizing task;
- committing the rendered factory output as an agent-facing board (it is a
  per-run artifact, routed per [generated-state postmortem](reviews/static-agent-facing-generated-index-postmortem.md)).

## Reuse without a rewrite

A new campaign joins the factory by:

1. declaring `allowed_factory_families`, `required_factory_controls`, and
   `factory_stop_rules` in its `campaign_profiles/<id>.yaml`;
2. writing an adapter contract from
   [research-factory-adapter-contract.md](research-factory-adapter-contract.md)
   (Exoplanet, TASK-0508, is the first worked example);
3. implementing a thin adapter against the shared layer — no core rewrite.

The Nuclear-first sprint contract is
[nuclear-residual-factory-sprint-protocol.md](nuclear-residual-factory-sprint-protocol.md).
The machine-readable per-run output is the `factory_summary` schema (TASK-0505).
