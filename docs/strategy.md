# Strategy

## Current Phase

`v0.2-public-alpha candidate — multi-campaign agent research network hardening`

The repository is still gated by maintainer review and release discipline, but
the strategic center has moved from a single flagship/private-alpha dry run to a
multi-campaign network where many agents can safely work in parallel.

The next capability milestone after `v0.2` is **`v0.3` — the Research Factory
Layer**: a reusable bounded workflow that turns one-lane audits into
high-throughput, controls-first candidate generation routed into negative and
shortlist memory (no automatic claims). Exit criteria and sequencing are in
[roadmap.md](./roadmap.md) (`v0.3 — Research Factory Layer`).

## Mission

Build verification-first scientific infrastructure for testing, falsifying,
scoring, and reusing physics hypotheses.

## Strategic North Star

Open Agent Science is the umbrella goal: prove that human-owned AI agents can
produce reproducible, reviewable, citable scientific outputs in shared public
memory.

Autonomous Physics Lab is the first domain proof-of-work for that goal:
physics-first, verification-first, and campaign-based. APL should show that
agents can preserve evidence, failures, limitations, replays, predictions, and
review tiers without turning every interesting pattern into a claim.

APL is not trying to generate dramatic claims on demand. It is trying to make
scientific work reproducible, reviewable, and reusable through deterministic
code and version-controlled evidence.

APL is also being shaped as an open agent network for science: many humans can
connect their AI agents to shared campaigns, while the repository coordinates
tasks, sandbox evidence, negative results, prediction registries, review gates,
and public scientific memory.

## Strategic Shift

The repository is no longer focused mainly on bootstrap infrastructure work or a
single scientific lane. The base now exists well enough to support a new
emphasis:

- maintain many safe, bounded, data-backed research lanes rather than minimizing
  task count for its own sake;
- distinguish good task growth (campaign-scoped, gated, dataset-backed lanes)
  from bad task sprawl (open-ended work without baselines, holdouts, or review
  gates);
- turn high-quality sandbox evidence into `AGENT_PUBLISHED` and
  `AGENT_VALIDATED` scientific memory when explicit result-promotion gates pass;
- after validation, route campaigns toward the next higher-validity gate
  instead of another internal audit loop: independent transfer, scoped
  maintainer ratification, external/no-peek reveal, or concrete source
  readiness;
- curate active and preparing campaigns with clear source state, allowed work,
  forbidden work, and honest limitations;
- keep public-launch work gated behind validation, review discipline, and
  conservative claim boundaries.

## Current Priorities

1. Operate APL as a multi-campaign open agent research network, not as a small
   collection of isolated local experiments.
2. Keep Nuclear Mass Surface as the flagship science track, but separate
   replayed point-estimator gains from prediction-ready uncertainty. `RESULT-0025`
   is useful evidence; prediction freeze still requires no-peek calibration and
   source-grade reveal discipline.
3. Treat Exoplanet Mass-Radius as a public-safe monitor/negative-control
   surface: pinned snapshots, residual failure maps, and null baselines are
   useful, but current residual scoring stays closed until a material
   source-version trigger or accepted canonical identity route appears.
4. Maintain several active source-first campaign lanes instead of one default
   secondary track: Textbook Formula Audit, Thermophysical Property Residuals,
   Materials Property Residuals, Quantum Size Effects, and Atomic-Clock
   Residuals.
5. Treat Materials Property Residuals and Thermophysical Property Residuals as
   reusable-dataset/benchmark-readiness lanes: `MD-0002` and ThermoML `Tb`
   results are source-pinned and useful, but external release, corpus expansion,
   and stronger wording remain gated by replay, rights, identity, and no-claim
   discipline.
6. Validate the contributor and agent workflow with measurable gates:
   task-based PRs, scientific sandbox PRs, independent replay or audit PRs,
   clean review-helper behavior, closeout, gated result publication, and zero
   automatic claim promotion.
7. Prepare and maintain a clear Mission Control and campaign-map layer so new
   contributors can see what APL is trying to do and where evidence already
   exists.
8. Treat open-agent-network coordination as a first-class design goal: many
   agents may work in parallel, but only through task contracts, disjoint
   branches or worktrees, disjoint artifact surfaces, evidence gates, and
   maintainer review.
9. Keep Koide and particle-mass work falsification-first, narrow in scope, and
   resistant to numerology overclaim.
10. Improve visual result summaries, campaign summaries, and contributor-facing
   navigation around the strongest current evidence, including negative-result
   surfaces.
11. Package the current result layer into a coherent v0.2 story without
   relaxing scope or limitation wording.
12. Keep post-validation campaigns pointed at explicit validity gates:
   transfer, ratification, external reveal, or source readiness. Repeated
   audits are useful only when they clear one of those gates.
13. Use [blind-holdout-benchmark-protocol.md](./blind-holdout-benchmark-protocol.md)
   for future prediction-style benchmarks that need a visible before/after
   target reveal boundary.
14. Distinguish retrospective time-split benchmarks from prospective prediction:
   post-AME2020 nuclear-mass evaluation is a stronger holdout surface, while
   true future predictions require a pre-registered prediction artifact.
15. Prepare public launch only after the explicit gates in
   [public-release-gates.md](./public-release-gates.md) are satisfied.

Future research direction is curated through
[future-research-portfolio.md](./future-research-portfolio.md). The current
portfolio should be read as a campaign portfolio, not a scarcity list:
`ACTIVE` lanes should stay bounded and data-backed; `PREPARE` lanes should
build source, schema, baseline, and holdout readiness; `GUARDRAIL` and
`WATCHLIST` lanes should not become implementation work without a new
maintainer-approved task and stronger gates.

## Current Goal

Demonstrate that APL can run honest scientific campaigns, gated evidence
publication, and multi-agent contributor work at the same time, without
relaxing verification standards or overstating benchmark results.

## Steering Metric

Task throughput is not the north-star metric. APL should optimize for durable
scientific-output throughput: reproducible `RESULT-*` artifacts, preserved
negative and inconclusive evidence, registered predictions awaiting reveal,
agent-validated replays, maintainer-reviewed scoped claims, and reusable
knowledge. A healthy campaign is not the one with the most activity; it is the
one that steadily converts bounded work into reviewable scientific memory while
making blockers and failed ideas visible.

Near public-alpha, the most important metrics are:

- `AGENT_PUBLISHED`, `AGENT_VALIDATED`, maintainer-reviewed, and externally
  replicated artifacts that remain clearly tiered;
- independent replay PRs and adversarial audit PRs;
- reusable source-pinned datasets with citation and reuse metadata;
- negative, null, overfit, or inconclusive results that prevent repeated weak
  work;
- external contributors or agent operators who can reproduce the branch,
  validation, review, and closeout loop without private context.

## Current North-Star Outcomes

- campaign-oriented scientific work with explicit boundaries, current evidence,
  and next-safe-task surfaces;
- reproducible results that preserve failure modes and limitation wording;
- contributor onboarding that does not require tribal knowledge to understand
  tasks, review expectations, or release posture.

Current visible evidence includes:

- the pendulum gauntlet result package from `EXP-0001/RUN-0003`;
- charged-lepton Koide reproduction from `EXP-0004/RUN-0004`;
- the tau holdout benchmark from `EXP-0005/RUN-0005`;
- the dimensional-analysis validator MVP result from `EXP-0006/RUN-0006`;
- the neutrino and quark Koide falsification results from `EXP-0007/RUN-0001`
  and `EXP-0008/RUN-0001`;
- the negative-results registry as a maintained output surface;
- the nuclear-mass baseline, negative/control memory, and `RESULT-0025`
  point-estimator surface, which still requires uncertainty calibration before
  prediction freeze;
- Materials `RESULT-0021`, Textbook/Stellar `RESULT-0022`, FIRAS/Wien
  `RESULT-0023`, Stellar high-mass transfer `RESULT-0024`, and ThermoML `Tb`
  `RESULT-0026` as scoped, review-tiered benchmark memory rather than broad
  physical claims.

These results are useful because they are reviewable and reproducible, not
because they justify expansive scientific claims.

## Current Execution Model

The repository uses a shared task pool with branch-based execution.

- a task defines the contract;
- an agent or human picks one atomic task;
- multiple agents can work in parallel when branches, worktrees, and artifact
  surfaces stay disjoint;
- validation runs before handoff;
- task files and board state remain the coordination layer;
- maintainer review stays the decision point for merge and closeout.

The repository was private through the contributor pilot and was opened publicly
on 2026-06-28, after the release gates were satisfied and the maintainer
confirmed the v0.2 narrative matched the evidence.

## Non-Goals

- Do not frame narrow benchmark outputs as discovery-level physics.
- Do not describe particle-mass results as explanations of mass generation.
- Do not collapse scoped reproductions and scoped falsifications into a single
  global statement about all Koide-like ideas.
- Do not claim universal validity from configured-range validation.
- Do not add dashboard, public API, literature ingestion, or public task
  network before current campaign and workflow gates are met.
- Do not turn `WATCHLIST` topics from
  [future-research-portfolio.md](./future-research-portfolio.md) into
  implementation work without a new maintainer task and stronger guardrails.
- Do not use LLM prose as a substitute for deterministic validation.

## Decision Rule

When choosing between faster expansion and stronger verification, choose
stronger verification.
