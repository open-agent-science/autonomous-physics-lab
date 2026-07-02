# Legacy Claim Novelty Audit And Calibration Migration Proposal

- Task: `TASK-0862`
- Scope: legacy `CLAIM-*` ledger hygiene after the novelty classification gate
  was adopted in `docs/claim-promotion-policy.md`.
- Verdict: `MIGRATION_PROPOSAL_READY_MAINTAINER_DECISION_REQUIRED`

## Boundary

This audit does not edit any claim, result, prediction, or knowledge artifact.
It separates historical support/review state from proposed public role. A claim
can remain historically `PARTIALLY_SUPPORTED` and `MAINTAINER_REVIEWED` while
also being proposed for a non-active calibration-memory role.

The immediate public-risk surface is `CLAIM-0001` and `CLAIM-0009`: both are
honestly scoped and useful platform calibration memories, but they should not be
presented as active scientific novelty claims.

## Proposed Vocabulary

Keep existing claim status vocabulary as the support axis:

- `support_status`: existing `status` field (`DRAFT`, `PARTIALLY_SUPPORTED`,
  `SUPPORTED`, `REFUTED`, `SUPERSEDED`).
- `review_tier`: existing review axis (`LEGACY_UNTIERED`, `AGENT_PUBLISHED`,
  `AGENT_VALIDATED`, `MAINTAINER_REVIEWED`, `EXTERNAL_REPLICATED`).

Add a separate public-role axis for future maintainer review:

- `novelty_class`: one of the current policy classes
  (`frontier_novel`, `reusable_dataset`, `valuable_negative`,
  `calibration_known_physics`) plus proposed advisory tags where needed.
- `claim_role`: proposed public role. Suggested values:
  `active_scientific_claim`, `calibration_memory`, `methodology_quality_floor`,
  `negative_control_memory`, `scope_review_hold`.
- `active_scientific_claim`: boolean public-facing recommendation. `false`
  means the artifact may remain useful and reviewed, but should not be surfaced
  as an active novelty claim.

This model avoids using `DRAFT` as a retirement bucket and avoids forcing
`SUPERSEDED` when nothing scientifically superseded the evidence.

## Per-Claim Ledger

| Claim | Current status | Review tier | Novelty class | Proposed claim role | Active scientific claim? | Evidence basis | Next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CLAIM-0001` | `PARTIALLY_SUPPORTED` | `MAINTAINER_REVIEWED` | `calibration_known_physics` | `calibration_memory` | no | Ideal-pendulum amplitude dependence and approximation accuracy are known-physics benchmark/calibration evidence; `RESULT-0001`, `RESULT-0003`, and `RESULT-0013` remain useful range-limited evidence. | Maintainer decision: keep support/review history, add a forward role/disposition marking it calibration memory and not an active novelty claim. |
| `CLAIM-0002` | `DRAFT` | `LEGACY_UNTIERED` | `calibration_known_physics` | `calibration_memory` | no | Linear damped oscillator regime structure is textbook known physics; `RESULT-0002` is useful deterministic platform verification. | Keep draft; if surfaced publicly, route as calibration/result memory rather than a claim promotion. |
| `CLAIM-0003` | `DRAFT` | `LEGACY_UNTIERED` | `calibration_known_physics` | `calibration_memory` | no | Charged-lepton Koide reproduction is a known numerical relation reproduction on a stored dataset, not an explanatory or novel physics result. | Keep draft; avoid promotion without a separate novelty/scope decision. |
| `CLAIM-0004` | `DRAFT` | `LEGACY_UNTIERED` | `calibration_known_physics` | `calibration_memory` | no | Historical tau holdout under exact Koide assumption is benchmark memory for a known relation, not a mechanism or new discovery. | Keep draft; maintain non-explanatory wording. |
| `CLAIM-0005` | `DRAFT` | `LEGACY_UNTIERED` | proposed `methodology_quality_floor` tag under `reusable_dataset`/tooling evidence | `methodology_quality_floor` | no for nature claim | Validator agreement on DA-CHALLENGE-001 is tool-quality evidence for APL, not a claim about nature; externally reusable mainly as a challenge-set benchmark. | Keep draft; consider a future non-claim tool-quality or dataset record if needed. |
| `CLAIM-0006` | `DRAFT` | `LEGACY_UNTIERED` | `valuable_negative` | `negative_control_memory` | potential negative claim after review | Quark-sector Koide follow-up fails in scoped PDG 2024 mixed-scale benchmark; negative result prevents overgeneralization from charged leptons. | Keep draft; candidate for separate maintainer Gate C negative-memory review. |
| `CLAIM-0007` | `DRAFT` | `LEGACY_UNTIERED` | `valuable_negative` | `negative_control_memory` | potential negative claim after review | Fixed standard Koide target fails cross-family survival in the falsifier MVP under encoded assumptions. | Keep draft; candidate for separate maintainer Gate C negative-memory review. |
| `CLAIM-0008` | `DRAFT` | `LEGACY_UNTIERED` | proposed `scope_unclear_high_risk` advisory tag | `scope_review_hold` | no | Muon g-2 formula-search stress-test hit has high overclaim risk: multiple-testing, target-choice, and physical-motivation limitations remain central. | Keep draft; do not promote; run a separate scope/overclaim review before any public claim wording. |
| `CLAIM-0009` | `PARTIALLY_SUPPORTED` | `MAINTAINER_REVIEWED` | `calibration_known_physics` | `calibration_memory` | no | Conservative quartic anharmonic oscillator period benchmark is established physics/calibration memory; `RESULT-0016` is valuable Gate-B-validated platform evidence but not active novelty. | Maintainer decision: keep support/review history, add a forward role/disposition marking it calibration memory and not an active novelty claim. |
| `CLAIM-0010` | `DRAFT` | `LEGACY_UNTIERED` | `reusable_dataset` with `scope_review_hold` caution | `scope_review_hold` | no for now | Nuclear mass baseline residual benchmark is campaign infrastructure and residual-surface memory; public novelty depends on later holdout/reveal semantics. | Keep draft; review dataset/holdout semantics before any claim path. |

## Proposed Migration For Promoted Calibration Claims

For `CLAIM-0001` and `CLAIM-0009`, do not revert
`PARTIALLY_SUPPORTED -> DRAFT`. That would mis-state the historical Gate C
review. Also do not force `SUPERSEDED`; no newer claim replaces the evidence.

Recommended future maintainer-owned disposition:

```yaml
support_status: PARTIALLY_SUPPORTED
review_tier: MAINTAINER_REVIEWED
novelty_class: calibration_known_physics
claim_role: calibration_memory
active_scientific_claim: false
public_disposition: >
  Valid platform-calibration / benchmark memory, preserved with its evidence
  links, but not surfaced as an active scientific novelty claim.
```

This should be recorded as a forward-dated disposition. Historical review notes
should remain unchanged.

## Special Flags

- `CLAIM-0008`: keep `DRAFT`; highest overclaim-risk claim surface. It needs a
  separate scope review before any promotion discussion.
- `CLAIM-0006` and `CLAIM-0007`: valuable negative-memory candidates, but
  still maintainer Gate C work. They should not be promoted in this audit.
- `CLAIM-0005`: proposes a `methodology_quality_floor` advisory tag because
  tool-quality evidence does not fit cleanly as either a nature claim or a
  novelty claim.

## Output Routing

- Canonical destination: `docs/reviews/legacy-claim-novelty-audit-and-calibration-migration.md`.
- Review tier: none; this is a review/proposal note, not a canonical
  `RESULT-*`, `CLAIM-*`, `PRED-*`, or `KNOW-*` artifact.
- Gate A: not applicable; no result publication.
- Gate B: not applicable; no independent result replay.
- Gate C: pending maintainer decision for any future claim-role or claim-status
  mutation.
- Claim impact: no claim files changed; proposed role migration only.
- Result impact: none.
- Prediction impact: none.
- Knowledge impact: none.
- Publication blocker: maintainer decision needed before adopting
  `calibration_memory`, `methodology_quality_floor`, or
  `scope_unclear_high_risk` as formal ledger vocabulary.

## Final Recommendation

Adopt the split-axis model in a later maintainer-owned migration PR. The urgent
public-facing action is to classify `CLAIM-0001` and `CLAIM-0009` as
`calibration_memory` with `active_scientific_claim: false`, while preserving
their support and review history.

## Maintainer Decision (2026-07-02)

Decision: **adopt the split-axis disposition** — CLAIM-0001/0009 gain novelty_class=calibration_known_physics, claim_role=calibration_memory, active_scientific_claim=false; support/review statuses preserved (execution: `TASK-0927`).
Recorded in [maintainer-decision-day-2026-07-02.md](./maintainer-decision-day-2026-07-02.md).
