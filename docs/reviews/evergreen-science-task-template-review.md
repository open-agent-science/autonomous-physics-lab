# Evergreen Science Task Template — Design Review

**Task:** TASK-0422
**Status:** workflow design review (no science run, no metrics, no claim)
**Domain:** cross_campaign_quality
**Artifacts under review:**

- `docs/templates/evergreen-science-task-template.yaml` (new)
- `docs/evergreen-science-queues.md` (new)
- `docs/scientific-campaign-curator.md` (cross-reference update)

## Scope

This review records the design rationale for the evergreen science task
template and its accompanying queue documentation. It does not run any
scientific attempt, compute any metric, register any prediction, or promote any
claim. The deliverables are workflow scaffolding: a reusable per-attempt
contract and the curator-facing explanation of how to issue and route it.

## Method

1. Read the curator role and protocol
   (`docs/scientific-campaign-curator.md`, `docs/campaign-curator-protocol.md`),
   the READY-pool health policy (`docs/task-queue-health-policy.md`), and the
   promotion surfaces (`docs/result-promotion-protocol.md`,
   `docs/result-promotion-scorecard.md`).
2. Confirmed the existing vocabulary the template must reuse rather than
   reinvent: verdicts (`VALID_IN_RANGE`, `PARTIALLY_VALID`, `INCONCLUSIVE`,
   `OVERFITTED`, `FALSIFIED`), review tiers (`AGENT_PUBLISHED`,
   `AGENT_VALIDATED`, `MAINTAINER_REVIEWED`, `EXTERNAL_REPLICATED`), and the
   Gate A / Gate B / Gate C structure.
3. Modelled the template on the canonical `tasks/TASK-TEMPLATE.yaml` shape and
   on the real `agent_runs/AGENT-RUN-*/agent_run.yaml` artifact set (run
   metadata, preflight checks, metrics, report, limitations) so issued tasks
   produce artifacts that already validate.
4. Wrote three worked examples (residual mining, source curation, adversarial
   control) so a curator can copy a filled shape instead of an empty skeleton.

## Findings

### F1. The template enforces a single bounded attempt

Every `bounded_attempt` field — campaign, pinned data surface, frozen baseline,
one hypothesis family, mandatory controls, declared metrics, and a declared
stop condition — must be filled before a run. This is the mechanism that turns
"keep trying" into "run one controlled attempt and stop." An attempt that
cannot fill a required field stops as a `source_blocker`, not an improvised run.

### F2. Terminal outcomes name their artifact class

The five terminal outcomes (`result_candidate`, `negative_result`,
`inconclusive_result`, `source_blocker`, `next_task_proposal`) each declare the
intended artifact class and its promotion gate. This keeps the routing decision
explicit at task-design time and consistent with
`docs/result-promotion-protocol.md`. Sandbox-only is the default; RESULT/PRED
promotion is gated on the issued task explicitly scoping it and on Gate A
passing.

### F3. No automatic claim or knowledge promotion

The template's `forbidden_claims` and every terminal outcome's `gate` field
restate that claim status transitions and knowledge endorsement remain
maintainer-only in Phase 1. A `result_candidate` may reach
`review_tier: AGENT_PUBLISHED` via Gate A, but that is explicitly *not* a claim
endorsement.

### F4. Negatives and inconclusives are preserved, not discarded

`negative_result` and `inconclusive_result` are first-class terminal outcomes
with their own artifact destinations. This preserves do-not-repeat memory, which
is the main defence against agents re-running failed lanes at scale.

### F5. The template reuses existing artifact and vocabulary surfaces

Accepted outputs map directly onto the existing `agent_runs/` artifact set and
the `docs/reviews/` note surface. The verdict and review-tier vocabularies are
the existing ones. No new schema, no new directory convention, and no new
promotion path is introduced.

## What This Review Did Not Do

- It did not run any scientific attempt or compute any metric.
- It did not create a canonical `TASK-XXXX` instance of the template.
- It did not register a prediction or write a RESULT/PRED/CLAIM/KNOW artifact.
- It did not modify canonical results, claims, or knowledge.
- It did not change campaign priorities or `missions/current.yaml`.

## Limitations

- The template is a convention, not enforced by code. A future task could add a
  lightweight schema or preflight check that validates an issued instance has
  all `bounded_attempt` fields and exactly one terminal outcome; that is
  deliberately out of scope here to avoid adding infrastructure before the
  convention is reviewed.
- The three worked examples are illustrative shapes, not issued tasks; their
  parameters are placeholders to be pinned by a real issuing task.
- The template assumes the campaign profile already declares its source,
  baseline, and control discipline; it standardises the per-attempt contract,
  it does not replace per-campaign policy.

## Verdict

`SANDBOX_PASS` for the workflow scaffold. The evergreen template, the queue
documentation, and the curator cross-reference give campaign directors a
bounded, reviewable per-attempt contract that routes every outcome — including
negatives, inconclusives, and blockers — through the existing result-promotion
protocol without granting any new promotion authority. No science was run and no
claim was promoted. The next step is for a maintainer or authorized campaign
director to issue the first canonical instance of this template for a chosen
campaign.

## Cross-References

- `docs/templates/evergreen-science-task-template.yaml`
- `docs/evergreen-science-queues.md`
- `docs/scientific-campaign-curator.md`
- `docs/campaign-curator-protocol.md`
- `docs/result-promotion-protocol.md`
- `docs/research-quality-gate.md`
- `docs/task-queue-health-policy.md`
