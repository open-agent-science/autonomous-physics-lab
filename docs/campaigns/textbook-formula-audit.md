# Textbook Formula Audit

## Goal

Stand up a verifier-first APL scientific campaign that audits well-known
"textbook" formulas across physics, astrophysics, and biological scaling
against modern open datasets, with explicit range, assumption, and
out-of-distribution failure mapping.

The target is **not** to validate or falsify any textbook formula in
universal terms. The target is a disciplined per-formula benchmark surface
where each audited formula is reported with:

- the dataset slice the audit covered;
- the explicit range of independent variables tested;
- the named train/test or holdout split;
- the verification gates applied (dimensional consistency, limiting behaviour,
  asymptotic alignment, monotonicity, evenness/oddness where relevant);
- a per-slice verdict from the campaign's allowed vocabulary
  (`VALID_IN_RANGE`, `PARTIALLY_VALID`, `INCONCLUSIVE`, `OVERFITTED`,
  `FALSIFIED`).

Every audited formula returns a scientist-readable per-slice report; no audit
returns a universal statement about the formula's truth.

## Verifier-First Positioning

APL's structural strength is that it is a **verifier**, not a symbolic-
regression engine. The Textbook Formula Audit campaign exists specifically to
exercise that strength against published, well-defined formula candidates.
Each audit answers a narrower question than "is this formula true":

- "Within this dataset slice, does the formula's prediction stay within a
  pre-declared tolerance?"
- "Outside the declared validity window, where and how does it break?"
- "Do the verification gates (dimensional consistency, limiting behaviour,
  asymptotic match, monotonicity) all pass for the formula on this slice?"
- "Is there a residual structure that the formula does not capture, and is
  that structure stable under matched controls?"

The campaign therefore plays directly to APL's `gauntlet`-style verification
gates and to the multi-tier review-promotion protocol introduced by
`docs/result-promotion-protocol.md`.

## Current Status

Scaffold plus first verifier lanes. This page records the campaign charter,
candidate list, and guardrails. The current public-verifier wave has exact-
reference fixtures for Stefan-Boltzmann and Wien displacement, and
`RESULT-0019` has advanced from `AGENT_PUBLISHED` to `AGENT_VALIDATED` after
Gate B replay. This validates the software/convention fixture route only; it
does not validate an empirical law.

The first empirical slice is now the **Stellar Mass-Luminosity (M-L)
out-of-distribution audit** on DEBCat direct dynamical-mass rows. `TASK-0740`
ran the first local Route 2 benchmark and found a sandbox-pass signal.
`TASK-0759` then completed stage-control, deterministic null/shuffle, and
split-sensitivity checks, and `TASK-0762` found the important baseline lesson:
fixed single-alpha `M^3.5` is inadequate as the sole frozen baseline on this
slice, while fitted-alpha and piecewise/stage-aware baselines are materially
better. `TASK-0763` committed the full normalized DEBCat rows and holdout
manifest under an explicit CC BY 4.0 permission grant. `TASK-0764` packaged
that evidence as `RESULT-0022`, and the result has since become
`AGENT_VALIDATED`. Follow-up control audits found the headline conclusion
stable across a small value-blind alternate-split slate, while a predeclared
piecewise baseline is not justified after complexity penalty. The current
blocker is maintainer-review wording and external-source posture, not another
Gate B replay or model search.
See
`docs/notes/textbook-formula-audit-candidate-list.md` for the ordered
candidate slate.

## Public Monitoring Snapshot

**Current question:** can APL audit famous formulas by source, range,
assumptions, verification gates, and out-of-distribution failure maps without
claiming universal truth or falsity?

**Shareable result:** the campaign scaffold, candidate slate, first
source/baseline planning artifacts, and a Gate-B-validated exact-reference
software/convention result now exist. `RESULT-0019` replayed with zero numeric
drift and remains scoped to the Stefan-Boltzmann synthetic fixture. The first
Stellar M-L empirical lane now has committed DEBCat rows, stage/split/null
controls, baseline-adequacy evidence, and `RESULT-0022` as an
`AGENT_VALIDATED` scoped benchmark.

**Not a claim:** no empirical textbook formula claim has been promoted. This
campaign does not claim that any formula is globally right or wrong.
`RESULT-0022` is independently replayed but not maintainer-reviewed. The
current evidence says only that `M^3.5` is not an adequate sole baseline for
the committed DEBCat slice under the completed controls.

**Active next work:** `TASK-0634` published the scoped Stefan-Boltzmann
software/convention result and `TASK-0635` replayed it through Gate B. The
empirical lane is now Stellar M-L: `TASK-0759`, `TASK-0762`, `TASK-0763`, and
`TASK-0764` closed the control, baseline-adequacy, full-dataset, and Gate A
packaging blockers. Later work made `RESULT-0022` Gate-B replayable and then
validated it, reconciled DEBCat scope flags, and ran split-stability and
piecewise-complexity controls.
`TASK-0783` selected the next formula slice only as a future source-curation
route: Wien displacement against a pinned FIRAS source artifact, with no
metrics until wavelength-domain peak semantics, checksums, license posture, and
spectral coverage are frozen.

**Expected next result:** a pinned FIRAS/Wien source package, or a
maintainer-review packet clarifying safe public wording for `RESULT-0019` and
`RESULT-0022`.

## Why It Matters

The textbook formula surface is unique to APL's value proposition:

- It is **dense with public datasets** (Gaia DR3, NASA Exoplanet Archive,
  NIST databases, PDG, open biological compendia) and does not require new
  experimental data.
- Each formula is a **well-defined falsifiable benchmark**, not an open-ended
  modelling problem.
- The audits produce **immediately legible results** ("formula X holds within
  slice Y to tolerance Z; breaks at boundary W").
- The audits exercise APL's verification gates on widely-cited, externally
  reviewable formulas, which strengthens AGENT_PUBLISHED → AGENT_VALIDATED
  → MAINTAINER_REVIEWED chains across multiple subject areas at once.
- Negative outcomes (`OVERFITTED`, `FALSIFIED` on a slice) are scientifically
  honest contributions, not failures of the workflow.

This is also the campaign best suited for **bringing parallel agents in** —
each formula is an isolated EXP-XXXX boundary; agents do not collide on
dataset surfaces or hypothesis lanes.

## What This Campaign Does Not Do

- It does **not** generate or claim new physical laws.
- It does **not** attempt to validate any textbook formula universally.
- It does **not** make discovery claims about cosmology, fundamental
  constants, particle masses, or stellar evolution.
- It does **not** infer composition, habitability, biosignatures, target
  priority, or any application-domain interpretation from any audited
  formula.
- It does **not** rebrand symbolic regression as formula discovery — APL is
  the verifier of candidates, not the candidate generator.
- It does **not** promote any audited formula's claim status; claim
  endorsement remains maintainer-only (Gate C) per
  `docs/result-promotion-protocol.md`.

## Expected Audit Lifecycle

A typical Textbook Formula Audit task follows a fixed lifecycle:

1. **Source-and-baseline planning task** — pin the dataset snapshot, declare
   the row schema, define the inclusion/exclusion filter, declare the baseline
   formula and its published source, declare the holdout policy.
2. **Sandbox audit run** — deterministic runner produces per-slice metrics,
   activates the campaign's verification gates, and reports residual
   structure under matched controls.
3. **Per-slice review** — review note records what the audit found, which
   slices passed each gate, which slices broke and at what boundary.
4. **Optional result promotion** — if the audit produces a stable per-slice
   pass / falsification under matched controls, the runner output may be
   proposed as an `AGENT_PUBLISHED` RESULT artifact per the result-promotion
   protocol. The audited formula's CLAIM status is not affected by the
   audit; only the audit's own RESULT receives a tier.

## Required Inputs (per audit)

Each audit task must declare and pin:

- the **dataset snapshot** with source, version, SHA-256 checksum, and
  retrieval timestamp (no live external fetch);
- the **row schema** including units, uncertainty semantics, and provenance
  fields;
- the **inclusion/exclusion filter** with pre- and post-filter row counts;
- the **frozen baseline formula** with published source, units convention,
  and explicit parameter values (no in-task refit on full snapshot);
- the **holdout policy**: which rows are train, which are test, and which
  axis the split is along (mass range, metallicity, evolutionary stage,
  catalog source date, etc.);
- the **verification gate slate**: which APL gates apply
  (dimensional consistency, limiting behaviour, asymptotic alignment,
  monotonicity, evenness, separatrix behaviour where relevant);
- the **per-slice tolerance** for each gate.

## Required Quality Checks (per audit)

- Report pre-filter and post-filter row counts before any metric is computed.
- Report baseline-relative metrics, per-slice subset behaviour, and not
  aggregate fit alone.
- Apply each declared verification gate and record PASS / FAIL with the
  numeric margin.
- Build at least one matched control or one deterministic negative control
  per slice that the audit interprets.
- Preserve negative, inconclusive, or null-beats-baseline outcomes as valid
  review surfaces.
- Run the shared research quality gate
  (`docs/research-quality-gate.md`) before any later autonomy PR handoff.
- State explicitly that no universal-law wording, application-domain
  inference, or discovery claim is produced.

## Forbidden Claims

The following framings are forbidden in any audit produced under this
campaign:

- "We validated / falsified [textbook formula]." — every audit is per-slice and
  per-range, and the per-slice verdict does not generalize to the formula as a
  whole.
- "[Textbook formula] is wrong / is right." — verdicts are scoped to the
  audited slice and the declared tolerance.
- Any **discovery framing** ("APL discovered that X law fails for Y class")
  — failures are documented, not promoted as discoveries.
- **Universal physical-law statements** based on a single audit slice.
- **Application-domain inference** from any audited formula (composition,
  evolutionary fate, habitability, biosignatures, drug efficacy, target
  priority, treatment recommendation, biological body-plan
  generalization, etc.).
- **Cross-formula generalization** ("therefore X% of physics textbook
  formulas overfit") — each audit reports only on its own slice.
- **Live data fetch** that bypasses snapshot pinning.

## Sandbox Permissions

| Action | Allowed? |
| --- | :-: |
| Create scoped notes under `docs/notes/` for candidate triage | ✓ |
| Create future hypothesis proposals under `hypothesis_proposals/textbook-formula-audit/` | ✓ |
| Create future experiment proposals under `experiment_proposals/textbook-formula-audit/` | ✓ |
| Create new canonical CLAIM-*, KNOW-*, or PRED-* artifacts | ✗ |
| Edit canonical hypotheses, experiments, or results outside this campaign's scope | ✗ |
| Edit `results/golden-results.yaml` | ✗ |
| Re-fit a frozen baseline formula on the full snapshot | ✗ |
| Run a live external API fetch during an audit | ✗ |
| Promote any audited formula's CLAIM status | ✗ |

## Audit-Output Tier Routing

Per `docs/result-promotion-protocol.md`:

- A first audit run produces a **sandbox-only** report under
  `agent_runs/AGENT-RUN-XXXX/` plus a review note under `docs/reviews/`.
- A clean deterministic audit may then be packaged as an `AGENT_PUBLISHED`
  RESULT artifact under `results/EXP-XXXX/RUN-XXXX/result.yaml` if the
  task contract authorizes that artifact class and Gate A passes.
- A different agent may then run Gate B replay via
  `scripts/apl_validate_agent_published_result.py` to upgrade the result
  to `AGENT_VALIDATED`.
- `MAINTAINER_REVIEWED` and any CLAIM status transition for the audited
  formula remain maintainer-only.

## Candidate Slate

See `docs/notes/textbook-formula-audit-candidate-list.md` for the ordered
candidate slate. The first empirical slice is the **Stellar Mass-Luminosity
(M-L) out-of-distribution audit**. Source/baseline, Route 2 local benchmark,
stage/split/null controls, baseline adequacy, full DEBCat dataset publication,
Gate A packaging, and Gate B replay have landed; `RESULT-0022` is now
`AGENT_VALIDATED` with conservative scope and no universal-law wording. The
next work is maintainer-review wording, an external transfer/source route, or
the still-blocked Wien/FIRAS metric lane after its temperature/domain contract
lands.

## Cross-References

- `campaign_profiles/textbook-formula-audit.yaml` — machine-readable
  campaign profile and autonomy contract.
- `docs/notes/textbook-formula-audit-candidate-list.md` — ordered candidate
  slate with rationale.
- `docs/campaigns/README.md` — campaign map.
- `docs/result-promotion-protocol.md` — multi-tier review protocol that
  applies to any audit RESULT artifact produced under this campaign.
- `docs/research-quality-gate.md` — shared cross-campaign quality gate.
- `docs/strategy.md` — strategic context; this campaign was identified as a
  candidate active/meta surface in the 2026-05-28 strategy review.
