# Nuclear RESULT-0025 Public-Safe Maintainer Review Packet

- Task: `TASK-0890`
- Result: `RESULT-0025` (`results/EXP-0018/RUN-0001/result.yaml`)
- Experiment / run: `EXP-0018` / `RUN-0001`
- Source domain: nuclear physics (NMD-0003 GP residual extrapolation)
- Current result review tier: `AGENT_PUBLISHED`
- Current result verdict: `PARTIALLY_VALID`
- Decision authority: maintainer
- Packet mode: `planning_only` (no code or metric execution)
- Packet verdict: `MAINTAINER_REVIEW_READY_POINT_ESTIMATOR_ONLY`

## Purpose And Boundary

This packet assembles the existing NMD-0003 GP residual extrapolation evidence
for a maintainer decision about **public-safe wording**. It separates what is
validated **in scope** (a retrospective point-estimator gain that survives
predeclared controls and replays exactly) from what remains **unusable** (a
heavy-tailed, miscalibrated uncertainty envelope that keeps the prediction
freeze blocked).

This packet does **not**:

- create or score any `PRED-*` entry, or change the prediction-freeze status;
- change any `RESULT-0025` metric, verdict, review tier, or input hash;
- inspect any future reveal target value or registry target row;
- create, edit, or promote any `CLAIM-*` or `KNOW-*` artifact;
- claim calibrated prediction intervals or reveal success.

The two evidence axes are kept strictly separate throughout:

- **Point accuracy** — how close the GP-corrected central estimate is to the
  retrospective post-AME2020 holdout values. *Validated in scope.*
- **Interval calibration** — whether the predictive uncertainty envelope is
  trustworthy for future prediction-interval semantics. *Not validated;
  heavy-tailed and miscalibrated.*

A strong point estimator with a miscalibrated interval is a normal and expected
state. It does not weaken the point evidence, and the point evidence does not
rescue the interval.

## Strongest Supported In-Scope Sentence

> On one frozen NMD-0003 residual surface with a single RBF Gaussian-process
> model on `[Z, N]`, the GP correction lowers the retrospective post-AME2020
> holdout mass MAE from a frozen baseline of `2.979273` MeV to `0.462129` MeV
> and clears the best predeclared control (`smooth_a_gp`) by `1.869312` MeV
> against a `0.25` MeV survival margin, and this point-accuracy result replays
> exactly (max absolute drift `0.0`) under an independent Gate B replay; the
> result is point-estimator evidence only and its uncertainty envelope remains
> heavy-tailed and miscalibrated.

This is the single strongest sentence the assembled evidence supports. It is
deliberately bounded to point accuracy, scope, and exact replay, and it carries
the uncertainty caveat inline so it cannot be quoted as an interval or
prediction claim.

## Exact Forbidden Interpretations

The following interpretations are **not** supported and must not appear in any
public card, summary, or campaign surface derived from this result:

- **No calibrated prediction intervals.** The uncertainty envelope is
  `HEAVY_TAILED_MISCALIBRATED` (RMS standardized residual `2.826769` versus a
  well-calibrated target near `1.0`). No statement of trustworthy 1-sigma or
  2-sigma predictive coverage is supported.
- **No reveal success.** This is a retrospective post-AME2020 time-split
  benchmark, not a blind prediction reveal. No reveal score, no "blind
  prediction", no prospective-reveal language.
- **No new nuclear law or broad mass formula.** One frozen residual surface and
  one GP model do not establish a nuclear-mass law, a broad mass formula, or a
  generalizable physical relation.
- **No discovery.** No "breakthrough", "first", "proved", "confirmed",
  "solved", or "discovered" wording, regardless of review tier.
- **No claim or knowledge promotion.** No `CLAIM-*` or `KNOW-*` is created or
  endorsed by this result; any such promotion is a separate maintainer-reviewed
  path.
- **No prediction-freeze unblock.** Point accuracy does not unblock TASK-0827
  prediction freeze; the freeze stays blocked on uncertainty calibration.

## Evidence Chain

| Stage | Evidence | Outcome |
| --- | --- | --- |
| Source point-gain detection | `agent_runs/AGENT-RUN-0080/metrics.json` (TASK-0824) | GP residual correction shows a large retrospective post-AME2020 holdout MAE gain. |
| Canonical result publication | `results/EXP-0018/RUN-0001/result.yaml` (TASK-0843) | `RESULT-0025`, `best_verdict: PARTIALLY_VALID`, `review_tier: AGENT_PUBLISHED`; Gate A conditions recorded as checked. |
| Uncertainty adjudication | `docs/reviews/nmd0003-gp-uncertainty-calibration-adjudication.md` (TASK-0844) | Verdict `POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED`; uniform interval inflation cannot fix the central/tail mismatch. |
| Independent Gate B replay | `docs/reviews/nmd0003-result0025-gp-gate-b-replay.md` (TASK-0864) | Verdict `GATE_B_PASS_POINT_METRICS_UNCERTAINTY_BLOCKED`; point metrics replay at max absolute drift `0.0`; uncertainty blocker reproduced. |
| No-peek uncertainty-route preflight | `TASK-0865` (status `REVIEW_READY`) | A separate in-flight task scoping whether any no-peek calibration route exists; prediction freeze stays blocked until it clears. |

The chain supports reproducibility of the point-estimator gain. It does **not**
provide a calibrated uncertainty envelope, a blind reveal, or independent
external replication of the underlying science.

## Evidence Table: Validated In Scope vs Not Usable

### Validated in scope (safe to surface with qualifiers)

| Evidence | Value | Source | Status |
| --- | --- | --- | --- |
| Holdout rows | `295` | result + Gate B replay | replays exactly |
| Frozen baseline holdout MAE (MeV) | `2.979273` | result + Gate B replay | replays exactly |
| GP-corrected holdout MAE (MeV) | `0.462129` | result + Gate B replay | replays exactly |
| GP MAE improvement (MeV) | `2.517144` | result + Gate B replay | replays exactly |
| Best predeclared control | `smooth_a_gp` | result + Gate B replay | replays exactly |
| GP minus best-control margin (MeV) | `1.869312` | result + Gate B replay | replays exactly |
| Predeclared survival margin (MeV) | `0.25` | result + Gate B replay | margin clears (`1.869312 > 0.25`) |
| Exact metric replay | max absolute drift `0.0` | Gate B replay note | independently reproduced |

These are the retrospective **point-accuracy** facts. They survive the
predeclared controls and reproduce exactly under independent replay. They are
the only material that may carry forward into public wording, and only with the
scope and uncertainty qualifiers stated above.

### Not usable (blocks any prediction-interval or freeze update)

| Evidence | Value | Expected / target | Status |
| --- | --- | --- | --- |
| Calibration verdict | `HEAVY_TAILED_MISCALIBRATED` | well-calibrated | blocker |
| RMS standardized residual | `2.826769` | near `1.0` | far off; heavy tail |
| Empirical 1-sigma coverage | `0.823729` | `0.682689` | over-covered centrally |
| Empirical 2-sigma coverage | `0.966102` | `0.954500` | near nominal, masks tail |
| Train-only inflation route (best tested) | `loo_99_abs_quantile_to_3sigma` scale `1.366877` → RMS z `2.06805` | well-calibrated | still `HEAVY_TAILED_MISCALIBRATED` |
| Worst region RMS z | `8.345306` (`high_eta_ge_0_25`) | near `1.0` | tail-dominated region |
| Top outlier | `Ga-84`, residual `26.33775` MeV, z `46.302384` | — | drives the heavy tail |
| Prediction-freeze status | `blocked_for_uncertainty` | — | TASK-0827 stays blocked |

The uncertainty envelope has a split personality: central coverage is already
too wide at 1-sigma while a small tail inflates the RMS standardized residual.
The adjudication showed that a single train-only interval-inflation rule cannot
make the envelope both calibrated and sharp. This is why **interval
calibration** remains unusable and the prediction freeze stays blocked.

## Why The Two Axes Stay Separate

- The **point estimator** is judged by holdout MAE and the control margin. Both
  pass and both replay exactly. This axis is `PARTIALLY_VALID` in the
  retrospective sense and is safe to surface with scope and uncertainty
  qualifiers.
- The **interval** is judged by coverage and standardized-residual diagnostics.
  These fail the calibration target, and the dedicated adjudication
  (`POINT_GAIN_ONLY_UNCERTAINTY_BLOCKED`) plus the Gate B replay both preserve
  the blocker. This axis is **not** usable and cannot be implied by the strong
  point accuracy.

Conflating the two — for example, citing the low MAE as evidence that the model
"predicts masses with quantified uncertainty" — is exactly the forbidden
overclaim this packet exists to prevent.

## STOP Condition

> **STOP — no public-card uncertainty or prediction wording.** Any public-card
> or campaign-surface text derived from `RESULT-0025` is blocked from stating,
> implying, or summarizing calibrated prediction intervals, predictive
> uncertainty quality, prediction-freeze readiness, or reveal evidence until the
> uncertainty-calibration blocker is independently cleared (the in-flight
> `TASK-0865` no-peek uncertainty-route preflight, followed by a future
> validated calibration task). Until then, only the bounded retrospective
> point-accuracy wording in this packet is public-safe. A secondary metadata
> caveat also applies: the committed `RESULT-0025` package preserves the
> originally published `TASK-0843` input task file, while the Gate B replay
> recorded an expected lifecycle drift in the copied task-YAML hash and replay
> git commit; this is bookkeeping drift, not a scientific input change, and any
> public wording must not present the task-hash drift as a metric or result
> change.

## Maintainer Decision Options

### Option (a): Publish a point-estimator memory card

Surface `RESULT-0025` on the public campaign surface as an
`AGENT_PUBLISHED` / Gate-B-replayed **point-estimator** memory, using the
recommended public wording below.

- Result impact: none (no metric, verdict, tier, or hash change here).
- Claim / knowledge / prediction impact: none.
- Benefit: makes a reproducible point-accuracy result visible without weakening
  the no-peek, uncertainty, or reveal gates.
- Required boundary: the card must keep the scope, exact-replay, no-calibrated-
  interval, no-reveal, and no-nuclear-law qualifiers. The result stays
  `AGENT_PUBLISHED`; any review-tier mutation to `MAINTAINER_REVIEWED` is a
  separate maintainer-controlled action not performed here.

### Option (b): Request metadata repair first

Ask for a small bookkeeping note (or a corrective review record) about the Gate
B task-YAML hash / git-commit lifecycle drift before publishing, so the public
surface points at unambiguous provenance.

- Result impact: none; the committed `RESULT-0025` input task file is already
  the originally published one. The drift is in the disposable replay copy.
- Benefit: removes any reviewer confusion about the task-hash drift line in the
  Gate B note.
- Cost: a small extra documentation step; the scientific evidence is unchanged.

### Option (c): Wait for TASK-0865

Take no public-card action until the in-flight `TASK-0865` no-peek
uncertainty-route preflight is resolved (`REVIEW_READY` at packet time).

- Benefit: lets the uncertainty story settle before any public surface mentions
  this result at all.
- Cost: the reproducible point-accuracy result stays invisible to the public
  surface in the meantime, even though it is independently the safest part of
  the evidence.
- Note: `TASK-0865` resolution does **not** by itself unblock prediction freeze;
  it only decides whether a future calibration route exists or the freeze path
  stops honestly.

### Option (d): Decline stronger public wording

Keep any existing public surface unchanged and explicitly decline to upgrade to
stronger wording (no interval, reveal, law, or discovery language) regardless of
the strong point accuracy.

- Benefit: zero coordination cost; preserves the most conservative posture.
- Cost: does not surface the reproducible point-estimator gain.
- This option is always available and is the floor: the strong MAE gain never
  justifies stronger-than-point-estimator wording while the interval is
  miscalibrated.

## Recommendation

Recommend **Option (a)** with the public wording below, optionally preceded by
the lightweight **Option (b)** metadata note. The completed Gate A publication,
the zero-drift Gate B point-metric replay, and the preserved uncertainty
adjudication are sufficient for a conservative point-estimator memory card. They
are **not** sufficient for any calibrated-interval, reveal, claim, knowledge,
nuclear-law, or discovery wording, and the STOP condition above governs every
public surface until the uncertainty blocker is independently cleared.

## Recommended Public Wording (copy-ready)

> On one frozen NMD-0003 residual surface, a single RBF Gaussian-process model on
> `[Z, N]` lowers the retrospective post-AME2020 holdout nuclear-mass MAE from a
> frozen baseline of `2.979273` MeV to `0.462129` MeV — a `2.517144` MeV
> improvement — and beats the best predeclared control (`smooth_a_gp`) by
> `1.869312` MeV against a `0.25` MeV survival margin. An independent Gate B
> replay reproduced these point metrics exactly (maximum absolute drift `0.0`).
> This is point-estimator evidence on a retrospective time-split holdout, not a
> blind prediction reveal. Its predictive uncertainty envelope is heavy-tailed
> and miscalibrated, so it provides no calibrated prediction intervals and does
> not unblock the nuclear prediction freeze. It establishes no nuclear-mass law,
> no broad mass formula, and no discovery; it is an agent-published,
> independently replayed retrospective point-estimator result only.

## Output Routing

- Task verdict: `MAINTAINER_REVIEW_READY_POINT_ESTIMATOR_ONLY`.
- Canonical destination:
  `docs/reviews/nmd0003-result0025-public-review-packet.md`.
- Review destination: maintainer decision on public-safe point-estimator
  wording and optional metadata note; ratification / public-wording packet only.
- Existing result tier: `AGENT_PUBLISHED`; unchanged by this task.
- Existing result verdict: `PARTIALLY_VALID`; unchanged by this task.
- Gate A status: existing `PASS` for `RESULT-0025` (recorded in the result's
  `agent_proposal_evaluation` block).
- Gate B status: existing `PASS` for point metrics (max absolute drift `0.0`),
  uncertainty blocker reproduced; metadata lifecycle drift recorded.
- Result impact: none; no metric, verdict, review tier, or input hash changed.
- Prediction impact: none; no `PRED-*` created or scored; prediction freeze
  remains blocked on uncertainty calibration.
- Claim impact: none; no `CLAIM-*` created, edited, or promoted.
- Knowledge impact: none; no `KNOW-*` created or edited.
- Blockers: calibrated prediction intervals and prediction freeze remain blocked
  outside this packet (see the STOP condition and the in-flight `TASK-0865`
  preflight); any later review-tier metadata update remains a maintainer
  decision.

## Final Verdict

`RESULT-0025` is ready for a maintainer wording decision as a **point-estimator
memory only**. The defensible public statement is the bounded retrospective
point-accuracy result above. The evidence does not support calibrated prediction
intervals, reveal success, a new nuclear law or broad mass formula, a discovery,
or any claim or knowledge promotion, and the prediction freeze stays blocked
until the uncertainty-calibration route is independently cleared.

## Maintainer Decision (2026-07-02)

Decision: **Option (a)** — publish the point-estimator card with the packet's copy-ready wording and inline uncertainty caveat, plus the light option-(b) bookkeeping note (execution: `TASK-0922`).
Recorded in [maintainer-decision-day-2026-07-02.md](./maintainer-decision-day-2026-07-02.md).
