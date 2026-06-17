# Nuclear Prediction Reveal-Checklist Reference Repair

- Task: `TASK-0714`
- Registry: `prediction_registry/nuclear_masses`
- Scope: mechanical reference-link hygiene only
- Verdict: `CHECKLIST_REFERENCES_REPAIRED_REVEAL_STILL_SOURCE_GATED`

## Purpose

The `TASK-0641` reveal-readiness matrix
(`docs/reviews/nuclear-prediction-reveal-readiness-matrix.md`) found many
committed nuclear `PRED-*` entries missing references to the existing approved
reveal protocol and source-readiness checklist documents. This task repairs
those reference links where the protocol already exists. It scores no
prediction, fetches no external data, and changes no prediction value, target
set, frozen model state, or reveal condition.

## Canonical documents (verified present before repair)

- `docs/nuclear-prediction-reveal-protocol.md` — EXISTS
- `docs/nuclear-reveal-source-readiness-checklist.md` — EXISTS

Because both approved documents exist, the missing-reference blockers are
mechanical hygiene, not a missing-protocol blocker. No promotion language is
drafted.

## Detection basis

`scripts/nuclear_prediction_registry_report.py` raises the two reference
blockers purely from `source_state.holdout_protocol_references`:

- `REVEAL_PROTOCOL_REFERENCE_MISSING` when `docs/nuclear-prediction-reveal-protocol.md`
  is absent from that list;
- `SOURCE_READINESS_CHECKLIST_REFERENCE_MISSING` when
  `docs/nuclear-reveal-source-readiness-checklist.md` is absent.

The repair therefore adds the missing path(s) to that list only.

## What changed

Reference paths were appended to `source_state.holdout_protocol_references` in
the affected entries, preserving existing references and each file's existing
list indentation. No other field was touched (`git diff` over the registry is
purely additive: `+96 / -0` across the prediction files).

| Group | Entries | Count | Reference(s) added |
| --- | --- | ---: | --- |
| Missing both | PRED-0001..0030, 0037, 0038, 0041..0050 | 42 | reveal-protocol **and** source-readiness checklist |
| Missing checklist only | PRED-0051..0062 | 12 | source-readiness checklist |
| Already complete | PRED-0063..0068 | 6 | none (unchanged) |

Total entries repaired: **54**.

The deterministic `registry_summary.yaml` was regenerated from the repaired
registry (`-100 / +0`; only `*_REFERENCE_MISSING` blocker rows removed).

## Before / after (generator blocker counts)

| Blocker | Before | After |
| --- | ---: | ---: |
| `REVEAL_PROTOCOL_REFERENCE_MISSING` | 42 | 0 |
| `SOURCE_READINESS_CHECKLIST_REFERENCE_MISSING` | 54 | 0 |
| `SOURCE_PREFLIGHT_REQUIRED` | 60 | 60 |
| `NO_PEEK_REVIEW_REQUIRED` | 60 | 60 |
| `MAINTAINER_APPROVAL_REQUIRED` | 60 | 60 |

The three scientific reveal gates are intentionally unchanged: all 60 entries
remain `AWAITING_SOURCE_PREFLIGHT` and `0` are reveal-ready. This task removes
only the mechanical checklist-reference blockers.

The `TASK-0641` matrix document is a point-in-time snapshot and is left as-is;
its two `*_REFERENCE_MISSING` counts are superseded by the regenerated
`registry_summary.yaml`.

## Boundaries honored

- No prediction target sets, quantities, frozen values, model metadata, or
  reveal conditions changed.
- No live nuclear data fetched, no reveal scored, no claim promoted.
- Edits are metadata-only reference additions to existing approved documents.

## Output routing

- Task verdict: `CHECKLIST_REFERENCES_REPAIRED_REVEAL_STILL_SOURCE_GATED`.
- Canonical destination: `docs/reviews/nuclear-prediction-reveal-checklist-reference-repair.md`.
- Review tier: `none` (registry reference hygiene; not a `RESULT-*` or new `PRED-*`).
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: none.
- Prediction impact: frozen values, targets, and reveal conditions unchanged;
  only `holdout_protocol_references` reference lists extended.
- Limitations / blockers: source preflight, no-peek review, and maintainer
  approval remain required before any reveal scoring.
