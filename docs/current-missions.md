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
settled. FRB has now crossed the sealed-prediction registration and GitHub
Release anchor gate; the time-sensitive FRB focus moves from pre-freeze work to
reveal-source discipline. Nuclear and Exoplanet remain the next high-value
replay/reveal surfaces.

The current director cycle follows a source-readiness wave that produced no new
numerical `RESULT`, but materially changed four routes: CHARA now has twelve
component rows across six systems, Kim-2020 CdSe has a twelve-observation
extraction contract, dimensional v2 has an unscored 80-item calibration surface,
and `f_K/f_pi` passed a bounded Lattice-QCD dependency incubator. The next wave
should convert those surfaces through explicit gates instead of reopening broad
audits.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science paths are:

1. protect the registered FRB chain after `PRED-0001`: preserve the GitHub
   Release anchor, use the TASK-0995 reveal-source contract, and do not read or
   score reveal labels before a separate maintainer-reviewed reveal task;
2. keep Exoplanet `RESULT-0027` as AGENT_VALIDATED negative/control memory with
   fair-null transparency; do not reopen residual scoring without a future
   NOTIFY-class source trigger or maintainer-approved coverage amendment;
3. independently replay the twelve CHARA rows, then run the frozen
   `RESULT-0022` relation and controls without refitting;
4. extract only the twelve predeclared Kim-2020 CdSe observations, and score the
   80-item dimensional v2 surface only as calibration evidence;
5. keep Materials OQMD value-blind until its acquisition PR lands, and keep the
   Lattice `f_K/f_pi` route at metadata/dependency level without central values.

Nuclear Mass Surface remains the flagship ambition, but interval-bearing
prediction remains blocked because approved no-peek uncertainty routes failed.
Exoplanet remains monitor-only on the unchanged snapshot even though
`RESULT-0027` now exists. Quantum has a source-scoped Almeida baseline and
AGENT_VALIDATED `RESULT-0029`, so the same ZnSe/InP transfer should not be
rerun as a new benchmark; Kim-2020 is now open only for bounded row extraction.
Atomic remains row-admissibility blocked after the
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
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Post-validation dataset/transfer lane: `RESULT-0021` is reviewed memory, MD-0002 is externally published, and bounded OQMD acquisition is under review | Predeclare only within-OQMD controls value-blind; split and metrics wait for merged source readiness |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with four scoped AGENT_VALIDATED results and twelve CHARA component rows across six systems | Independent row replay and a frozen-relation no-refit transfer; seven additional systems remain source-limited |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with negative/control memory, exact-replayed `RESULT-0025` point-estimator evidence, failed uncertainty calibration, DZ10 full-table parity PASS, and the executed tier-1 point-only freeze (`PRED-0069..0072`, sealed 2026-07-05) | External anchoring (`TASK-0945` pack), reveal-source watch discipline, approved `TASK-0305` scoring lane; no interval-bearing freeze until calibration repair |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, `NO_NOTIFY` monitor check, and AGENT_VALIDATED `RESULT-0027` negative/control packaging | Monitor-only until a NOTIFY-class source trigger or maintainer-approved coverage amendment appears; no residual scoring on the unchanged snapshot |
| [FRB / Radio Transients](./campaigns/fresh-physics-data-axes.md#frb-selection-effect-audit) | Registered sealed-prediction chain with checksum/schema-gated Catalog-1 interval exposure pair, committed 479-row pre-T exposure feature surface, frozen exposure-only model surface, maintainer-approved `PRED-0001`, and GitHub Release anchor tag `pred-frb-pret-repeater-propensity-20260710` | Reveal-source contract discipline via TASK-0995; no label reading, success wording, population claim, or reveal scoring before a separate maintainer-reviewed reveal task |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-scoped Almeida baseline exists, AGENT_VALIDATED `RESULT-0029` preserves the ZnSe miss, and Kim-2020 has a frozen twelve-observation extraction contract | Extract and reconcile only those rows; no metric, correction search, or repeat ZnSe/InP transfer |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | Quality-floor lane with an unscored 80-item exact-v2 surface and same-owner role limit | Run one blind calibration score; do not use it for `CLAIM-0005` promotion |
| [Lattice-QCD Aggregated Consistency](./campaigns/fresh-physics-data-axes.md#lattice-qcd) | Near-active `f_K/f_pi` source/dependency pilot after an incubator GO | Audit 8-12 primary publications without central values, loader work, or metrics |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with source-limited Yb/Sr memory, covariance policy, diagnostic-only Pizzocaro aggregation, blocked McGrew/NIST route, and `KEEP_MONITOR_ONLY` multispecies verdict | `TASK-0990` monitor-only trigger ledger; no constants-drift or metric rerun |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | ThermoML `Tb` benchmark lane with AGENT_VALIDATED `RESULT-0026`, frozen Joback baseline, rights boundary, and AGENT_VALIDATED esters/lactones negative/control `RESULT-0028` | `TASK-0986` source-access contract packet; no replay loop, broader property claims, or raw archive vendoring |

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
| Dataset/source-readiness gate | Materials Property Residuals | MD-0002 is published (DOI `10.5281/zenodo.21207072`); bounded OQMD acquisition is under review, and only value-blind within-source control planning may proceed in parallel. |
| Source-replay / transfer gate | Textbook Formula Audit / Stellar M-L / Wien-FIRAS | CHARA now has twelve rows across six systems and a dependence policy; independently replay provenance, then score the fixed relation without refit. |
| External-reveal / uncertainty gate | Nuclear Mass Surface | Tier-1 point-only freeze executed, sealed (2026-07-05), and externally anchored (Zenodo DOI `10.5281/zenodo.21240451`); `TASK-0992` continues source-watch discipline while `TASK-0305` remains the approved scoring lane. |
| Monitor / negative-control gate | Exoplanet Mass-Radius | `RESULT-0027` is AGENT_VALIDATED; keep source-version monitoring metadata-only and wait for a future trigger before scoring. |
| Sealed-prediction reveal discipline | FRB / radio transients | `PRED-0001` is registered and externally anchored by GitHub Release; keep future work to TASK-0995-compliant reveal-source manifests and maintainer-reviewed reveal scoring. |
| Transfer/source gate and negative memory | Quantum Size Effects | Preserve `RESULT-0029`; Kim-2020 is open for exactly twelve predeclared observations, not a benchmark or correction search. |
| Pinned-dataset / aggregation blocked | Atomic-Clock Residuals | `KEEP_MONITOR_ONLY` is the current scientific posture; `TASK-0990` should make the reopen triggers durable. |
| Source-pinned thermophysical benchmark | Thermophysical Property Residuals | `RESULT-0026` and `RESULT-0028` are AGENT_VALIDATED; `TASK-0986` is the source-access/revised-contract path. |
| Calibration / quality-floor gates | Anharmonic, Dimensional, Pendulum, Particle Mass Relations | Dimensional v2 is ready for one calibration-only score; do not restart broad formula search or infer claim support from same-owner curation. |
| Near-active source/dependency gate | Lattice-QCD aggregated consistency | `f_K/f_pi` may receive one primary-publication metadata/dependency pilot; central values and metrics remain closed. |
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
