# Nuclear local-curvature adversarial controls review

**Task:** `TASK-0351`  
**Agent run:** `AGENT-RUN-0031`  
**Predecessor:** `TASK-0339` / `AGENT-RUN-0026` (TASK-0339 sandbox local-curvature lane)
**Freeze protocol:** `TASK-0352` (no-leakage freeze contract)

## Scope

This review records the outcome of attacking the TASK-0339 local-curvature sandbox signal with three new adversarial controls in addition to the two controls the predecessor lane already carried. It does not promote any claim, does not register a prediction entry, and does not authorize a reveal.

## Adversarial Controls Added

- **LOCAL-CONTROL-003** — neighbor-availability leakage control. Uses only the single closest same-Z neighbor (by `|ΔN|`). A genuine local-curvature signal should still beat the baseline. A signal that depends on neighbor density rather than neighbor content will weaken under this control.
- **LOCAL-CONTROL-004** — chain-label shuffle control. Computes the isotope-neighbor mean using a deterministically permuted Z label (each Z mapped to a Z roughly half the observed-Z list away). If the signal is driven by real chain-local curvature, this control should not beat the baseline at all.
- **LOCAL-CONTROL-005** — chain-blind smooth local-regression control. Fits a 1-D linear regression over the same A-window the LOCAL-CONTROL-002 smoother uses and predicts at the target row's A. If the candidates beat this smoother by a meaningful margin, they carry chain-specific information beyond generic smoothness.

## Headline Result

- **Lane verdict:** `PARTIALLY_VALID`.
- **Primary survival margin (MeV):** 0.25 on the `full_known` subset.
- **Best primary candidate (predecessor metric):** `LOCAL-CURVATURE-001` with delta MAE -2.286136 MeV.

## Candidate vs Strongest Control (Primary Subset)

| Candidate | Strongest control on `full_known` | Margin (control − candidate) | Survives? |
| --- | --- | ---: | ---: |
| `LOCAL-CURVATURE-001` | `LOCAL-CONTROL-005` | +0.544296 | yes |
| `LOCAL-CURVATURE-002` | `LOCAL-CONTROL-005` | -0.179776 | **no** |
| `LOCAL-CURVATURE-003` | `LOCAL-CONTROL-005` | -1.766016 | **no** |

## Decision Per TASK-0352 Freeze Protocol

At least one candidate beats the strongest control on the primary subset by the required margin AND wins more than half of the per-subset comparisons. The signal is preserved as sandbox evidence that survived adversarial controls.

A future predictive implementation task is allowed only after the TASK-0352 no-leakage freeze protocol's six minimum controls (self-exclusion ablation, chain-shuffled, smooth-window, near-null, per-fold cache audit, source-status separation) are also satisfied. This review does not by itself unblock the predictive lane.

## Limitations

- Features still use committed full-known neighbor residual context. The headline numbers remain retrospective diagnostics, not blind predictions.
- The survival margin (0.25 MeV) is chosen conservatively from existing control magnitudes; tightening it is allowed in a future task but must be done before evaluating the next candidate.
- The three new controls are not exhaustive. Stronger label shuffles, richer smoothers, and explicit leave-one-out feature shapes remain available for future adversarial work.

## What This Review Did Not Do

- It did not fetch live data, run reveal scoring, register a prediction-registry entry, edit a `PRED-*.yaml`, or promote a claim.
- It did not rewrite the predecessor AGENT-RUN-0026 metrics or verdict.
- It did not relax the TASK-0352 no-leakage freeze protocol.

## Verdict

`PARTIALLY_VALID`
