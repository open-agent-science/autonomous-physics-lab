# FRB Anchor Zenodo Rights And Publication Review

- Task: `TASK-1021`
- Registered prediction: `prediction_registry/radio_transients/PRED-0001.yaml`
- GitHub anchor record-back:
  `docs/reviews/frb/frb-prediction-freeze-external-anchor-record-back.md`
- Capsule helper: `scripts/package_frb_prediction_freeze_anchor_capsule.py`
- Verdict: `REDUCED_CAPSULE_RECOMMENDED`

## Boundary

This review does not upload to Zenodo, mint a DOI, create new archive bytes,
edit the GitHub Release asset, change `PRED-0001`, inspect reveal labels, score
the prediction, or create a RESULT, CLAIM, or KNOW artifact.

The existing GitHub tag and Release remain accepted as a checksum anchor for
the registered FRB pre-T exposure-only point-score/rank prediction. This review
answers a narrower question: whether the current nine-file anchor ZIP is safe to
publish externally as a Zenodo artifact under a single record/license.

## Current-ZIP Verdict

Do not upload the current nine-file FRB anchor ZIP to Zenodo as a `Dataset` or
blanket CC BY 4.0 archive.

The blocker is not the checksum, ZIP construction, or prediction-registration
science. The blocker is rights/publication scope: several capsule members carry
source-derived, value-bearing CHIME/FRB-linked scores, ranks, feature surfaces,
or model surfaces. The repository can keep those committed under the recorded
APL source-rights boundary, and the GitHub Release can checksum-anchor them,
but a Zenodo record would flatten the archive into one external publication
surface and one license statement unless a separate rights decision narrows the
payload.

## Evidence Used

- `docs/published-source-dataset-standard.md` now requires an anchor-capsule DOI
  gate before DOI minting for mixed-source archive capsules.
- `data/DATA_LICENSES.yaml` records CHIME/FRB Catalog 1 and Catalog 2 sources as
  public-read/citation sources without explicit source-byte redistribution
  licenses, and records the pre-T exposure/model surfaces as APL-derived
  CHIME/FRB-linked fixtures.
- `docs/reviews/frb/frb-prediction-freeze-anchor-upload-pack.md` and
  `docs/reviews/frb/frb-prediction-freeze-external-anchor-record-back.md`
  record the exact nine-member capsule, release URL, asset bytes, and SHA-256.

## Nine-Member Capsule Classification

| Order | Path | Role | Rights/publication class | Zenodo-as-is decision |
| ---: | --- | --- | --- | --- |
| 1 | `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` | TASK-0965 registration pack | Mixed/value-bearing: stages or records 479 source-level scores/ranks and target digest derived from CHIME/FRB-linked exposure surfaces | Exclude from reduced capsule by default; include only by maintainer-signed richer/full route |
| 2 | `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml` | Approved Class 2 prediction-freeze decision | APL-authored decision metadata | Safe to include in reduced capsule |
| 3 | `prediction_registry/radio_transients/PRED-0001.yaml` | Registered prediction entry | Mixed/value-bearing: 479 registered point scores/ranks keyed by FRB source ids | Exclude from safest reduced capsule; represent by SHA-256, target digest, count, tag, and repository pointer |
| 4 | `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | Frozen model surface | Source-derived value-bearing surface with per-source scores and ranks | Exclude from reduced capsule |
| 5 | `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | Model-selection contract | Mostly APL-authored method metadata; still coupled to source-derived surface hashes and model-selection context | Optional only after maintainer review; not required for the safest reduced capsule |
| 6 | `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | Pre-T exposure feature surface | Source-derived value-bearing per-source exposure feature surface | Exclude from reduced capsule |
| 7 | `docs/reviews/frb-sealed-prediction-registration-pack.md` | Pack review note | Mixed narrative: includes top-score examples and target-payload facts | Exclude from reduced capsule or replace with a redacted README |
| 8 | `docs/reviews/frb-campaign-activation-20260708.md` | Campaign activation note | APL-authored campaign/governance context | Safe but not necessary for minimal reduced capsule |
| 9 | `docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md` | Catalog-1 pair gate note | Source locator/checksum/schema metadata, no source bytes or per-source exposure rows | Safe as supporting rights metadata if the reduced capsule needs source context |

## Recommended Route

Choose `GO_REDUCED_CAPSULE` after maintainer review.

The reduced Zenodo capsule should be framed as a sealed prediction
pre-registration/checksum anchor, not as an open reusable FRB dataset. It should
publish only APL-authored or rights-clear metadata and a manifest proving the
identity of excluded sealed members by checksum.

Minimum recommended reduced-capsule membership:

- generated `README.md` with no-claim and no-dataset wording;
- generated `FRB_REDUCED_ANCHOR_MANIFEST.yaml` or `.json`;
- `decisions/DEC-20260709-frb-prediction-freeze-stub.yaml`;
- `docs/reviews/frb/frb-prediction-freeze-registration.md`;
- `docs/reviews/frb/frb-prediction-freeze-anchor-upload-pack.md`;
- `docs/reviews/frb/frb-prediction-freeze-external-anchor-record-back.md`;
- this review note.

The generated manifest should include the full GitHub Release asset checksum
and the excluded-member manifest below. It may also include the public GitHub
tag, release URL, registration merge commit, source-freeze commit, registered
target count, target payload SHA-256, and PRED SHA-256. It should not include
the full 479-row PRED payload unless the maintainer explicitly approves a
richer route.

## Excluded-Member Manifest Required For The Reduced Capsule

The reduced capsule must include a checksum manifest for every original sealed
member not redistributed through Zenodo.

| Path | Role | Bytes | SHA-256 | Source commit/tag | Exclusion reason |
| --- | --- | ---: | --- | --- | --- |
| `data/radio_transients/frb_sealed_prediction_registration_pack.yaml` | task_0965_registration_pack | 190860 | `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5` | source freeze `83eca7501aea3e4f9869324b5ec2cd722fd7e676`; tag `pred-frb-pret-repeater-propensity-20260710` | Mixed/value-bearing registration pack with source-level scores/ranks and target digest; not blanket-licensed for external redistribution |
| `prediction_registry/radio_transients/PRED-0001.yaml` | registered_radio_transients_pred_entry | 172220 | `442323fe63c1170fecae042e3f5612c1177069e74a39632e92c37fa04f7f3c80` | registration merge `059227ba0fcb6c0601bd4c70cf312c6f094aee48`; tag `pred-frb-pret-repeater-propensity-20260710` | Registered 479 source-level scores/ranks; publish checksum and public repo pointer unless maintainer approves richer route |
| `data/radio_transients/frb_pre_t_repeater_propensity_model_surface.yaml` | task_0964_frozen_model_surface | 46200 | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` | source freeze `83eca7501aea3e4f9869324b5ec2cd722fd7e676`; tag `pred-frb-pret-repeater-propensity-20260710` | Source-derived model/score surface; keep represented by checksum only |
| `data/radio_transients/frb_pre_t_model_selection_contract.yaml` | task_0964_model_selection_contract | 4253 | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` | source freeze `83eca7501aea3e4f9869324b5ec2cd722fd7e676`; tag `pred-frb-pret-repeater-propensity-20260710` | Not required for minimal DOI capsule; method contract can remain in GitHub unless maintainer chooses richer metadata route |
| `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` | task_0963_pre_t_input_surface | 177389 | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` | source freeze `83eca7501aea3e4f9869324b5ec2cd722fd7e676`; tag `pred-frb-pret-repeater-propensity-20260710` | Source-derived per-source exposure feature surface; no explicit bulk redistribution license recorded |
| `docs/reviews/frb-sealed-prediction-registration-pack.md` | task_0965_pack_note | 3876 | `9f38ae2aa7b5de6950af367b02de188fc7850a7b7fa942624c9c4c4716f9ad63` | source freeze `83eca7501aea3e4f9869324b5ec2cd722fd7e676`; tag `pred-frb-pret-repeater-propensity-20260710` | Includes top-score examples; use a reduced README instead of redistributing this note |

If the future reduced capsule also omits `docs/reviews/frb-campaign-activation-20260708.md`
or `docs/reviews/frb-catalog1-interval-exposure-pair-checksum-schema-gate.md`,
list them in the generated manifest as optional context omitted for minimality,
not as rights-blocked value-bearing data.

## Maintainer Options

| Option | Meaning | Recommendation |
| --- | --- | --- |
| `GO_REDUCED_CAPSULE` | Build a reduced metadata/checksum capsule and publish that to Zenodo as a sealed pre-registration anchor. Excluded source-derived members are represented only by checksums, tag, commit, byte size, and repository/release pointers. | Recommended |
| `HOLD_FULL_CAPSULE_RIGHTS_REVIEW` | Do not publish any Zenodo DOI until each of the nine original members has an explicit per-file redistribution and license determination. | Valid but slower; required if the goal is to publish the current full ZIP |
| `STOP_ZENODO_FOR_NOW` | Keep only the GitHub tag/release anchor and do not pursue a DOI. | Safe but weaker than a third-party archive timestamp |

## Required Wording For Any Future Zenodo Record

Use wording in this shape:

> This is a reduced checksum anchor for a sealed prospective APL prediction
> registration. It is not an open reusable FRB dataset, not a reveal result,
> not a success verdict, not a calibrated repeater probability, and not an FRB
> population, morphology, or discovery claim. Source-derived sealed prediction,
> feature, and model surfaces are represented by checksum and public repository
> pointers only; they are not redistributed or licensed by this Zenodo record.

Avoid `Dataset` framing unless a later rights review explicitly clears the
payload under the reusable-dataset standard. Prefer a resource type and title
that say `sealed prediction`, `pre-registration anchor`, or `checksum capsule`.

## Future Task Shape

If the maintainer chooses `GO_REDUCED_CAPSULE`, the next implementation task
should build a deterministic reduced capsule, regression-test its allowlist and
excluded-member manifest, prepare copy-paste Zenodo metadata, and stop before
upload. The maintainer upload/publish click and DOI record-back remain a
separate approval/execution surface.

## Output Routing

- Canonical destination: this rights/publication review note.
- Review tier: no change; `PRED-0001` remains a maintainer-reviewed registered
  prediction.
- Gate A / Gate B: not applicable.
- Prediction impact: none; `PRED-0001` is unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Publication impact: current full ZIP is `doi_deferred`; reduced-capsule DOI
  route is recommended pending explicit maintainer approval.
