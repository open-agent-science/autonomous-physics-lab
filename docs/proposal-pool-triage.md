# Proposal-Pool Triage

## Why this exists

Agents are expected to surface bugs, friction, mid-flow research ideas, and
blockers as task proposals (`docs/task-proposal-protocol.md`). As that inflow
grows, the proposal pool must stay processable, or proposals silently
accumulate and the "pending decision" view becomes dishonest (already-accepted
proposals whose status was never updated inflate the backlog).

This document defines how the pool is processed: a mechanical reconciliation
layer that any role can run, plus a clear routing of genuinely-pending
proposals to the responsible role. The maintainer stays the gate for canonical
id assignment, rejection, and science scope.

## Core principle: mechanical reconciliation vs domain judgment

Processing the pool is two different jobs:

- **Mechanical reconciliation** — who already delivered a proposal, which
  declared statuses drift from reality, which look like duplicates. This is
  deterministic and automated by `scripts/apl_proposal_triage.py`.
- **Domain judgment** — is a pending idea worth a canonical task now, at what
  priority. This is routed to the right role and gated by the maintainer.

The declared `status` field stays authoritative and human-readable. The tool
computes an `effective_state` from canonical signals and reports any mismatch;
it never silently rewrites `status`.

## Effective state

For each proposal the tool derives `effective_state` from canonical signals
(`promotion.canonical_task_id`, canonical task existence and its status, and
"accepted-by-reference" — a canonical task that lists the proposal in its
`input.related_objects`):

| effective_state | meaning |
| --- | --- |
| `pending` | no canonical task yet; awaiting a domain decision |
| `accepted` | a canonical task exists and is in flight |
| `resolved` | the canonical task is `DONE` (proposal delivered) |
| `rejected` | declared `REJECTED` |
| `superseded` | declared `SUPERSEDED` |

The proposal `status` enum stays `PROPOSED`, `ACCEPTED`, `REJECTED`,
`SUPERSEDED`. An idea that a role decides not to take now is simply left as an
active `PROPOSED` proposal — there is no separate "deferred" status, because a
deferral with no clear return condition is just an open proposal.

**Drift** is any mismatch a human should reconcile — e.g. declared `PROPOSED`
but a canonical task exists, declared `ACCEPTED` with no task link, a dangling
`canonical_task_id`, or `promotion.decision: accepted` while status is still
`PROPOSED`.

## Routing

Routing is a **suggestion, not an assignment**. Every role can read all pending
proposals and self-select whether a proposal is in its competence; the tool only
proposes a likely owner:

| Suggested to | What |
| --- | --- |
| **review-agent** | any drift / already-delivered proposals → mechanical closeout |
| **Scientific Campaign Director** | pending proposals with a clear science signal |
| **Architect** | pending proposals with a clear infra / workflow signal |
| **unrouted** | ambiguous (both signals or neither) — shown to every role to claim by judgment |
| (none) | in-flight `accepted` or terminal `rejected`/`superseded` |

Science vs infra is decided from keyword signals over the proposal `type` and
`related_domain`. A proposal is suggested to the Director only when it has a
science signal and no infrastructure signal, and to the Architect only when it
has an infrastructure signal and no science signal. When the script **cannot
determine fit confidently** (both signals, or neither), the proposal is
`unrouted` and surfaced to every role so an agent decides whether it is theirs —
the script never forces a guess.

## Duplicate detection is advisory

The tool reports `possible duplicate` clusters (shared slug tokens among
pending proposals). This is a **low-confidence advisory signal only** — the
**agent decides, never the script**. The tool never sets `REJECTED` or
`SUPERSEDED`; a role or the maintainer confirms or dismisses each pair by
judgment.

## Who accepts a proposal, and when

Triage and routing do not accept anything. The decision chain is:

1. **A routed role triages and recommends.** The Scientific Campaign Director
   (science) or the Architect (infra), reading the routed/unrouted queue,
   recommends one outcome per pending proposal: take-now, keep-active (leave it
   as an open `PROPOSED` proposal), `REJECTED`, or duplicate-of-another
   (`SUPERSEDED`). Roles never assign a canonical id and never set a terminal
   status on their own.
2. **The maintainer accepts.** Acceptance happens when the maintainer (or a
   maintainer-authorized task-admin/director in the same turn) creates a
   canonical `TASK-XXXX` for the idea — directly or via the `TASK-QUEUE` lane.
   At that point the proposal moves to `ACCEPTED` and records
   `promotion.canonical_task_id`. This is the only step that assigns a canonical
   id (`docs/agent-task-protocol.md`, `docs/campaign-curator-protocol.md`).
3. **The review-agent closes out.** When the canonical task reaches `DONE`, the
   proposal is reconciled to its delivered state in a maintainer-approved
   closeout (see below).

So: roles **recommend**, the maintainer **accepts** (the moment a canonical task
is created), and the review-agent **closes out** after delivery. Keeping an idea
active and rejection are role recommendations the maintainer confirms.

## The tool

```bash
# Full advisory report (counts, drift, suggested closeouts, routing, duplicates)
python3 scripts/apl_proposal_triage.py

# Machine-readable
python3 scripts/apl_proposal_triage.py --json

# Only one role's queue
python3 scripts/apl_proposal_triage.py --role scientific-director
python3 scripts/apl_proposal_triage.py --role architect
```

`validate-repo --strict` also reports proposal status drift as an **INFO**
advisory (`proposal_status_drift`), so it never breaks the standard
`--fail-on-warnings` flow. A maintainer running an explicit pool audit can
escalate it to an error with `APL_ENFORCE_PROPOSAL_DRIFT=1`.

## Closeout (the systemic fix)

The accepted-but-not-closed debt regrows unless delivery updates the proposal.
The tool's **Suggested closeouts** section lists proposals whose canonical task
is `DONE` but whose declared proposal status is still open. The practical file
change is still `status: ACCEPTED`; `resolved` is a computed effective state,
not a YAML status. Applying it stays a **maintainer-approved, manual** step —
there is no automatic post-merge rewrite in this first iteration.

Use the review-agent closeout lane for this mechanical reconciliation, but keep
the PR proposal-only:

- branch: `agent/<contributor-id>/<agent-id>/closeout-<short-slug>`;
- title: `TASK-CLOSEOUT: <short summary>`;
- changed files: only `tasks/proposals/*.yaml`;
- each changed proposal must set `status: ACCEPTED`,
  `promotion.decision: accepted`, and `promotion.canonical_task_id` to an
  existing canonical task whose status is already `DONE`;
- validation: `python3 scripts/apl_proposal_triage.py` and
  `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`.

This closeout lane may not accept new proposals on the merits, reject stale
ideas, supersede duplicates, promote claims/results, or make a science-scope
decision. It only reconciles proposal metadata after canonical delivery is
already recorded elsewhere.

## Cadence

- **Threshold:** when the genuinely-pending count grows past the
  READY-pool-health target, run a triage sweep
  (`docs/task-queue-health-policy.md`).
- **Periodic:** the review-agent surfaces the Stage 0 report on a light cadence;
  the Scientific Campaign Director and Architect monitor their routed queues as
  a standing responsibility (`agents/scientific-curator.yaml`,
  `agents/architect.yaml`).
- **On delivery:** when a canonical task reaches `DONE`, its proposal should be
  closed out in the next maintainer-approved closeout PR.

## Boundaries (what this layer does not do)

- It does not make `status` a fully derived field — `status` stays explicit and
  human-readable; the tool only reports `effective_state` and any mismatch.
- It does not add new top-level proposal statuses. An idea not taken now stays an
  active `PROPOSED` proposal; a confirmed duplicate is recorded as `SUPERSEDED`
  with the canonical reference as metadata (`DUPLICATE_OF` is not a status).
- It does not auto-fix proposals on merge.
- It does not assign canonical task ids, accept/reject proposals, decide
  duplicates, or make science-scope decisions — those stay with the routed
  roles (recommend) and the maintainer (accept).

## Cross-references

- `docs/task-proposal-protocol.md` — how proposals are created and validated.
- `docs/maintainer-review-agent.md` — review-agent review and closeout.
- `docs/scientific-campaign-curator.md` / `docs/campaign-curator-protocol.md` —
  the Scientific Campaign Director role.
- `agents/architect.yaml` — the Architect role.
- `docs/task-queue-health-policy.md` — pool-health thresholds.
