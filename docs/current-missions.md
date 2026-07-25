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

**Lattice-QCD Aggregated Consistency** is the top-ranked currently executable
mission in `missions/current.yaml`. Its eleven-publication `f_K/f_pi` graph has
two merged partial-hold dependency audits: several shared lineages are now
explicit, but substantial cross-publication axes remain `UNKNOWN`. TASK-1081 is
the sole READY Lattice gate and may freeze value-admissibility policy before any
central values are admitted; TASK-1101 activation adjudication remains blocked.
FRB has crossed the sealed-prediction registration and GitHub Release anchor
gate; Nuclear, Exoplanet, and Atomic remain reveal- or trigger-gated.

The current director cycle follows four informative stops. The CHARA replay
verified all five frozen input hashes but could not start metric comparison
because `RESULT-0031` lacked durable publisher identity at replay time.
TASK-1088 has since restored that identity from merged PR #1609 without
changing scientific content; replay now waits for an identity-independent
executor. The two four-row Kim-2020 axes are underpowered and no independent
CdSe source cleared the frozen source gates. ThermoML now has a value-blind,
availability-capped contract of at most 74 rows, but no fixture or score. The
checksum-matched ThermoML archive is now available through the canonical
private-source workspace. OQMD `RESULT-0032` is canonical AGENT_PUBLISHED
`INVALID` negative/control memory: its exact-pair model loses to the stronger
IUPAC group-pair null and awaits identity-independent replay without rescue
fitting.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science paths are:

1. complete READY TASK-1081 to freeze the Lattice `f_K/f_pi` value-
   admissibility policy; preserve TASK-1079/1080 as partial-hold memory;
2. pursue the clean TASK-1082 external-freeze route for the Dimensional
   Analysis Validator while preserving TASK-1083
   `LABEL_SEMANTICS_BLOCKED` source memory;
3. run READY TASK-1089 only with an executor that clears the identity-
   independence check against the now-recorded CHARA publisher, preserving its
   unchanged `INCONCLUSIVE` result;
4. run READY TASK-1091 against the checksum-matched private ThermoML archive
   and enforce the five-row article cap and information floor; keep scoring
   separate;
5. independently replay OQMD `RESULT-0032` through TASK-1090 when its identity
   gate clears, preserving `INVALID` / `FAIL` without a rescue model;
6. preserve the registered FRB chain and the trigger-only Nuclear, Exoplanet,
   Atomic, and Quantum lanes instead of manufacturing filler work.

Nuclear Mass Surface remains the flagship ambition, but interval-bearing
prediction remains blocked because approved no-peek uncertainty routes failed;
its clean source scout found only pre-registration official records, so the
next step is an event-trigger ledger rather than another periodic scout.
Exoplanet remains monitor-only on the unchanged snapshot even though
`RESULT-0027` now exists. Quantum has a source-scoped Almeida baseline and
AGENT_VALIDATED `RESULT-0029`; its Kim-2020 branch is now also terminal under
the present evidence after `HOLD_UNDERPOWERED` and
`STOP_NO_INDEPENDENT_ROUTE`. Atomic remains monitor-only after the ratified
reopen-trigger ledger; a future action needs a genuinely admissible source or
approved contract.
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
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Post-validation dataset/transfer lane: `RESULT-0021` is reviewed memory, MD-0002 is externally published, and OQMD `RESULT-0032` is AGENT_PUBLISHED INVALID negative/control memory | Use TASK-1090 for identity-independent replay only; preserve FAIL and do not rescue-fit or pool databases |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with four scoped AGENT_VALIDATED results and AGENT_PUBLISHED INCONCLUSIVE CHARA `RESULT-0031`; publisher provenance is repaired | Run READY TASK-1089 with an identity-independent executor; keep HD 284163 separate |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with negative/control memory, exact-replayed `RESULT-0025`, failed uncertainty calibration, an anchored point-only freeze, and a clean scout that found only pre-registration sources | Ratify the post-registration trigger ledger; no repeated scout, target matching, or scoring before a qualifying official event |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, `NO_NOTIFY` monitor check, and AGENT_VALIDATED `RESULT-0027` negative/control packaging | Monitor-only until a NOTIFY-class source trigger or maintainer-approved coverage amendment appears; no residual scoring on the unchanged snapshot |
| [FRB / Radio Transients](./campaigns/fresh-physics-data-axes.md#frb-selection-effect-audit) | Registered sealed-prediction chain with checksum/schema-gated Catalog-1 interval exposure pair, committed 479-row pre-T exposure feature surface, frozen exposure-only model surface, maintainer-approved `PRED-0001`, and GitHub Release anchor tag `pred-frb-pret-repeater-propensity-20260710` | Reveal-source contract discipline via TASK-0995; no label reading, success wording, population claim, or reveal scoring before a separate maintainer-reviewed reveal task |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | AGENT_VALIDATED `RESULT-0029` preserves the ZnSe miss; the two four-row Kim-2020 axes are underpowered and no independent route cleared the source gates | Monitor for a genuinely new qualifying source; no score, pooled axis, or repeated generic scout |
| [Dimensional Analysis Validator](./campaigns/dimensional-analysis-validator.md) | AGENT_VALIDATED `RESULT-0030` is exact-replayed but remains same-owner calibration memory | Retry a no-score external freeze only under clean no-exposure control; separately scout third-party labelled corpora |
| [Lattice-QCD Aggregated Consistency](./campaigns/fresh-physics-data-axes.md#lattice-qcd) | Eleven-publication `f_K/f_pi` manifest/graph with two REVIEW_READY partial-hold dependency audits | Complete READY TASK-1081 value-admissibility policy; TASK-1101 activation adjudication remains blocked |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with source-limited Yb/Sr memory, covariance policy, blocked alternatives, and a ratified monitor-only trigger ledger | Wait for a qualifying source trigger; no constants-drift or metric rerun |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | ThermoML `Tb` lane with AGENT_VALIDATED `RESULT-0026` and failed-family `RESULT-0028`; exact-80 is stopped and an at-most-74-row contract plus private source are ready | Run TASK-1091 and pass value-blind article-cap/information-floor gates; scoring remains separate |

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
| Dataset/source-readiness gate | Materials Property Residuals | MD-0002 is published (DOI `10.5281/zenodo.21207072`); OQMD `RESULT-0032` is bounded AGENT_PUBLISHED INVALID negative/control memory awaiting identity-independent replay. |
| Source-replay / transfer gate | Textbook Formula Audit / Stellar M-L / Wien-FIRAS | CHARA `RESULT-0031` is bounded INCONCLUSIVE with repaired publisher provenance; Gate B now waits for an identity-independent executor. |
| External-reveal / uncertainty gate | Nuclear Mass Surface | Tier-1 point-only freeze is externally anchored; a clean scout found only pre-registration sources, so event-trigger monitoring precedes any future source manifest or scoring. |
| Monitor / negative-control gate | Exoplanet Mass-Radius | `RESULT-0027` is AGENT_VALIDATED; keep source-version monitoring metadata-only and wait for a future trigger before scoring. |
| Sealed-prediction reveal discipline | FRB / radio transients | `PRED-0001` is registered and externally anchored by GitHub Release; keep future work to TASK-0995-compliant reveal-source manifests and maintainer-reviewed reveal scoring. |
| Transfer/source gate and negative memory | Quantum Size Effects | Preserve `RESULT-0029`; the current CdSe route is monitor-only after underpowered and no-independent-route stops. |
| Pinned-dataset / aggregation blocked | Atomic-Clock Residuals | `KEEP_MONITOR_ONLY` and the reopen-trigger ledger are durable; wait for a qualifying event. |
| Source-pinned thermophysical benchmark | Thermophysical Property Residuals | `RESULT-0026` and `RESULT-0028` are AGENT_VALIDATED; an at-most-74-row contract and private source are ready, while extraction and scoring remain separate. |
| Calibration / quality-floor gates | Anharmonic, Dimensional, Pendulum, Particle Mass Relations | Anharmonic `CLAIM-0009` is MAINTAINER_REVIEWED calibration memory; Dimensional still needs a genuinely external no-score surface. |
| Near-active source/dependency gate | Lattice-QCD aggregated consistency | `f_K/f_pi` has two partial-hold dependency audits; TASK-1081 value policy must pass before blocked TASK-1101 can adjudicate activation. |
| New-axis source incubator | Gravitational-wave catalog consistency | Pin official GWTC-5/GWOSC version, rights, API, and selection-function semantics; return one bounded candidate question or STOP before any event rows or campaign activation. |
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
