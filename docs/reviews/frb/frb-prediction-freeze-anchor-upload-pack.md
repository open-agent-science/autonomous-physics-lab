# FRB Prediction Freeze Anchor Upload Pack

- Task: `TASK-1020`
- Verdict: `ANCHOR_UPLOAD_PACK_READY`
- Registered prediction: `prediction_registry/radio_transients/PRED-0001.yaml`
- Registration PR: <https://github.com/open-agent-science/autonomous-physics-lab/pull/1511>
- Registration merge commit: `059227ba0fcb6c0601bd4c70cf312c6f094aee48`
- Source/model freeze commit recorded in the PRED payload:
  `83eca7501aea3e4f9869324b5ec2cd722fd7e676`

## Boundary

This task prepares the deterministic upload pack for the external anchor. It
does not create a git tag, GitHub Release, external upload, DOI, RESULT, CLAIM,
KNOW, reveal score, or edited prediction payload.

The recommended external tag target is the registration merge commit
`059227ba0fcb6c0601bd4c70cf312c6f094aee48`, because that is the first main
commit containing the registered `PRED-0001` artifact. The earlier
`83eca7501aea3e4f9869324b5ec2cd722fd7e676` value remains the approved
source/model freeze commit recorded inside the prediction payload, not the
repository commit to tag for the post-merge external anchor. The later board
sync commit `b82f80f382f3b97e2229df0b2885a6faae9d1b4e` is not needed as the
tag target.

## Deterministic Command

```bash
python3 scripts/package_frb_prediction_freeze_anchor_capsule.py \
  --output-dir /private/tmp/apl-frb-anchor-task1020 \
  --repo-root . \
  --force
```

The helper refuses repository-local output unless `--allow-repo-output` is
passed for disposable local testing. ZIP entries use `ZIP_STORED`, fixed
`1980-01-01T00:00:00` timestamps, and the approved nine-path capsule manifest
from `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`.

## Capsule

| Field | Value |
| --- | --- |
| Archive filename | `frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip` |
| Archive bytes | `608067` |
| Archive SHA-256 | `7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039` |
| Archive MD5 | `bfaa5aa17006c4f6b1697267d96fef8b` |
| Compression | `zip_stored` |
| Fixed ZIP timestamp | `1980-01-01T00:00:00` |

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

## Maintainer-Only External Anchor Commands

Run these after reviewing and merging this upload-pack PR. Replace
`/private/tmp/apl-frb-anchor-task1020` if you built the capsule somewhere else.

```bash
git fetch origin
git tag -a pred-frb-pret-repeater-propensity-20260710 \
  059227ba0fcb6c0601bd4c70cf312c6f094aee48 \
  -m "FRB pre-T repeater-propensity prediction freeze"
git push origin pred-frb-pret-repeater-propensity-20260710
gh release create pred-frb-pret-repeater-propensity-20260710 \
  /private/tmp/apl-frb-anchor-task1020/frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip \
  --title "FRB pre-T repeater-propensity prediction freeze" \
  --notes "Registered prospective FRB pre-T exposure-only point-score/rank prediction freeze. No reveal result, success verdict, uncertainty, morphology, population, discovery, RESULT, CLAIM, or KNOW artifact is implied. Capsule SHA-256: 7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039."
```

If a Zenodo or other archival DOI is minted later, record only the release URL,
DOI, archive byte size, SHA-256, and any platform MD5 in a follow-up record-back
PR. That follow-up must not change `PRED-0001`.

## Output Routing

- Canonical destination: this upload-pack note and
  `scripts/package_frb_prediction_freeze_anchor_capsule.py`.
- Review tier: maintainer-reviewed prediction already exists; this task does
  not change its review tier.
- Gate A / Gate B: not applicable.
- Prediction impact: none; `PRED-0001` is unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: external tag/release/DOI are still maintainer-only
  actions after merge.
