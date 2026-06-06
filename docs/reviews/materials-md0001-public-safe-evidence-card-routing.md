# Materials MD-0001 Public-Safe Evidence Card Routing

Task: `TASK-0607`
Domain: Materials Property Residuals
Mode: public-safe routing
Verdict: `PUBLIC_SAFE_EVIDENCE_CARD_ROUTED`

## Scope

This task packages the existing MD-0001 evidence trail into existing campaign
and public-monitoring surfaces. It creates no new dashboard, dataset, metrics,
result, prediction, claim, knowledge artifact, external repository, or DOI.

Inputs routed:

- `docs/reviews/materials-md0001-baseline-residual-benchmark.md`
- `docs/reviews/materials-md0001-independent-baseline-replay.md`
- `docs/reviews/materials-md0001-band-gap-null-control-audit.md`
- `docs/reviews/materials-md0001-benchmark-promotion-preflight.md`
- `docs/reviews/materials-md0001-formation-energy-null-control-audit.md`
- `docs/reviews/materials-md0001-split-sensitivity-audit.md`
- `docs/campaigns/materials-property-residuals.md`
- `docs/campaigns/public-science-dashboard.md`

## Public-Safe Card

Short version:

`MD-0001` is APL's first reusable Materials benchmark pilot: a Materials
Project stable-binary-oxides slice with `169` computed-DFT rows, source
metadata, checksum discipline, schema coverage, and a frozen holdout. The first
conservative baseline was exactly replayed. Formation energy is the clearer
diagnostic axis: the cation-group baseline has holdout MAE `0.646030` eV/atom
versus global-median MAE `0.967090` eV/atom, survives deterministic null
controls, and is split-robust across seeded holdouts. Band gap is weaker: the
first null-control audit found a modest edge, but the later split-sensitivity
audit found band-gap ordering split-fragile.

Limitation line:

The rows are computed DFT values, not experimental measurements. MD-0001 is not
a material recommendation, synthesis guide, device claim, biomedical claim,
prediction, new materials law, promoted result, external dataset repository, or
DOI.

## Routed Surfaces

Updated surfaces:

- `docs/campaigns/materials-property-residuals.md`
- `docs/campaigns/public-science-dashboard.md`

The updates keep MD-0001 framed as a reusable-dataset and benchmark pilot. They
state the dataset size, computed-DFT-only limitation, formation-energy baseline
advantage, weak band-gap control result, split-fragile band-gap ordering, and
do-not-promote decision.

## Next Task Recommendation

Recommended next Materials direction: `MD-0002` widening, after the active
result-or-dataset gate authorizes that route.

Formation-energy controls and split sensitivity have already run on MD-0001, so
the remaining public-safe science value is a source-first wider replication
slice, not another MD-0001 control repeat. The widening step should remain
metadata-first and no-live-fetch until a maintainer-approved acquisition package
pins source version, row cap, checksum, citation/reuse metadata, and holdout
rules.

## Output Routing

Canonical destination: existing public/campaign surfaces plus this routing note.

Review tier: none. Gate A is not attempted because no result artifact is
created. Gate B is not applicable.

Claim impact: none. No material-property, material-design, synthesis, device,
biomedical, prediction, or new-law statement is created.

Knowledge impact: none. The public card is explanatory scientific memory, not
accepted knowledge.

Publication blocker: MD-0001 remains blocked from RESULT/PRED/CLAIM promotion
by the frozen holdout boundary and by its pilot, computed-DFT-only scope. Dataset
publication still needs maintainer-approved citation/reuse/version packaging.
