# FRB Prediction-Freeze Anchor Capsule Dry Run

- Task: `TASK-0994`
- Verdict: `ANCHOR_DRY_RUN_READY`
- Dry-run builder: `scripts/package_frb_prediction_anchor_dry_run.py`
- Dry-run archive: `frb-pret-prediction-freeze-anchor-dry-run-v0.1.0.zip`
- Dry-run archive bytes: `612208`
- Dry-run archive SHA-256:
  `6657398e88e080862d9195d4a18f891a904716df2901654310b3dfc27d3a8165`

## Boundary

This is an anchor-capsule dry run only. It did not create a git tag, GitHub
Release, external upload, DOI, registered `PRED-*` entry, result, claim, or
knowledge artifact. The dry-run archive was built in an untracked local output
directory and is not committed.

Post-approval note, 2026-07-10: after `TASK-0996` records `GO_REGISTER`, this
dry-run capsule is historical. The helper is expected to refuse rebuilding
against the approved decision record; use the `TASK-0996` registration note for
the current non-dry-run anchor checksum path.

The staged `PRED-0001` member inside the dry-run archive is generated from the
TASK-0965 pack and keeps the maintainer placeholders for
`registered_at_utc` and `source_state.git_commit`. It is a dry-run payload, not
an active prediction-registry entry.

## Deterministic Command

```bash
python3 scripts/package_frb_prediction_anchor_dry_run.py \
  --output-dir /private/tmp/frb-anchor-dry-run-0994 \
  --force
```

The helper refuses repository-local output unless `--allow-repo-output` is
passed for disposable local testing. ZIP entries use `ZIP_STORED`, fixed
`1980-01-01T00:00:00` timestamps, and an explicit allowlist order.

## Dry-Run Allowlist

| # | Role | Path | Bytes | SHA-256 |
| ---: | --- | --- | ---: | --- |
| 1 | Class 2 prediction-freeze decision stub | `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml` | 2,181 | `2554cc15eda2e12ec08dcc5ba44e240d135fd915c8f8ebbdb67c7c2c6ea725b5` |
| 2 | Generated staged PRED payload from TASK-0965 pack | `staged_payloads/prediction_registry/radio_transients/PRED-0001.draft.yaml` | 170,764 | `ca5f0f77bb17c19dc730aa194ba7cd5cdffdef95b515057d7288405338007b8b` |
| 3 | TASK-0965 registration pack | `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` | 190,860 | `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5` |
| 4 | TASK-0964 frozen model surface | `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | 46,200 | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` |
| 5 | TASK-0964 model-selection contract | `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | 4,253 | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` |
| 6 | TASK-0963 pre-T input surface | `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | 177,389 | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` |
| 7 | TASK-0965 pack review note | `docs/reviews/frb-sealed-prediction-registration-pack.md` | 3,876 | `9f38ae2aa7b5de6950af367b02de188fc7850a7b7fa942624c9c4c4716f9ad63` |
| 8 | TASK-0964 model-freeze review note | `docs/reviews/frb-pre-t-model-selection-freeze.md` | 2,007 | `7e789554c6c3156e8a73ddd3d8527b7ea16f1eafbfd60248590663e2b691ad3e` |
| 9 | TASK-0963 feature-surface review note | `docs/reviews/frb-catalog1-pre-t-exposure-feature-surface.md` | 4,242 | `477fdad7b5ba46c67003f6e4c1d61ec477e013d7f8c0205d7cde3a9cbd4921bf` |
| 10 | Campaign activation note | `docs/reviews/frb-campaign-activation-20260708.md` | 2,045 | `c4deb4e4182fefa218ec7e101c8ed8006bc806f5480ce5b55d71e0013d72a5b7` |
| 11 | Catalog-1 pair checksum/schema gate note | `docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md` | 6,181 | `81cd0fbc983c6160a52ff80fd85985a06dd395bdc5f5c8d831839b9db4dda4f2` |

The generated staged PRED member records 479 source targets and the TASK-0965
draft target payload checksum
`b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf`.

## Maintainer-Only Post-Approval Checklist

1. Record an explicit Class 2 `prediction_freeze` approval.
2. Commit the real `prediction_registry/radio_transients/PRED-0001.yaml`
   entry with maintainer decision timestamp and approved freeze commit.
3. Replace the dry-run decision stub and generated `.draft.yaml` member with
   the approved decision and registered PRED entry, then rebuild a non-dry-run
   capsule.
4. Create an annotated tag at the approved freeze commit, using a tag such as
   `pred-frb-pret-repeater-propensity-YYYYMMDD`.
5. Create a GitHub Release for that tag and attach the deterministic capsule.
6. Optionally publish an archive/DOI record and record back the archive URL,
   byte size, SHA-256, and any DOI.
7. Keep all wording pre-reveal: registration is not a reveal result, not a
   success verdict, and not an FRB population or discovery claim.

## Output Routing

- Canonical destination: this dry-run note and the deterministic builder.
- Review tier: maintainer decision required before any real external anchor.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Prediction impact: none; no registry entry is written.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: explicit Class 2 maintainer prediction-freeze approval
  and a subsequent non-dry-run anchor execution remain required.
