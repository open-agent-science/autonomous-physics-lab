# FRB Reduced Pre-Registration Anchor Capsule Implementation

- Task: `TASK-1024`
- Controlling decision: `DEC-20260712-frb-reduced-anchor-publication`
- Decision option: `GO_REDUCED_CAPSULE`
- Implementation verdict: `REDUCED_CAPSULE_READY_FOR_MAINTAINER_UPLOAD`
- DOI-readiness verdict: `REDUCED_CAPSULE_REQUIRED`
- Builder: `scripts/package_frb_prediction_reduced_anchor_capsule.py`

## Boundary

This implementation builds deterministic local bytes for the approved reduced
metadata/checksum route. It does not upload to Zenodo, mint a DOI, modify the
existing GitHub Release asset, inspect reveal labels, score the registered
prediction, alter `PRED-0001`, or create a RESULT, CLAIM, or KNOW artifact.

The current nine-member GitHub Release ZIP remains the full sealed checksum
anchor. It is not approved for blanket external redistribution or licensing.
The reduced capsule publishes only APL-authored decision and review metadata;
all omitted sealed members remain represented by path, role, byte size,
SHA-256, source commit, source tag, and exclusion reason.

## Decision Gate

The builder refuses packaging unless the committed decision still records all
of the following:

- selected option `GO_REDUCED_CAPSULE`;
- route `reduced_metadata_checksum_capsule`;
- deterministic local building allowed;
- excluded members represented by checksum only;
- automatic upload and DOI minting disabled;
- no maintainer veto and no recorded revert;
- required verdicts `REDUCED_CAPSULE_REQUIRED` and
  `REDUCED_CAPSULE_READY_FOR_MAINTAINER_UPLOAD`.

## Deterministic Build

```bash
python3 scripts/package_frb_prediction_reduced_anchor_capsule.py \
  --repo-root . \
  --output-dir <local-output-dir> \
  --force
```

The helper refuses repository-local output by default. ZIP entries use
`ZIP_STORED`, fixed `1980-01-01T00:00:00` timestamps, a fixed allowlist, and
pinned input size/SHA-256 checks.

| Field | Value |
| --- | --- |
| Filename | `frb-pret-reduced-pre-registration-anchor-v1.0.0.zip` |
| Archive members | 9 |
| Archive bytes | `50077` |
| Archive SHA-256 | `141a4ef4e0e1bfe626abb721cccf2d170249b91d910cb125132efa4b019ec49a` |
| Compression | `zip_stored` |
| Fixed timestamp | `1980-01-01T00:00:00` |
| Full-anchor SHA-256 referenced | `7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039` |

Two builds in separate local output directories were byte-identical.

## Reduced Allowlist

| Order | Archive member | Role |
| ---: | --- | --- |
| 1 | `README.md` | Generated no-claim, no-dataset, and license-scope boundary |
| 2 | `FRB_REDUCED_ANCHOR_MANIFEST.json` | Generated allowlist, excluded-member ledger, pins, policy, and upload metadata |
| 3 | `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml` | Approved prediction-freeze decision |
| 4 | `decisions/DEC-20260712-frb-reduced-anchor-publication.yaml` | Approved reduced-capsule rights decision |
| 5 | `docs/reviews/frb/frb-prediction-freeze-registration.md` | Prediction registration record |
| 6 | `docs/reviews/frb/frb-prediction-freeze-anchor-upload-pack.md` | Full-anchor package record |
| 7 | `docs/reviews/frb/frb-prediction-freeze-external-anchor-record-back.md` | GitHub Release anchor record |
| 8 | `docs/reviews/frb/frb-anchor-zenodo-rights-publication-review.md` | Rights review and reduced-route basis |
| 9 | `LICENSE` | Repository MIT copyright and permission notice for included APL-authored/generated metadata |

The archive includes no `predicted_score` field, no `rank_descending` field,
no row-level FRB target id, and none of the excluded paths below.

## Excluded Sealed Members

The source tag for every entry is
`pred-frb-pret-repeater-propensity-20260710`.

| Path | Role | Bytes | SHA-256 | Source commit | Exclusion reason |
| --- | --- | ---: | --- | --- | --- |
| `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` | `task_0965_registration_pack` | 190860 | `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Mixed/value-bearing registration pack with source-level scores, ranks, and target digest; checksum only. |
| `prediction_registry/radio_transients/PRED-0001.yaml` | `registered_radio_transients_pred_entry` | 172220 | `442323fe63c1170fecae042e3f5612c1177069e74a39632e92c37fa04f7f3c80` | `059227ba0fcb6c0601bd4c70cf312c6f094aee48` | Registered source-level point scores and ranks; checksum and public repository pointer only. |
| `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | `task_0964_frozen_model_surface` | 46200 | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Source-derived model and score surface; checksum only. |
| `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | `task_0964_model_selection_contract` | 4253 | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Coupled to source-surface hashes and unnecessary for the minimal metadata anchor. |
| `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | `task_0963_pre_t_input_surface` | 177389 | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Source-derived per-source exposure features have no recorded bulk redistribution license. |
| `docs/reviews/frb-sealed-prediction-registration-pack.md` | `task_0965_pack_note` | 3876 | `9f38ae2aa7b5de6950af367b02de188fc7850a7b7fa942624c9c4c4716f9ad63` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Narrative includes top-score examples; replaced by the reduced README. |
| `docs/reviews/frb-campaign-activation-20260708.md` | `campaign_activation_note` | 2045 | `c4deb4e4182fefa218ec7e101c8ed8006bc806f5480ce5b55d71e0013d72a5b7` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Optional campaign context omitted for minimality. |
| `docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md` | `catalog1_pair_gate_note` | 6181 | `81cd0fbc983c6160a52ff80fd85985a06dd395bdc5f5c8d831839b9db4dda4f2` | `83eca7501aea3e4f9869324b5ec2cd722fd7e676` | Optional source-gate context remains in the public repository. |

## Copy-Paste Zenodo Metadata

**Title:** `APL FRB sealed prediction pre-registration checksum anchor (reduced capsule)`

**Resource type:** `Other`

**Access right:** `Open`

**Version:** `1.0.0`

**Creators:**

1. `Hladun, Roman` - ORCID `0009-0004-4853-5212`
2. `Autonomous Physics Lab contributors`

**Description:**

> This is a reduced checksum anchor for a sealed prospective Autonomous Physics
> Lab prediction registration. It is not an open reusable FRB dataset, not a
> reveal result, not a success verdict, not a calibrated repeater probability,
> and not an FRB population, morphology, or discovery claim. Source-derived
> sealed prediction, feature, model, score, and rank surfaces are represented
> by checksum and public repository pointers only; they are not redistributed
> or licensed by this record.

**License:** `MIT`, scoped only to the APL-authored and generated metadata
included in this reduced archive. The archive includes the repository
copyright and permission notice as `LICENSE`; it does not license any
checksum-referenced excluded member.

**Keywords:** `sealed prediction; pre-registration; checksum anchor; fast radio
bursts; open agent science; reproducibility`

**Related identifiers:**

- `IsSupplementTo` ->
  `https://github.com/open-agent-science/autonomous-physics-lab/releases/tag/pred-frb-pret-repeater-propensity-20260710`
- `IsSupplementTo` ->
  `https://github.com/open-agent-science/autonomous-physics-lab`

## Maintainer Stop Line

The implementation task stops here. The archive exists only in ignored local
output. Uploading it, selecting final Zenodo form fields, clicking Publish,
minting a DOI, and recording the external DOI are separate maintainer actions.
No external publication was attempted in this task.

## Validation

- Builder regression suite verifies deterministic bytes, the nine-member
  allowlist, the complete eight-member exclusion ledger, fixed ZIP metadata,
  decision-veto blocking, repository-output refusal, and value-bearing-field
  leakage guards.
- The existing full-capsule pins are re-verified before every reduced build;
  the implementation does not maintain a second copy of the original sealed
  member checksums.

## Output Routing

- Canonical destination: reduced-capsule builder, regression tests, and this
  implementation packet.
- Review tier: no change; `PRED-0001` remains `MAINTAINER_REVIEWED`.
- Gate A / Gate B: not applicable; this is packaging, not a new scientific
  result or prediction.
- Prediction impact: none.
- Claim impact: none.
- Knowledge impact: none.
- DOI-readiness verdict: `REDUCED_CAPSULE_REQUIRED`.
- Publication blocker: maintainer upload/Publish and DOI record-back remain
  outstanding; the full nine-member ZIP remains not DOI-ready as a blanket
  licensed archive.
