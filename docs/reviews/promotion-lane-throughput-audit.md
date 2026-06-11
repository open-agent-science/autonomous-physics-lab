# Promotion-Lane Throughput Audit

**Task:** `TASK-0716` (canonical task YAML in `tasks/`)
**Source proposal:** [`tasks/proposals/20260610-roman-promotion-lane-throughput.yaml`](../../tasks/proposals/20260610-roman-promotion-lane-throughput.yaml)
**Mode:** planning only (no engine run, no live fetch, no new metrics, no promotion)
**Domain:** `scientific_result_publication`
**Date:** 2026-06-11
**Verdict:** `not_applicable` (lane throughput audit; produces no scientific verdict)

## Purpose And Boundary

This audit looks at the **promotion lane itself** — where evidence narrows as it
moves toward canonical `RESULT-*` / `CLAIM-*` / `KNOW-*` memory — and names the
smallest changes that restore throughput **without weakening any gate**.

It is deliberately **not**:

- a per-artifact promotion classification. That already exists as a one-time
  routing inventory in
  [`cross-campaign-result-promotion-inventory.md`](./cross-campaign-result-promotion-inventory.md)
  (`TASK-0659`); this audit references it instead of re-listing artifacts.
- a recurring dashboard or digest. Live state stays in its dynamic sources
  (`python3 scripts/apl_mission.py --output onboarding`,
  [`results/golden-results.yaml`](../../results/golden-results.yaml),
  [`prediction_registry/nuclear_masses/registry_summary.yaml`](../../prediction_registry/nuclear_masses/registry_summary.yaml)).
- a promotion action. No `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact is
  created, edited, or promoted here. Every recommendation routes through a
  separate reviewed task and the gates in
  [`result-promotion-protocol.md`](../result-promotion-protocol.md).

Re-run only when the promotion frontier materially moves (a new tiered result,
a wired gate helper, or the first promoted claim/knowledge entry).

## Lane Inventory (measured 2026-06-11)

| Stage | Count | Notes |
| --- | --- | --- |
| `RESULT-*` artifacts (`results/**/result.yaml`) | 19 | Across `EXP-0001`–`EXP-0013`. |
| — carrying an explicit `review_tier` | 4 | 2 `AGENT_PUBLISHED`, 2 `AGENT_VALIDATED`. |
| — untiered / legacy (`LEGACY_UNTIERED`) | 15 | Predate the four-tier model; no Gate A block attached. |
| `PRED-*` entries (`prediction_registry/**`) | 64 | Nuclear + exoplanet; `REGISTERED`, pre-reveal, no claim promotion allowed. |
| `CLAIM-*` files | 10 | **All `status: DRAFT`** (`CLAIM-0001`…`CLAIM-0010`). |
| `KNOW-*` promoted knowledge entries | 0 | `knowledge/` holds 12 reference/notes files, none tier-promoted. |
| `docs/reviews/` notes | 281 | Review/gate/audit memory vastly outweighs canonical output. |

The shape confirms the proposal's premise: the lane is **wide on review memory,
narrow on canonical output, and zero at the knowledge tier**. The output side is
as blocked as the input side was before the acquisition work.

## Where The Lane Narrows (throughput diagnosis)

Three distinct choke points, each at a different gate. They are independent — a
fix to one does not unblock the others.

### 1. Gate B replay tooling is unwired (structural choke between PUBLISHED → VALIDATED)

Gate A (Result Publication Gate) **is** wired and agent-autonomous:
[`scripts/apl_validate_agent_published_result.py`](../../scripts/apl_validate_agent_published_result.py)
mechanically checks an `AGENT_PUBLISHED` artifact.

Gate B (Independent Replay Gate) is **defined but not wired as a reusable
runner**. `result-promotion-protocol.md` ("First Sprint", item 2) and
[`maintainer-review-agent.md`](../maintainer-review-agent.md) both flag that
"until the Gate B replay helper is wired, the review remains a [manual step]".
Today only **campaign-specific** replay scripts exist
([`run_nuclear_f2_independent_replay.py`](../../scripts/run_nuclear_f2_independent_replay.py),
[`run_exoplanet_second_snapshot_baseline_replay_preflight.py`](../../scripts/run_exoplanet_second_snapshot_baseline_replay_preflight.py)),
not the generic "wrap a published `command`, re-execute deterministically, emit a
`validation_record` diff" runner the protocol describes. Consequence: the
agent-to-agent self-validation lane cannot fire, so `AGENT_PUBLISHED` results
stall instead of reaching `AGENT_VALIDATED`. This is the **single highest-leverage
tooling gap**: it is the only choke that a tooling change (not a maintainer
decision) can open.

### 2. CLAIM tier has no agent handoff past DRAFT (maintainer-decision choke)

All 10 claims sit at `DRAFT`. Per
[`claim-promotion-policy.md`](../claim-promotion-policy.md), every `CLAIM-*`
status transition is **maintainer-only in Phase 1** — this is policy, not a
defect, and must not be weakened. But there is no lightweight **evidence-assembly
handoff** that lets an agent present a claim as "review-ready" (evidence
references gathered, gates cited, wording scoped) for a single maintainer
flip. The lowest-risk first target named by the protocol is `CLAIM-0001`
(pendulum). The throughput fix here is a *handoff artifact*, not a status change.

### 3. Untiered legacy results have no Gate-A backfill path (latent choke)

15 of 19 results carry no `review_tier`. They are not wrong — they predate the
model — but they are invisible to Gate A/B tooling and cannot enter the replay
lane. A bounded backfill (attach `review_tier` + `agent_proposal_evaluation` to
the subset that already meets Gate A) would widen the lane mouth. This is
lower-priority than (1) and (2) and is partially covered by the existing
inventory's Gate A column; flagged here for completeness, not recommended as a
new task this cycle (see Deduplication).

## Promotion Backlog (strongest candidates this cycle)

Classes per [`campaign-curator-protocol.md`](../campaign-curator-protocol.md).
The per-artifact frontier already lives in the cross-campaign inventory; this
backlog lists only the candidates whose **next action is a throughput move**.

| Candidate | Source path | Class | Recommended next action | Blocker / reason | Overclaim risk |
| --- | --- | --- | --- | --- | --- |
| `RESULT-0019` textbook Stefan–Boltzmann exact-ref fixture | [`results/EXP-0013/RUN-0001/result.yaml`](../../results/EXP-0013/RUN-0001/result.yaml) | `replay-needed` | First target for a **generic Gate B replay runner** — deterministic, exact-reference, lowest-risk replay in the repo. | Gate B helper unwired (choke 1). | Low — software fixture, not a physics discovery. |
| `RESULT-0018` nuclear F2 component-ablation preflight | [`results/EXP-0012/RUN-0002/result.yaml`](../../results/EXP-0012/RUN-0002/result.yaml) | `replay-needed` | Second Gate B replay target once the runner exists; ties to `TASK-0635`. | Gate B helper unwired; `INCONCLUSIVE` verdict keeps it diagnostic-only. | Low — verdict already conservative. |
| `CLAIM-0001` pendulum period–amplitude | [`claims/CLAIM-0001-pendulum-period-amplitude.md`](../../claims/CLAIM-0001-pendulum-period-amplitude.md) | `claim-review-candidate` | Prepare a maintainer **evidence-assembly handoff** (references + gate citations + scoped wording) for a single DRAFT→review decision. | `needs_maintainer_decision` — Phase 1 keeps the flip maintainer-only. | Low — mature, range-bounded, well-replicated. |
| `RESULT-0017` pendulum overfit negative result | [`results/EXP-0001/RUN-0006/result.yaml`](../../results/EXP-0001/RUN-0006/result.yaml) | `negative-result-backfill` | Already `AGENT_PUBLISHED`; becomes a Gate B replay candidate once the runner lands. Preserve as published negative memory meanwhile. | Gate B helper unwired. | Low — explicitly `OVERFITTED`. |
| `RESULT-0016` anharmonic (past Gate B) | [`results/EXP-0011/RUN-0002/result.yaml`](../../results/EXP-0011/RUN-0002/result.yaml) | `claim-review-candidate` | Gate B already done; next is maintainer review of `CLAIM-0009`. No agent action available. | `needs_maintainer_decision`. | Low. |
| 15 untiered legacy results | `results/EXP-000X/**` | `do-not-promote` (this cycle) | Leave as-is; backfill only if a scoped Gate-A task is explicitly opened. | `duplicate_or_superseded` — partially covered by `TASK-0659` inventory; opening a wave now would be filler. | n/a |
| 64 `PRED-*` pre-reveal entries | `prediction_registry/**` | `do-not-promote` (pre-reveal) | Leave frozen until reveal triggers fire. | `leakage_or_holdout_risk` — `pre_reveal_claim_promotion_allowed: false`. | High if revealed early — do not touch. |

## Missing Gate A/B Tooling (the smallest pieces that unblock the lane)

1. **Generic Gate B replay runner** — *missing, highest leverage.* A small
   cross-platform helper that takes a published `RESULT-*`, re-executes its
   recorded `command` deterministically, and emits a `validation_record` diff
   (metrics match within tolerance, or drift documented). Wraps the existing
   campaign-specific replay scripts' pattern into the reusable form the protocol
   already specifies. Without it, no `AGENT_PUBLISHED` result can become
   `AGENT_VALIDATED` autonomously.
2. **Claim evidence-assembly handoff template** — *missing, decision-side.* A
   minimal "review-ready DRAFT claim" checklist/handoff (evidence refs, gate
   citations, scoped wording) that prepares a single maintainer flip **without**
   changing claim status. Does not weaken `claim-promotion-policy.md`; it only
   makes the maintainer step cheap.
3. **Gate A is sufficient; no new tooling needed** — `apl_validate_agent_published_result.py`
   covers the publication gate. No change recommended here.

## Recommended Follow-Up Tasks (≤3, each tied to a named artifact + output path)

> Advisory only. These are proposals; canonical `TASK-XXXX` ids require
> maintainer approval. None promotes an artifact.

1. **Wire the generic Gate B replay runner and validate it on `RESULT-0019`.**
   - Evidence artifact: [`results/EXP-0013/RUN-0001/result.yaml`](../../results/EXP-0013/RUN-0001/result.yaml)
   - Output path: `scripts/apl_gate_b_replay.py` (+ focused test) and a
     `validation_record` on `RESULT-0019` → eligible `AGENT_VALIDATED` upgrade.
   - Why: opens choke 1, the only tooling-openable bottleneck; lowest-risk
     deterministic target proves the runner before nuclear/exoplanet replays.

2. **Prepare a maintainer evidence-assembly handoff for `CLAIM-0001` (DRAFT, no status change).**
   - Evidence artifact: [`claims/CLAIM-0001-pendulum-period-amplitude.md`](../../claims/CLAIM-0001-pendulum-period-amplitude.md)
   - Output path: `docs/reviews/claim-0001-evidence-assembly-handoff.md`.
   - Why: opens choke 2 for the single lowest-risk claim while keeping the
     DRAFT→supported flip maintainer-only per `claim-promotion-policy.md`.

3. **(Conditional) Replay `RESULT-0018` once the Gate B runner exists.**
   - Evidence artifact: [`results/EXP-0012/RUN-0002/result.yaml`](../../results/EXP-0012/RUN-0002/result.yaml)
   - Output path: `validation_record` on `RESULT-0018` (ties to `TASK-0635`).
   - Why: second Gate B exercise; depends on task 1, so queue it after.

No more than these three. Adding a legacy-backfill wave or a new inventory page
this cycle would be filler — the untiered results are already mapped by
`TASK-0659`, and a recurring dashboard is explicitly rejected by the curator
protocol.

## Guardrails Honored

- No claim, result, prediction, or knowledge artifact promoted, created, or
  edited.
- No gate weakened. Gate B definition, `claim-promotion-policy.md` maintainer-only
  rule, and pre-reveal `PRED-*` holdout boundaries left intact; recommendations
  only *complete missing tooling* and *prepare maintainer handoffs*.
- No duplicate digest/dashboard. References the existing cross-campaign inventory
  and dynamic sources instead of re-listing artifacts.
- ≤3 follow-up tasks, each tied to a named evidence artifact and output path.

## Output Routing Summary

- **Task verdict:** `not_applicable` (lane throughput audit; no scientific
  verdict).
- **Canonical destination:** this review note
  (`docs/reviews/promotion-lane-throughput-audit.md`) plus an `IN_PROGRESS →
  REVIEW_READY` transition on `TASK-0716`.
- **Review tier:** `none` (no tiered RESULT/PRED/CLAIM/KNOW artifact produced).
- **Gate A/B status:** not attempted (audit does not run a gate; it reports gate
  *tooling* state — Gate A wired, Gate B runner missing).
- **Claim impact:** no claim change. Recommends a future evidence-assembly
  handoff for `CLAIM-0001`; the DRAFT status is untouched.
- **Knowledge impact:** no knowledge change; task proposals only.
- **Limitations / blockers:** counts are a point-in-time snapshot of the local
  checkout; the generic Gate B replay runner is the primary missing tooling and
  blocks the autonomous PUBLISHED→VALIDATED lane; all three recommended tasks
  require maintainer canonical-id assignment before execution.
