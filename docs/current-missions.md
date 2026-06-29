# Current Missions

APL uses an **Agent First / Research First / Parallel Work** entrypoint.

The default path for a new coding agent is not "scan every file and pick
something small." The default path is:

```bash
python3 scripts/apl_mission.py --output onboarding
```

Onboarding mode should explain the current scientific mission, show a few
`READY` options with estimated effort, recommend one, and wait before editing
files. For autonomous agent context after the user already understands the
flow, use:

```bash
python3 scripts/apl_mission.py --output agent
```

The older `--onboarding` and `--agent-prompt` aliases are preserved for
compatibility, but new docs should prefer the explicit `--output ...` form.

Support, review, and closeout work remain explicit:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Mission policy and campaign guardrails live in
[`../missions/current.yaml`](../missions/current.yaml). Live task candidates
come from canonical `tasks/TASK-*.yaml` files through the mission script. For
lighter navigation than the full generated board, use:
[`public-science-dashboard.md`](./campaigns/public-science-dashboard.md),
[`research.md`](./task-views/research.md),
[`support.md`](./task-views/support.md),
[`release.md`](./task-views/release.md),
[`watchlist.md`](./task-views/watchlist.md), and
[`blocked.md`](./task-views/blocked.md).

For parallel-capacity planning — how many agents fit each lane — read each
campaign's `agent_capacity` block in
[`campaign_profiles/_catalog.yaml`](../campaign_profiles/_catalog.yaml) (the
generated portfolio index) and
query the on-demand task-to-campaign index
(`python3 scripts/apl_task_campaign_index.py`).

## Recommended Mission Now

**Materials Property Residuals** is the current flagship validation
mission.

The current director cycle is a post-agent-wave task-queue refill. Many
near-term science tasks have landed, leaving the live executor pool too thin
for parallel research agents. The next wave should move validated,
source-limited, or blocker-limited surfaces through explicit gates instead of
reopening broad audits.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science paths are:

1. replay ThermoML `Tb` `RESULT-0026` through Gate B (`TASK-0894`);
2. run the no-peek Nuclear uncertainty-calibration metric audit for
   `RESULT-0025` (`TASK-0899`);
3. repair or explicitly preserve the Stellar high-mass `RESULT-0024` metadata
   caveat (`TASK-0898`);
4. adjudicate source routes before new data rows in Atomic, Particle, Quantum,
   Exoplanet, Materials, and ThermoML (`TASK-0900` through `TASK-0906`);
5. prepare public/maintainer wording for already validated verifier evidence
   without promoting calibration-known physics to discovery claims
   (`TASK-0897`);
6. resolve mature quality-floor blockers such as the Dimensional
   `RESULT-0020` packaging contest (`TASK-0782`).

Nuclear Mass Surface remains the flagship ambition, but prediction freeze is
still blocked by uncertainty calibration and source-grade reveal discipline.
Exoplanet remains monitor-only until either canonical null-baseline packaging
is explicitly accepted as a negative/control memory path or a material
source-version trigger appears. Quantum has a source-scoped Almeida baseline
and a narrow ZnSe source route, but the next work is frozen-row readiness, not
correction search. Atomic remains row-admissibility blocked until the
McGrew/NIST route is adjudicated or a maintainer approves a harmonized
aggregation contract.
At handoff, agents should route the output through
[`result-promotion-protocol.md`](./result-promotion-protocol.md): state the
verdict, destination, review tier, Gate A/B status, limitations, and blockers.

New campaign ideas should enter through source/schema/baseline scaffolds first,
not broad hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation ambition, several active
post-validation gate surfaces, one public-safe monitor surface, and several
source-gated or quality-floor lanes. That mix is deliberate: some agents should
close source and dataset blockers, others should prepare ratification packets
or transfer scouts, and curators should keep blocked campaigns visible without
turning watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Post-validation dataset/transfer lane: `RESULT-0021` is reviewed memory, repository-local MD-0002 metadata is closed, transfer-negative memory is preserved, and external release is maintainer-gated | `TASK-0900` deterministic archive-package dry run; no upload, DOI minting, row mutation, metric mutation, or claim wording |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with validated exact-reference, Stellar M-L, and FIRAS/Wien surfaces; high-mass transfer replay has zero metric drift but a metadata caveat | `TASK-0897` RESULT-0023 public/maintainer wording and `TASK-0898` RESULT-0024 metadata-caveat repair/preservation; no universal formula wording |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with negative/control memory, exact-replayed `RESULT-0025` point-estimator evidence, unresolved interval calibration, and a metadata-only DZ10 route awaiting closeout | `TASK-0899` no-peek uncertainty-calibration audit; no prediction freeze, reveal scoring, or new DZ10 executor work until closeout/follow-up |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, and Gate-A-blocked negative/control packaging | `TASK-0904` canonical null-baseline identity decision or `TASK-0905` source-version monitor check 3; no residual scoring unless a NOTIFY-class trigger appears |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-scoped Almeida baseline exists, Toufanian ZnSe has narrow factual-extract source readiness, and effective-mass transfer is negative memory | `TASK-0903` ZnSe frozen-row transfer-readiness gate; it does not unblock archived `TASK-0226` |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with source-limited Yb/Sr memory, covariance policy, diagnostic-only Pizzocaro aggregation, and a plausible McGrew/NIST route | `TASK-0901` adjudicate primary-ratio semantics and independence before any row curation or metrics |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | Newly active ThermoML `Tb` benchmark lane with AGENT_PUBLISHED `RESULT-0026`, frozen Joback baseline, rights boundary, and esters/lactones negative memory | `TASK-0894` Gate B replay or `TASK-0906` local-only 80-row identity/count preflight; no raw archive vendoring or broad property claim |

Mature quality-floor tracks still matter: Pendulum, Dimensional Analysis, and
Particle Mass Relations keep the repository honest about exact references,
falsification, and overclaim resistance. They are not the default landing-page
focus unless the maintainer asks for replay, documentation, or benchmark
hygiene work.

## Campaign Portfolio Direction

APL should grow by adding bounded campaign lanes, not by asking agents to search
open-endedly. Good growth means each lane has a source surface, baseline,
holdout or replay discipline, allowed work, forbidden work, and a clear
promotion route for evidence.

Near-term portfolio shape:

| Portfolio role | Campaigns | Notes |
| --- | --- | --- |
| Dataset/source-readiness gate | Materials Property Residuals | Run a deterministic MD-0002 archive-package dry run before any external upload/DOI decision. |
| Source-readiness / ratification gate | Textbook Formula Audit / Stellar M-L / Wien-FIRAS | Ratify public wording for `RESULT-0023` and fix or preserve the `RESULT-0024` metadata caveat before stronger tier wording. |
| External-reveal / uncertainty gate | Nuclear Mass Surface | Keep prediction freeze blocked until no-peek uncertainty calibration passes; preserve point-estimator gains as limited evidence. |
| Monitor / negative-control gate | Exoplanet Mass-Radius | Decide whether the null-baseline memory gets canonical identities and keep source-version monitoring metadata-only. |
| Transfer/source gate and negative memory | Quantum Size Effects | Freeze/adjudicate the narrow ZnSe row set before any transfer benchmark; keep archived correction search closed. |
| Pinned-dataset / aggregation blocked | Atomic-Clock Residuals | Adjudicate McGrew/NIST primary-ratio and independence semantics; do not use Pizzocaro as a benchmark row without an admissible contract. |
| Source-pinned thermophysical benchmark | Thermophysical Property Residuals | Replay `RESULT-0026` and test local-only 80-row expansion feasibility before any corpus or rights decision. |
| Ratification / quality-floor gates | Anharmonic, Dimensional, Pendulum, Particle Mass Relations | Prepare narrow maintainer packets, negative-memory cards, source pins, or packaging adjudications; do not restart broad formula search. |
| Guardrail/watchlist | g-2, Hubble, broad constants, particle-mass formula search | Keep schema, admissibility, or falsification-first only unless a maintainer creates a stronger gated task. |

## Default Research Mode

Research Mode is for:

- bounded hypothesis tests;
- replay and split-sensitivity checks;
- adversarial audits of sandbox evidence;
- source and provenance review;
- negative, null, overfit, or inconclusive result preservation;
- PR-ready result, evidence, or blocker artifacts.

Research Mode is now evidence-publication aware, but not claim-promotion
driven. Agents publish reproducible evidence only when task scope and gates
allow it; agents validate each other; maintainers endorse interpretation; and
external data confirms predictions. Claim status transitions and knowledge
endorsement remain maintainer-only in Phase 1.

The broader organization frame is Open Agent Science. APL is the first physics
proof-of-work: agents should optimize for citable, replayable scientific memory
and visible limitations, not for raw task count or dramatic discovery wording.

## Parallel Agent Policy

Multiple agents can work in parallel when they increase coverage rather than
duplicate effort.

Use these rules:

- one local checkout should usually run one task at a time;
- parallel local agents should use separate branches or git worktrees;
- prefer disjoint campaigns, datasets, hypothesis families, or review
  surfaces;
- same-campaign parallel work is allowed only when artifact surfaces are
  clearly separated;
- executor agents should offer only `READY` tasks as available work;
- `REVIEW_READY`, `DONE`, and `BLOCKED` tasks are for review, closeout, or
  maintainer triage, not new executor work;
- do not guess new canonical task ids during parallel work unless the
  maintainer explicitly asks for canonical task creation.

## What To Avoid Right Now

- Do not run Nuclear reveal scoring until a source-grade post-freeze data
  release passes the reveal source gate.
- Do not treat retrospective Nuclear audits as future blind validation.
- Do not present `LOCAL-CURVATURE-001` as a surviving Nuclear no-leakage
  candidate after `TASK-0394`; route it through negative/inconclusive memory.
- Do not start the Quantum baseline benchmark until direct measurement rows or
  an explicit weaker calibration-consistency scope is approved.
- Do not fit atomic-clock or anomaly-style campaigns before source and
  covariance semantics are reviewable.
- Do not present exoplanet regime scouts as corrections or planet-composition
  discoveries; after the null-baseline family audit, compact-radius is public-
  safe only as a control-sensitive benchmark diagnostic with scorecard
  limitations attached.
- Do not broaden Textbook Formula Audit metrics or public wording beyond each
  pinned slice's source, baseline, replay, and no-claim contract.

## Copy-Paste Agent Prompt

Generate the current prompt with:

```bash
python3 scripts/apl_mission.py --output agent
```

Short onboarding version:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run `python3 scripts/apl_mission.py --output onboarding`.
Follow the printed onboarding instructions: explain the current research
mission, show READY options, recommend one, and wait for my choice before
editing files. Prefer a science-execution task over tooling or infrastructure
when a suitable READY option exists.
```
