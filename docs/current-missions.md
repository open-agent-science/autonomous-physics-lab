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

**Materials Property Residuals** is the top-ranked current mission in a
post-validation next-wave posture. APL now has several validated or
source-limited campaign surfaces; the highest-leverage near-term work is to
move them through explicit next-validity gates instead of repeating internal
audits.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science path is:

1. prepare the Materials `MD-0002` external archive/DOI decision after
   repository-local metadata closeout (`TASK-0887`);
2. independently replay workflow-packaged FIRAS/Wien `RESULT-0023`
   (`TASK-0885`);
3. route validated or source-limited campaigns into one of four gates:
   transfer, ratification, external reveal, or source readiness;
4. preserve negative/control memory where a campaign has reached a no-go or
   monitor-only state.

Nuclear Mass Surface remains the flagship ambition, but reveal scoring is still
externally source-gated and should not be the default executor lane while
other campaigns have cleaner source-readiness and ratification tasks. Exoplanet
remains monitor-only until a materially changed pinned snapshot or approved
`EXO-0003` trigger appears. Quantum has a source-scoped Almeida baseline, but
`TASK-0277` kept open-ended autonomous correction search blocked; the current
useful Quantum work is the ZnSe/Toufanian source-license gate (`TASK-0870`) and
the already-routed effective-mass transfer negative memory. Atomic remains
blocked on admitted independent rows or an approved aggregation contract, with
new executor work limited to source-route scouting or explicit maintainer
aggregation decisions.
At handoff, agents should route the output through
[`result-promotion-protocol.md`](./result-promotion-protocol.md): state the
verdict, destination, review tier, Gate A/B status, limitations, and blockers.

Nuclear Mass Surface remains the flagship validation challenge, but the latest
controls-first lanes landed as negative, inconclusive, diagnostic-only,
chain-local, or validation-regressing memory. The best Nuclear work now is
value-blind reveal-source scouting and negative/control memory preservation.
Quantum Size Effects remains transfer-gated after a source-scoped Almeida
baseline: the next source/material route is license-gated, and the failed
effective-mass transfer should be preserved as negative/control memory before
another transfer lane is opened.
Atomic-Clock Residuals should wait for admitted independent rows or an approved
aggregation contract; the Pizzocaro PSD covariance artifact is useful
diagnostic evidence, but its row-admissibility gate preserved the aggregation
blocker. New campaign ideas should enter through source/schema/baseline
scaffolds first, not broad hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation ambition, several active
post-validation gate surfaces, one public-safe monitor surface, and several
source-gated or quality-floor lanes. That mix is deliberate: some agents should
close source and dataset blockers, others should prepare ratification packets
or transfer scouts, and curators should keep blocked campaigns visible without
turning watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Post-validation dataset/transfer lane: `RESULT-0021` is reviewed memory, repository-local MD-0002 metadata is closed, and the disjoint-family transfer failure is preserved as negative memory | `TASK-0887` external archive/DOI decision; no metric, row, or claim mutation |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with validated exact-reference and Stellar M-L surfaces, workflow-packaged FIRAS/Wien `RESULT-0023`, and high-mass transfer `RESULT-0024` replay memory | `TASK-0885` RESULT-0023 Gate B replay and `TASK-0886` RESULT-0024 maintainer-review packet; no universal formula wording |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with negative/control memory, source-gated prospective reveal, and RESULT-0025 point-estimator evidence that remains uncertainty-blocked for PRED freeze | `TASK-0865` uncertainty-route preflight, `TASK-0878` DZ10 parity reference, or `TASK-0890` RESULT-0025 public-safe review packet; reveal scoring still blocked |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, and closed current-snapshot residual scoring | preserve negative/control memory and monitor source-version triggers before any new residual audit |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-scoped Almeida baseline exists, open-ended correction search remains blocked, and effective-mass transfer failure is routed as negative memory | `TASK-0870` ZnSe/Toufanian source-license verification; it does not unblock archived `TASK-0226` |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with source-limited Yb/Sr memory, covariance policy, and diagnostic-only Pizzocaro aggregation contract | `TASK-0889` independent absolute Yb/Sr source-route scout, or wait for an approved aggregation/harmonization contract before metrics |
| [Thermophysical Property Residuals](./campaigns/thermophysical-property-residuals.md) | Newly active ThermoML `Tb` benchmark lane with AGENT_PUBLISHED `RESULT-0026`, frozen Joback baseline, source-rights boundary, and failed-family memory to preserve | `TASK-0894` Gate B replay, `TASK-0895` value-free corpus-expansion preflight, or `TASK-0896` failed-family negative memory; no raw archive vendoring or broad property claim |

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
| Dataset/source-readiness gate | Materials Property Residuals | Decide external archive/DOI posture for MD-0002 and preserve transfer-negative memory before any broader claim. |
| Source-readiness / transfer gate | Textbook Formula Audit / Stellar M-L / Wien-FIRAS | Replay `RESULT-0023` and prepare safe `RESULT-0024` review wording before any stronger public framing. |
| External-reveal gate | Nuclear Mass Surface | Keep reveal scoring blocked until a no-peek source passes; `TASK-0821` may scout one source route value-blind. Preserve negative/inconclusive memory. |
| Monitor / trigger-gated benchmark | Exoplanet Mass-Radius | Preserve the current pinned-snapshot compact-radius surface as negative/control memory; continue source-version discipline and reopen residual audits only after a materially changed snapshot or approved trigger. |
| Transfer/source gate and negative memory | Quantum Size Effects | Verify the ZnSe/Toufanian source-license route; keep the routed effective-mass negative memory and archived `TASK-0226` closed unless a later maintainer-approved pilot task exists. |
| Pinned-dataset / aggregation blocked | Atomic-Clock Residuals | Scout a new independent absolute Yb/Sr route or wait for maintainer aggregation approval; do not use Pizzocaro as a benchmark row without an admissible contract. |
| Source-pinned thermophysical benchmark | Thermophysical Property Residuals | Replay `RESULT-0026`, preflight value-free ThermoML Tb expansion, and preserve esters/lactones negative memory before any broader property-estimation lane. |
| Ratification / quality-floor gates | Anharmonic, Dimensional, Pendulum, Particle Mass Relations | Prepare narrow maintainer packets, negative-memory cards, or scheme/source preflights; do not restart broad formula search. |
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
