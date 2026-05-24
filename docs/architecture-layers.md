# Architecture Layers

APL uses a simple four-layer architecture model. This is an orientation map,
not a request to reorganize the repository layout.

The goal is to help humans and agents understand where work belongs while
keeping the codebase fast to change.

## Layer 1 - Research Agent Core

This layer coordinates work.

It includes:

- mission control and agent onboarding;
- canonical task YAML files;
- generated task views;
- task queue health checks;
- PR review and closeout discipline;
- scientific campaign curator helpers.

Representative files:

- `scripts/apl_mission.py`
- `physics_lab/registry/mission_control.py`
- `physics_lab/registry/campaign_curator.py`
- `docs/agent-task-protocol.md`
- `docs/maintainer-review-agent.md`
- `docs/task-queue-health-policy.md`
- `tasks/TASK-*.yaml`

Rule of thumb: this layer should make good work easier to choose and review.
It should not perform experiments or promote claims by itself.

## Layer 2 - Scientific Memory

This layer stores what APL has learned.

It includes:

- hypotheses;
- experiments;
- canonical results;
- sandbox agent runs;
- claims;
- knowledge notes;
- prediction registries;
- negative and inconclusive evidence.

Representative directories:

- `hypotheses/`
- `experiments/`
- `results/`
- `agent_runs/`
- `claims/`
- `knowledge/`
- `prediction_registry/`
- `docs/reviews/`
- `docs/results/`

Rule of thumb: scientific memory must be versioned, reviewable, and explicit
about limitations. A sandbox result is not a claim.

## Layer 3 - Domain Campaigns

This layer defines the scientific surfaces where agents do useful work.

Current and emerging campaigns include:

- Nuclear Mass Surface;
- Exoplanet Mass-Radius;
- Quantum Size Effects;
- Atomic Clock Residuals;
- Pendulum Formula Falsification;
- Particle Mass Relations;
- Dimensional Analysis Validator.

Representative files:

- `docs/campaigns/`
- `campaign_profiles/`
- campaign-specific protocols under `docs/`
- campaign-specific data folders under `data/`
- campaign-specific runners and loaders under `physics_lab/`

Campaigns can be at different maturity levels:

- `SOURCE_SURFACE`
- `PINNED_DATASET`
- `BASELINE_READY`
- `FAILURE_MAP_READY`
- `HYPOTHESIS_PILOT_READY`
- `PREDICTION_FREEZE_READY`
- `REVEAL_READY`
- `CLAIM_CANDIDATE`
- `NEGATIVE_MEMORY`

Rule of thumb: campaign maturity controls what agents should do next. A
source-gated campaign should receive source/review tasks, not formula search.

## Layer 4 - Data / Reveal / Claim Gates

This layer decides whether evidence is strong enough to move forward.

It includes:

- source manifests;
- artifact checksums;
- direct-row provenance;
- extraction ledgers;
- no-peek and reveal protocols;
- holdout protocols;
- prediction-registry readiness reports;
- result-promotion scorecards;
- public wording reviews.

Representative files:

- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `docs/result-promotion-scorecard.md`
- `physics_lab/schemas/result_candidate_review.schema.json`
- source manifests under `data/`
- prediction registries under `prediction_registry/`

Rule of thumb: this layer is intentionally stricter than the agent layer. It
protects APL from turning interesting patterns into unsupported claims.

## How Work Should Flow

```text
Research Agent Core
  -> chooses a bounded task
  -> runs or reviews a Domain Campaign artifact
  -> stores output in Scientific Memory
  -> passes or fails Data / Reveal / Claim Gates
  -> becomes follow-up work, negative memory, benchmark summary, or claim candidate
```

Most work should touch one or two layers. Broad refactors that touch all four
layers should be rare and explicitly reviewed.

## Non-Goal

This layer model is not a mandate to split packages, move directories, or add
framework abstractions. APL should stay file-based, reviewable, and easy for
agents to navigate until a concrete pain point requires deeper refactoring.
