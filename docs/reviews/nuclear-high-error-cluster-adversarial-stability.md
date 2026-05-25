# Nuclear high-error cluster adversarial stability review

**Task:** `TASK-0367`  
**Agent run:** `AGENT-RUN-0033`  
**Predecessor:** `TASK-0343` / `AGENT-RUN-0030` (high-error cluster hypothesis lane)  
**Lane verdict:** `INCONCLUSIVE`

## Scope

This review records the outcome of attacking the AGENT-RUN-0030 high-error cluster signal with three stronger adversarial controls and two stability diagnostics. It does not promote any claim, does not register a prediction-registry entry, does not rewrite the predecessor lane metrics, and does not authorize a reveal.

## New Adversarial Controls

- **HIGHCLUSTER-ADV-001** — random-permutation cluster-label control. Uses a deterministic random permutation (seed 367) of the exclusive cluster labels across rows. Stronger than the predecessor cyclic-shift control because a random permutation cannot preserve any residual locality structure that a cyclic shift can keep accidentally.
- **HIGHCLUSTER-ADV-002** — pure local-density smoother. Uses the raw per-row local-density count without high-error gating. Competes directly with HIGHCLUSTER-003's density-gated feature; if HIGHCLUSTER-003 is dominated by smooth density structure, this control captures it without the cluster membership label.
- **HIGHCLUSTER-ADV-003** — near-null deterministic jitter. Uses a per-row Normal(0, 0.001 MeV) seeded with 3670. Acts as the null floor: a candidate that does not beat this control by orders of magnitude is consistent with noise.

## Stability Diagnostics

- **High-error threshold perturbation.** Re-fits each candidate at baseline-residual percentiles 65, 70, 75, 80 and reports the full-known Δ MAE and fitted coefficient at each threshold. A genuine cluster signal should improve the surface at every nearby threshold and should not flip the coefficient sign.
- **Leave-one-out coefficient stability.** Re-fits each candidate on every 10-of-11 subset of the NMD-0002 training slice and reports the coefficient spread, sign-flip count, and full-known Δ MAE range. A LOO-stable candidate has no sign flips and a coefficient range under `1.00`.

## Headline Result

- **Lane verdict:** `INCONCLUSIVE`.
- **Best primary candidate:** `HIGHCLUSTER-001` with Δ MAE -0.629378 MeV.
- **Primary survival margin:** 0.25 MeV on the `full_known` subset.

## Per-Candidate Verdict

| Candidate | Survives primary? | Subset win rate | Threshold stable? | LOO stable? | High-error-only overfit? | Verdict |
| --- | --- | ---: | --- | --- | --- | --- |
| `HIGHCLUSTER-001` | yes | 0.806 | yes | **no** | no | `INCONCLUSIVE` |
| `HIGHCLUSTER-002` | **no** | 0.000 | **no** | yes | no | `FALSIFIED` |
| `HIGHCLUSTER-003` | yes | 0.806 | yes | **no** | no | `INCONCLUSIVE` |

## Candidate vs Strongest Control (Primary Subset)

| Candidate | Strongest control on full_known | Candidate Δ MAE | Control Δ MAE | Margin (control − candidate) | Survives ≥ 0.25 MeV? |
| --- | --- | ---: | ---: | ---: | --- |
| `HIGHCLUSTER-001` | `HIGHCLUSTER-CONTROL-003` | -0.629378 | -0.022701 | +0.606677 | yes |
| `HIGHCLUSTER-002` | `HIGHCLUSTER-CONTROL-003` | +0.000000 | -0.022701 | -0.022701 | **no** |
| `HIGHCLUSTER-003` | `HIGHCLUSTER-CONTROL-003` | -0.354350 | -0.022701 | +0.331648 | yes |

## Decision

The lane is mixed: at least one candidate clears one adversarial gate but not all of them. The signal is preserved as sandbox diagnostic evidence and does not authorize a predictive lane. Additional controls or a richer training slice may be needed before the verdict is revisited.

## Limitations

- High-error membership and cluster labels still come from committed retrospective residuals; this lane sharpens controls but remains a diagnostic rather than a blind prediction.
- Coefficients are fit on the 11-row NMD-0002 training slice, so the leave-one-out stability check is itself a small-sample diagnostic.
- The three new adversarial controls do not exhaust the space of possible attacks (e.g. stronger label shuffles weighted by chain structure, richer non-linear smoothers, or feature-set ablations).
- Threshold perturbation rebuilds the ClusterIndex at each percentile, so cluster-membership composition shifts between thresholds; the diagnostic measures coefficient and delta stability rather than a fixed cluster definition.
- No live source fetch, reveal scoring, registry write, claim update, or canonical result write is authorized.

## What This Review Did Not Do

- It did not fetch live data, run reveal scoring, register a prediction-registry entry, edit a PRED-*.yaml, or promote a claim.
- It did not rewrite the predecessor AGENT-RUN-0030 metrics or verdict.
- It did not modify canonical RESULT-* artifacts.

## Verdict

`INCONCLUSIVE`
