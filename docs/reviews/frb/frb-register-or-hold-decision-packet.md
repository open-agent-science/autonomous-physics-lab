# FRB Register-Or-Hold Decision Packet

- Task: `TASK-1014`
- Domain: radio transients / FRB pre-T repeater-propensity registration
- Packet verdict: `READY_FOR_MAINTAINER_DECISION`
- Decision surface: Class 2 maintainer-only prediction freeze for `TASK-0996`

## Boundary

This packet does not register `prediction_registry/radio_transients/PRED-0001.yaml`,
create a tag or release, inspect reveal labels, fetch a later catalog, score
outcomes, change any target, score, rank, or scoring-rule field, or create a
`RESULT`, `PRED`, `CLAIM`, or `KNOW` artifact.

The decision stub remains unapproved: `decision_record.status: dry_run_only`.
`TASK-0996` remains blocked unless a maintainer explicitly approves a Class 2
prediction-freeze decision using this packet or a follow-up packet.

## Current Hash Checklist

Computed from the repaired main-branch state on 2026-07-10.

| Artifact | Bytes | SHA-256 / digest |
| --- | ---: | --- |
| Registration pack, `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` | 190,860 | `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5` |
| Decision stub, `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml` | 2,181 | `2554cc15eda2e12ec08dcc5ba44e240d135fd915c8f8ebbdb67c7c2c6ea725b5` |
| Generated staged PRED payload, `staged_payloads/prediction_registry/radio_transients/PRED-0001.draft.yaml` | 170,764 | `ca5f0f77bb17c19dc730aa194ba7cd5cdffdef95b515057d7288405338007b8b` |
| Staged `draft_entry_sha256` | n/a | `23c2a685fef0b141d3605fb9a89e38f5409cc78a6b5b1e0efd841a9d8cd67014` |
| Target payload, `draft_entry_targets_sha256` | 479 targets | `b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf` |
| Anchor dry-run capsule, `frb-pret-prediction-freeze-anchor-dry-run-v0.1.0.zip` | 612,208 | `6657398e88e080862d9195d4a18f891a904716df2901654310b3dfc27d3a8165` |

Source freeze pins carried by the pack:

| Source artifact | SHA-256 / digest |
| --- | --- |
| Frozen model surface | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` |
| Model-selection contract | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` |
| Pre-T input surface | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` |
| Per-source score payload | `00404c62efb1edc300f008f53961e691cb1c06208ef5a032ff83b0bf8ddb60d7` |
| Feature-table payload | `3e564bc58452b34db133b72d1177bd99eb7fc8ac76036641edb9aa513a65d139` |

## Schema And Placeholder Gate

The staged FRB payload routes to the generic prediction schema:
`infer_kind_from_path("prediction_registry/radio_transients/PRED-0001.yaml")`
returns `prediction`.

Dry-run validation result:

- with maintainer placeholders substituted by an ISO `Z` timestamp and a
  40-hex commit, the staged payload has zero schema errors;
- with the original placeholders intact, the generic prediction schema rejects
  `registered_at_utc` and `source_state/git_commit`;
- `tests/test_frb_pred_registration_pack.py`,
  `tests/test_frb_anchor_capsule_dry_run.py`, and the targeted registry
  placeholder/routing tests pass.

This satisfies the repaired R1/R2 route without writing a registry artifact.

## No-Label Registration Boundary

The frozen split epoch is `T=2019-07-02` (`MJD 58666.0`). The registered payload
would contain 479 source-level point scores and ranks only.

The fixed scoring rule is:

```text
score_pre_t = log1p(E_upper_hours + E_lower_hours)
E_hours = 4 * exposure_count / 3600
```

The label-free feature boundary allows only pre-T source identity and exposure
score fields: `source_id`, `E_upper_hours`, `E_lower_hours`, and `score_pre_t`.
The pack excludes repeat labels, `repeater_name`, Catalog 2 full-window
exposure, morphology columns, post-T source associations, and later reveal
fields. The target set, scores, ranks, and scoring rule are frozen by the
target payload digest above.

## Reveal-Source Contract Summary

Any future reveal remains a separate maintainer-reviewed task. It must freeze a
manifest before reading labels and use only one of these source classes:

1. an official CHIME/FRB catalog snapshot;
2. an official CHIME/FRB repeat-source or source-association table;
3. a maintainer-approved public external reveal record set.

The future source must be checksum-pinned or otherwise immutable, dated after
`T`, citable, license-reviewed, and rich enough to apply the contract's
label-status enum without changing the frozen source set, scores, ranks, or
formula. No reveal metric may be given positive-outcome wording before a
separate reviewed reveal result.

## Maintainer Options

| Option | Meaning | Minimum evidence to change path |
| --- | --- | --- |
| `GO_REGISTER` | Maintainer approves `TASK-0996` to register the prediction from the repaired pack. | No extra evidence required beyond explicit maintainer approval, green validation, and byte-identity checks below. |
| `HOLD_FOR_INDEPENDENT_REVIEW` | Maintainer wants one more independent review before approving the Class 2 freeze. | A non-authoring reviewer repeats the hash checklist, schema placeholder gate, no-label boundary review, and anchor dry-run without reading reveal labels. |
| `STOP_SOURCE_OR_EXPOSURE_WEAK` | Maintainer decides the pre-T exposure source or source/exposure semantics are too weak for registration. | A new source-readiness or feature-surface task would need to pin stronger admissible source/exposure evidence before any renewed freeze packet. |

## `GO_REGISTER` Unblock Checklist For `TASK-0996`

`TASK-0996` can be unblocked only if all of the following are true:

1. a maintainer records explicit Class 2 `prediction_freeze` approval;
2. the approval cites this packet, the registration pack SHA, the target payload
   digest, and the approved freeze commit;
3. `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` remains
   byte-identical to the hash listed above;
4. the source model surface, model-selection contract, input surface, per-source
   score digest, and feature-table digest remain byte-identical to the hashes
   listed above;
5. the generated staged payload still has the same `draft_entry_sha256` and
   `draft_entry_targets_sha256` before maintainer placeholders are replaced;
6. the registered PRED entry changes only the maintainer decision timestamp,
   approved freeze commit, and approval/anchor record-back fields specified by
   the approved task;
7. the registered entry validates under the generic prediction schema and
   `validate-repo --strict --fail-on-warnings` covers the
   `prediction_registry/radio_transients/` path;
8. no reveal labels, outcome scores, target edits, rank edits, formula edits,
   claims, or positive-outcome wording enter the registration PR;
9. any non-dry-run anchor capsule records its bytes and SHA-256 after the
   approved registry artifact exists.

## Packet Recommendation

The repaired pack is ready for a maintainer decision surface. The packet does
not autonomously select registration; it says `GO_REGISTER` is technically
available if the maintainer accepts the no-label, point-score-only boundary and
executes `TASK-0996` under the unblock checklist above.

If the maintainer wants stronger separation from the agents that repaired the
pack, choose `HOLD_FOR_INDEPENDENT_REVIEW`. Choose
`STOP_SOURCE_OR_EXPOSURE_WEAK` only if the pre-T source/exposure construction
itself is judged insufficient despite the repaired registration machinery.

## Output-Routing Summary

- Task verdict: `not_applicable` for scientific result status; packet verdict
  is `READY_FOR_MAINTAINER_DECISION`.
- Canonical destination: this decision packet under `docs/reviews/frb/`.
- Review tier: none.
- Gate A / Gate B: not applicable.
- Prediction impact: none; no `PRED-*` artifact is written or registered.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: explicit maintainer Class 2 freeze approval remains
  required before `TASK-0996` can execute.
