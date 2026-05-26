# Result Promotion Protocol

## Purpose

This protocol is the **single master document** that an agent or contributor
consults at the end of any task to decide:

1. Which canonical output class their finding belongs to.
2. Where on disk that class lives.
3. What promotion criteria the agent can fulfil **autonomously** versus what
   requires maintainer review or external replication.

It operationalizes the vocabulary already established by
[AGENTS.md](../AGENTS.md) ("hypothesis / claim / result / knowledge /
theory") and the per-domain policies (claim promotion, prediction
registry, blind-holdout benchmark, nuclear reveal). It does **not** rewrite
those policies; it ties them together and fills two operational gaps:

- a **mapping rule** that turns any task verdict into a canonical destination;
- a **multi-tier review model** so the maintainer is no longer a hard
  bottleneck for every visible scientific artifact.

If this protocol disagrees with the linked per-domain policies on any
specific gate, the per-domain policy wins for that domain.

## Why This Document Exists

As of the current commit there are **387 closed tasks, 35 sandbox
`AGENT-RUN-*` entries, 11 hypotheses, 11 experiments, 10 `DRAFT` claims, 7
`PRED-*` nuclear entries, and 0 `KNOW-*` knowledge artifacts**. The
architecture supports promotion — schemas and per-domain policies all exist
— but agents do not currently have a single document that maps a task
verdict onto a canonical destination. The default behaviour ("write a
sandbox `AGENT-RUN-*`, recommend more audits") therefore dominates, and
nothing accumulates into canonical scientific memory.

This document is the missing operational layer.

## Output Classes (Seven)

APL distinguishes seven scientific output classes. Each has a canonical
location, a schema, and a promotion-criteria set.

| # | Class | Canonical path | Schema | Authoritative policy |
| --- | --- | --- | --- | --- |
| 1 | **Benchmark result** | `results/EXP-XXXX/RUN-XXXX/result.yaml` + index in `results/golden-results.yaml` | `physics_lab/schemas/result.schema.json` | This document + [`claim-promotion-policy.md`](./claim-promotion-policy.md) |
| 2 | **Validated-in-scope result** | Same as (1) with non-empty `verification.verdicts` and explicit scope | Same | This document |
| 3 | **Negative / falsification result** | Same as (1) with `best_verdict: FALSIFIED` or `OVERFITTED` | Same | This document |
| 4 | **Partially valid result** | Same as (1) with `best_verdict: PARTIALLY_VALID` or `VALID_IN_RANGE` and an explicit `scope` block | Same | This document + [`claim-promotion-policy.md`](./claim-promotion-policy.md) |
| 5 | **Prediction awaiting reveal** | `prediction_registry/<domain>/PRED-XXXX.yaml` (e.g. `prediction_registry/nuclear_masses/PRED-0001.yaml`) | Domain-specific (e.g. `physics_lab/schemas/nuclear_mass_prediction.schema.json`); generic baseline in `physics_lab/schemas/prediction.schema.json` | [`prediction-registry-policy.md`](./prediction-registry-policy.md), [`blind-holdout-benchmark-protocol.md`](./blind-holdout-benchmark-protocol.md), [`nuclear-prediction-reveal-protocol.md`](./nuclear-prediction-reveal-protocol.md) |
| 6 | **Claim** | `claims/CLAIM-XXXX.md` | `physics_lab/schemas/claim.schema.json` | [`claim-promotion-policy.md`](./claim-promotion-policy.md) |
| 7 | **Knowledge** | `knowledge/KNOW-XXXX.md` | `physics_lab/schemas/knowledge.schema.json` | This document |

Sandbox-only diagnostic evidence (such as `agent_runs/AGENT-RUN-XXXX/`)
remains a valid intermediate surface but is **not** a canonical output
class. The treadmill that this protocol exists to break is precisely the
pattern of "write another `AGENT-RUN-*` and propose more follow-ups" with
nothing ever crossing into the seven classes above.

## Verdict-to-Class Mapping Rule

Every task verdict from this point forward maps onto exactly one canonical
class. Agents must consult this table at end-of-task instead of defaulting
to `agent_runs/`.

| Task verdict (from agent run / lane) | Default canonical class | Notes |
| --- | --- | --- |
| `VALID` | (1) Benchmark result | Strongest verdict. Writes `RESULT-*` with `best_verdict: VALID`. |
| `VALID_IN_RANGE` | (2) Validated-in-scope result | Same path as (1) with explicit `scope` block. |
| `PARTIALLY_VALID` | (4) Partially valid result | Same path as (1) with `best_verdict: PARTIALLY_VALID`, explicit failure modes in `limitations`. |
| `INCONCLUSIVE` | (3) Negative / falsification result | Writes `RESULT-*` with `best_verdict: INCONCLUSIVE`. Used when the diagnostic could not separate signal from null. |
| `OVERFITTED` | (3) Negative / falsification result | `best_verdict: OVERFITTED`. Documents why the candidate failed adversarial controls. |
| `FALSIFIED` | (3) Negative / falsification result | `best_verdict: FALSIFIED`. Documents what was ruled out. Equally valuable. |
| (pre-registration, no verdict yet) | (5) Prediction awaiting reveal | `PRED-*` under the per-domain registry directory. |
| (post-reveal score) | (1)–(4) depending on score | Reveal task writes a new `RESULT-*` referencing the `PRED-*` it scored. |
| (cross-cutting reusable lesson distilled from ≥2 promoted classes) | (7) Knowledge | `KNOW-*` (maintainer-only in Phase 1; see below). |
| (Statement of fact about nature backed by ≥1 result) | (6) Claim | `CLAIM-*`. Claim references `RESULT-*` ids in its `evidence.results` block. Status changes are maintainer-only in Phase 1; see below. |

The mapping rule is intentionally generous about (3). Negative,
inconclusive, and overfit results are first-class scientific memory in this
repository. They do not lose status by being negative — only by being
hidden in `agent_runs/`.

## Decision Tree (Agent Cheat Sheet)

When an agent finishes a task and is about to write its outputs, it should
walk this tree once:

```
Finished a task. What did I produce?

  ├── Did I write a deterministic engine run with a verdict?
  │     ├── Yes → write a RESULT-* entry (class 1-4 by verdict) with
  │     │        review_tier: AGENT_PROPOSED. Do not write only an
  │     │        AGENT-RUN-*.
  │     └── No  → was this triage / planning / source curation?
  │              ├── Triage / planning → docs/reviews/<topic>.md
  │              ├── Source curation   → data/<campaign>/source_artifacts/
  │              └── Sandbox-only audit (no engine run) → AGENT-RUN-* is OK
  │
  ├── Is there a pre-registration step I should record before later reveal?
  │     ├── Yes → write a PRED-* entry under
  │     │        prediction_registry/<domain>/ with
  │     │        review_tier: AGENT_PROPOSED.
  │     └── No  → continue.
  │
  ├── Does my RESULT-* support an existing CLAIM-* or warrant a new one?
  │     ├── New claim file warranted → may create a new CLAIM-*.md but
  │     │   status MUST remain DRAFT with review_tier: AGENT_PROPOSED.
  │     │   Any DRAFT → PARTIALLY_SUPPORTED transition is maintainer-only
  │     │   in Phase 1 (see Class 6 below).
  │     ├── Existing claim already PARTIALLY_SUPPORTED or stronger →
  │     │   do not edit status; instead reference the new RESULT-* in the
  │     │   claim's evidence.results block via a separate small PR
  │     │   reviewed by the maintainer.
  │     └── No → continue.
  │
  └── Does this finding generalise across ≥2 promoted CLAIM-* or RESULT-*
        in the same domain?
        ├── Yes → file a TASK-PROPOSAL for a KNOW-* entry; the actual
        │        knowledge file is maintainer-only in Phase 1.
        └── No  → done.
```

The bias is towards **writing the canonical record** rather than burying
the finding in a sandbox AGENT-RUN. The `review_tier` field below makes
that safe for RESULT-* and PRED-*. CLAIM-* and KNOW-* are intentionally
kept conservative in Phase 1.

## Multi-Tier Review Model

This is the most important change introduced by this document.

### Why a Tier Model

The previous policy treated the maintainer as the only gate for any
canonical scientific artifact. In a single-maintainer private alpha, that
gate becomes a structural bottleneck: even when an agent has produced a
clean reproducible result, the corresponding `RESULT-*` could not appear
in `results/` without explicit human action, and there is no incentive to
do so quickly. The corpus therefore accumulates sandbox evidence forever.

This protocol introduces a second axis — `review_tier` — that is
**orthogonal** to the existing status enum. An artifact's status (`DRAFT`,
`PARTIALLY_SUPPORTED`, `SUPPORTED`, etc.) describes the evidence strength;
its `review_tier` describes who has reviewed the artifact.

`review_tier` is explicitly **not** an evidence-strength field. An
`AGENT_PROPOSED` claim that sits at `status: DRAFT` is still `DRAFT`-strength
evidence — the tier just records who wrote the file.

### The Three Tiers

| Tier | Who set it | What it means | Trust qualifier required when citing |
| --- | --- | --- | --- |
| `AGENT_PROPOSED` | An agent, on its own, after meeting the agent-promotion gates. | The agent assembled the artifact, has populated the required `agent_proposal_evaluation` block, and has not bypassed any global forbidden rule. The maintainer has not yet reviewed. | "Agent-proposed, not yet maintainer-reviewed." |
| `MAINTAINER_REVIEWED` | The maintainer, after reading the artifact and its evidence. | Maintainer has signed off on both the status and the scope wording. | None required beyond normal scope wording. |
| `EXTERNAL_REPLICATED` | The maintainer, after recording an independent replication. | At least one independent contributor / agent / lab has re-derived the same result from primary sources. The replication record is committed. | None required beyond normal scope wording. |

Tiers are monotonic in trust but not in time:

```
   AGENT_PROPOSED  →  MAINTAINER_REVIEWED  →  EXTERNAL_REPLICATED
                  (asynchronous)        (slow, optional)
```

An artifact may sit in `AGENT_PROPOSED` indefinitely without harm — it is
visible, indexable, and citeable with the trust qualifier. A maintainer
review later can upgrade it, downgrade it back, or leave it. The
maintainer is no longer a hard gate on visibility for RESULT-* and PRED-*
artifacts.

### Legacy Files (Backward Compatibility)

Files committed **before** this protocol have no `review_tier` field.
For schema-validation compatibility only, they are classified as
`LEGACY_UNTIERED`. This classification is:

- a validation convenience, not an evidence endorsement;
- equivalent to "maintainer-merged through the historical PR flow,
  with no explicit per-artifact review tier recorded";
- **not** equivalent to `MAINTAINER_REVIEWED` for the purpose of any new
  scientific judgement.

In particular, the 10 existing `DRAFT` claims remain `DRAFT` — their
`LEGACY_UNTIERED` tier does not upgrade their evidence strength. New
artifacts written after this protocol merges should set `review_tier`
explicitly; tooling may default-display absent-tier as `LEGACY_UNTIERED`
without any implied review status.

### Schema Coverage

`review_tier` (optional) and `agent_proposal_evaluation` (optional,
required only when `review_tier: AGENT_PROPOSED`) are added as optional
fields on the four canonical-artifact schemas in this PR:

- `physics_lab/schemas/result.schema.json`
- `physics_lab/schemas/claim.schema.json`
- `physics_lab/schemas/knowledge.schema.json`
- `physics_lab/schemas/prediction.schema.json` (new file)

The fields are optional to preserve validation on the 15 existing
`RESULT-*`, 10 existing `CLAIM-*`, 0 existing `KNOW-*`, and 7 existing
`PRED-*` files. A follow-up may make the fields required on new
artifacts after the corpus has adopted them.

## Agent Promotion Gates (Per Class)

These are the **autonomous** gates an agent must satisfy before writing
`review_tier: AGENT_PROPOSED` on any canonical artifact. An agent
that cannot meet all listed gates for a class must downgrade to a lower
class or stop at sandbox.

### Class 1–4: Result Promotion Gates (`RESULT-*`)

An agent may write a new `RESULT-*` entry with `review_tier:
AGENT_PROPOSED` if and only if:

1. **Deterministic run** — the result is produced by a committed
   deterministic engine command (`code_reference` and `command` fields
   filled).
2. **Verification block populated** — `verification` block lists at least
   one explicit check, with a non-empty `best_verdict`.
3. **Input hashes recorded** — `input_file_hashes` contains every input
   dataset / config used.
4. **Limitations not empty** — `limitations` has at least one entry.
5. **Engine version pinned** — `engine_version` and `git_commit` filled.
6. **No protected-artifact rewrite** — does not modify an existing
   `RESULT-*` already pinned in `results/golden-results.yaml`.

These gates are mechanical. A CI validation step can enforce them.

### Class 5: Prediction Pre-Registration Gates (`PRED-*`)

An agent may write a new `PRED-*` entry with `review_tier:
AGENT_PROPOSED` if and only if:

1. **No-peek state** — `live_external_fetch_allowed: false` and no
   reveal-relevant measurement source has been read in the task that
   creates the entry.
2. **Frozen model state** — `source_state` references a specific
   `RESULT-*` and a specific git commit.
3. **Named target set** — every prediction target is named with full
   identity (e.g. nuclide id + Z + N + A; or planet id + host).
4. **Reveal conditions explicit** — the entry documents what later
   reviewed source allows comparison and who controls reveal.
5. **No claim promotion implied** — the entry's `claim_ceiling` field
   states that the prediction by itself is not claim evidence.

The per-domain prediction registry policy
([`prediction-registry-policy.md`](./prediction-registry-policy.md)) adds
additional domain-specific gates.

### Class 6: Claim Authoring (`CLAIM-*`) — Phase 1 Restriction

**In Phase 1 of this protocol, claim status transitions are
maintainer-only.** An agent may not autonomously move a claim from
`DRAFT` to `PARTIALLY_SUPPORTED`, `SUPPORTED`, `REFUTED`, or `SUPERSEDED`.

What an agent **may** do:

- Create a new `CLAIM-*.md` file with `status: DRAFT` and
  `review_tier: AGENT_PROPOSED`, provided that:
  1. At least one referenced `RESULT-*` exists and passes its in-scope
     verification gate.
  2. The claim body uses one of the wording patterns required by
     [`claim-promotion-policy.md`](./claim-promotion-policy.md).
  3. Known out-of-scope failure modes are explicitly listed.
  4. No breakthrough or discovery wording is used.
  5. The `agent_proposal_evaluation` block is populated.
- Add a new `RESULT-*` reference to an **existing** claim's
  `evidence.results` block **without changing the claim's status**.
  Status changes remain maintainer-only.

What an agent may **not** do in Phase 1:

- Move a claim from `DRAFT` to any other status.
- Edit a `MAINTAINER_REVIEWED` or `EXTERNAL_REPLICATED` claim's body
  wording beyond adding a `RESULT-*` reference.
- Re-tier an existing claim's `review_tier` upward.

The intent: the agent's evidence-assembly work is visible (the claim
file is on disk with all referenced evidence) but the act of asserting
"this claim is now supported by evidence" remains a maintainer step.

A Phase 2 relaxation may allow agent-driven `DRAFT → PARTIALLY_SUPPORTED`
once we have empirical experience with Phase 1.

### Class 7: Knowledge Authoring (`KNOW-*`) — Phase 1 Restriction

**In Phase 1 of this protocol, knowledge entries are maintainer-only.**

What an agent **may** do:

- File a `TASK-PROPOSAL` recommending a new `KNOW-*` entry, with a
  drafted body and the linked claims listed.
- Discuss the proposed knowledge in a review document under `docs/reviews/`.

What an agent may **not** do in Phase 1:

- Write a new `KNOW-*` file directly.
- Edit an existing `KNOW-*` file.

Reason: knowledge entries are the strongest form of scientific memory
in the repository. They distill across multiple claims. Until the
maintainer has seen Phase 1 in operation, no agent-written knowledge
files enter the corpus.

A Phase 2 relaxation may allow `AGENT_PROPOSED` knowledge entries once
sufficient `MAINTAINER_REVIEWED` claims exist to distill from.

## What Remains Strictly Maintainer-Only

The following actions remain **maintainer-only** regardless of tier:

- moving any artifact to `SUPPORTED`, `REFUTED`, or `SUPERSEDED`;
- moving any `CLAIM-*` from `DRAFT` to `PARTIALLY_SUPPORTED` (Phase 1);
- creating or editing any `KNOW-*` file (Phase 1);
- pinning a new entry into `results/golden-results.yaml`;
- modifying an entry that is already pinned in `results/golden-results.yaml`;
- merging a PR that promotes an artifact (the PR itself opens as draft;
  the maintainer marks ready and merges — see "PR Discipline" below);
- writing the `review_tier: EXTERNAL_REPLICATED` upgrade record;
- relaxing any rule listed in `global_forbidden` from `apl_mission.py`.

This preserves the maintainer's role as the credibility custodian while
removing the maintainer from the critical path for ordinary visibility
of RESULT-* and PRED-* artifacts.

## PR Discipline for Agent-Proposed Artifacts

A PR that introduces or modifies any artifact with
`review_tier: AGENT_PROPOSED` is subject to the following discipline:

1. **Open as draft.** The PR must be created as a GitHub draft and may
   not be marked ready for review by the agent until a maintainer
   confirms the artifact contents.
2. **No agent auto-merge.** Even if CI is green and any review-helper
   bot returns `MERGE_OK`, the merge step is reserved to the maintainer.
   Agents must not call `gh pr merge` or any equivalent on a PR that
   contains `AGENT_PROPOSED` artifacts.
3. **One artifact class per PR (recommended).** Mixing `AGENT_PROPOSED`
   RESULT-* changes with `AGENT_PROPOSED` PRED-* changes in the same PR
   is allowed but discouraged; per-class PRs are easier to review.
4. **No promotion-chain shortcuts.** An agent may not in the same PR
   (a) create an `AGENT_PROPOSED` `RESULT-*`, (b) reference it from a
   new `AGENT_PROPOSED` `CLAIM-*` it also creates, and (c) reference
   that claim from a new `AGENT_PROPOSED` `KNOW-*` (KNOW-* is in any
   case maintainer-only in Phase 1). Promotion must be staged across
   PRs so each tier is reviewable.
5. **Explicit qualifier in PR body.** The PR description must include
   the sentence "This PR contains AGENT_PROPOSED artifacts that have
   not yet been maintainer-reviewed." so a reader of the PR list sees
   the trust level without opening the diff.

These rules complement, not replace, the per-task `apl_task_pr_helper.py`
flow. They are GitHub-level safeguards on top of repository-level safeguards.

## `agent_proposal_evaluation` Block (Required for `AGENT_PROPOSED` Artifacts)

Every canonical artifact written with `review_tier: AGENT_PROPOSED`
must embed an `agent_proposal_evaluation` block. The block is a small
YAML or front-matter section that records which gates were checked.

Example for a `CLAIM-*` file (Phase 1 — status must remain `DRAFT`):

```yaml
agent_proposal_evaluation:
  review_tier_proposed: AGENT_PROPOSED
  promotion_target_status: DRAFT  # Phase 1: claims stay DRAFT
  gates_checked:
    referenced_results_pass_verification: true
    scope_wording_uses_required_pattern: true
    limitations_explicit: true
    no_breakthrough_wording: true
    no_global_forbidden_violation: true
    agent_did_not_change_existing_claim_status: true
  evidence_summary: >
    Brief 2-3 sentence summary of why the gates above are met. References
    the specific RESULT-* ids and the in-scope verdicts.
  followup_for_maintainer: >
    What the agent would like the maintainer to confirm or override. For
    Phase 1 this typically reads: "If the maintainer agrees with the
    evidence-assembly work, please consider moving status from DRAFT to
    PARTIALLY_SUPPORTED in a separate maintainer-authored PR."
```

Example for a `RESULT-*` file:

```yaml
agent_proposal_evaluation:
  review_tier_proposed: AGENT_PROPOSED
  best_verdict_proposed: PARTIALLY_VALID
  gates_checked:
    deterministic_run: true
    verification_block_populated: true
    input_hashes_recorded: true
    limitations_listed: true
    engine_version_and_commit_pinned: true
    no_protected_artifact_rewrite: true
  evidence_summary: >
    Brief 2-3 sentence summary of what the run produced and why
    PARTIALLY_VALID is the appropriate verdict.
```

A maintainer who later upgrades the artifact to `MAINTAINER_REVIEWED`
should not delete the `agent_proposal_evaluation` block; it remains as
audit history.

## Cross-Reference: Per-Class Authoritative Policies

This master protocol does not duplicate per-class detail. For the strict
per-class rules, consult:

- **CLAIM-***: [`claim-promotion-policy.md`](./claim-promotion-policy.md)
  — DRAFT / PARTIALLY_SUPPORTED / SUPPORTED / REFUTED / SUPERSEDED
  vocabulary and required wording patterns.
- **PRED-***: [`prediction-registry-policy.md`](./prediction-registry-policy.md)
  — registry layout, frozen-state requirements, no-peek state.
- **PRED-*** **reveal**: [`nuclear-prediction-reveal-protocol.md`](./nuclear-prediction-reveal-protocol.md)
  — stepwise reveal workflow for nuclear-mass predictions. Other domains
  may add their own reveal protocols under the same naming convention.
- **Blind holdout benchmark protocol**: [`blind-holdout-benchmark-protocol.md`](./blind-holdout-benchmark-protocol.md)
  — pre-reveal package and reveal record format for any benchmark with
  a before/after target reveal.
- **Campaign curator brief**:
  [`campaign-curator-protocol.md`](./campaign-curator-protocol.md)
  — how a campaign-level promotion decision is recorded.

If any of these policies disagree with this master protocol on a specific
gate, the per-class policy wins for that class.

## What This Protocol Does Not Change

- Existing `CLAIM-*`, `RESULT-*`, `PRED-*`, `KNOW-*` files are unchanged.
  No `DRAFT` claim is promoted by this PR.
- The `global_forbidden` rules from `apl_mission.py` are unchanged.
- The maintainer review agent
  ([`maintainer-review-agent.md`](./maintainer-review-agent.md)) keeps
  its existing authority; it now has a new artifact type
  (`AGENT_PROPOSED` entries) to review on a slower, non-blocking
  cadence.

The four canonical-artifact schemas (`claim`, `result`, `knowledge`,
`prediction`) gain two **optional** fields (`review_tier`,
`agent_proposal_evaluation`) so the protocol's vocabulary is
schema-supported on day one. No existing artifact requires these fields;
new agent-authored artifacts must include them per the gates above.

## Anti-Patterns

The following patterns continue to be wrong and must be flagged in PR
review:

- **Hidden sandbox loop**: writing another `AGENT-RUN-*` for a finding
  that fits one of the seven canonical classes. The mapping table above
  removes the excuse "I did not know where to put it".
- **Discovery wording without `EXTERNAL_REPLICATED`**: language such as
  "breakthrough", "first discovery of", "new physics" remains
  forbidden regardless of tier.
- **Skipping the `agent_proposal_evaluation` block on `AGENT_PROPOSED`
  artifacts**: the block is the artifact's audit trail; without it the
  tier is invalid.
- **Maintainer-tier silence as approval**: a maintainer's failure to
  review does **not** upgrade `AGENT_PROPOSED` to
  `MAINTAINER_REVIEWED`. The upgrade is an explicit edit.
- **Promotion-chain shortcuts**: see PR Discipline rule 4 above.
- **Agent auto-merging an `AGENT_PROPOSED` PR**: see PR Discipline rule
  2 above.
- **Agent moving a CLAIM-* status in Phase 1**: see Class 6 above.
  Status changes are maintainer-only.
- **Agent writing or editing a KNOW-* file in Phase 1**: see Class 7
  above. KNOW-* is entirely maintainer-only in Phase 1.

## Migration Note

The 10 existing `DRAFT` claims, 7 existing `PRED-*` entries, 15 existing
`RESULT-*` artifacts, and 0 existing `KNOW-*` entries all keep their
current status under the implicit `LEGACY_UNTIERED` tier (which is a
validation convenience, not an evidence endorsement — see "Legacy Files"
above). No change.

New agent-driven work starting after this PR merges may use
`AGENT_PROPOSED` to put `RESULT-*` and `PRED-*` artifacts on disk
without maintainer pre-approval, provided the gates above are met and
the `agent_proposal_evaluation` block is populated. Agent-authored
CLAIM-* files are permitted at `status: DRAFT` only in Phase 1.

## Pathway to New Scientific Knowledge

The point of this protocol is not procedural symmetry. It is to make APL
actually produce new scientific knowledge over time. The pathway is:

```
deterministic engine run
      │
      ▼
RESULT-* (AGENT_PROPOSED)              ← agent writes directly
      │
      │  maintainer review (asynchronous, non-blocking)
      ▼
RESULT-* (MAINTAINER_REVIEWED)
      │
      │  maintainer authors a status transition on a referenced CLAIM-*
      ▼
CLAIM-* (MAINTAINER_REVIEWED, PARTIALLY_SUPPORTED or SUPPORTED)
      │
      │  ≥2 same-domain MAINTAINER_REVIEWED claims with a shared lesson
      ▼
KNOW-* (MAINTAINER_REVIEWED)           ← Phase 1: maintainer-only
      │
      │  optional: independent replication by a separate agent / lab
      ▼
review_tier: EXTERNAL_REPLICATED       ← strongest scientific memory
```

Three concrete generators of new scientific knowledge become possible
once this protocol is in force:

1. **Reproducible-baseline accumulation.** Every clean deterministic run
   in any campaign becomes a `RESULT-*` with `AGENT_PROPOSED`
   immediately, instead of sitting in `agent_runs/`. Over weeks the
   `results/` corpus grows from 15 frozen entries into a true baseline
   catalogue (e.g. pendulum approximations at varying angles, nuclear
   semi-empirical residuals across mass ranges, exoplanet failure-map
   regimes). This catalogue is the foundation for any later claim.

2. **Pre-registered predictions with real reveal windows.** The `PRED-*`
   path is already supported for nuclear masses; this protocol makes it
   class-1 work for any domain. An agent can today register a frozen
   forecast for the next AME release, a published exoplanet catalogue
   update, or an upcoming atomic-clock comparison; the reveal-day
   comparison then produces the first real predictive evidence the
   repository owns. Without this protocol, that workflow had no canonical
   home outside nuclear; now it does.

3. **Distilled knowledge from accumulated claims.** Once enough
   `PARTIALLY_SUPPORTED` claims share a common pattern in the same
   domain, a maintainer can write a `KNOW-*` entry that captures the
   cross-claim lesson. Phase 1 keeps `KNOW-*` authoring maintainer-only;
   agents may file a `TASK-PROPOSAL` recommending a knowledge entry but
   not write the file themselves.

The single biggest unlock is that an agent that produces a clean
deterministic run **today** can put it in a canonical, citeable,
accumulating `RESULT-*` location without waiting for the maintainer.
Until the corpus grows, claims and knowledge will remain rare; once the
corpus grows, claim promotion (a maintainer step) and knowledge
authoring (a maintainer step in Phase 1) become tractable.

## First Sprint (What Changes The Day After This Merges)

The following concrete actions become possible immediately and should be
prioritised as the first work after this protocol merges. They are not
authorised by this PR — they are example next tasks.

1. **Backfill `RESULT-*` from existing sandbox `AGENT-RUN-*` runs that
   meet the result gates.** The 35 existing `AGENT-RUN-*` entries
   include several deterministic engine runs that would qualify as
   `RESULT-*` with `AGENT_PROPOSED`. A scoped backfill task can
   promote the qualifying subset over a small number of PRs, growing the
   canonical `results/` corpus immediately without rerunning any
   experiments.

2. **Promote the lowest-risk DRAFT claim through maintainer review.**
   The pendulum claim
   (`CLAIM-0001-pendulum-period-amplitude.md`) already has the cleanest
   evidence and explicitly says inside its own body that
   `PARTIALLY_SUPPORTED` is the safest next status. The maintainer can
   move this claim to `PARTIALLY_SUPPORTED` with
   `review_tier: MAINTAINER_REVIEWED` as the first promoted claim in
   APL history. An agent may prepare the supporting evidence assembly
   PR (referencing the relevant `RESULT-*` ids) but not flip the status.

3. **Pre-register one cross-domain prediction.** Pick one campaign with
   a clear upcoming external reveal (Nuclear → next AME release;
   Exoplanet → next NASA Exoplanet Archive snapshot; Atomic Clocks →
   next published BACON-style comparison) and write a `PRED-*` entry
   with a reveal-day script. An agent may do this autonomously under
   `review_tier: AGENT_PROPOSED`.

4. **Plan the first `KNOW-*` candidate.** Once two same-domain
   `MAINTAINER_REVIEWED` claims exist, a maintainer (not an agent in
   Phase 1) may draft the first knowledge entry.

If these four actions are completed within a few weeks, APL transitions
from "no canonical scientific output" to "an active corpus of
agent-proposed and maintainer-reviewed results, with at least one
pre-registered prediction awaiting reveal and at least one
maintainer-promoted claim". That is the inflection point this protocol
exists to enable.

## Operational Effect (Why This Matters)

Before this protocol, an agent finishing a clean reproducible task had
two paths: write a sandbox `AGENT-RUN-*` (visible but not canonical), or
ask the maintainer to promote. With a single maintainer in a private
alpha, the second path effectively never fires, so 35 sandbox runs sit
beside 0 canonical results.

After this protocol, the same agent has a third path: write the
canonical `RESULT-*` directly (or `PRED-*` for a pre-registration) with
`review_tier: AGENT_PROPOSED` and a populated
`agent_proposal_evaluation` block. The maintainer can review at their
own pace; in the meantime the result is visible, indexable, and
citeable with an explicit trust qualifier. The treadmill stops for
result-class work.

For the more sensitive CLAIM-* and KNOW-* classes, Phase 1 keeps the
maintainer in the loop for any status transition. The agent's work
remains visible (as `DRAFT` claim files with `AGENT_PROPOSED` tier and
evidence assembled) but the assertion that "this claim is supported"
remains a maintainer step. Phase 2 may relax this once we have
operational experience with Phase 1.

This is the operational change. Everything else in this document is the
discipline needed to make it safe.
