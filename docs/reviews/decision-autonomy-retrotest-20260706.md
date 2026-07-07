# Decision Autonomy Retrotest — Decision Day #2 Replayed (2026-07-06)

- Task: TASK-0952. Policy under test: `policy/decision-autonomy.yaml` (v0).
- Method: the eight maintainer decisions of Decision Day #2
  (`docs/reviews/maintainer-decision-day-2026-07-06.md`) are replayed
  against the matrix as a fixed calibration set. The same set is enforced in
  `tests/test_decision_autonomy_policy.py::test_retro_calibration_decision_day_2`.
- Non-claims: retro classification only; no decision is re-made, applied,
  or altered by this note.

## Retro-classification

| Decision | decision_type | Matrix class | Verdict |
| --- | --- | --- | --- |
| D2-1 FRB C1-pair conditional GO (schema gate only) | `source_readiness_go` | class_1_lazy_consensus | routing: quorum-routable |
| D2-2 ThermoML 80-row rights route | `data_rights_decision` | class_2_maintainer_only | correctly human-only |
| D2-3 Atomic KEEP_MONITOR_ONLY ratification | `campaign_hold_monitor` | class_1_lazy_consensus | routing: quorum-routable |
| D2-4 Muon g-2 park (stress-test memory) | `claim_role_classification` | class_1_lazy_consensus | routing: quorum-routable |
| D2-5 TASK-0305 source-manifest GO | `source_readiness_go` | class_1_lazy_consensus | routing: quorum-routable |
| D2-6 Board hygiene batch | `board_hygiene` | class_0_auto | hygiene: policy-auto |
| D2-7 Stale proposal adjudication | `proposal_adjudication` | class_0_auto | hygiene: policy-auto |
| D2-8 Next external artifact (software DOI + capsule) | `external_publication` | class_2_maintainer_only | correctly human-only |

## Expected-outcome verification (per the GO mandate)

- Routing/hygiene decisions -> AUTO or DUAL_AGENT: **6 of 8** (2x class_0,
  4x class_1). Confirmed.
- DOI / legal / public-exposure decisions -> MAINTAINER_ONLY: **2 of 2**
  (D2-2 rights, D2-8 external publication). Confirmed. (The related
  prediction-freeze decision class is exercised by the standing matrix
  entry `prediction_freeze -> class_2`, not by this set: D2 contained no
  new freeze decision — R2 explicitly forbids repeating one without a new
  maintainer decision.)
- Reading consistent with the empirical session: the maintainer accepted
  8/8 recommendations, and the 6 quorum-routable ones are exactly where his
  role was ratification rather than judgment. Acceptance-rate evidence
  justifies this dry run — not full autonomous governance.

## Calibration verdict

`RETROTEST_PASS` — zero misclassifications against the maintainer's actual
decisions; the non-reducible list captured both human-mandatory cases.
Phase 2 (auto-apply class_0) remains gated on the live dry-run criteria in
`docs/reviews/decision-autonomy-dry-run-plan.md`.
