# Result Promotion Protocol

> **Operating principle.** Agents publish evidence. Agents validate each
> other. Maintainers endorse claims. External data confirms predictions.

## Purpose

This protocol is the **single master document** that an agent or contributor
consults at the end of any task to decide:

1. Which canonical output class their finding belongs to.
2. Where on disk that class lives.
3. What promotion criteria the agent can fulfil **autonomously** versus what
   requires independent agent replay, maintainer review, or external
   replication.

It operationalizes the vocabulary already established by
[AGENTS.md](../AGENTS.md) ("hypothesis / claim / result / knowledge /
theory") and the per-domain policies (claim promotion, prediction
registry, blind-holdout benchmark, nuclear reveal). It does **not** rewrite
those policies; it ties them together and fills three operational gaps:

- a **mapping rule** that turns any task verdict into a canonical destination;
- a **multi-tier review model** that separates *evidence publication* from
  *interpretation endorsement*, so the maintainer is no longer a hard
  bottleneck for every visible scientific artifact;
- an **agent-to-agent validation lane** so the corpus self-corrects without
  waiting for human review of every result.

If this protocol disagrees with the linked per-domain policies on any
specific gate, the per-domain policy wins for that domain.

## Why This Document Exists

As of the current commit there are **387 closed tasks, 35 sandbox
`AGENT-RUN-*` entries, 11 hypotheses, 11 experiments, 10 `DRAFT` claims, 7
`PRED-*` nuclear entries, and 0 `KNOW-*` knowledge artifacts**. The
architecture supports promotion — schemas and per-domain policies all exist
— but agents do not currently have a single document that maps a task
verdict onto a canonical destination, and the unwritten norm has been
"only the maintainer may move anything into `results/`, `claims/`,
`knowledge/`, or `prediction_registry/<non-nuclear>/`". Under a
single-maintainer private alpha that norm guaranteed indefinite
accumulation of sandbox evidence with zero canonical scientific output.

This document is the missing operational layer. The core policy shift is:

| Old rule | New rule |
| --- | --- |
| "No automatic claim promotion." | "Automatic **evidence/result** publication is allowed after mechanical gates. Automatic **claim endorsement** still requires a higher review tier." |

Same credibility floor. Much higher throughput for evidence accumulation.

## Output Classes (Seven)

APL distinguishes seven scientific output classes. Each has a canonical
location, a schema, and a promotion-criteria set.

| # | Class | Canonical path | Schema | Authoritative policy |
| --- | --- | --- | --- | --- |
| 1 | **Benchmark result** | `results/EXP-XXXX/RUN-XXXX/result.yaml` + index in `results/golden-results.yaml` | `physics_lab/schemas/result.schema.json` | This document + [`claim-promotion-policy.md`](./claim-promotion-policy.md) |
| 2 | **Validated-in-scope result** | Same as (1) with non-empty `verification.verdicts` and explicit scope | Same | This document |
| 3 | **Negative / falsification result** | Same as (1) with `best_verdict: FALSIFIED` or `OVERFITTED` | Same | This document |
| 4 | **Partially valid result** | Same as (1) with `best_verdict: PARTIALLY_VALID` or `VALID_IN_RANGE` and an explicit `scope` block | Same | This document + [`claim-promotion-policy.md`](./claim-promotion-policy.md) |
| 5 | **Prediction awaiting reveal** | `prediction_registry/<domain>/PRED-XXXX.yaml` | Domain-specific (e.g. `physics_lab/schemas/nuclear_mass_prediction.schema.json`); generic baseline in `physics_lab/schemas/prediction.schema.json` | [`prediction-registry-policy.md`](./prediction-registry-policy.md), [`blind-holdout-benchmark-protocol.md`](./blind-holdout-benchmark-protocol.md), [`nuclear-prediction-reveal-protocol.md`](./nuclear-prediction-reveal-protocol.md) |
| 6 | **Claim** | `claims/CLAIM-XXXX.md` | `physics_lab/schemas/claim.schema.json` | [`claim-promotion-policy.md`](./claim-promotion-policy.md) |
| 7 | **Knowledge** | `knowledge/KNOW-XXXX.md` | `physics_lab/schemas/knowledge.schema.json` | This document |

Sandbox-only diagnostic evidence (`agent_runs/AGENT-RUN-XXXX/`) remains a
valid intermediate surface but is **not** a canonical output class. The
treadmill that this protocol exists to break is precisely the pattern of
"write another `AGENT-RUN-*` and propose more follow-ups" with nothing
ever crossing into the seven classes above.

## Two Axes: Tier vs Verdict

Every canonical artifact is described along two orthogonal axes.

**Axis 1 — `review_tier` (who has reviewed)**: see "Multi-Tier Review Model"
below.

**Axis 2 — class-specific status / verdict (how strong the evidence is)**:

| Class | Status / verdict field | Vocabulary |
| --- | --- | --- |
| RESULT-* | `best_verdict` | `VALID`, `VALID_IN_RANGE`, `PARTIALLY_VALID`, `INCONCLUSIVE`, `OVERFITTED`, `FALSIFIED` |
| PRED-* | `registry_status` | `DRAFT`, `REGISTERED`, `REVEAL_PENDING`, `REVEAL_COMPLETE`, `SUPERSEDED`, `WITHDRAWN` |
| CLAIM-* | `status` | `DRAFT`, `PARTIALLY_SUPPORTED`, `SUPPORTED`, `REFUTED`, `SUPERSEDED` |
| KNOW-* | (no status field — entry presence implies acceptance into the corpus) | — |

A `RESULT-*` at `best_verdict: FALSIFIED` with `review_tier: AGENT_PUBLISHED`
is a **published negative result** — a legitimate scientific artifact. A
`RESULT-*` at `best_verdict: VALID` with `review_tier: AGENT_PUBLISHED` is
a **published positive result** — also legitimate, but the verdict says
"the engine ran and produced a passing in-scope check", not "this is
endorsed as a claim about nature". The latter requires a CLAIM-* with a
higher tier.

This separation — *verdict* (mechanical) versus *interpretation*
(semantic) — is the core safety property of the protocol.

> **Schema caveat (TASK-0432).** `result.schema.json` does **not** currently
> accept `FALSIFIED` for `best_verdict`; it uses `INVALID` for the
> negative/falsification verdict. Until the schema↔protocol split is resolved
> (see [notes/result-verdict-vocabulary-audit.md](notes/result-verdict-vocabulary-audit.md)),
> publish a negative `RESULT-*` with `best_verdict: INVALID` so it passes
> `validate-repo --strict`. `FALSIFIED` remains the falsification term in the
> `agent_run`, `hypothesis`, and `microtask_run` layers that feed the result.

## Verdict-to-Class Mapping Rule

Every task verdict from this point forward maps onto exactly one canonical
class. Agents must consult this table at end-of-task instead of defaulting
to `agent_runs/`.

| Task verdict (from agent run / lane) | Default canonical class | Notes |
| --- | --- | --- |
| `VALID` | (1) Benchmark result | Strongest verdict. Writes `RESULT-*` with `best_verdict: VALID`. |
| `VALID_IN_RANGE` | (2) Validated-in-scope result | Same path as (1) with explicit `scope` block. |
| `PARTIALLY_VALID` | (4) Partially valid result | Same path as (1) with `best_verdict: PARTIALLY_VALID`, explicit failure modes in `limitations`. |
| `INCONCLUSIVE` | (3) Negative / falsification result | Writes `RESULT-*` with `best_verdict: INCONCLUSIVE`. |
| `OVERFITTED` | (3) Negative / falsification result | `best_verdict: OVERFITTED`. Documents why the candidate failed adversarial controls. |
| `FALSIFIED` | (3) Negative / falsification result | `best_verdict: FALSIFIED`. Documents what was ruled out. Equally valuable. |
| (pre-registration, no verdict yet) | (5) Prediction awaiting reveal | `PRED-*` under the per-domain registry directory. |
| (post-reveal score) | (1)–(4) depending on score | Reveal task writes a new `RESULT-*` referencing the `PRED-*` it scored. |
| (cross-cutting reusable lesson distilled from ≥2 promoted classes) | (7) Knowledge | `KNOW-*` (maintainer-only in Phase 1; see below). |
| (Statement of fact about nature backed by ≥1 result) | (6) Claim | `CLAIM-*`. Status changes are maintainer-only in Phase 1; see below. |

The mapping rule is intentionally generous about (3). Negative,
inconclusive, and overfit results are first-class scientific memory in this
repository.

## Decision Tree (Agent Cheat Sheet)

When an agent finishes a task and is about to write its outputs, it should
walk this tree once:

```
Finished a task. What did I produce?

  ├── Did I write a deterministic engine run with a verdict?
  │     ├── Yes → write a RESULT-* entry (class 1-4 by verdict) with
  │     │        review_tier: AGENT_PUBLISHED. Do not write only an
  │     │        AGENT-RUN-*.
  │     └── No  → was this triage / planning / source curation?
  │              ├── Triage / planning → docs/reviews/<topic>.md
  │              ├── Source curation   → data/<campaign>/source_artifacts/
  │              └── Sandbox-only audit (no engine run) → AGENT-RUN-* is OK
  │
  ├── Am I a second agent independently replaying an existing
  │   AGENT_PUBLISHED RESULT-*?
  │     ├── Yes + metrics match within tolerance → upgrade that RESULT-*'s
  │     │        review_tier to AGENT_VALIDATED and append a
  │     │        validation_record entry.
  │     ├── Yes + metrics drift → open a contested-result PR with the
  │     │        drift documented. Do not silently upgrade.
  │     └── No  → continue.
  │
  ├── Is there a pre-registration step I should record before later reveal?
  │     ├── Yes → write a PRED-* entry under
  │     │        prediction_registry/<domain>/ with
  │     │        review_tier: AGENT_PUBLISHED.
  │     └── No  → continue.
  │
  ├── Does my RESULT-* support an existing CLAIM-* or warrant a new one?
  │     ├── New claim file warranted → may create a new CLAIM-*.md but
  │     │   status MUST remain DRAFT with review_tier: AGENT_PUBLISHED.
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
the finding in a sandbox AGENT-RUN.

## Multi-Tier Review Model

This is the most important change introduced by this document.

### Why a Tier Model

The previous policy treated the maintainer as the only gate for any
canonical scientific artifact. In a single-maintainer private alpha, that
gate becomes a structural bottleneck: even when an agent has produced a
clean reproducible result, the corresponding `RESULT-*` could not appear
in `results/` without explicit human action, and the corpus therefore
accumulated sandbox evidence forever.

This protocol introduces a second axis — `review_tier` — that is
**orthogonal** to the existing status/verdict enums (see "Two Axes"
above). An artifact's verdict describes the evidence strength; its
`review_tier` describes who has reviewed the artifact.

`review_tier` is explicitly **not** an evidence-strength field. An
`AGENT_PUBLISHED` claim that sits at `status: DRAFT` is still
`DRAFT`-strength evidence — the tier just records who wrote the file.

### The Four Tiers

| Tier | Who set it | What it means | Trust qualifier required when citing |
| --- | --- | --- | --- |
| `AGENT_PUBLISHED` | An agent, on its own, after passing the **Result Publication Gate** (Gate A) | The agent assembled a canonical artifact, has populated the required `agent_proposal_evaluation` block, and has not bypassed any global forbidden rule. No second agent or maintainer has reviewed yet. | "Agent-published, not yet independently validated." |
| `AGENT_VALIDATED` | A *different* agent that ran an independent replay and passed the **Independent Replay Gate** (Gate B). | The artifact has been deterministically reproduced by a second agent and the metrics match within tolerance (or any drift is explicitly documented). | "Agent-validated by independent replay; not yet maintainer-reviewed." |
| `MAINTAINER_REVIEWED` | The maintainer, after passing the **Claim Endorsement Gate** (Gate C) for the artifact. | Maintainer has signed off on both the status/verdict and the scope wording. For a CLAIM-* this is the only way to move beyond `DRAFT` in Phase 1. | None required beyond normal scope wording. |
| `EXTERNAL_REPLICATED` | The maintainer, after recording an independent external replication (another lab, another contributor outside the standing agent pool, or a successful external reveal of a pre-registered prediction). | At least one independent party has re-derived the same result from primary sources. The replication record is committed. | None required beyond normal scope wording. |

Tiers are monotonic in trust but not in time:

```
   AGENT_PUBLISHED → AGENT_VALIDATED → MAINTAINER_REVIEWED → EXTERNAL_REPLICATED
                  (Gate B)        (Gate C, asynchronous)  (slow, optional)
```

An artifact may sit in `AGENT_PUBLISHED` indefinitely without harm — it
is visible, indexable, and citeable with the trust qualifier. Another
agent may upgrade it to `AGENT_VALIDATED` at any time by running the
independent replay. A maintainer review later can upgrade further,
downgrade back, or leave it.

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
`LEGACY_UNTIERED` tier does not upgrade their evidence strength.

### Schema Coverage

`review_tier` (optional) and `agent_proposal_evaluation` (optional,
required only when `review_tier: AGENT_PUBLISHED` or
`AGENT_VALIDATED`) are added as optional fields on the four
canonical-artifact schemas in this PR:

- `physics_lab/schemas/result.schema.json`
- `physics_lab/schemas/claim.schema.json`
- `physics_lab/schemas/knowledge.schema.json`
- `physics_lab/schemas/prediction.schema.json`

## The Three Gates

The promotion ladder has three explicit gates. Gates are checked
mechanically wherever possible.

### Gate A — Result Publication Gate (mechanical, agent-autonomous)

An agent may write a new `RESULT-*` or `PRED-*` entry with
`review_tier: AGENT_PUBLISHED` if and only if **all** mechanical
conditions hold:

For `RESULT-*`:

1. **Deterministic run** — the result is produced by a committed
   deterministic engine command (`code_reference` and `command` fields
   filled, replay must reproduce the values).
2. **Verification block populated** — `verification` block lists at least
   one explicit check, with a non-empty `best_verdict`.
3. **Input hashes recorded** — `input_file_hashes` contains every input
   dataset / config used.
4. **Limitations not empty** — `limitations` has at least one entry.
5. **Engine version + git commit pinned** — `engine_version` and
   `git_commit` filled.
6. **Schema validation passes** — `validate-repo --strict
   --fail-on-warnings` returns 0 errors and 0 warnings on the new file.
7. **No protected-artifact rewrite** — does not modify an existing
   `RESULT-*` already pinned in `results/golden-results.yaml`.
8. **No forbidden overclaim wording** — no `global_forbidden` term appears
   in a positive (non-anti-pattern) context.
9. **Dataset provenance valid where applicable** — for results referencing
   source datasets, the source provenance fields (license, checksum,
   retrieval date) are present.

For `PRED-*`: the equivalent mechanical conditions in
[`prediction-registry-policy.md`](./prediction-registry-policy.md):
no-peek state, frozen model reference, named target set, reveal
conditions explicit, non-claim ceiling.

These gates are mechanical. A CI validation step can enforce them. Once
the gates pass, the agent **may publish the canonical artifact without
maintainer pre-approval**. The PR still opens as draft and the
maintainer still merges (see "PR Discipline" below), but the maintainer
is no longer reviewing the scientific content; they are confirming the
gates were applied.

### Gate B — Independent Replay Gate (agent-to-agent, Phase 2)

An *independent* agent (a different `agent_id`, or the same `agent_id`
in a different session with no access to the original's intermediate
state) may upgrade an `AGENT_PUBLISHED` artifact to `AGENT_VALIDATED`
if and only if:

1. **Same inputs** — the replay uses the exact `input_file_hashes` from
   the published artifact.
2. **Same deterministic command** — the replay runs the published
   `command` against the published `code_reference` at the published
   `git_commit`.
3. **Metrics match within tolerance** — the produced metrics agree with
   the published metrics within a documented tolerance, OR any drift is
   explicitly captured in a `validation_record` block on the artifact
   (drift then triggers a contested-result PR rather than a silent
   upgrade).
4. **Verdict unchanged** — the replay produces the same `best_verdict`.
5. **No protected-artifact rewrite** — the upgrade PR adds a
   `validation_record` and bumps `review_tier`; it does not edit
   metrics, verdict, or any other field.

Gate B review metadata is not part of the golden-result material hash.
Changing `review_tier`, `agent_proposal_evaluation`, or replay bookkeeping
paths records who replayed the result and how; it does not by itself justify a
scientific rebaseline. Scores, verification metrics, `best_model_id`,
`best_verdict`, input file SHA-256 digests, and other interpretation-changing
result payload fields remain material hash inputs.

**Phase 1 status of Gate B:** the gate definition is final, but the
agent-side replay tooling (a thin runner that wraps `command` and
diff-checks metrics) is a separate follow-up task. Until that tooling
lands, `AGENT_VALIDATED` may only be set by the maintainer after a
manual replay. Phase 2 enables agent-autonomous Gate B.

### Gate C — Claim Endorsement Gate (maintainer-only in Phase 1)

This gate gates **interpretation**, not evidence. An artifact passes
Gate C only when a maintainer (or external replication record) confirms
that the scope wording and scientific status of the artifact matches the
underlying evidence.

In Phase 1, Gate C is required for:

- Any `CLAIM-*` status change away from `DRAFT`.
- Any `KNOW-*` create or edit (KNOW-* is entirely maintainer-only in
  Phase 1).
- Pinning a `RESULT-*` into `results/golden-results.yaml`.
- Modifying any artifact already pinned in `golden-results.yaml`.
- Recording `review_tier: EXTERNAL_REPLICATED`.
- Relaxing any `global_forbidden` rule.

In Phase 2 (after operational experience with Phase 1) Gate C may relax
for `DRAFT → PARTIALLY_SUPPORTED` claim transitions if backed by at
least one `AGENT_VALIDATED` result and the agent satisfies the existing
[`claim-promotion-policy.md`](./claim-promotion-policy.md) wording
requirements.

## Agent Authoring Rules Per Class

### Classes 1–4: `RESULT-*` — agent-autonomous via Gate A

An agent may write a new `RESULT-*` with `review_tier: AGENT_PUBLISHED`
once Gate A passes. The `agent_proposal_evaluation` block must list
which Gate A conditions were verified.

A second agent may upgrade `AGENT_PUBLISHED` → `AGENT_VALIDATED` via
Gate B (Phase 2 once replay tooling lands; maintainer-mediated until
then).

### Class 5: `PRED-*` — agent-autonomous via Gate A

An agent may write a new `PRED-*` with `review_tier: AGENT_PUBLISHED`
once the Gate A conditions in
[`prediction-registry-policy.md`](./prediction-registry-policy.md) pass.

### Class 6: `CLAIM-*` — agent may **author**, maintainer **endorses**

What an agent **may** do:

- Create a new `CLAIM-*.md` file with `status: DRAFT` and
  `review_tier: AGENT_PUBLISHED`, provided the
  [`claim-promotion-policy.md`](./claim-promotion-policy.md) authoring
  requirements (referenced `RESULT-*`, scope wording pattern, explicit
  limitations, no breakthrough wording) are met and the
  `agent_proposal_evaluation` block is populated.
- Add a new `RESULT-*` reference to an **existing** claim's
  `evidence.results` block **without changing the claim's status**.

What an agent may **not** do in Phase 1:

- Move a claim from `DRAFT` to any other status (Gate C).
- Edit a `MAINTAINER_REVIEWED` or `EXTERNAL_REPLICATED` claim's body
  wording beyond adding a `RESULT-*` reference.
- Re-tier an existing claim's `review_tier` upward.

A Phase 2 relaxation may allow agent-driven `DRAFT → PARTIALLY_SUPPORTED`
when the referenced `RESULT-*` is `AGENT_VALIDATED` (i.e. an independent
agent has confirmed the result).

### Class 7: `KNOW-*` — maintainer-only in Phase 1

What an agent **may** do:

- File a `TASK-PROPOSAL` recommending a new `KNOW-*` entry, with a
  drafted body and the linked claims listed.

What an agent may **not** do in Phase 1:

- Write a new `KNOW-*` file directly.
- Edit an existing `KNOW-*` file.

A Phase 2 relaxation may allow `AGENT_PUBLISHED` knowledge entries once
sufficient `MAINTAINER_REVIEWED` claims exist to distill from.

## What Remains Strictly Maintainer-Only

The following actions remain **maintainer-only** regardless of tier:

- moving any artifact to `SUPPORTED`, `REFUTED`, or `SUPERSEDED`;
- moving any `CLAIM-*` from `DRAFT` to `PARTIALLY_SUPPORTED` (Phase 1);
- creating or editing any `KNOW-*` file (Phase 1);
- pinning a new entry into `results/golden-results.yaml`;
- modifying an entry that is already pinned in `results/golden-results.yaml`;
- merging a PR that contains `AGENT_PUBLISHED` artifacts (the agent
  opens the PR as draft; the maintainer marks ready and merges — see
  "PR Discipline" below);
- writing the `review_tier: EXTERNAL_REPLICATED` upgrade record;
- relaxing any rule listed in `global_forbidden` from `apl_mission.py`.

This preserves the maintainer's role as the credibility custodian for
*interpretation* while removing the maintainer from the critical path
for *evidence visibility*.

## PR Discipline for Agent-Authored Artifacts

A PR that introduces or modifies any artifact with
`review_tier: AGENT_PUBLISHED` or `AGENT_VALIDATED` is subject to the
following discipline:

1. **Open as draft.** The PR must be created as a GitHub draft and may
   not be marked ready for review by the agent until a maintainer
   confirms the gates were applied. The agent may run
   `apl_review_pr.py` to confirm gates mechanically, but readiness
   marking is the maintainer's call.
2. **No agent auto-merge.** Even if CI is green and the review-helper
   bot returns `MERGE_OK`, the merge step is reserved to the maintainer
   in Phase 1. Phase 2 may introduce a labelled auto-merge lane for
   pure RESULT-* / PRED-* publication PRs that pass Gate A
   mechanically, gated by branch protection. That auto-merge lane is
   **not** enabled by this PR.
3. **One artifact class per PR (recommended).** Mixing `AGENT_PUBLISHED`
   RESULT-* changes with `AGENT_PUBLISHED` PRED-* changes in the same
   PR is allowed but discouraged.
4. **No promotion-chain shortcuts.** An agent may not in the same PR
   (a) create an `AGENT_PUBLISHED` `RESULT-*`, (b) reference it from a
   new `AGENT_PUBLISHED` `CLAIM-*` it also creates, and (c) reference
   that claim from a new `AGENT_PUBLISHED` `KNOW-*` (KNOW-* is in any
   case maintainer-only in Phase 1). Promotion must be staged across
   PRs so each tier is reviewable.
5. **Explicit qualifier in PR body.** The PR description must include
   one of the sentences:
   - "This PR contains AGENT_PUBLISHED artifacts that have not yet been
     independently validated or maintainer-reviewed."
   - "This PR upgrades AGENT_PUBLISHED artifact(s) to AGENT_VALIDATED
     via independent replay; the upgrade is not maintainer endorsement."
6. **Contested-result PRs follow the same discipline.** If an agent's
   replay produces drift that prevents an `AGENT_PUBLISHED` →
   `AGENT_VALIDATED` upgrade, the contesting agent opens a separate PR
   that adds a `validation_record` entry documenting the drift; it
   does **not** mutate the original published metrics.

## `agent_proposal_evaluation` Block

Every canonical artifact written with `review_tier: AGENT_PUBLISHED`
must embed an `agent_proposal_evaluation` block. The block records
which Gate A conditions were checked. The same block format is reused
for `AGENT_VALIDATED` upgrades by adding a `validation_record` entry.

Example for a `RESULT-*` file (Gate A):

```yaml
agent_proposal_evaluation:
  review_tier_proposed: AGENT_PUBLISHED
  best_verdict_proposed: PARTIALLY_VALID
  gates_checked:
    deterministic_run: true
    verification_block_populated: true
    input_hashes_recorded: true
    limitations_listed: true
    engine_version_and_commit_pinned: true
    schema_validation_passes: true
    no_protected_artifact_rewrite: true
    no_forbidden_overclaim_wording: true
    dataset_provenance_valid: true
  evidence_summary: >
    Brief 2-3 sentence summary of what the run produced and why
    PARTIALLY_VALID is the appropriate verdict.
```

Example for an `AGENT_VALIDATED` upgrade (Gate B, added on top of an
existing `AGENT_PUBLISHED` block):

```yaml
agent_proposal_evaluation:
  review_tier_proposed: AGENT_VALIDATED
  best_verdict_proposed: PARTIALLY_VALID  # unchanged from original
  gates_checked:
    same_inputs_used: true
    same_deterministic_command_used: true
    metrics_match_within_tolerance: true
    verdict_unchanged: true
    no_protected_artifact_rewrite: true
  evidence_summary: >
    Independent replay by <agent_id_2> reproduced the published
    metrics within 1e-6 absolute tolerance on all reported subsets.
  validation_record:
    replayed_by:
      contributor_id: roman
      agent_id: codex   # different from original AGENT_PUBLISHED author
    replayed_at_utc: 2026-06-01T12:00:00Z
    replay_command: <same as published>
    tolerance_used: 1.0e-6
    drift_observed: none
```

Example for a `CLAIM-*` file (Phase 1 — status stays `DRAFT`):

```yaml
agent_proposal_evaluation:
  review_tier_proposed: AGENT_PUBLISHED
  promotion_target_status: DRAFT  # Phase 1: claims stay DRAFT
  gates_checked:
    referenced_results_pass_verification: true
    scope_wording_uses_required_pattern: true
    limitations_explicit: true
    no_breakthrough_wording: true
    no_global_forbidden_violation: true
    agent_did_not_change_existing_claim_status: true
  evidence_summary: >
    Brief 2-3 sentence summary of why the gates above are met.
  followup_for_maintainer: >
    If the maintainer agrees with the evidence-assembly work, please
    consider moving status from DRAFT to PARTIALLY_SUPPORTED in a
    separate maintainer-authored PR.
```

A maintainer who later upgrades the artifact to `MAINTAINER_REVIEWED`
should not delete the block; it remains as audit history.

## Cross-Reference: Per-Class Authoritative Policies

This master protocol does not duplicate per-class detail. For the strict
per-class rules, consult:

- **CLAIM-***: [`claim-promotion-policy.md`](./claim-promotion-policy.md)
  — DRAFT / PARTIALLY_SUPPORTED / SUPPORTED / REFUTED / SUPERSEDED
  vocabulary and required wording patterns.
- **PRED-***: [`prediction-registry-policy.md`](./prediction-registry-policy.md)
  — registry layout, frozen-state requirements, no-peek state.
- **PRED-*** **reveal**: [`nuclear-prediction-reveal-protocol.md`](./nuclear-prediction-reveal-protocol.md)
  — stepwise reveal workflow for nuclear-mass predictions.
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
- The four canonical-artifact schemas gain two **optional** fields
  (`review_tier`, `agent_proposal_evaluation`); no existing artifact
  requires these fields.
- GitHub-level branch-protection / auto-merge configuration is NOT
  changed by this PR. The Phase 2 auto-merge lane for pure Gate A
  publication PRs requires a separate task to wire up the
  `safe-publication` label, the branch-protection allowlist, and the
  CI workflow that checks Gate A mechanically.

## Anti-Patterns

- **Hidden sandbox loop**: writing another `AGENT-RUN-*` for a finding
  that fits one of the seven canonical classes.
- **Discovery wording without `EXTERNAL_REPLICATED`**: language such as
  "breakthrough", "first discovery of", "new physics", "proved",
  "solved" remains forbidden regardless of tier.
- **Skipping the `agent_proposal_evaluation` block on `AGENT_PUBLISHED`
  or `AGENT_VALIDATED` artifacts**: the block is the artifact's audit
  trail; without it the tier is invalid.
- **Silent metric edit during AGENT_VALIDATED upgrade**: the validating
  agent may not edit any field except `review_tier` and
  `agent_proposal_evaluation`. Any drift requires a contested-result PR.
- **Maintainer-tier silence as approval**: a maintainer's failure to
  review does **not** upgrade `AGENT_PUBLISHED` to `AGENT_VALIDATED` or
  `MAINTAINER_REVIEWED`. The upgrade is an explicit edit.
- **Promotion-chain shortcuts**: see PR Discipline rule 4 above.
- **Agent auto-merging an `AGENT_PUBLISHED` PR in Phase 1**: see PR
  Discipline rule 2 above.
- **Agent moving a CLAIM-* status in Phase 1**: see Class 6 above.
- **Agent writing or editing a KNOW-* file in Phase 1**: see Class 7
  above.

## Migration Note

The 10 existing `DRAFT` claims, 7 existing `PRED-*` entries, 15 existing
`RESULT-*` artifacts, and 0 existing `KNOW-*` entries all keep their
current status under the implicit `LEGACY_UNTIERED` tier. No change.

New agent-driven work starting after this PR merges may use
`AGENT_PUBLISHED` to put `RESULT-*` and `PRED-*` artifacts on disk
without maintainer pre-approval, provided Gate A passes and the
`agent_proposal_evaluation` block is populated. Agent-authored CLAIM-*
files are permitted at `status: DRAFT` only in Phase 1. KNOW-* remains
maintainer-only in Phase 1.

## Pathway to New Scientific Knowledge

```
deterministic engine run
      │
      │  (Gate A — mechanical, agent-autonomous)
      ▼
RESULT-* (AGENT_PUBLISHED)              ← agent writes directly
      │
      │  (Gate B — independent agent replay, Phase 2)
      ▼
RESULT-* (AGENT_VALIDATED)              ← second agent confirms
      │
      │  (Gate C — maintainer endorsement, semantic)
      ▼
RESULT-* (MAINTAINER_REVIEWED) + CLAIM-* status transition
      │
      │  ≥2 same-domain MAINTAINER_REVIEWED claims with a shared lesson
      ▼
KNOW-* (MAINTAINER_REVIEWED)            ← Phase 1: maintainer-only
      │
      │  optional: independent external replication
      ▼
review_tier: EXTERNAL_REPLICATED        ← strongest scientific memory
```

Three concrete generators of new scientific knowledge become possible
once this protocol is in force:

1. **Reproducible-baseline accumulation.** Every clean deterministic run
   in any campaign becomes a `RESULT-*` with `AGENT_PUBLISHED`
   immediately, instead of sitting in `agent_runs/`. Over weeks the
   `results/` corpus grows from 15 frozen entries into a true baseline
   catalogue.

2. **Agent-to-agent replay validation.** A standing replay agent can
   walk recent `AGENT_PUBLISHED` results and upgrade them to
   `AGENT_VALIDATED` via Gate B, producing a self-correcting corpus
   that does not depend on maintainer time per artifact.

3. **Pre-registered predictions with real reveal windows.** The `PRED-*`
   path now works for any domain. Agents can register frozen forecasts
   autonomously; reveal-day comparison produces the first real
   predictive evidence the repository owns.

## First Sprint (What Changes The Day After This Merges)

These actions become possible immediately and should be prioritised as
the first work after this protocol merges. They are not authorised by
this PR — they are example next tasks.

1. **Backfill `RESULT-*` from existing sandbox `AGENT-RUN-*` runs that
   meet Gate A.** Scoped backfill task can promote the qualifying
   subset over a small number of PRs.
2. **Wire Gate B replay tooling.** A small runner that wraps a published
   `command`, re-executes it deterministically, and produces a
   `validation_record` diff — enables agent-to-agent validation lane.
3. **Promote the lowest-risk DRAFT claim through Gate C.** Pendulum
   (`CLAIM-0001`) is the safest first target. An agent prepares
   evidence assembly; the maintainer flips the status.
4. **Pre-register one cross-domain prediction under Gate A.** Pick a
   campaign with a clear upcoming external reveal.
5. **(Phase 2) Wire the `safe-publication` auto-merge lane.** A
   GitHub Actions workflow that mechanically checks Gate A and, if all
   green, allows `safe-publication`-labelled PRs to be merged without
   maintainer click. Requires explicit maintainer authorisation to
   enable.

## Operational Effect (Why This Matters)

Before this protocol, an agent finishing a clean reproducible task had
two paths: write a sandbox `AGENT-RUN-*` (visible but not canonical), or
ask the maintainer to promote. With a single maintainer in a private
alpha, the second path effectively never fires.

After this protocol, the same agent has a third path: write the
canonical `RESULT-*` directly (or `PRED-*` for a pre-registration) with
`review_tier: AGENT_PUBLISHED` and a populated
`agent_proposal_evaluation` block. The maintainer can review at their
own pace; in the meantime the result is visible, indexable, and
citeable with an explicit trust qualifier. A second agent can upgrade
to `AGENT_VALIDATED` autonomously via Gate B (once Phase 2 tooling
lands).

For the more sensitive CLAIM-* and KNOW-* classes, Phase 1 keeps the
maintainer in the loop for any interpretation step. The agent's work
remains visible (as `DRAFT` claim files with `AGENT_PUBLISHED` tier and
evidence assembled) but the assertion that "this claim is supported"
remains a maintainer step. Phase 2 may relax this once we have
operational experience and a working Gate B agent-replay lane.

This is the operational change. Everything else in this document is the
discipline needed to make it safe.
