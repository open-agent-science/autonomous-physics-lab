# FRB Sealed Prediction Registration Pack

- Task: `TASK-0965`
- Pack: `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`
- Pack SHA-256: `0839eba264f312752a82161ea184a4ee3f94f94cf4198fe9e0b591f52bd36f6d`
- Decision stub: `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml`
- Decision stub SHA-256: `e11ceb7e54cdaa86e3b42e79d352f7d2fbdabca239bcf0da4c7fb2363818bc5e`
- Status: `PREPARED_PENDING_MAINTAINER_PREDICTION_FREEZE`

## Boundary

This task prepares the FRB prediction-registration surface but does not execute
registration. No `prediction_registry/radio_transients/PRED-0001.yaml` file is
written, no reveal labels are read, and no external anchor is created. The
registered artifact appears only after an explicit Class 2 maintainer
`prediction_freeze` decision.

## Frozen Input

The pack is derived solely from the TASK-0964 frozen model surface:

| Artifact | SHA-256 |
| --- | --- |
| `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` |
| `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` |
| `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` |
| per-source score payload | `00404c62efb1edc300f008f53961e691cb1c06208ef5a032ff83b0bf8ddb60d7` |

The scoring rule is frozen verbatim:
`score_pre_t = log1p(E_upper_hours + E_lower_hours)` with `E_hours = 4 * exposure_count / 3600`. The feature boundary remains
`label_contact=false`; the pack reads no repeat labels, Catalog 2 full-window
exposure, morphology fields, or post-T source associations.

## Sealed Entry Shape

The pack stages one draft registry entry for
`prediction_registry/radio_transients/PRED-0001.yaml` on approval. It contains
479 source-level point scores and ranks.

| Rank | Source | Frozen score |
| ---: | --- | ---: |
| 1 | `FRB20190405B` | 7.78732393351 |
| 2 | `FRB20190210C` | 7.78464337893 |
| 3 | `FRB20190224D` | 7.77662683978 |
| 4 | `FRB20190518D` | 7.76098834826 |
| 5 | `FRB20190320E` | 7.5911506201 |
| 6 | `FRB20180907D` | 7.38741010194 |
| 7 | `FRB20190425B` | 7.06010052046 |
| 8 | `FRB20181225B` | 6.79450570166 |
| 9 | `FRB20190609B` | 6.7329573486 |
| 10 | `FRB20190223A` | 6.52180680957 |

Target payload SHA-256:
`b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf`.

These scores are exposure-only propensity ranks. They are not calibrated
probabilities, intervals, discovery claims, population claims, or a success
verdict.

## Reveal Conditions

Future labels must come only from a checksum-pinned later CHIME/FRB snapshot or
maintainer-approved external reveal record. Positive repeat status requires
repeat evidence published strictly after `T=2019-07-02`. A reveal comparison is
a separate reviewed task and must leave the frozen source set, scores, ranks,
and scoring rule unchanged.

## External Anchor Plan

After maintainer approval, create an annotated tag at the approved freeze
commit, publish a GitHub Release for the tag, and attach a deterministic archive
capsule containing the approved decision, registered PRED entry, this pack, the
TASK-0964 surface and contract, the TASK-0963 input surface, and this review
note. Record the capsule byte size, SHA-256, and any archive DOI in a follow-up
anchor note. Until that approval happens, the anchor is planned only.

## Output Routing

- Canonical destination: `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`.
- Review tier: maintainer decision required before registration.
- Prediction impact: staged only; no registered `PRED-*` artifact is written.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: explicit Class 2 maintainer `prediction_freeze`
  decision.
