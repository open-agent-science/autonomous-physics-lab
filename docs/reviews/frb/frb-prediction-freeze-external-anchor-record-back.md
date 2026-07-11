# FRB Prediction Freeze External Anchor Record-Back

- Task context: `TASK-1020` follow-up record-back
- Registered prediction: `prediction_registry/radio_transients/PRED-0001.yaml`
- Registration PR: <https://github.com/open-agent-science/autonomous-physics-lab/pull/1511>
- Upload-pack PR: <https://github.com/open-agent-science/autonomous-physics-lab/pull/1512>
- Verdict: `EXTERNAL_ANCHOR_RECORDED`

## Boundary

This record-back documents the post-merge external anchor for the already
registered FRB pre-T exposure-only repeater-propensity prediction. It does not
change `PRED-0001`, the approved decision record, the approved registration
pack, the nine-member capsule payload, any target id, score, rank, source path,
formula, reveal condition, RESULT, CLAIM, KNOW, or reveal score.

No repeat labels, morphology labels, post-T source associations, reveal
snapshots, or success metrics were fetched, inspected, summarized, or compared
for this record-back.

## External Anchor

| Field | Value |
| --- | --- |
| External tag | `pred-frb-pret-repeater-propensity-20260710` |
| Tag target commit | `059227ba0fcb6c0601bd4c70cf312c6f094aee48` |
| Tag object SHA | `609dcddd90debe18ab6adfba215ed276d608d094` |
| GitHub Release URL | <https://github.com/open-agent-science/autonomous-physics-lab/releases/tag/pred-frb-pret-repeater-propensity-20260710> |
| Release title | `FRB pre-T repeater-propensity prediction freeze` |
| Release created UTC | `2026-07-10T22:33:50Z` |
| Release published UTC | `2026-07-10T22:36:40Z` |
| Release asset | `frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip` |
| Release asset URL | <https://github.com/open-agent-science/autonomous-physics-lab/releases/download/pred-frb-pret-repeater-propensity-20260710/frb-pret-repeater-propensity-freeze-anchor-v1.0.0.zip> |
| Asset bytes | `608067` |
| Asset SHA-256 | `7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039` |
| GitHub asset digest | `sha256:7f7f44e83dca50b84ba5f2ce310b305172140c04fcf7ae9484fbab0dfa8e1039` |
| Local MD5 | `bfaa5aa17006c4f6b1697267d96fef8b` |
| DOI status | `not_minted` |

The tag target is the registration merge commit, the first `main` commit that
contains the registered `PRED-0001` artifact. The approved source/model freeze
commit remains `83eca7501aea3e4f9869324b5ec2cd722fd7e676` inside the
prediction payload.

The GitHub Release anchor is a checksum/timestamp surface, not an external DOI
or reusable-dataset license decision. The current nine-file capsule remains
`doi_deferred`; see
`docs/reviews/frb/frb-anchor-zenodo-rights-publication-review.md` for the
recommended reduced-capsule route.

## Output Routing

- Canonical destination: this record-back note plus the existing registration
  and upload-pack notes.
- Review tier: no change; `PRED-0001` remains `MAINTAINER_REVIEWED`.
- Gate A / Gate B: not applicable.
- Prediction impact: none; the registered prediction payload is unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: no reveal result exists. Any future reveal comparison
  must use the TASK-0995 reveal-source contract and cite this anchored capsule
  checksum. Any Zenodo or other archival DOI requires the reduced-capsule or
  full-capsule rights route described in
  `docs/reviews/frb/frb-anchor-zenodo-rights-publication-review.md`.
