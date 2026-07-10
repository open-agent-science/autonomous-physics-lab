# FRB Prediction Freeze Registration

- Task: `TASK-0996`
- Decision: `GO_REGISTER`
- Decision packet: `docs/reviews/frb/frb-register-or-hold-decision-packet.md`
- Registered prediction: `prediction_registry/radio_transients/PRED-0001.yaml`
- Task verdict: `PRED_REGISTERED_AND_ANCHORED`

## Maintainer Approval

The maintainer approved `GO_REGISTER` for the FRB Class 2 prediction freeze in
the active Codex conversation on 2026-07-10. The approval is scoped to the
repaired TASK-0965 registration pack and the TASK-1014 decision packet.

This is a point-score-only prediction registration. It is not a reveal result,
success verdict, calibrated probability, FRB population claim, repeater
discovery claim, result promotion, claim promotion, or knowledge update.

## Registered Payload

| Field | Value |
| --- | --- |
| Registered at UTC | `2026-07-10T21:00:36Z` |
| Approved freeze commit | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` |
| Registration pack SHA-256 | `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5` |
| Target payload SHA-256 | `b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf` |
| Registered PRED SHA-256 | `442323fe63c1170fecae042e3f5612c1177069e74a39632e92c37fa04f7f3c80` |
| Decision record SHA-256 | `ff99cd7055796a811711d1887a25a1d6fa3d1493c335a337151834221aec8a28` |

The registered PRED entry is copied from the staged
`would_register_on_maintainer_approval` payload. Only the maintainer decision
timestamp, approved freeze commit, and approval/anchor record-back fields were
added. The 479 targets, scores, ranks, source set, scoring rule, and target
payload digest remain unchanged.

## Boundary Checks

- No reveal labels were fetched, inspected, scored, summarized, or compared.
- No target id, score, rank, source path, source SHA, formula, or scoring rule
  was edited.
- `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` remains
  byte-identical to the TASK-1014 hash.
- Future reveal scoring remains a separate maintainer-reviewed task governed by
  `docs/reviews/frb-reveal-source-admissibility-contract.md`.

## Anchor Record-Back

The final anchor manifest uses the approved registration pack's nine-path
`capsule_manifest`. The earlier TASK-0994 dry-run capsule had eleven members:
it included a generated staged PRED draft plus two extra pre-approval review
notes for audit context. This registration follows the approved pack manifest as
the governing non-dry-run anchor contract.

The deterministic capsule was built locally for checksum record-back during
registration. After `TASK-1020`, the maintainer completed the GitHub Release
anchor for the same capsule bytes. No DOI has been minted.

| Capsule Field | Value |
| --- | --- |
| Archive filename | `frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip` |
| Archive bytes | `608067` |
| Archive SHA-256 | `7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039` |
| Compression | `zip_stored` |
| Fixed ZIP timestamp | `1980-01-01T00:00:00` |

| External Anchor Field | Value |
| --- | --- |
| External tag | `pred-frb-pret-repeater-propensity-20260710` |
| Tag target commit | `059227ba0fcb6c0601bd4c70cf312c6f094aee48` |
| GitHub Release URL | <https://github.com/open-agent-science/autonomous-physics-lab/releases/tag/pred-frb-pret-repeater-propensity-20260710> |
| Release asset URL | <https://github.com/open-agent-science/autonomous-physics-lab/releases/download/pred-frb-pret-repeater-propensity-20260710/frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip> |
| Release published UTC | `2026-07-10T22:36:40Z` |
| GitHub asset digest | `sha256:7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039` |
| DOI status | `not_minted` |

| Order | Path | Bytes | SHA-256 | Role |
| ---: | --- | ---: | --- | --- |
| 1 | `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` | 190860 | `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5` | task_0965_registration_pack |
| 2 | `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml` | 3243 | `ff99cd7055796a811711d1887a25a1d6fa3d1493c335a337151834221aec8a28` | approved_class_2_prediction_freeze_decision |
| 3 | `prediction_registry/radio_transients/PRED-0001.yaml` | 172220 | `442323fe63c1170fecae042e3f5612c1177069e74a39632e92c37fa04f7f3c80` | registered_radio_transients_pred_entry |
| 4 | `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | 46200 | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` | task_0964_frozen_model_surface |
| 5 | `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | 4253 | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` | task_0964_model_selection_contract |
| 6 | `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | 177389 | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` | task_0963_pre_t_input_surface |
| 7 | `docs/reviews/frb-sealed-prediction-registration-pack.md` | 3876 | `9f38ae2aa7b5de6950af367b02de188fc7850a7b7fa942624c9c4c4716f9ad63` | task_0965_pack_note |
| 8 | `docs/reviews/frb-campaign-activation-20260708.md` | 2045 | `c4deb4e4182fefa218ec7e101c8ed8006bc806f5480ce5b55d71e0013d72a5b7` | campaign_activation_note |
| 9 | `docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md` | 6181 | `81cd0fbc983c6160a52ff80fd85985a06dd395bdc5f5c8d831839b9db4dda4f2` | catalog1_pair_gate_note |

## External Anchor Completion

`TASK-1020` prepared the maintainer-only external anchor command surface and
deterministic capsule helper in
`docs/reviews/frb/frb-prediction-freeze-anchor-upload-pack.md`. The completed
GitHub Release anchor is recorded in
`docs/reviews/frb/frb-prediction-freeze-external-anchor-record-back.md`.

The external anchor does not change the registered PRED payload.

## Output Routing

- Canonical destination: registered `PRED-0001` plus this registration note.
- Review tier: `MAINTAINER_REVIEWED` prediction registration, because the
  Class 2 maintainer approval is the precondition for writing the PRED entry.
- Gate A / Gate B: not applicable.
- Prediction impact: `prediction_registry/radio_transients/PRED-0001.yaml`
  registered.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: no reveal result exists; future reveal scoring requires a
  separate maintainer-reviewed task.
