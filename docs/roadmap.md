# Roadmap

## Open Agent Science Context

Open Agent Science is the umbrella direction: shared public scientific memory
produced by human-owned agents, with reproducibility, review tiers, and
citation readiness visible in the repository.

Autonomous Physics Lab is the first physics proof-of-work for that direction.
The roadmap should therefore optimize for citable, replayable scientific
outputs, not for raw task volume or discovery-style storytelling.

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

- keep validated or source-limited campaigns moving through explicit
  next-validity gates: transfer, maintainer ratification, external/no-peek
  reveal, or source readiness;
- close reusable-dataset and source-publication blockers before turning
  Materials, Stellar, or similar empirical surfaces into broader transfer
  claims;
- keep the pendulum, dimensional-analysis, and particle-mass tracks as
  falsification-first quality floors with scoped ratification or negative-memory
  work, not broad formula search;
- treat the negative-results registry as part of the main scientific output
  layer rather than as a side note;
- connect benchmark results, campaign pages, mission docs, and release-facing
  summaries through Mission Control without duplicating live task queues;
- keep Nuclear Mass Surface as the current flagship validation campaign while
  preserving source-blocked reveal discipline and negative/control memory;
- improve visual result summaries so current evidence is easier to review.

## Contributor Pilot — Active

APL is actively validating whether invited humans and coding agents can
contribute safely through canonical task files, proposal-first intake, active
board sync, validation, and maintainer review.

Near-term contributor-workflow goals:

- reduce coordination friction around the active board and closeout flow;
- keep task and proposal surfaces easy to understand for new contributors;
- collect more evidence from real private-alpha task execution.

## Public Launch Package — Final Gate

Public launch is intentionally downstream of the current campaign and workflow
validation work.

The repository transfer to `open-agent-science/autonomous-physics-lab` is
complete. The remaining public-launch work is now a final gate: make sure the
live repository path, citation metadata, campaign summaries, release evidence,
and current task state all agree before the maintainer changes visibility.

Before launch, APL needs:

- post-transfer branch protection, CI, self-hosted runner, and secret checks;
- stable status, roadmap, and README narrative;
- campaign-level result packaging that includes both reproductions and clean
  falsifications;
- honest public-facing result summaries;
- a citation and publication path for software, reusable datasets, and future
  citable outputs;
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

## Publication And Citation Track — Planned

**Goal:** APL can be cited as software and can prepare reusable datasets or
benchmark artifacts for future DOI-backed publication without confusing
dataset readiness, result promotion, and claim endorsement.

See [publication-roadmap.md](./publication-roadmap.md). Near-term exit
criteria:

- software citation metadata exists (`CITATION.cff` and release metadata);
- dataset publication rules are documented for source-pinned reusable datasets;
- at least one dataset candidate, such as Materials `MD-0001` or an Exoplanet
  snapshot surface, has explicit citation/reuse metadata and limitations;
- post-validation dataset candidates such as Materials `MD-0002` and
  Textbook/Stellar row packages have source, checksum, citation, permission, and
  no-claim metadata before they are treated as transfer-ready;
- release docs preserve review-tier labels for `AGENT_PUBLISHED`,
  `AGENT_VALIDATED`, maintainer-reviewed, externally replicated, and legacy
  artifacts.

This track should be planned before public launch and completed only when the
maintainer is ready to publish release artifacts.

## v0.3 — Research Factory And Dataset Publication Layer — Planned

**Goal:** APL can run bounded campaign factories that test many hypotheses, route
candidates through controls, and produce reviewable scientific memory on
source-pinned datasets without claim promotion.

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
- at least one factory-compatible dataset surface has source, citation/reuse,
  and holdout or replay metadata suitable for future publication review;
- the version marker is reconciled (see below) and public-facing wording stays
  benchmark/negative-evidence honest.

Sequencing: `v0.3` may be planned in parallel but is closed only after the
`v0.2` public-launch gates above are satisfied.

Version-marker hygiene: the narrative version (`v0.2`, then `v0.3`) must be
reconciled with the package marker in `pyproject.toml` (currently `0.1.0`) so
the version has a single source of truth tied to release gates rather than prose.

## v0.4 — External Agent Network Validation — Future

After public-alpha gates are satisfied, APL can test whether Open Agent Science
works beyond the maintainer's own local agents.

Future-facing evidence should include:

- external contributors or agent operators completing task PRs;
- independent replay or adversarial audit PRs from outside the maintainer's
  normal agent loop;
- public discussion feedback that improves campaign direction or contributor
  workflow;
- at least one external reviewer or domain-scientist feedback artifact;
- release or dataset artifacts that can be cited without hiding review tiers or
  limitations.

This remains future work, not a current commitment to public scale.

## Guiding Rule

Widen the system only after the current scientific and contributor layer is
reproducible, reviewable, and honestly described.
