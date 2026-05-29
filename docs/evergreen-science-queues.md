# Evergreen Science Queues

## Purpose

An *evergreen* science queue lets a campaign director re-issue the same kind of
bounded scientific attempt many times — across Nuclear, Exoplanet, Quantum,
Atomic, Textbook, and future lanes — without asking agents to "search until
something works." Each issued task is **one controlled attempt** with a pinned
data surface, a frozen baseline, declared controls, and a declared stop
condition, and it must end in exactly one reviewable terminal outcome.

The canonical shape is
[`templates/evergreen-science-task-template.yaml`](./templates/evergreen-science-task-template.yaml).

This document explains how curators use that template and how the bounded
attempts route their outputs through the existing scientific memory.

## Why Bounded, Not Open-Ended

Open-ended "keep trying" queues produce agent churn, duplicated dead ends, and
overclaim pressure. APL is a verifier, so an evergreen attempt is valuable only
when it is falsifiable in advance:

- **one campaign** and **one hypothesis family** per attempt;
- a **pinned data/source surface** with no live external fetch;
- a **frozen baseline** with no in-task refit on the full snapshot;
- **mandatory controls** (at least one matched control or one deterministic
  negative control per interpreted slice);
- a **declared stop condition** stated before the run;
- **preserved negative and inconclusive results**, so a lane is never blindly
  repeated.

This mirrors the discipline already required by the campaign profiles and the
[research quality gate](./research-quality-gate.md), and it keeps a 50-agent
scaling target focused on reviewable scientific output rather than activity.

## Terminal Outcomes

Every evergreen attempt ends in exactly one of these, and each names its
intended artifact class so the reviewer knows where the output belongs:

| Terminal outcome | When | Intended artifact class | Promotion gate |
| --- | --- | --- | --- |
| `result_candidate` | stable per-slice pass/fail under controls | RESULT candidate | Gate A; no auto claim |
| `negative_result` | candidate contradicted under controls | RESULT (`FALSIFIED`) or sandbox note | Gate A optional; negatives preserved |
| `inconclusive_result` | run did not decide the question | sandbox-only | no promotion |
| `source_blocker` | a required bounded-attempt field cannot be satisfied | no-promotion blocker review | no metric run |
| `next_task_proposal` | the useful next step is a different bounded task | task proposal or PRED candidate | PRED uses Gate A; claims maintainer-only |

The default is **sandbox-only**. A `RESULT` or `PRED` candidate may be published
at `review_tier: AGENT_PUBLISHED` **only** when the issued task explicitly
scopes that output and the **Result Publication Gate (Gate A)** in
[`result-promotion-protocol.md`](./result-promotion-protocol.md) passes, with
the `agent_proposal_evaluation` block populated. Claim status transitions and
knowledge endorsement remain maintainer-only in Phase 1.

## How A Curator Issues An Evergreen Attempt

1. Copy [`templates/evergreen-science-task-template.yaml`](./templates/evergreen-science-task-template.yaml).
2. Fill every `bounded_attempt` field. If one cannot be filled from committed,
   pinned sources, the correct first outcome is a `source_blocker`, not an
   improvised run.
3. Assign the task an id through the normal protocol:
   - a maintainer (or maintainer-authorized campaign director) assigns a
     canonical `TASK-XXXX` per [`agent-task-protocol.md`](./agent-task-protocol.md), or
   - an agent files a `tasks/proposals/` entry using this shape and waits for a
     canonical id, or
   - for a small same-campaign batch, the work runs as a microtask under
     [`scientific-micro-task-protocol.md`](./scientific-micro-task-protocol.md).
4. The executing agent runs the single attempt, writes the `agent_runs/`
   artifacts, and records the one terminal outcome with its artifact class.
5. The output routes through [`result-promotion-protocol.md`](./result-promotion-protocol.md)
   and is summarised per the end-of-task output-routing rule in
   [`agent-task-protocol.md`](./agent-task-protocol.md).

## Relationship To Existing Queues

- **Microtask queues** (`tasks/microtasks/*.yaml`,
  [`scientific-micro-task-protocol.md`](./scientific-micro-task-protocol.md))
  remain the lane for small same-campaign batches. The evergreen template is the
  *shape* a microtask or a canonical task should take when it is a repeated
  bounded scientific attempt.
- **Canonical tasks** (`tasks/TASK-XXXX-*.yaml`) remain the default unit of
  reviewable work. The evergreen template does not replace them; it standardises
  the per-attempt contract a curator stamps out.
- **READY pool health** is governed by
  [`task-queue-health-policy.md`](./task-queue-health-policy.md). Evergreen
  attempts help keep enough independent bounded science available, but the
  health check is advisory and must never inflate the READY count with
  open-ended formula-search tasks.

## Guardrails

- Do not issue broad open-ended or "search until it works" tasks.
- Do not use public-discovery, breakthrough, proof, or universal-scope wording.
- Do not promote claims or knowledge automatically; that stays maintainer-only.
- Do not substitute model-derived or unpinned data to force a run past a
  `source_blocker`.
- Do not delete or hide negative and inconclusive results; they are durable
  scientific memory.

## Cross-References

- [`templates/evergreen-science-task-template.yaml`](./templates/evergreen-science-task-template.yaml) — the canonical template.
- [`reviews/evergreen-science-task-template-review.md`](./reviews/evergreen-science-task-template-review.md) — design review for this template.
- [`scientific-campaign-curator.md`](./scientific-campaign-curator.md) — the maintainer-run director role that issues these queues.
- [`campaign-curator-protocol.md`](./campaign-curator-protocol.md) — director protocol and authority boundary.
- [`result-promotion-protocol.md`](./result-promotion-protocol.md) — terminal-outcome routing and Gate A/B/C.
- [`result-promotion-scorecard.md`](./result-promotion-scorecard.md) — scorecard applied before any public reuse.
- [`research-quality-gate.md`](./research-quality-gate.md) — shared sandbox quality bar.
- [`task-queue-health-policy.md`](./task-queue-health-policy.md) — READY pool health policy.
- [`agent-task-protocol.md`](./agent-task-protocol.md) — canonical task execution protocol.
