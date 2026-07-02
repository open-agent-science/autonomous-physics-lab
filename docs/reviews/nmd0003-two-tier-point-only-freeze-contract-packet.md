# NMD-0003 Two-Tier Point-Only Prediction-Freeze Contract — Maintainer Decision Packet

- Task: `TASK-0929`
- Domain: nuclear physics (NMD-0003 GP residual mass extrapolation)
- Packet mode: `planning_only` (no code, no metric, no freeze in this task)
- Packet verdict: `MAINTAINER_AMENDMENT_DECISION_READY_POINT_ONLY_TIER_1`
- Decision authority: maintainer (Gate C)
- Freeze execution: a separate follow-up task, only after the maintainer approves an option here

## Purpose And Boundary

This packet preflights a **maintainer amendment** to the prediction protocol: a
two-tier prediction-freeze vocabulary that separates a **tier-1 point-only
freeze** (allowed now, explicitly uncertainty-caveated, scored by MAE and rank
against frozen baselines at a future reveal) from a **tier-2 interval-bearing
freeze** (still gated on fresh-surface calibration validation). It exists to
resolve the structural deadlock recorded in decision D10 of
[maintainer-decision-day-2026-07-02.md](./maintainer-decision-day-2026-07-02.md):
an interval-bearing freeze needs validated calibration; calibration validation
now needs a fresh surface; and the fresh surface is the next AME-class release,
by which time freezing the frontier is worthless because the answers exist.

A **point-only** tier-1 freeze captures the time-sensitive pre-registration
value honestly — a frozen central-value forecast with no interval claim — while
tier-2 stays honestly blocked.

This packet is a **decision preflight only**. It does **not**:

- freeze, register, or score any `PRED-*` entry;
- run any metric or engine command;
- create, edit, or promote any `RESULT-*`, `CLAIM-*`, or `KNOW-*` artifact;
- modify `TASK-0827` or change its blocked status;
- inspect any future reveal target value or any registry target row;
- assert calibrated prediction intervals, predictive-uncertainty quality,
  reveal success, or a nuclear-mass law.

The maintainer decides at Gate C among the options in
[Maintainer Decision Options](#maintainer-decision-options); the actual freeze,
if approved, is a **separate** scoped follow-up task under the normal review
gates.

## Background: Why A Two-Tier Vocabulary

The single-tier freeze design in `TASK-0827` bundles **point value +
calibrated uncertainty** into one `PRED-*` payload and freezes them together.
The no-peek calibration audit (`TASK-0899`,
[nmd0003-gp-uncertainty-calibration-audit.md](./nmd0003-gp-uncertainty-calibration-audit.md))
**failed all three predeclared route families**: the best family reached only
~`0.62` 1-sigma coverage against a `0.6827` target and an RMS standardized
residual of ~`4.3` against a well-calibrated target near `1.0`. No family met
the predeclared success conditions. `TASK-0827` therefore stays blocked because
its interval half is not trustworthy.

The point half is a different story. The retrospective post-AME2020 evidence in
`RESULT-0025` (`results/EXP-0018/RUN-0001/result.yaml`) shows a GP-corrected
holdout MAE of `0.462129` MeV versus a frozen baseline of `2.979273` MeV, a
`2.517144` MeV improvement that clears the best predeclared control
(`smooth_a_gp`) by `1.869312` MeV against a `0.25` MeV survival margin, and
this point-accuracy result replayed exactly under an independent Gate B replay
(maximum absolute drift `0.0`). The maintainer has already approved publishing
this as a **point-estimator memory card** (decision D4;
[nmd0003-result0025-public-review-packet.md](./nmd0003-result0025-public-review-packet.md)).

The two axes are orthogonal. A strong point estimator with a miscalibrated
interval is a normal, expected state. The proposal is to let the freeze
vocabulary reflect that split so the point-accuracy value can be pre-registered
now without waiting on, or borrowing credibility from, the blocked interval.

## The Two-Tier Vocabulary (proposed amendment)

| | Tier-1 point-only freeze | Tier-2 interval-bearing freeze |
| --- | --- | --- |
| Payload | central-value forecast per nuclide only | central value **plus** calibrated 1-sigma / 2-sigma interval |
| Uncertainty claim | **none** (explicit calibration-failure caveat carried inline) | calibrated predictive-interval claim |
| Reveal scoring | MAE and rank vs frozen baselines | MAE and rank **plus** interval coverage / sharpness |
| Precondition | this maintainer amendment (`TASK-0929` Gate C) | validated calibration on a fresh surface per the `TASK-0925` contract |
| Status of the blocking task | does **not** unblock `TASK-0827` | `TASK-0827` (or its successor) remains the interval-bearing freeze; still blocked here |
| Upgrade path | upgradable to tier-2 later **without re-freezing the points** | terminal (already carries intervals) |

Key vocabulary rules:

1. **Tier-1 is a strictly weaker artifact, not a bypass.** It pre-registers a
   frozen central value and nothing else. It carries no interval, no coverage
   claim, and no prediction-readiness wording. It does **not** unblock
   `TASK-0827`, which remains the interval-bearing freeze and remains blocked.
2. **Tier-2 stays gated.** No tier-2 freeze may be created until a
   second-generation calibration method is validated on a **fresh surface** per
   the `TASK-0925` contract (role-disjoint reveal split and/or trickle
   measurement registry). The seen post-AME2020 holdout is diagnostic
   background only and can never unblock an interval claim.
3. **Tier-1 is upgradable without re-freezing points.** See
   [Upgrade Path](#upgrade-path-tier-1-to-tier-2-without-re-freezing-points).
   Intervals are added later as a **separate, additive** `PRED-*` field bound to
   the already-frozen central values; the frozen points and their freeze
   timestamp are never rewritten, so the point pre-registration keeps its
   original no-peek provenance.

## Tier-1 Candidate Specification (precise)

This is the concrete tier-1 point-only freeze the maintainer is being asked to
approve, decline, or defer. The freeze itself is **not** performed here; this
section specifies exactly what a follow-up task would freeze if approved.

### Frozen model (point estimator)

- Model: the frozen NMD-0003 residual GP, `model_nmd0003_residual_gp_zn_rbf`
  (single RBF Gaussian process on `[Z, N]` residuals over one frozen
  liquid-drop baseline), code reference
  `physics_lab/engines/nmd0003_residual_gp.py`, as published in `RESULT-0025`
  (`results/EXP-0018/RUN-0001/result.yaml`).
- **Point output only.** The GP posterior mean is the frozen forecast. The GP
  posterior standard deviation and every derived interval multiplier are
  **excluded** from the tier-1 payload — they are the miscalibrated quantity
  and must not be frozen or cited.
- No re-fit, no hyperparameter retune, no baseline change. The freeze reuses the
  committed frozen surface exactly.

### Frontier nuclide set (no-peek, identity only)

The tier-1 target set is the neutron-rich frontier manifest already defined,
leakage-screened, and reviewed for exactly this purpose:
`data/nuclear_masses/frontier_prediction_targets.yaml`
(`FRONTIER-PRED-TARGETS-0001`, defined under `TASK-0826`;
[nuclear-frontier-prediction-target-set.md](./nuclear-frontier-prediction-target-set.md)).

- 37 candidate targets by `(Z, N)` identity across four extrapolation-dominated
  shell regions, with **0** committed-value hits against the NMD-0003 training
  rows and the post-AME2020 holdout rows at design time:
  - `N=50` neutron-rich isotones around and below Ni-78 (9 targets);
  - `N=82` neutron-rich isotones below the Sn–Cd line (8 targets);
  - `N=126` r-process waiting-point region, neutron-rich rare-earth / pre-Pb
    (10 targets);
  - light neutron-rich O / F / Ne / Na / Mg toward the drip line (10 targets).
- Leakage boundary is inherited verbatim from the manifest: a target is
  admissible only if its `(Z, N)` identity has no committed measured value in
  the two screened in-repo files. The excluded committed neighbors
  (for example Ni-78, Sn-132, Cd-130) must **not** be added as targets.
- Source-state (whether each target is genuinely unmeasured at freeze time) is
  re-verified by the future **freeze** task under the reveal protocol, not
  asserted here.

### Frozen baseline set (for rank scoring at reveal)

The tier-1 freeze pins, alongside the GP point forecast, the frozen
central-value forecasts of the following comparators over the same 37 targets,
so the reveal can score **rank** as well as absolute MAE:

- **DZ10-published-variant** — the 10-term Duflo–Zuker published-equation
  variant (`nmd0003_dz10_published_equation_variant_v2`, arXiv:0912.0882;
  [nmd0003-duflo-zuker-structured-baseline.md](./nmd0003-duflo-zuker-structured-baseline.md)),
  the strongest published-form baseline in the campaign
  (retrospective post-AME2020 MAE `1.256383` MeV). This is a clearly-cited
  published variant, **not** an archival DZ10-code parity run.
- **Frozen liquid-drop baseline** — the inherited frozen baseline from
  `RESULT-0012` (`results/EXP-0012/RUN-0001/result.yaml`), post-AME2020 MAE
  `2.979273` MeV. This is the null-of-record: the smooth macroscopic model the
  GP residual correction is layered on.
- **Best predeclared null/global control** — `smooth_a_gp`, the smooth
  GP-of-`A` control that was the strongest predeclared control in the
  `RESULT-0025` survival test. This is the "does the frontier structure matter
  beyond a smooth global trend" comparator.

All baseline forecasts are frozen from committed, deterministic engine commands
at freeze time; none reads any post-freeze measured value.

### Reveal metrics (point-only)

At a future reveal against an admissible source, the tier-1 scoring is:

- **MAE** of the GP point forecast over the revealed subset of the 37 targets
  (MeV), reported per region and pooled;
- **Rank** of the GP against the frozen baseline set on the same revealed
  subset (does the frozen GP point forecast beat DZ10-published-variant, the
  frozen liquid-drop baseline, and `smooth_a_gp` on out-of-sample frontier
  masses);
- optional per-region MAE breakdown to expose whether any single shell region
  dominates the error, mirroring the seen-holdout tail behavior.

**No interval coverage, no sharpness, and no calibration metric is in scope for
tier-1** — there is no interval to score. Those belong to tier-2.

### Admissible reveal sources

- **Source class A — the next AME / NUBASE-class evaluation** is the primary
  admissible reveal source, consistent with the reveal protocol
  ([../nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md))
  and the standing source watch. A flagged Penning-trap / storage-ring result
  in a watched frontier region may qualify a **subset** reveal under the same
  protocol.
- A source is admissible only when it postdates the freeze, is independently
  reviewable, and is pinned with its own source manifest, checksum record, and
  no-peek audit by the reveal task. This packet pins **no** source and reveals
  **nothing**; it only names the admissible class.
- Until an admissible post-freeze source exists, the tier-1 `PRED-*` entries sit
  in a no-peek `REGISTERED` / reveal-pending state exactly like any other frozen
  prediction. The freeze has standing value precisely because it is timestamped
  **before** any such source is published.

## Mandatory Caveat Wording

The following caveat block is **mandatory** and must appear, unweakened, in this
packet, in any follow-up freeze task's YAML and PR, and in every tier-1
`PRED-*` artifact, memory card, or campaign surface derived from the tier-1
freeze. It is the honesty floor of the whole amendment.

> **Tier-1 point-only freeze — mandatory caveat.** The NMD-0003 predictive
> uncertainty calibration **failed** the no-peek audit (`TASK-0899`): all three
> predeclared route families missed the predeclared coverage and
> standardized-residual conditions (best family ~`0.62` 1-sigma coverage,
> RMS standardized residual ~`4.3`). **Calibrated prediction intervals are
> unavailable.** This freeze registers **point (central-value) forecasts
> only**. It makes **no interval or uncertainty claim**, **no** statement of
> trustworthy 1-sigma / 2-sigma predictive coverage, and **no** prediction-
> readiness or "prediction-ready" wording. It is scored at reveal by **MAE and
> rank against frozen baselines only**. It is **not** a reveal result and **not**
> a blind-prediction success until an admissible source is revealed and scored.
> This tier-1 freeze does **not** unblock `TASK-0827`: `TASK-0827` remains the
> interval-bearing freeze and remains **blocked** for interval-bearing freezes
> until calibration is validated on a fresh surface per the `TASK-0925`
> contract. It establishes **no** nuclear-mass law, **no** broad mass formula,
> and **no** discovery.

Explicitly forbidden in any tier-1 surface (regardless of review tier):

- calibrated prediction intervals, predictive-uncertainty quality, or coverage
  claims;
- reveal-success or blind-prediction-verified language, or any
  prospective-reveal framing, before an actual scored reveal;
- prediction-readiness or interval-freeze-readiness wording, or any phrasing
  implying the interval path is unblocked;
- any framing that the `TASK-0827` interval freeze is unblocked, that the
  freeze-calibration deadlock is closed, or that a nuclear freeze has shipped;
- the standard discovery-grade superlatives barred by `global_forbidden` (the
  breakthrough / world-first / verification / demonstration / resolution family
  of wording), regardless of review tier;
- any new-nuclear-law, broad-mass-formula, or constants-anomaly wording;
- any `CLAIM-*` / `KNOW-*` creation or promotion off the back of the tier-1
  freeze.

## Upgrade Path: Tier-1 To Tier-2 Without Re-Freezing Points

The amendment requires that a tier-1 freeze be **upgradable** to tier-2 later
without re-freezing the points, so the point pre-registration keeps its original
no-peek timestamp and provenance:

1. Tier-1 freezes central-value forecasts into `PRED-*` entries with an explicit
   `freeze_tier: point_only` marker and no interval fields. The frozen central
   values, the frozen baseline forecasts, and the freeze timestamp are the
   immutable core.
2. When (and only when) a second-generation calibration method is **validated on
   a fresh surface** per the `TASK-0925` contract, a **separate** upgrade task
   adds interval fields as an **additive** amendment bound to the **already
   frozen** central values. It does not rewrite, re-fit, or re-time the points.
3. The upgrade is recorded as a new tier marker (`freeze_tier: interval_bearing`)
   plus an `interval_calibration_record` referencing the fresh-surface
   validation; the point-forecast provenance and its freeze timestamp are
   preserved as history.
4. If calibration is never validated, the tier-1 freeze remains a permanently
   valid point-only pre-registration, scored on MAE and rank alone. Nothing is
   stranded.

This makes tier-1 a genuine down payment on tier-2, not a competing artifact:
the expensive, time-sensitive thing (a no-peek frozen frontier central-value
forecast) is captured now; the interval is layered on later if and when it
earns trust.

## Interaction With The Blocked Lanes

- **`TASK-0827` stays blocked and unmodified.** It remains the interval-bearing
  freeze. This packet does not touch its YAML, its status, or its scope, and no
  option below changes that. Tier-1 approval is explicitly **not** a `TASK-0827`
  unblock.
- **`TASK-0925` remains the tier-2 gate.** It is the BLOCKED, protocol-only lane
  that predeclares the second-generation calibration route families and defines
  the fresh-surface validation contract (role-disjoint reveal split + trickle
  measurement registry). Tier-2 freezes are gated on that contract clearing on a
  fresh surface; no pass on the seen post-AME2020 holdout can substitute.
- **`TASK-0899` is the caveat's evidentiary basis.** Its no-peek failure is the
  reason intervals are unavailable and is cited verbatim in the mandatory
  caveat.

## Maintainer Decision Options

### Option A — Approve the tier-1 point-only freeze as a follow-up task (recommended)

Adopt the two-tier vocabulary and authorize a **separate** scoped follow-up task
to execute the tier-1 point-only freeze exactly as specified in
[Tier-1 Candidate Specification](#tier-1-candidate-specification-precise): the
frozen NMD-0003 GP point forecasts and the frozen baseline set (DZ10-published-
variant, frozen liquid-drop baseline, `smooth_a_gp`) over the 37 no-peek
frontier targets, MAE + rank reveal metrics, next AME/NUBASE-class evaluation as
the admissible reveal source, with the mandatory caveat carried in every
artifact.

- Protocol impact: adds the tier-1 / tier-2 vocabulary to the prediction
  protocol as a maintainer amendment.
- Freeze impact here: none (the freeze is the follow-up task).
- `TASK-0827` impact: none; it stays blocked as the interval-bearing freeze.
- Benefit: captures the time-sensitive, no-peek frontier point pre-registration
  before the next AME-class release, honestly and without any interval claim.
- Required boundary: the follow-up task must be point-only, must carry the
  mandatory caveat, must not unblock `TASK-0827`, and must make the freeze
  Gate-A-compliant for `PRED-*` (frozen model reference, named target set,
  reveal conditions explicit, non-claim ceiling).

### Option B — Decline the tier-1 freeze

Do not adopt a point-only tier. Keep the single-tier (interval-bearing) freeze
design only; the frontier freeze waits until calibration is validated.

- Benefit: one freeze vocabulary; nothing frozen until intervals are trustworthy.
- Cost: the time-sensitive point pre-registration value is lost — by the time
  calibration could be validated (needs a fresh surface = the next AME-class
  release), the frontier answers exist and freezing them is worthless. This is
  exactly the deadlock D10 identified.

### Option C — Defer the decision

Take no amendment action now; revisit after another input lands (for example the
`TASK-0925` protocol-only contract is written, or the source watch reports
movement toward the next AME-class edition).

- Benefit: more information before amending the protocol.
- Cost: the point pre-registration window keeps narrowing while deferred; the
  value of a tier-1 freeze is strictly decreasing in time.

## Recommendation

Recommend **Option A**. The point-accuracy evidence is already published and
independently replayed (`RESULT-0025`, Gate B max absolute drift `0.0`), the
no-peek frontier target set already exists and is leakage-screened
(`FRONTIER-PRED-TARGETS-0001`), and the honesty floor is fully specified by the
mandatory caveat. A point-only tier-1 freeze captures the genuinely
time-sensitive pre-registration value — a frozen, timestamped, no-peek frontier
central-value forecast scored later by MAE and rank — **without** making any
uncertainty claim and **without** unblocking `TASK-0827`. Tier-2 stays honestly
gated on the `TASK-0925` fresh-surface contract, and tier-1 is upgradable to
tier-2 later without re-freezing points, so approving Option A forecloses
nothing.

This recommendation is a **planning recommendation only**. It authorizes no
freeze by itself; the maintainer's Gate C selection below governs, and any
approved freeze is a separate follow-up task under the normal review gates.

## Maintainer Decision Checklist

Before selecting an option, the maintainer should confirm:

- [ ] The two-tier vocabulary is understood: tier-1 = point-only (no interval,
      no uncertainty claim); tier-2 = interval-bearing (still gated).
- [ ] Tier-1 approval is **not** a `TASK-0827` unblock and does **not** modify
      `TASK-0827`.
- [ ] The tier-1 target set is the existing no-peek `FRONTIER-PRED-TARGETS-0001`
      manifest (37 targets, 4 regions, 0 committed-value hits at design time),
      with source-state re-verified by the future freeze task.
- [ ] The frozen baseline set is agreed: DZ10-published-variant, the frozen
      liquid-drop baseline (`RESULT-0012`), and `smooth_a_gp`.
- [ ] The reveal metrics are point-only: MAE and rank vs baselines; **no**
      interval coverage/sharpness scoring.
- [ ] The admissible reveal source is the next AME/NUBASE-class evaluation (with
      qualifying Penning-trap/storage-ring subsets under the reveal protocol).
- [ ] The mandatory caveat wording (calibration failed → intervals unavailable;
      no interval/uncertainty claim; no prediction-readiness wording; no
      `TASK-0827`-unblocked framing) will be carried, unweakened, into the
      follow-up freeze task and every tier-1 artifact.
- [ ] The upgrade path is acceptable: intervals may be added later as an additive
      amendment bound to the already-frozen points, without re-freezing them, and
      only after fresh-surface calibration validation per the `TASK-0925`
      contract.
- [ ] Tier-2 remains gated on the `TASK-0925` fresh-surface validation contract;
      no pass on the seen post-AME2020 holdout can substitute.
- [ ] Selected option: **A (approve)** / **B (decline)** / **C (defer)**.
- [ ] If A: the follow-up freeze task is a **separate** scoped task, opened under
      the normal review gates, Gate-A-compliant for `PRED-*`.

## Output-Routing Summary

- Task verdict: `MAINTAINER_AMENDMENT_DECISION_READY_POINT_ONLY_TIER_1`.
- Scope: protocol-amendment **preflight** only; no scoring, no freeze, no metric
  run performed in this task.
- Canonical destination:
  `docs/reviews/nmd0003-two-tier-point-only-freeze-contract-packet.md`
  (this decision packet).
- Review destination: maintainer Gate C decision on the two-tier freeze
  vocabulary amendment (approve tier-1 point-only freeze as a follow-up task /
  decline / defer).
- Review tier: `none` (planning/decision packet; not a tiered scientific
  artifact).
- Gate A status: not attempted (no `RESULT-*` / `PRED-*` created).
  Gate B status: not attempted.
- Result impact: **none** — no `RESULT-*` created, edited, scored, or
  re-verified; `RESULT-0025` unchanged.
- Prediction impact: **none** — no `PRED-*` created, frozen, registered, or
  scored; no frontier target value inspected. Any tier-1 freeze is a separate
  follow-up task after maintainer approval.
- Claim impact: **none** — no `CLAIM-*` created, edited, or promoted.
- Knowledge impact: **none** — no `KNOW-*` created or edited.
- `TASK-0827` impact: **none** — not modified; remains BLOCKED as the
  interval-bearing freeze.
- `TASK-0925` impact: **none** — remains the BLOCKED protocol-only tier-2 gate;
  referenced only as the fresh-surface validation contract that continues to
  gate tier-2.
- Limitations and blockers:
  - This is a decision packet; it authorizes no freeze. The maintainer decides
    at Gate C, and any approved tier-1 freeze is a separate scoped follow-up
    task under the normal review gates.
  - The tier-1 point estimator inherits the `RESULT-0025` scope limits: one
    frozen NMD-0003 residual surface, one RBF GP on `[Z, N]`, one frozen
    liquid-drop baseline; a different baseline or model class would shift the
    residual surface.
  - Calibrated prediction intervals remain unavailable (`TASK-0899` no-peek
    failure); tier-2 remains blocked on fresh-surface calibration validation per
    the `TASK-0925` contract.
  - Frontier target source-state is current-as-of-design-time only; the future
    freeze task must re-verify no-peek source state under the reveal protocol.
