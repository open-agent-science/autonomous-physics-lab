# Research Factory Adapter Contract (template)

A campaign joins the shared [Research Factory Protocol](research-factory-protocol.md)
by writing an adapter contract from this template. The contract is a
**planning/protocol artifact**: it declares how a campaign plugs into the shared
layer before any runner code or sprint exists. The first worked example is the
Exoplanet contract
([exoplanet-factory-adapter-contract.md](exoplanet-factory-adapter-contract.md),
TASK-0508).

Each adapter contract must declare the following sections.

## Adapter identity

- campaign profile path (`campaign_profiles/<id>.yaml`);
- adapter id and contract version;
- status (`CONTRACT_ONLY` until the shared layer and campaign gates are accepted);
- first-implementation gate (shared protocol + `factory_summary` schema accepted);
- campaign gate (the maintainer decision that lets a real sprint start).

## Required inputs

The pinned dataset + source policy, the frozen/null baseline, the loader and
inclusion filters, the split/axis labels, the row fields used, the evidence
gates the sprint depends on, the candidate cap, and the output-routing surface.
No live fetch.

## Allowed factory families

The campaign's `allowed_factory_families`, each with an allowed scope and a
**required guard** (the control that must run before any positive route).
Forbidden families are listed explicitly.

## Required controls

The campaign's `required_factory_controls`: at minimum a null-baseline
comparison, matched controls, a shuffled/label-destruction negative control
where applicable, a declared minimum row-count floor, and a complexity penalty.
A candidate missing a required control routes to `DATA_QUALITY_BLOCKED`.

## Route verdict mapping

Map the canonical route verdicts (`NEGATIVE_RESULT`, `INCONCLUSIVE`,
`SHORTLIST_CANDIDATE`, `READY_FOR_REPLAY`, `READY_FOR_PRED_FREEZE`,
`REJECTED_BY_CONTROL`, `LOCAL_ONLY`, `DATA_QUALITY_BLOCKED`) to campaign meaning.
Do not invent a campaign-only verdict. No verdict creates a `RESULT-*`, `PRED-*`,
`CLAIM-*`, or `KNOW-*` by itself.

## Campaign-specific factory summary fields

The campaign-specific fields to add to the shared `factory_summary` (TASK-0505),
in addition to the shared fields (dataset, baseline, candidate counts, controls,
route verdict, limitations, reproducibility metadata).

## Stop rules

The campaign's `factory_stop_rules`: conditions under which a future sprint must
stop before execution (missing pinned dataset, live fetch attempt, forbidden
family framing, control-violating routing, or any artifact-promotion attempt
without a maintainer-approved promotion task).

## Recommended follow-up shape

The next step is **not** a `READY` sprint. List candidate `TASK-PROPOSAL` shapes
(adapter smoke run, control-aware go/no-go, conditional audits) that a maintainer
may later accept. Until one is accepted, the adapter stays `CONTRACT_ONLY`.
