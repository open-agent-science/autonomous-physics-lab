# Nuclear New-Lanes Decision After Uncertainty And Adversarial Controls

**Task:** TASK-0365
**Status:** synthesis review (no agent run; no model fits; no PRED entries; no claims)
**Campaign:** Nuclear Mass Surface

## Scope

This synthesis turns the recent Nuclear hypothesis wave into one
maintainer-facing decision artifact instead of six per-lane
impressions. It records what each lane found, classifies the
signal-vs-control posture, names the explicit go/no-go on a
no-leakage local-curvature predictive task, names the go/no-go on
high-error cluster work, and recommends at most three next
Nuclear tasks while avoiding another broad audit loop.

It does **not** run any candidate, does **not** score any reveal,
does **not** add any `PRED-XXXX.yaml`, does **not** update claims
or knowledge files, does **not** rewrite any prior agent-run
verdict, and does **not** relax the TASK-0303 source preflight,
the TASK-0352 freeze protocol, or the TASK-0368 no-leakage
contract.

## Lanes Synthesised

| Lane | Task | Agent run | Status | Verdict in committed review |
| --- | --- | --- | --- | --- |
| Deformation proxy | TASK-0338 | AGENT-RUN-0025 | DONE | INCONCLUSIVE |
| Local curvature (sandbox) | TASK-0339 | AGENT-RUN-0026 | DONE | INCONCLUSIVE |
| Odd-even shell interaction | TASK-0340 | AGENT-RUN-0027 | DONE | INCONCLUSIVE |
| Measured/extrapolated boundary | TASK-0341 | AGENT-RUN-0028 | DONE | INCONCLUSIVE |
| Uncertainty-weighted residual | TASK-0342 | AGENT-RUN-0029 | DONE | INCONCLUSIVE |
| High-error cluster | TASK-0343 | AGENT-RUN-0030 | DONE | PARTIALLY_VALID |
| Local curvature adversarial controls | TASK-0351 | AGENT-RUN-0031 | DONE | PARTIALLY_VALID |

Pre-conditions for this synthesis (TASK-0342, TASK-0343,
TASK-0351 in DONE or preserved blocker state) are all met.

## Signal-vs-Control Classification

Each lane is placed in one of four buckets based on how its primary
candidate fared against its matched controls on the committed
diagnostic subsets:

### Bucket A — Robust under controls

- **Local curvature, `LOCAL-CURVATURE-001` only** (TASK-0351 /
  AGENT-RUN-0031). The candidate beats the strongest control
  (`LOCAL-CONTROL-005` chain-blind smoother) by +0.544 MeV on
  the `full_known` primary subset and wins more than half of the
  per-subset comparisons. The other two predecessor candidates
  (`LOCAL-CURVATURE-002`, `LOCAL-CURVATURE-003`) were **falsified**
  by the adversarial controls and stay sandbox memory only.
- This bucket has exactly one candidate. It is the strongest
  surviving Nuclear residual signal, and it is the only candidate
  that is admissible into a future no-leakage predictive
  implementation lane (per TASK-0368 family F1).

### Bucket B — Control-sensitive (signal real but controls bind)

- **High-error cluster, `HIGHCLUSTER-001`/`-003`** (TASK-0343 /
  AGENT-RUN-0030). Both candidates beat the matched-random and
  smooth-A controls on `full_known` and on the high-error /
  neutron-rich subsets, but the cluster labels are derived from
  baseline residuals, so the `cluster_label_shuffle_control`
  posture is decisive: the shuffle control itself shows
  PARTIALLY_VALID on some subsets, meaning the cluster-label
  channel carries information independent of the candidate
  hypothesis. The signal is real but the predictive use is
  blocked until the cluster label is re-anchored on Z/N/A-only
  features.

### Bucket C — Control-dominated (matched controls beat the
candidates)

- **Odd-even shell interaction** (TASK-0340 / AGENT-RUN-0027). All
  three `ODD-SHELL-*` candidates regress on `full_known` while
  `ODD-SHELL-CONTROL-002` (shell-only) reaches −0.081 MeV. The
  shell-only baseline does everything the interaction candidates
  do plus more. Lane closed as preserved negative evidence.
- **Measured/extrapolated boundary** (TASK-0341 / AGENT-RUN-0028).
  `BOUNDARY-CONTROL-004` (smooth-A) reaches −0.405 MeV on
  `full_known`; the boundary candidates max out at −0.012 MeV.
  The source-status channel is dominated by smoothness of `A`.

### Bucket D — Null evidence (no consistent improvement)

- **Deformation proxy** (TASK-0338 / AGENT-RUN-0025). All three
  candidates regress on `full_known` and on the primary holdout;
  the best is +0.008 MeV on full_known. Useful failure-mode atlas
  of one family of Z/N/A-derived proxies; preserved sandbox
  memory only.
- **Uncertainty-weighted residual** (TASK-0342 / AGENT-RUN-0029).
  Uncertainty fields are committed at `review_only` grade
  (sigma-norm err ~259 across the full slice). The weighted /
  filtered variants do not change the unweighted MAE and do not
  produce a candidate-vs-baseline improvement. Useful as the
  TASK-0368 F5 input-discipline anchor (uncertainties must be
  committed and the weighting frozen before any predictive use).

## Go/No-Go Decisions

### D1. No-leakage local-curvature predictive implementation

**GO.** Open a separate maintainer-approved canonical task to
implement `LOCAL-CURVATURE-001` end-to-end against the TASK-0352
freeze protocol and the TASK-0368 F1 promotion path. The task
must:

- use only the F1-admissible candidate (`LOCAL-CURVATURE-001`);
- use leave-one-out neighbor windows
  (`F1-REQ-LOO-WINDOW`);
- consume only **baseline-only** neighbor residuals
  (`F1-REQ-BASELINE-ONLY-INPUT`);
- regenerate the neighbor cache per fold
  (`F1-REQ-PER-FOLD-CACHE`);
- exclude `PRED-XXXX` target rows from every other row's window
  (`F1-REQ-PRED-EXCLUSION`);
- declare and document the missing-neighbor strategy
  (`F1-REQ-MISSING-NEIGHBOR-DECLARED`);
- pass the six TASK-0352 minimum controls
  (self-exclusion ablation, chain-shuffled, smooth-window,
  near-null, per-fold cache audit, source-status separation)
  with a primary survival margin ≥ 0.25 MeV on `full_known` and
  majority wins on per-subset diagnostics;
- not create a `PRED-XXXX.yaml` entry. The PRED entry is a
  downstream task assigned only after the predictive
  implementation is reviewed.

`LOCAL-CURVATURE-002` and `LOCAL-CURVATURE-003` are **not**
admissible. They were falsified by TASK-0351 and must stay
sandbox memory only.

### D2. High-error cluster work

**HOLD diagnostic, NO predictive go.** The lane is preserved as
the campaign's high-error failure-mode atlas. Do **not** open a
predictive implementation task. Do **not** merge `HIGHCLUSTER-*`
into the local-curvature controls — the cluster-label shuffle is
control-sensitive enough that mixing them dilutes the F1 control
gate.

A bounded follow-up under TASK-0368 family F2 may rebuild the
cluster labels from Z/N/A-only features
(`F2-REQ-LABEL-FROM-Z-N-ONLY`) and rerun the matched-control
gate. Until that lands, no predictive use is authorised.

### D3. Odd-even shell interaction, deformation proxy,
measured/extrapolated boundary

**STOP.** All three lanes are preserved sandbox memory.
`ODD-SHELL-*` is dominated by the shell-only control,
`DEFORM-PROXY-*` shows no consistent improvement, and
`BOUNDARY-*` is dominated by the smooth-A control. No
predictive implementation task is authorised. No new sandbox
batches in any of these lanes. New families (parity-pair,
asymmetric-refinement) need their own TASK-0368 classification
before entering scope.

### D4. Uncertainty-weighted residual

**HOLD diagnostic, KEEP as TASK-0368 F5 anchor.** The lane
itself is INCONCLUSIVE for a candidate-vs-baseline improvement,
but it is the empirical anchor that motivates the F5 promotion
path: `F5-REQ-COMMITTED-UNCERTAINTY-ONLY`,
`F5-REQ-WEIGHTING-FROZEN`, `F5-REQ-NEAR-NULL-CONTROL`. Future
F5 candidates may exist; they are not opened by this synthesis.

## Recommended Next Nuclear Tasks (≤ 3)

These are recommendations only; this synthesis does not create
canonical tasks. Each requires a separate maintainer-approved
canonical-task assignment per `docs/agent-task-protocol.md`.

1. **R1 — Implement no-leakage local-curvature candidate
   end-to-end.** Scope:
   `scripts/run_nuclear_local_curvature_no_leakage_implementation.py`,
   leave-one-out neighbor cache, per-fold rebuild, all six
   TASK-0352 minimum controls, paired hypothesis +
   experiment proposals, schema-valid AGENT-RUN-NNNN bundle,
   `docs/reviews/nuclear-local-curvature-no-leakage-implementation.md`.
   No PRED entry. No reveal. Difficulty: high.
2. **R2 — F2 label refactor for high-error cluster.** Scope:
   rebuild cluster labels from Z/N/A-only features, rerun the
   TASK-0343 control gate, write
   `docs/reviews/nuclear-high-error-cluster-label-refactor.md`
   recording whether F2 re-enters predictive-eligible scope. No
   new candidate fits. Difficulty: medium.
3. **R3 — Reveal-readiness gap pass on the existing
   PRED-0063..PRED-0068 mini-wave.** Scope: re-confirm the
   TASK-0303 source preflight against any new source candidates
   surfaced since TASK-0307, and produce a one-page
   `docs/reviews/nuclear-shell-axis-mini-wave-reveal-readiness-update.md`
   declaring whether `TASK-0305` can move from blocked to
   READY. Difficulty: medium.

The synthesis explicitly avoids opening a fourth recommendation.
Three independent lanes are the upper bound for the next phase of
Nuclear work; widening the queue risks recreating the broad audit
loop this synthesis exists to close.

## What This Synthesis Did Not Do

- It did not promote any candidate to a claim, knowledge entry,
  RESULT-*, or canonical hypothesis.
- It did not edit any prior agent-run verdict.
- It did not relax the TASK-0303 source preflight, the TASK-0352
  freeze protocol, the TASK-0368 no-leakage contract, or the
  prediction-reveal protocol.
- It did not authorise any live data fetch, any reveal scoring,
  any prediction-registry entry, or any canonical artifact write.
- It did not open any canonical task. R1 / R2 / R3 are
  recommendations only.

## Limitations

- Each lane's verdict is the one recorded in its committed
  review. This synthesis does not re-run the lanes and does not
  recompute the deltas.
- The +0.544 MeV survival margin for `LOCAL-CURVATURE-001` is the
  primary-subset value on `full_known`; per-subset majority is
  required for the TASK-0352 freeze protocol and was satisfied at
  TASK-0351 time. R1 must re-confirm both numbers under the
  leave-one-out cache before any PRED entry is considered.
- Bucket assignments use committed per-lane control posture. New
  controls beyond those committed at the per-lane review are not
  considered here; if R1 surfaces a new control that closes the
  signal under leave-one-out, the F1 promotion path itself blocks
  the PRED entry.
- The synthesis does not score or recommend any specific
  shell-axis PRED expansion; R3 is a readiness check, not a
  registration task.
