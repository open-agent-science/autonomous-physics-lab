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
| (cross-cutting reusable lesson distilled from ≥2 promoted classes) | (7) Knowledge | `KNOW-*`. |
| (Statement of fact about nature backed by ≥1 result) | (6) Claim | `CLAIM-*`. Claim references `RESULT-*` ids in its `evidence.results` block. |

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
  │     ├── Yes → write a RESULT-* entry (class 1-4 by verdict). Do not
  │     │        write only an AGENT-RUN-*.
  │     └── No  → was this triage / planning / source curation?
  │              ├── Triage / planning → docs/reviews/<topic>.md
  │              ├── Source curation   → data/<campaign>/source_artifacts/
  │              └── Sandbox-only audit (no engine run) → AGENT-RUN-* is OK
  │
  ├── Is there a pre-registration step I should record before later reveal?
  │     ├── Yes → write a PRED-* entry under
  │     │        prediction_registry/<domain>/.
  │     └── No  → continue.
  │
  ├── Does my RESULT-* support an existing CLAIM-* or warrant a new one?
  │     ├── Yes + I meet the agent-promotion gates below
  │     │   → either create a new CLAIM-*.md or update an existing one
  │     │     with status PARTIALLY_SUPPORTED and review_tier:
  │     │     AGENT_SELF_PROMOTED.
  │     └── No → continue.
  │
  └── Does this finding generalise across ≥2 promoted CLAIM-* or RESULT-*
        in the same domain?
        ├── Yes → write KNOW-* with review_tier: AGENT_SELF_PROMOTED.
        └── No  → done.
```

The bias is towards **writing the canonical record** rather than burying
the finding in a sandbox AGENT-RUN. The `review_tier` field below makes
that safe.

## Multi-Tier Review Model

This is the most important change introduced by this document.

### Why a Tier Model

The previous policy treated the maintainer as the only gate for any
canonical scientific artifact. In a single-maintainer private alpha, that
gate becomes a structural bottleneck: even when an agent has produced a
clean reproducible result, the corresponding `CLAIM-*` cannot move out of
`DRAFT` without explicit human action, and there is no incentive to do so
quickly. The corpus therefore accumulates sandbox evidence forever.

This protocol introduces a second axis — `review_tier` — that is
**orthogonal** to the existing status enum. An artifact's status (`DRAFT`,
`PARTIALLY_SUPPORTED`, `SUPPORTED`, etc.) describes the evidence strength;
its `review_tier` describes who has reviewed it.

### The Three Tiers

| Tier | Who set it | What it means | Trust qualifier required when citing |
| --- | --- | --- | --- |
| `AGENT_SELF_PROMOTED` | An agent, on its own, after meeting the agent-promotion gates. | The agent believes the evidence supports the claimed status, has filled the required self-evaluation block, and has not bypassed any global forbidden rule. The maintainer has not yet reviewed. | "Agent-promoted, not yet maintainer-reviewed." |
| `MAINTAINER_REVIEWED` | The maintainer, after reading the artifact and its evidence. | Maintainer has signed off on both the status and the scope wording. | None required beyond normal scope wording. |
| `EXTERNAL_REPLICATED` | The maintainer, after recording an independent replication. | At least one independent contributor / agent / lab has re-derived the same result from primary sources. The replication record is committed. | None required beyond normal scope wording. |

Tiers are monotonic in trust but not in time:

```
   AGENT_SELF_PROMOTED  →  MAINTAINER_REVIEWED  →  EXTERNAL_REPLICATED
                       (asynchronous)        (slow, optional)
```

A claim may sit in `AGENT_SELF_PROMOTED` indefinitely without harm — it is
visible, scored, and citeable with the trust qualifier. A maintainer
review later can upgrade it, downgrade it back to `DRAFT`, or leave it.
The maintainer is no longer a hard gate on visibility.

### Schema Implication

`review_tier` is added as an **optional** field on `CLAIM-*`, `RESULT-*`,
`KNOW-*`, and `PRED-*` files. Files committed before this protocol have
no `review_tier` value; for backward compatibility they are treated as
`MAINTAINER_REVIEWED` (which is the implicit assumption all existing
files were committed under). New agent-promoted files **must** set
`review_tier: AGENT_SELF_PROMOTED` explicitly.

Schema-level changes are intentionally minimal in this protocol PR. A
follow-up may extend the schemas to require `review_tier` on new
artifacts; this PR leaves it optional to avoid breaking validation on the
existing 10 DRAFT claims and 7 PRED entries.

## Agent Promotion Gates (Per Class)

These are the **autonomous** gates an agent must satisfy before writing
`review_tier: AGENT_SELF_PROMOTED` on any canonical artifact. An agent
that cannot meet all listed gates for a class must downgrade to a lower
class or stop at sandbox.

### Class 1–4: Result Promotion Gates (`RESULT-*`)

An agent may write a new `RESULT-*` entry with `review_tier:
AGENT_SELF_PROMOTED` if and only if:

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
AGENT_SELF_PROMOTED` if and only if:

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

### Class 6: Claim Promotion Gates (`CLAIM-*`)

An agent may move an existing `CLAIM-*` from `DRAFT` to
`PARTIALLY_SUPPORTED` with `review_tier: AGENT_SELF_PROMOTED` if and only
if:

1. **At least one referenced `RESULT-*` exists** and passes its in-scope
   verification gate (i.e. is `MAINTAINER_REVIEWED` or
   `AGENT_SELF_PROMOTED` itself with the gates above met).
2. **Scope language present** — the claim body uses one of the wording
   patterns required by
   [`claim-promotion-policy.md`](./claim-promotion-policy.md) (e.g.
   "valid only within the tested range", "for the linear, unforced
   case").
3. **Limitations explicit** — the claim body lists known out-of-scope
   failure modes.
4. **No breakthrough or discovery wording** — the existing
   `global_forbidden` rules from `apl_mission.py` remain in force.
5. **Self-evaluation block filled** — the claim file contains an
   `agent_self_evaluation` section explaining which gates were checked
   and which were not.

An agent may **not** autonomously move a claim to `SUPPORTED`. Promoting
to `SUPPORTED` requires `MAINTAINER_REVIEWED` or higher.

An agent may **not** autonomously move a claim to `REFUTED` or
`SUPERSEDED`. Those transitions still require maintainer action because
they invalidate prior published memory.

### Class 7: Knowledge Promotion Gates (`KNOW-*`)

An agent may write a new `KNOW-*` entry with `review_tier:
AGENT_SELF_PROMOTED` if and only if:

1. **Source claims listed** — `linked_objects.claims` references at
   least two existing claims (each at `PARTIALLY_SUPPORTED` or stronger,
   any tier).
2. **Common domain** — the linked claims share a `domain`.
3. **Reusable assertion** — the body states a reusable lesson that is
   not simply the conjunction of the source claims.
4. **No new claim is being created in the same PR** — knowledge
   promotion may not be used as a backdoor to bypass the claim gates.

## What Remains Strictly Maintainer-Only

The following actions remain **maintainer-only** regardless of tier:

- moving any artifact to `SUPPORTED`, `REFUTED`, or `SUPERSEDED`;
- pinning a new entry into `results/golden-results.yaml`;
- modifying an entry that is already pinned in `results/golden-results.yaml`;
- merging a PR that promotes an artifact (the PR itself opens as draft;
  the maintainer marks ready and merges);
- writing the `review_tier: EXTERNAL_REPLICATED` upgrade record;
- relaxing any rule listed in `global_forbidden` from `apl_mission.py`.

This preserves the maintainer's role as the credibility custodian while
removing the maintainer from the critical path for ordinary visibility.

## Self-Evaluation Block (Required for Agent-Promoted Artifacts)

Every canonical artifact written with `review_tier: AGENT_SELF_PROMOTED`
must embed a self-evaluation block. The block is a small YAML or
front-matter section that records which gates were checked.

Example for a `CLAIM-*` file:

```yaml
agent_self_evaluation:
  review_tier_proposed: AGENT_SELF_PROMOTED
  promotion_target_status: PARTIALLY_SUPPORTED
  gates_checked:
    referenced_results_pass_verification: true
    scope_wording_uses_required_pattern: true
    limitations_explicit: true
    no_breakthrough_wording: true
    no_global_forbidden_violation: true
  evidence_summary: >
    Brief 2-3 sentence summary of why these gates are met. References
    the specific RESULT-* ids and the in-scope verdicts.
  followup_for_maintainer: >
    What the agent would like the maintainer to confirm or override.
```

Example for a `RESULT-*` file:

```yaml
agent_self_evaluation:
  review_tier_proposed: AGENT_SELF_PROMOTED
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
should not delete the `agent_self_evaluation` block; it remains as audit
history.

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
- Existing schemas for `CLAIM-*`, `RESULT-*`, `KNOW-*` are unchanged.
  The `review_tier` field is documented here as required for new
  agent-promoted artifacts but is not enforced via schema in this PR; a
  follow-up may enforce it after the corpus has caught up.
- The `global_forbidden` rules from `apl_mission.py` are unchanged.
- The maintainer review agent
  ([`maintainer-review-agent.md`](./maintainer-review-agent.md)) keeps
  its existing authority; it now has a new artifact type
  (`AGENT_SELF_PROMOTED` entries) to review on a slower, non-blocking
  cadence.

## Anti-Patterns

The following patterns continue to be wrong and must be flagged in PR
review:

- **Hidden sandbox loop**: writing another `AGENT-RUN-*` for a finding
  that fits one of the seven canonical classes. The mapping table above
  removes the excuse "I did not know where to put it".
- **Discovery wording without `EXTERNAL_REPLICATED`**: language such as
  "breakthrough", "first discovery of", "new physics" remains
  forbidden regardless of tier.
- **Skipping the self-evaluation block on `AGENT_SELF_PROMOTED`
  artifacts**: the block is the artifact's audit trail; without it the
  tier is invalid.
- **Maintainer-tier silence as approval**: a maintainer's failure to
  review does **not** upgrade `AGENT_SELF_PROMOTED` to
  `MAINTAINER_REVIEWED`. The upgrade is an explicit edit.
- **Promotion-chain shortcuts**: an agent may not in the same PR (a)
  create a `RESULT-*` with `AGENT_SELF_PROMOTED`, (b) reference it from
  a new `AGENT_SELF_PROMOTED` `CLAIM-*`, and (c) reference that claim
  from an `AGENT_SELF_PROMOTED` `KNOW-*`. Promotion must be staged
  across PRs so each tier is reviewable.

## Migration Note

The 10 existing `DRAFT` claims, 7 existing `PRED-*` entries, 15 existing
`RESULT-*` artifacts, and 0 existing `KNOW-*` entries all keep their
current status under the implicit `MAINTAINER_REVIEWED` tier. No change.

New agent-driven work starting after this PR merges may use
`AGENT_SELF_PROMOTED` to put canonical artifacts on disk without
maintainer pre-approval, provided the gates above are met and the
self-evaluation block is populated.

## Pathway to New Scientific Knowledge

The point of this protocol is not procedural symmetry. It is to make APL
actually produce new scientific knowledge over time. The pathway is:

```
deterministic engine run
      │
      ▼
RESULT-* (AGENT_SELF_PROMOTED)         ← agent writes directly
      │
      │  same-domain accumulation across multiple PRs by multiple agents
      ▼
CLAIM-* (AGENT_SELF_PROMOTED, PARTIALLY_SUPPORTED)
      │
      │  asynchronous maintainer review (no longer gating)
      ▼
CLAIM-* (MAINTAINER_REVIEWED, PARTIALLY_SUPPORTED or SUPPORTED)
      │
      │  ≥2 same-domain MAINTAINER_REVIEWED claims with a shared lesson
      ▼
KNOW-* (AGENT_SELF_PROMOTED → MAINTAINER_REVIEWED)
      │
      │  optional: independent replication by a separate agent / lab
      ▼
review_tier: EXTERNAL_REPLICATED   ← strongest scientific memory
```

Three concrete generators of new scientific knowledge become possible
once this protocol is in force:

1. **Reproducible-baseline accumulation.** Every clean deterministic run
   in any campaign becomes a `RESULT-*` with `AGENT_SELF_PROMOTED`
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
   domain (for example: "high-error nuclear residuals cluster around
   near-magic regions across multiple training slices"), an agent can
   write a `KNOW-*` entry that captures the cross-claim lesson. This is
   the path from individual claims to reusable physics knowledge.

The single biggest unlock is that an agent that produces a clean result
**today** can put it in a canonical, citeable, accumulating location
without waiting for the maintainer. Until the corpus grows, claims and
knowledge will remain rare; once the corpus grows, they become inevitable.

## First Sprint (What Changes The Day After This Merges)

The following concrete actions become possible immediately and should be
prioritised as the first work after this protocol merges. They are not
authorised by this PR — they are example next tasks.

1. **Backfill `RESULT-*` from existing sandbox `AGENT-RUN-*` runs that
   meet the result gates.** The 35 existing `AGENT-RUN-*` entries
   include several deterministic engine runs that would qualify as
   `RESULT-*` with `AGENT_SELF_PROMOTED`. A scoped backfill task can
   promote the qualifying subset over a small number of PRs, growing the
   canonical `results/` corpus immediately without rerunning any
   experiments.

2. **Promote the lowest-risk DRAFT claim through the new tier.** The
   pendulum claim (`CLAIM-0001-pendulum-period-amplitude.md`) already
   has the cleanest evidence and explicitly says inside its own body
   that `PARTIALLY_SUPPORTED` is the safest next status. An agent
   promoting it to `PARTIALLY_SUPPORTED` with
   `review_tier: AGENT_SELF_PROMOTED` and a populated
   `agent_self_evaluation` block is the smoke test that proves the new
   protocol works.

3. **Pre-register one cross-domain prediction.** Pick one campaign with
   a clear upcoming external reveal (Nuclear → next AME release;
   Exoplanet → next NASA Exoplanet Archive snapshot; Atomic Clocks →
   next published BACON-style comparison) and write a `PRED-*` entry
   with a reveal-day script. This is the only path to a real "first
   discovery" outcome.

4. **Document the first `KNOW-*` candidate.** Once two same-domain
   `MAINTAINER_REVIEWED` claims exist, draft the first knowledge entry.
   This is intentionally listed last because it depends on (2)
   producing reviewed claims first.

If these four actions are completed within a few weeks, APL transitions
from "no canonical scientific output" to "an active corpus of
agent-promoted and maintainer-reviewed results, with at least one
pre-registered prediction awaiting reveal". That is the inflection point
this protocol exists to enable.

## Operational Effect (Why This Matters)

Before this protocol, an agent finishing a clean reproducible task had
two paths: write a sandbox `AGENT-RUN-*` (visible but not canonical), or
ask the maintainer to promote. With a single maintainer in a private
alpha, the second path effectively never fires, so 35 sandbox runs sit
beside 0 canonical results.

After this protocol, the same agent has a third path: write the
canonical `RESULT-*` directly with `review_tier: AGENT_SELF_PROMOTED`
and a populated self-evaluation block. The maintainer can review at
their own pace; in the meantime the result is visible, indexable, and
citeable with an explicit trust qualifier. The treadmill stops.

This is the operational change. Everything else in this document is the
discipline needed to make it safe.
