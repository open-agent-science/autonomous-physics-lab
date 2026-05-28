# Strategy

## Current Phase

`v0.2-public-alpha candidate — multi-campaign agent research network hardening`

The repository is still gated by maintainer review and release discipline, but
the strategic center has moved from a single flagship/private-alpha dry run to a
multi-campaign network where many agents can safely work in parallel.

## Mission

Build verification-first scientific infrastructure for testing, falsifying,
scoring, and reusing physics hypotheses.

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
- curate active and preparing campaigns with clear source state, allowed work,
  forbidden work, and honest limitations;
- keep public-launch work gated behind validation, review discipline, and
  conservative claim boundaries.

## Current Priorities

1. Operate APL as a multi-campaign open agent research network, not as a small
   collection of isolated local experiments.
2. Keep Nuclear Mass Surface as the flagship science track,
   using baseline residual maps, shell-closure diagnostics, holdout discipline,
   post-AME2020 time-split validation, and conservative correction-term framing
   instead of broad discovery claims.
3. Promote Exoplanet Mass-Radius as the active secondary benchmark surface:
   pinned snapshots, baseline comparisons, residual failure maps, and
   selection-effect audits are useful without claiming a new planet law.
4. Prepare new campaign lanes through source-first scaffolds before hypothesis
   batches: Textbook Formula Audit, Materials/JARVIS-style property residuals,
   Quantum Size Effects, and Atomic-Clock Residuals.
5. Validate the contributor and agent workflow with measurable gates:
   task-based PRs, scientific sandbox PRs, independent replay or audit PRs,
   clean review-helper behavior, closeout, gated result publication, and zero
   automatic claim promotion.
6. Prepare and maintain a clear Mission Control and campaign-map layer so new
   contributors can see what APL is trying to do and where evidence already
   exists.
7. Treat open-agent-network coordination as a first-class design goal: many
   agents may work in parallel, but only through task contracts, disjoint
   branches or worktrees, disjoint artifact surfaces, evidence gates, and
   maintainer review.
8. Keep Koide and particle-mass work falsification-first, narrow in scope, and
   resistant to numerology overclaim.
9. Improve visual result summaries, campaign summaries, and contributor-facing
   navigation around the strongest current evidence, including negative-result
   surfaces.
10. Package the current result layer into a coherent v0.2 story without
   relaxing scope or limitation wording.
11. Use [blind-holdout-benchmark-protocol.md](./blind-holdout-benchmark-protocol.md)
   for future prediction-style benchmarks that need a visible before/after
   target reveal boundary.
12. Distinguish retrospective time-split benchmarks from prospective prediction:
   post-AME2020 nuclear-mass evaluation is a stronger holdout surface, while
   true future predictions require a pre-registered prediction artifact.
13. Prepare public launch only after the explicit gates in
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
- the nuclear-mass baseline and sandbox autonomy surface, including split
  sensitivity replay, as a flagship validation track that still requires
  stronger time-split evidence before any broader scientific claim.

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

The repository remains private until the release gates are satisfied and a
maintainer decides the v0.2 narrative matches the evidence.

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
