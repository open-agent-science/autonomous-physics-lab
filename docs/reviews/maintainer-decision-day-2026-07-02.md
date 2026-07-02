# Maintainer Decision Day — 2026-07-02

Task: `TASK-0921`
Maintainer: gladunrv (interactive Gate C session, 2026-07-02)
Base reviewed: `origin/main` at `733af954`

This memo records one batch of explicit maintainer decisions over the pending
Gate C decision packets, plus three strategic routing decisions. Each decision
was made against the linked packet's own options. This memo and its PR change
no `RESULT-*`, `CLAIM-*`, `PRED-*`, or `KNOW-*` artifact by themselves; every
execution happens through the scoped follow-up task named per decision, under
the normal review gates.

An independent strategist-agent decision set was cross-checked against the
repository state before this session; where its items were already executed
(DZ10 A-prime, Chen-Kipping negative routing, split-axis claim model) they are
not re-decided here, and its two gaps (the FRB frontier lane and the
uncertainty-calibration fork) are decided explicitly below.

## Decisions

### D1. RESULT-0022 (Stellar M-L baseline adequacy) — Option 2 + Option 3

Approve the packet's tightly scoped public capsule (frozen DEBCat slice,
baseline-adequacy wording, no universal-law claim) AND commission a planning
scout for a second, independently curated stellar dataset.
Execution: `TASK-0922` (capsule), `TASK-0928` (external dataset scout).
Packet: [stellar-ml-result0022-maintainer-review-packet.md](./stellar-ml-result0022-maintainer-review-packet.md).

### D2. RESULT-0023 (FIRAS/Wien self-consistency) — Option 1

Keep as `AGENT_VALIDATED` calibration/verifier memory. No public push; the
documented circularity caveat stands. No follow-up task.
Packet: [firas-wien-result0023-maintainer-review-packet.md](./firas-wien-result0023-maintainer-review-packet.md).

### D3. RESULT-0024 (Stellar high-mass transfer) — Option (c)

Authorize a metadata-only update that records the Gate B validation and moves
`review_tier` to `AGENT_VALIDATED`, with the task-input-hash lifecycle caveat
recorded verbatim in the validation record. Scientific basis: zero metric
drift in the independent replay; the hash mismatch is task-file lifecycle
bookkeeping already root-caused (TASK-0898) and being structurally fixed
(TASK-0917). Public wording stays at the same-source, small-holdout,
no-universal-law ceiling.
Execution: `TASK-0923`.
Packet: [stellar-result0024-high-mass-transfer-maintainer-review-packet.md](./stellar-result0024-high-mass-transfer-maintainer-review-packet.md).

### D4. RESULT-0025 (NMD-0003 GP point estimator) — Option (a)

Publish the point-estimator memory card with the packet's copy-ready wording:
retrospective post-AME2020 holdout MAE improvement (2.979 -> 0.462 MeV) with
the inline caveat that predictive uncertainty is miscalibrated and no interval,
reveal, or prediction-freeze use is implied. Include the lightweight option (b)
bookkeeping note about the Gate B lifecycle hash drift.
Execution: `TASK-0922`.
Packet: [nmd0003-result0025-public-review-packet.md](./nmd0003-result0025-public-review-packet.md).

### D5. MD-0002 external dataset release — Zenodo DOI route

Approve the Zenodo-like DOI archive route: maintainer-approved release tag,
deterministic archive from the allowlist (helper: TASK-0908), creator metadata
(Roman Hladun, ORCID 0009-0004-4853-5212), CC BY 4.0 preserved, Materials
Project attribution retained, archive SHA-256 and DOI recorded back into the
repository after minting. The Zenodo account and the publish click remain
maintainer physical actions.
Execution: `TASK-0924` (release execution + DOI record-back), after `TASK-0908`.
Packet: [materials-md0002-external-release-decision-packet.md](./materials-md0002-external-release-decision-packet.md).

### D6. Particle-mass common-scheme source — accept the AHS route

Accept the Antusch-Hinze-Saad accepted-manuscript table (arXiv:2510.01312v2,
all six quarks in MS-bar at M_Z, PDG-2024 inputs) as the single source surface
for the common-scheme Koide falsifier rerun. `CLAIM-0006` / `CLAIM-0007`
remain `DRAFT`; any Gate C promotion still requires the scheme cleanup this
source enables plus a separate maintainer review. Broad formula search stays
closed.
Execution: `TASK-0926` (source pinning only; no Koide metric run inside it).
Packet: [particle-mass-common-scheme-source-policy-decision.md](./particle-mass-common-scheme-source-policy-decision.md).

### D7. Exoplanet null-baseline identities — Option A

Approve creating the minimal canonical experiment/hypothesis identities so the
already-replayed (zero-drift) negative/control memory can be packaged as a
RESULT. No new metrics, no residual rescoring; the campaign remains
monitor-only afterwards.
Execution: existing `TASK-0909` (green-lit) then `TASK-0919`.
Packet: [exoplanet-null-baseline-canonical-identity-decision.md](./exoplanet-null-baseline-canonical-identity-decision.md).

### D8. Quantum ZnSe/InP — approve the strict no-refit transfer contract

Approve `TASK-0914` producing a STRICT_NO_REFIT transfer contract (frozen row
IDs, size-harmonization rule, model family, controls, survival threshold —
all predeclared before any metric), which unblocks the bounded benchmark
`TASK-0920`. Both transfer and no-transfer outcomes are acceptable science;
no universal size-law wording; broad correction search stays closed.
Execution: existing `TASK-0914` -> `TASK-0920`.

### D9. Atomic-clock residuals — memory card + HOLD for new metrics

Route the Yb/Sr diagnostic as source-limited consistency memory. No new
metric work until a new independent direct row or an approved
aggregation/harmonization contract exists; the independent-source scout
(`TASK-0913`) continues as the campaign's source-readiness gate. No
constants-drift, anomaly, or new-constant wording.
Packet context: [atomic-mcgrew-ybsr-source-route-adjudication.md](./atomic-mcgrew-ybsr-source-route-adjudication.md).

### D10. Nuclear uncertainty calibration — commission a second-generation method now

The no-peek calibration audit (TASK-0899) failed all three predeclared route
families; the prediction freeze (`TASK-0827`) stays blocked. Initial decision:
rather than placing the lane on HOLD, commission ONE bounded second-generation
calibration-method task with predeclared route families and hard stop
conditions, run under the same no-peek discipline. The negative/blocker
packaging of the first failure (`TASK-0912`) proceeds independently; the
point-estimator card is covered by D4.

**Refined the same day (2026-07-02, joint scientific-director + strategist
review, maintainer-approved):** re-scoring any second-generation method on the
same post-AME2020 holdout is no longer clean no-peek — its failure metrics
(1-sigma coverage ~0.62, RMS z ~4.3) are known, so gen-2 design is necessarily
informed by them, and a pass would risk methodology shopping. Refinement:

- `TASK-0925` is demoted to a BLOCKED, low-priority, **protocol-only** lane:
  predeclare gen-2 route families and define a fresh-surface validation
  contract (role-disjoint reveal split + trickle measurement registry). The
  seen holdout is diagnostic background only; **no pass on it can ever unblock
  `TASK-0827`**, and any future run must be a separate task labeled
  `post_hoc_methodology_stress_test`.
- The live nuclear path is the **two-tier point-only freeze contract
  preflight** (`TASK-0929`, high priority): point predictions only, no
  calibrated intervals, no uncertainty claim, MAE/rank scoring against frozen
  baselines at a future reveal, explicit `TASK-0899` failure caveat — a
  maintainer-approved amendment to the prediction protocol, not a bypass of
  `TASK-0827`. This captures the time-sensitive pre-registration value before
  the next AME-class release.

Execution: `TASK-0929` (live path), `TASK-0925` (blocked protocol-only lane),
`TASK-0912` (unchanged).
Audit: [nmd0003-gp-uncertainty-calibration-audit.md](./nmd0003-gp-uncertainty-calibration-audit.md).

### D11. Claim ledger — adopt the split-axis disposition for CLAIM-0001 / CLAIM-0009

Adopt the legacy-claim audit's split-axis model: `support_status` and
`review_tier` are preserved exactly as reviewed (`PARTIALLY_SUPPORTED`,
`MAINTAINER_REVIEWED`); the claims gain `novelty_class:
calibration_known_physics`, `claim_role: calibration_memory`, and
`active_scientific_claim: false`. No downgrade to DRAFT, no
RETIRED_TO_CALIBRATION status, no history rewrite. The vocabulary addition
lands in the claim-promotion policy in the same migration PR.
Execution: `TASK-0927` (maintainer-owned migration PR).
Audit: [legacy-claim-novelty-audit-and-calibration-migration.md](./legacy-claim-novelty-audit-and-calibration-migration.md).

### D12. FRB — flagship frontier lane with a July freeze target

Designate the FRB CHIME Catalog 2 repeater lane as the Q3 flagship frontier
path: it is the only current lane with a credible route to a pre-registered
prospective prediction. Critical path: `TASK-0910` (pin exposure-map source
artifact; priority raised to high) -> construct numeric T-truncated exposure
values -> freeze the repeater model under controls -> register PRED entries.
Target: PRED registration by end of July 2026 (the T-truncated split ages).
The date is a steering target conditional on each gate clearing in order
(source maps first, then T-truncated exposure values, then model/PRED); it is
not a delivery commitment, and no source, leakage, or control gate may be
weakened to meet it. Later chain tasks are created as their predecessors land,
not pre-seeded.

### D13. Queue/WIP policy — not adopted

The proposed WIP rule (no new task wave while REVIEW_READY > 8; top-up READY
to 12-16) was reviewed but NOT adopted as protocol in this session. It stays
an open process suggestion.

## Cross-check note

Strategist-set items already executed before this session and therefore not
re-decided: Nuclear DZ10 A-prime (published-variant stronger baseline, no
canonical-DZ-parity claim; follow-up parity gates `TASK-0878`/`TASK-0911`
exist), Exoplanet Chen-Kipping audit routed as control-sensitive negative
memory (TASK-0866), and the four-gate post-validation routing, which is
already codified in `docs/campaign-curator-protocol.md`.

## Explicit Non-Claims

- No `RESULT-*`, `CLAIM-*`, `PRED-*`, or `KNOW-*` artifact is modified by this
  memo or its PR; all changes flow through the named follow-up tasks and their
  own reviews.
- No discovery-level, universal-law, or constants-anomaly wording is
  authorized by any decision above; every approved capsule keeps its packet's
  scoped limitations.
