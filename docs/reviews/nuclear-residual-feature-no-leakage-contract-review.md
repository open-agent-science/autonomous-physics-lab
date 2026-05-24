# Nuclear Residual-Feature No-Leakage Contract Review

**Task:** TASK-0368
**Status:** review (policy-only; no agent run; no model fits; no claims; no PRED entries)
**Campaign:** Nuclear Mass Surface

## Inputs reviewed

- `docs/nuclear-residual-feature-no-leakage-contract.md`
  (this task's new contract)
- `docs/nuclear-local-curvature-no-leakage-freeze-protocol.md`
  (TASK-0352 freeze protocol)
- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/reviews/nuclear-local-curvature-hypothesis-lane.md`
  (TASK-0339 / AGENT-RUN-0026)
- `docs/reviews/nuclear-local-curvature-adversarial-controls.md`
  (TASK-0351 / AGENT-RUN-0031)
- `docs/reviews/nuclear-high-error-cluster-hypothesis-lane.md`
  (TASK-0343 / AGENT-RUN-0030)
- `prediction_registry/nuclear_masses/README.md`

## Scope

This review records the rationale, the design decisions, and the
explicit non-goals behind the new
`docs/nuclear-residual-feature-no-leakage-contract.md`. It does
not run any candidate, does not score any reveal, does not edit
any frozen prediction-registry entry, does not change the
TASK-0352 freeze protocol, and does not change the
TASK-0303 shell-axis source preflight.

## Why a Cross-Family Contract Now

Five Nuclear residual lanes have surfaced in recent sandbox work:

- **F1 local curvature** — TASK-0339 / AGENT-RUN-0026 (large
  retrospective signal, `INCONCLUSIVE`); TASK-0351 /
  AGENT-RUN-0031 (`LOCAL-CURVATURE-001` survived three
  adversarial controls, `-002` and `-003` falsified).
- **F2 high-error cluster** — TASK-0343 / AGENT-RUN-0030
  (`HIGHCLUSTER-001` and `-003` partially valid; cluster labels
  derived from baseline residuals).
- **F3 shell axis** — already governed by TASK-0303 source
  preflight and the frozen `PRED-0063`..`PRED-0068` mini-wave.
- **F4 source status (measured vs extrapolated)** —
  TASK-0341 / AGENT-RUN-0028 retrospective diagnostic;
  `INCONCLUSIVE`.
- **F5 uncertainty-weighted residual** — TASK-0342 lane
  recently landed; uncertainty fields are committed but the
  weighting-scheme freeze is the missing piece.

Each lane already has its own per-task review. None of them are
authorised to enter the prediction registry until a no-leakage
predictive implementation task wraps them in the appropriate
control surface. The freeze protocol (TASK-0352) defines the
per-feature mechanics for F1, but does not classify which families
are predictive-eligible, which are diagnostic-only, and which are
blocked. Doing that classification now prevents the campaign from
opening five parallel "could this go to a PRED entry?" reviews
later.

## Design Decisions

### D1. Classification axes

Each family is named with an eligibility class
(`predictive_eligible` / `diagnostic_only` / `blocked`), a leakage
profile, and a numbered promotion path. The numbered REQ ids
(e.g. `F1-REQ-LOO-WINDOW`, `F5-REQ-WEIGHTING-FROZEN`) are
deliberately stable so a future predictive implementation task
can reference them as preflight checks without re-deriving the
list.

### D2. F1 admissible candidate is named explicitly

Only `LOCAL-CURVATURE-001` is admissible as a future F1
implementation target. `LOCAL-CURVATURE-002` and `-003` were
falsified by TASK-0351 and are preserved as sandbox memory
only. Naming this explicitly prevents accidental "let's try
`-002` with the no-leakage cache" attempts that would re-introduce
falsified signal under a new label.

### D3. F2 is held diagnostic-only until cluster labels are
residual-free

The TASK-0343 high-error cluster lane uses cluster labels derived
from baseline residuals (the cluster boundary is a residual
percentile). A predictive use must label clusters from `Z`, `N`,
`A`, magic-number proximity, and committed uncertainties only.
The contract requires the TASK-0343 control gate to be rerun
against the residual-free label before F2 re-enters predictive
scope.

### D4. F4 is permanently blocked from predictive use

Source-status is a provenance label, not a feature of nuclear
structure. A predictor that consumes it would learn to separate
training-slice rows from holdout rows. This is documented as a
hard line, not a movable threshold; the field stays a
provenance-diagnostic field forever.

### D5. F5 requires the weighting scheme to be frozen in the
experiment proposal

Uncertainty-weighted residual features are admissible only when
the weights are derived from committed measurement uncertainties
**and** the weighting scheme is frozen in the
`experiment_proposals/nuclear-mass/EXP-PROPOSAL-XXXX.yaml`
**before** any candidate is fit. This catches the failure mode
where an empirical "high-error percentile flag" is hand-tuned to
favor the candidate after seeing residuals.

### D6. Minimal artifact checklist is a checklist, not a schema

The checklist enumerates eight artifacts every later predictive
implementation task must deliver. It deliberately mirrors the
shape of the existing autonomous_research_pilot bundle
(`agent_run.yaml`, `metrics.json`, `report.md`,
`limitations.md`, `preflight.md`, `review_summary.md`) plus the
contract-specific items (per-fold cache commit SHA, paired
hypothesis + experiment proposals, control suite with the F-family
specific minimum controls). It does not add a new JSON schema,
because the existing schemas already enforce the structural
shape; what was missing was the family-aware control-and-input
checklist.

## Non-Goals

This contract does not:

- add any `PRED-XXXX.yaml` entry;
- score any reveal;
- run a new sandbox lane;
- promote any candidate to a claim, knowledge entry, RESULT-*, or
  canonical hypothesis;
- relax the TASK-0303 shell-axis source preflight;
- relax the TASK-0352 freeze protocol;
- relax the `docs/nuclear-prediction-reveal-protocol.md`;
- create canonical follow-up tasks. The R-F1 / R-F2 / R-F5
  recommendations in the contract are advisory; each requires a
  separate maintainer-approved task before any execution.

## Verdict

**`POLICY_LOCKED`** — the contract is the cross-family eligibility
gate for any future Nuclear no-leakage predictive implementation.
Per-family follow-up tasks (R-F1, R-F2, R-F5) are recommendations
only and must be assigned through the canonical task protocol or
the task-proposal protocol.

## Limitations

- The classification is based on the residual lanes that have
  surfaced so far. New families (parity-pair residuals,
  deformation-proxy residuals, asymmetric refinement candidates)
  require their own classification before any predictive
  implementation.
- This is a policy document. It does not lint, validate, or block
  a PR by itself; the per-task preflight checks in any future
  predictive implementation task are the enforcement surface.
- The minimum survival margin (0.25 MeV) and the six-control
  minimum for F1 are inherited from TASK-0352; this contract does
  not change those numbers.
- The contract does not authorise any live data fetch or any
  canonical artifact write.
