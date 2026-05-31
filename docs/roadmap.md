# Roadmap

## Private Alpha Infrastructure — Mostly Done

The repository already has the core private-alpha foundation needed to support
scientific campaigns:

- deterministic benchmark execution and CLI workflows;
- repository validation and strict validation modes;
- version-controlled scientific memory;
- task protocol, proposal workflow, and active-board sync;
- maintainer review and closeout helpers;
- contributor pilot documentation and branch-based execution rules.

This layer is still being polished, but it is no longer the main strategic
bottleneck.

## Scientific Campaign Layer — Active

Current focus is on turning APL from a narrow infrastructure prototype into a
campaign-oriented scientific system.

Near-term campaign work:

- keep the pendulum benchmark legible through better summaries and diagnostics;
- keep the particle-mass track falsification-first and scope-limited while
  packaging the charged-lepton, tau, neutrino, and quark results as one
  coherent campaign story;
- treat the negative-results registry as part of the main scientific output
  layer rather than as a side note;
- connect benchmark results, campaign pages, status docs, and release-facing
  summaries through a clearer Mission Control layer;
- keep Nuclear Mass Surface as the current flagship validation campaign while
  preserving `AGENT-RUN-0007` as an inconclusive guard and post-AME2020
  scoring as retrospective evidence, not strict blind prediction;
- improve visual result summaries so current evidence is easier to review.

## Contributor Pilot — Active

APL is actively validating whether invited humans and coding agents can
contribute safely through canonical task files, proposal-first intake, active
board sync, validation, and maintainer review.

Near-term contributor-workflow goals:

- reduce coordination friction around the active board and closeout flow;
- keep task and proposal surfaces easy to understand for new contributors;
- collect more evidence from real private-alpha task execution.

## Public Launch Package — Pending

Public launch is intentionally downstream of the current campaign and workflow
validation work.

Before launch, APL needs:

- stable status, roadmap, and README narrative;
- campaign-level result packaging that includes both reproductions and clean
  falsifications;
- honest public-facing result summaries;
- a final wording audit across public-facing docs;
- release-gate evidence across technical stability, contributor workflow, and
  measurable results;
- confidence that the public story matches the actual repository state.

Immediate v0.2 packaging work:

- refresh top-level status and roadmap docs to reflect current campaign
  evidence;
- package the Koide track as a falsification-first campaign rather than as
  disconnected notes;
- keep `EXP-0010` framed as a guarded stress-test surface rather than as a
  public success result;
- reflect `EXP-0011`, `EXP-0012`, Nuclear Mass Surface, and the
  `TASK-0196` before `TASK-0197` post-AME2020 validation sequence without
  promoting sandbox candidates;
- run one final public overclaim audit before any public-opening decision.

## v0.3 — Research Factory Layer — Planned

**Goal:** APL can run bounded campaign factories that test many hypotheses, route
candidates through controls, and produce reviewable scientific memory without
claim promotion.

`v0.3` is the next capability milestone after the `v0.2` public-alpha hardening.
It is a deliberate step change, not more hardening: APL moves from
one-lane-at-a-time hypothesis audits to a reusable **Research Factory** — a
deterministic bounded workflow that campaign adapters call to generate many
scoped candidates under locked controls and route the output into scientific
memory without promoting claims. See
[notes/research-factory-layer-plan.md](notes/research-factory-layer-plan.md).

`v0.3` is defined by an evidence-facing milestone, not by "the code exists". Exit
criteria:

- reusable factory **protocol** (TASK-0504) and **summary-artifact schema**
  (TASK-0505) are merged;
- the **factory core + first (Nuclear) adapter** (TASK-0506) is implemented;
- at least **one completed factory sprint** (TASK-0507) routes real bounded
  candidates into `NEGATIVE_RESULT` / `INCONCLUSIVE` / `SHORTLIST_CANDIDATE`
  memory under mandatory controls, with **no automatic claims, predictions, or
  discovery wording**;
- a **second-campaign adapter contract** (TASK-0508, Exoplanet) demonstrates
  reuse — proving the factory is a *layer*, not a Nuclear-only tool;
- the version marker is reconciled (see below) and public-facing wording stays
  benchmark/negative-evidence honest.

Sequencing: `v0.3` may be planned in parallel but is closed only after the
`v0.2` public-launch gates above are satisfied.

Version-marker hygiene: the narrative version (`v0.2`, then `v0.3`) must be
reconciled with the package marker in `pyproject.toml` (currently `0.1.0`) so
the version has a single source of truth tied to release gates rather than prose.

## Public Task Network — Future

After private-alpha gates are satisfied, APL can expand toward a more openly
participatory task network.

Future-facing possibilities include:

- broader public contributor intake;
- more visible campaign dashboards or status surfaces;
- additional benchmark families once current workflow discipline is stable.

These remain future work, not current commitments.

## Guiding Rule

Widen the system only after the current scientific and contributor layer is
reproducible, reviewable, and honestly described.
