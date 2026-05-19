# Strategy

## Current Phase

`v0.1-private-alpha — scientific campaign and contributor workflow validation`

Near-term packaging target:

`v0.2` public-facing material preparation, still gated behind private review
and release discipline.

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

The repository is no longer focused mainly on bootstrap infrastructure work.
That base now exists well enough to support a new emphasis:

- curate active scientific campaigns with clear scope and honest limitations;
- validate private contributors and their agents through a branch-based,
  reviewable workflow before any public opening;
- improve project-level orientation so results, tasks, and risks stay legible;
- keep public-launch work gated behind validation and review discipline.

## Current Priorities

1. Curate scientific campaigns rather than broadening into many unfinished
   benchmark ideas at once.
2. Elevate a nuclear mass surface campaign as the next flagship science track,
   using baseline residual maps, shell-closure diagnostics, holdout discipline,
   post-AME2020 time-split validation, and conservative correction-term framing
   instead of broad discovery claims.
3. Validate the private contributor and agent workflow with measurable gates:
   task-based PRs, scientific sandbox PRs, independent replay or audit PRs,
   clean review-helper behavior, closeout, and zero automatic claim promotion.
4. Prepare and maintain a clear Mission Control and campaign-map layer so new
   contributors can see what APL is trying to do and where evidence already
   exists.
5. Treat open-agent-network coordination as a first-class design goal: many
   agents may work in parallel, but only through task contracts, disjoint
   branches or worktrees, sandbox-first evidence, and maintainer review.
6. Keep Koide and particle-mass work falsification-first, narrow in scope, and
   resistant to numerology overclaim.
7. Improve visual result summaries, campaign summaries, and contributor-facing
   navigation around the strongest current evidence, including negative-result
   surfaces.
8. Package the current result layer into a coherent v0.2 story without
   relaxing scope or limitation wording.
9. Use [blind-holdout-benchmark-protocol.md](./blind-holdout-benchmark-protocol.md)
   for future prediction-style benchmarks that need a visible before/after
   target reveal boundary.
10. Distinguish retrospective time-split benchmarks from prospective prediction:
   post-AME2020 nuclear-mass evaluation is a stronger holdout surface, while
   true future predictions require a pre-registered prediction artifact.
11. Prepare public launch only after the explicit gates in
   [public-release-gates.md](./public-release-gates.md) are satisfied.

Future research direction is curated through
[future-research-portfolio.md](./future-research-portfolio.md). The current
portfolio keeps Nuclear Mass Surface in `NOW`, scoped quantum-size,
thought-experiment, and electromagnetic-invariance work in `NEXT`, and keeps
Hubble tension, muon g-2 follow-up, broad constants derivation, and broad
mass-relation searches in `WATCHLIST`.

## Current Goal

Demonstrate that APL can run honest scientific campaigns and a disciplined
private contributor validation phase at the same time, without relaxing
verification standards or overstating benchmark results.

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
