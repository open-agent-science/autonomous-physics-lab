# Decision Autonomy Policy — v0 (dry-run)

- Status: **v0, DRY-RUN ONLY.** No autonomy class may auto-apply anything in
  this phase (`can_apply_now: false` everywhere in
  `policy/decision-autonomy.yaml`). Agents produce decision packets; humans
  still click.
- Established by: maintainer decision (Decision Day #2 follow-up, 2026-07-06,
  `docs/reviews/maintainer-decision-day-2026-07-06.md`; TASK-0952).
- Machine-readable matrix: `policy/decision-autonomy.yaml`. Packet template:
  `decisions/DECISION-TEMPLATE.yaml`. CLI: `scripts/apl_decision.py`
  (propose / validate / list / apply — apply refuses in v0). Dry-run
  protocol: `docs/reviews/decision-autonomy-dry-run-plan.md`; retrotest:
  `docs/reviews/decision-autonomy-retrotest-20260706.md`.

## Principle

**Agents do not make maintainer decisions. Agents apply standing maintainer
policy.** The maintainer decides once — at the policy level; agents classify
concrete situations against the approved matrix, verify the gates, and apply
the pre-approved default. The human handles exceptions, holds a veto, and
owns a non-reducible list of decision types outright.

The autonomy boundary is **reversibility x external exposure**, not task
difficulty. Public naming: "standing-policy autonomy" / "guarded lazy
consensus". Never describe this mechanism as "default-yes" in public
surfaces.

## Classes

### Class 0 — policy-auto (reversible internal hygiene)

Examples: closeout of already-merged tasks; board/generated-view hygiene;
task SUPERSEDED when the superseding task is DONE; proposal backlinks and
age-based adjudication per directive; docs drift fixes limited to typos,
links, and factual sync.

Gates (all required): CI green; `validate-repo --strict` green; review agent
MERGE_OK; **no** RESULT/PRED/CLAIM/KNOW status change; no external
publication; no license ambiguity; no public claim-wording change.

### Class 1 — guarded lazy consensus (reversible internal routing)

Examples: negative/control memory routing; campaign HOLD/MONITOR after an
explicit blocker; no-broad-pilot decisions; source-readiness GO when the
manifest is already verified; claim novelty/role classification without
support-status change; bounded scout approval; task-queue top-up within the
WIP rules.

Gates: quorum of **K>=2 agent votes from separate sessions** with recorded
model/tool (cross-vendor **preferred**; mandatory for auto-apply in Phase 3
— a same-vendor quorum may classify in dry-run but must escalate rather than
apply); **one formal devil's advocate** (fields below) — if the advocate
finds a real blocker, escalation is automatic; decision packet committed;
48-hour veto window (Phase 3+) with a maintainer digest; no maintainer-only
artifact touched.

Devil's advocate is a required packet block, not a vibe:

```yaml
devils_advocate:
  alternative_considered: ...
  strongest_objection: ...
  why_rejected: ...
  escalation_required: false
```

### Class 2 — maintainer-only (non-reducible)

CLAIM support-status changes; KNOW creation / accepted scientific
interpretation; Zenodo/DOI publication and any external release; license /
permission / third-party data-rights ambiguity; external communications
(authors, reviewers, articles, launches); prediction freezes; repo
visibility, branch protection, secrets; git history rewrite; **any change to
this policy, the matrix, or the CODEOWNERS guard**.

This list may grow by maintainer decision; it may never shrink by agent
decision. Unknown decision types are **default-deny**: anything not mapped
in the matrix is treated as Class 2.

## Mechanics

- **Decision packets.** Every non-trivial routing decision becomes a
  `decisions/DEC-YYYYMMDD-<slug>.yaml` (template committed). The packet
  records class, reversibility, external exposure, artifact-impact flags,
  quorum votes, the devil's-advocate block, veto deadline, and
  `decided_by: policy_auto | agent_quorum | maintainer`. Decision Day memos
  reference packets instead of duplicating them — one canonical surface.
- **Veto and rollback.** A maintainer veto within the window blocks apply. A
  post-apply disagreement is executed as a `revert` decision packet with the
  reason recorded (never a silent revert) and increments
  `decision_reversal_count`.
- **Expedite path.** A batch/window item that blocks a high-priority lane
  may be pulled for immediate individual maintainer decision.
- **Standing directives** (approved now, executed as packets):
  1. *Stale blocker*: a BLOCKED task whose blockers are all DONE or
     superseded gets a decision packet; if the superseding path already
     executed, propose SUPERSEDED.
  2. *Proposal age*: proposals older than 30 days are adjudicated — ACCEPT
     cheap infra aligned with strategy; REJECT broad pre-consolidation
     scaffolds; BACKLINK already-implemented ones.
  3. *High-risk claim*: numerology-adjacent or high-overclaim DRAFT claims
     with inconclusive evidence are proposed for stress-test-memory parking
     unless new external evidence exists.
  4. *Campaign no-go*: a campaign with repeated source scouts and no
     admissible artifact moves to HOLD/MONITOR unless a new source route or
     maintainer-approved external input exists.
  5. *Queue throttle*: no large task wave while REVIEW_READY >= 8; top up to
     12-16 READY only after the review queue is under control.
- **Graduation / demotion (metrics-driven).** A decision type with
  escalation+veto rate ~0 over 4 weeks may be proposed for demotion by one
  class (maintainer approves the matrix change); any wrong autonomous
  decision promotes its type up one class immediately.
- **Metrics** (collected from packets): decision_count_by_class,
  auto_decision_count, maintainer_escalation_count, veto_count/veto_rate,
  wrong_classification_count, decision_reversal_count, time_to_decision,
  review_ready_age. Month-1 target: 50-70% of routing decisions handled by
  policy/dry-run/lazy consensus; **0** automatic claim promotions; **0**
  automatic external-publication decisions; **0** serious wrong autonomous
  decisions.

## Red lines (never automatic, any phase)

No automatic: strong scientific claim endorsement; Zenodo/DOI publication;
external emails or announcements; prediction freezes; legal/rights
decisions; branch-protection/repo-setting changes; public launch wording;
expansion of this policy's autonomy.

## Phases

1. **Phase 1 (now, 1-2 weeks):** dry-run. Packets + classification only;
   nothing auto-applies (including Class 0). Success criteria in the dry-run
   plan; calibration starts from the retro-classification of the eight
   Decision Day #2 decisions.
2. **Phase 2:** auto-apply Class 0 (maintainer flips `can_apply_now` for
   class_0 in the matrix).
3. **Phase 3:** guarded lazy consensus for Class 1 (48h veto window,
   cross-vendor quorum mandatory for apply).
4. **Phase 4:** sampling audit (maintainer reviews 10-20% of applied
   decisions) with metrics-driven class demotions.
