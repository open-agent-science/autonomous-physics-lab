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

**Materials Property Residuals** remains the top-ranked mission entry in
`missions/current.yaml`, but its immediate metric/release work is mostly
settled. The live time-sensitive task-queue focus is FRB sealed-prediction
preparation, with Nuclear and Exoplanet as the next high-value replay/reveal
surfaces.

The current director cycle is a post-agent-wave task-queue refill. Many
near-term science tasks have landed, leaving the live executor pool too thin
for parallel research agents. The next wave should move validated,
source-limited, or blocker-limited surfaces through explicit gates instead of
reopening broad audits.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science paths are:

1. complete the activated FRB chain: use the `TASK-0964` frozen exposure-only
   model surface for the `TASK-0965` sealed-prediction registration pack under
   explicit maintainer approval;
2. repair Exoplanet `RESULT-0027` for Gate-B-safe replay and fair-null
   transparency (`TASK-0959`), without reopening residual scoring;
3. score the approved Nuclear shell-axis mini-wave reveal only through the
   source-approved `TASK-0305` lane, while keeping interval-bearing claims
   blocked until uncertainty calibration is repaired;
4. enforce future result replayability after the Exoplanet bridge lands
   (`TASK-0960`);
5. use source-gated campaigns for blocker memory and revised contracts only:
   Quantum `RESULT-0029` is already inconclusive/control memory, ThermoML has
   both `RESULT-0026` and `RESULT-0028`, and Atomic remains source/admissibility
   gated.

Nuclear Mass Surface remains the flagship ambition, but interval-bearing
prediction remains blocked because approved no-peek uncertainty routes failed.
Exoplanet remains monitor-only on the unchanged snapshot even though
`RESULT-0027` now exists. Quantum has a source-scoped Almeida baseline and
AGENT_PUBLISHED `RESULT-0029`, so the same ZnSe/InP transfer should not be
rerun as a new benchmark. Atomic remains row-admissibility blocked after the
McGrew/NIST route failed; the next route needs a genuinely admissible source or
a maintainer-approved multi-species contract.
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
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Post-validation dataset/transfer lane: `RESULT-0021` is reviewed memory, repository-local MD-0002 metadata is closed, transfer-negative memory is preserved, the dataset is externally published (Zenodo DOI `10.5281/zenodo.21207072`, v0.1.0, 2026-07-05, integrity-confirmed) | Reuse/citation surfaces and the second-dataset decision packet; no row mutation, metric mutation, or claim wording |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with validated exact-reference, Stellar M-L, FIRAS/Wien surfaces, and AGENT_VALIDATED same-source `RESULT-0024` high-mass transfer memory | Keep same-source/source-limited wording; no universal formula wording |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with negative/control memory, exact-replayed `RESULT-0025` point-estimator evidence, failed uncertainty calibration, DZ10 full-table parity PASS, and the executed tier-1 point-only freeze (`PRED-0069..0072`, sealed 2026-07-05) | External anchoring (`TASK-0945` pack), reveal-source watch discipline, approved `TASK-0305` scoring lane; no interval-bearing freeze until calibration repair |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, `NO_NOTIFY` monitor check, and AGENT_PUBLISHED `RESULT-0027` negative/control packaging | `TASK-0959` Gate-B-safe workflow repair and fair-null transparency; no residual scoring unless a NOTIFY-class trigger appears |
| [FRB / Radio Transients](./campaigns/fresh-physics-data-axes.md#frb-selection-effect-audit) | Activated sealed-prediction chain with checksum/schema-gated Catalog-1 interval exposure pair, committed 479-row pre-T exposure feature surface, and frozen exposure-only model surface | `TASK-0965` registration pack; no FRB result or claim before reveal |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-scoped Almeida baseline exists, Toufanian ZnSe rows are frozen as limited factual extracts, and `RESULT-0029` preserves the strict no-refit transfer miss as inconclusive/control memory | No immediate metric task; new work needs new source evidence or a maintainer-approved contract change |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with source-limited Yb/Sr memory, covariance policy, diagnostic-only Pizzocaro aggregation, and blocked McGrew/NIST route | `TASK-0913` scout one post-2021 independent primary Yb/Sr source before row curation or metrics |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | ThermoML `Tb` benchmark lane with AGENT_VALIDATED `RESULT-0026`, frozen Joback baseline, rights boundary, and AGENT_PUBLISHED esters/lactones negative/control `RESULT-0028` | Expansion/source-access decisions or `RESULT-0028` replay only; no broader property claims |

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
| Dataset/source-readiness gate | Materials Property Residuals | MD-0002 is published (DOI `10.5281/zenodo.21207072`); the gate now applies to the next dataset candidate (ThermoML bounded extract pending the maintainer rights decision; MD-0001). |
| Source-readiness / ratification gate | Textbook Formula Audit / Stellar M-L / Wien-FIRAS | Ratify public wording for `RESULT-0023` and fix or preserve the `RESULT-0024` metadata caveat before stronger tier wording. |
| External-reveal / uncertainty gate | Nuclear Mass Surface | Tier-1 point-only freeze executed, sealed (2026-07-05), and externally anchored (Zenodo DOI `10.5281/zenodo.21240451`); keep the interval-bearing freeze blocked until calibration repair; maintain reveal-source watch discipline. |
| Monitor / negative-control gate | Exoplanet Mass-Radius | `RESULT-0027` is AGENT_PUBLISHED; bridge it to a Gate-B-safe workflow and keep source-version monitoring metadata-only. |
| Sealed-prediction preparation | FRB / radio transients | `TASK-0963` built the pre-T feature surface and `TASK-0964` froze the exposure-only model surface; execute `TASK-0965` without label leakage or success wording. |
| Transfer/source gate and negative memory | Quantum Size Effects | Preserve `RESULT-0029` as inconclusive/control transfer memory; keep archived correction search closed. |
| Pinned-dataset / aggregation blocked | Atomic-Clock Residuals | Scout one post-2021 independent primary Yb/Sr source; do not use Pizzocaro or McGrew/NIST as benchmark rows without an admissible contract. |
| Source-pinned thermophysical benchmark | Thermophysical Property Residuals | `RESULT-0026` is AGENT_VALIDATED and `RESULT-0028` preserves the failed family; expansion remains source-access/revised-contract gated. |
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
