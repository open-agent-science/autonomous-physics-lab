# Exoplanet compact/sub-Neptune residual hypothesis pilot

- Agent run: `AGENT-RUN-0036`
- Task: `TASK-0390`
- Snapshot: `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
- Verdict: **SANDBOX_PASS**

## Scope

This review packages a sandbox-only compact/sub-Neptune residual hypothesis pilot. It uses only committed PSCompPars snapshot rows, keeps the Chen-Kipping baseline frozen, and keeps true-mass rows separate from diagnostic minimum-mass rows.

No live fetch, baseline refit, canonical result, prediction-registry entry, claim, knowledge edit, composition inference, habitability wording, biosignature wording, target-priority ranking, or universal planet-law wording is authorized by this review.

## Controls

- `per_class_median`: shifts CK17 by the eligible-set median residual within each CK17 mass class.
- `shuffled_label`: deterministic shuffled-label control preserving candidate row count.
- `matched_size_neighbor`: sample-size matched nearest-mass same-class control.

## Executed Hypotheses

| hypothesis | label | count | RMSE | adverse control | delta vs eligible | delta vs adverse control | outcome |
| --- | --- | ---: | ---: | --- | ---: | ---: | --- |
| CSN-001 | compact_radius_lt1p5Re | 92 | 0.263350 | per_class_median | 0.105180 | 0.025680 | residual_stress_above_eligible_and_controls |
| CSN-002 | sub_neptune_radius_1p5_4Re | 340 | 0.204175 | per_class_median | 0.046004 | 0.016128 | residual_stress_above_eligible_only |
| CSN-003 | compact_or_sub_neptune_radius_lt4Re | 432 | 0.218126 | per_class_median | 0.059956 | 0.018476 | residual_stress_above_eligible_only |

## Generated But Not Executed

- `CSN-004` (`neptunian_sub_neptune_overlap`): generated only; candidate count 328, RMSE 0.165159.
- `CSN-005` (`compact_subneptune_tight_radius_uncertainty`): generated only; candidate count 288, RMSE 0.170218.
- `CSN-006` (`compact_subneptune_cool_host`): generated only; candidate count 219, RMSE 0.233687.

## Negative And Null Results

Generated-only hypotheses were not promoted beyond candidate stats. Executed hypotheses that do not clear both eligible and adverse-control margins remain visible in `agent_runs/AGENT-RUN-0036/metrics.json`.

## Output Routing

- Task verdict: `SANDBOX_PASS`.
- Canonical destination: sandbox-only `agent_runs/AGENT-RUN-0036/` and this review note.
- Review tier: none.
- Gate A: not attempted.
- Gate B: not attempted.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Publication blocker: task scope authorizes sandbox evidence only.
