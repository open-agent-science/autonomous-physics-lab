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
broader Convergence + Next Science Wave posture. APL has new frontier result
artifacts in Materials (`RESULT-0021`) and Textbook/Stellar (`RESULT-0022`), so
the highest-leverage near-term work is independent Gate B replay, scoped result
communication, and bounded follow-up audits that keep claims conservative.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science path is:

1. run Gate B replay for Materials `RESULT-0021`;
2. run Gate B replay for Stellar M-L `RESULT-0022`;
3. prepare tightly scoped public capsules and maintainer decision packets only
   after review-tier status is explicit;
4. open the next bounded science wave through Materials control audits,
   Stellar split/complexity audits, and one source-only Wien/FIRAS curation
   slice.

Nuclear Mass Surface remains the flagship ambition, but reveal scoring is still
externally source-gated and should not be the default executor lane while
Materials and Stellar have fresh replayable results. Exoplanet remains
monitor-only until a materially changed pinned snapshot or approved `EXO-0003`
trigger appears. Quantum remains blocked on the exact Almeida raster or
WebPlotDigitizer export. Atomic remains blocked on admitted independent rows or
an approved aggregation contract.
At handoff, agents should route the output through
[`result-promotion-protocol.md`](./result-promotion-protocol.md): state the
verdict, destination, review tier, Gate A/B status, limitations, and blockers.

Nuclear Mass Surface remains the flagship validation challenge, but the latest
controls-first lanes landed as negative, inconclusive, diagnostic-only,
chain-local, or validation-regressing memory. The best Nuclear work now is
reveal-readiness, F2/factory result routing, and only tightly bounded
controls-first follow-up. Quantum Size Effects remains source-readiness gated:
Almeida has cleared the source/license path, but direct rows still require the
exact size-axis raster or replayable WebPlotDigitizer export; Vossmeyer remains
a separate access/source-artifact blocker, not an executable row lane.
Atomic-Clock Residuals should wait for admitted independent rows or an approved
aggregation contract; the Pizzocaro PSD covariance artifact is useful
diagnostic evidence, but its row-admissibility gate preserved the aggregation
blocker. New campaign ideas should enter through source/schema/baseline
scaffolds first, not broad hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation ambition, two active result-validation
surfaces, one public-safe monitor surface, and several source-gated or
quality-floor lanes. That mix is deliberate: some agents should validate and
stress the strongest current evidence, others should build source/baseline
discipline, and curators should keep blocked campaigns visible without turning
watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Active result-validation lane: `MD-0002` is source-pinned and `RESULT-0021` is AGENT_PUBLISHED for a computed-DFT formation-energy benchmark | Gate B replay first, then bounded family-holdout and descriptor/control audits; no material-design or new-law claims |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with a Gate-B-validated exact-reference result and AGENT_PUBLISHED Stellar M-L `RESULT-0022` on frozen DEBCat rows | Gate B replay, DEBCat metadata cleanup, split/complexity audits, and source-only Wien/FIRAS curation before any new metrics |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with baseline residuals, sandbox scouts, frozen predictions, no-leakage contract, reveal-readiness blockers, and several negative/control lanes | one bounded no-leakage sprint or reveal-source work only; reveal scoring remains blocked until a source-grade post-freeze release appears |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, and closed current-snapshot residual scoring | preserve negative/control memory and monitor source-version triggers before any new residual audit |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign before any measurement benchmark; Almeida is license/source-pinned but row curation is blocked on exact raster/export | only resume row-readiness when the maintainer supplies Almeida Figure 1b / SI Figure S2b raster or replayable WebPlotDigitizer export |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with Beloy rows, real-row loader, synthetic dry-run, Nemitz/Pizzocaro/Lange source surfaces, and covariance policy | wait for admitted independent rows or an approved aggregation/harmonization contract; no benchmark metrics yet |

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
| Active result-validation lane | Materials Property Residuals | `RESULT-0021` is the strongest new dataset-backed benchmark; validate it independently and stress-test only with bounded controls. |
| Active result-validation lane | Textbook Formula Audit / Stellar M-L | `RESULT-0022` is the public-friendly empirical formula audit surface; validate it independently and avoid universal-law wording. |
| Flagship validation challenge | Nuclear Mass Surface | Keep reveal scoring blocked until a no-peek source passes. Preserve local-curvature, pairing-asymmetry, magic-parity, mixed shell-axis transfer, factory no-shortlist, and broad-refit validation regression as negative/inconclusive memory unless a later review creates a narrower publication artifact. |
| Monitor / trigger-gated benchmark | Exoplanet Mass-Radius | Preserve the current pinned-snapshot compact-radius surface as negative/control memory; continue source-version discipline and reopen residual audits only after a materially changed snapshot or approved trigger. |
| Source-readiness blocked | Quantum Size Effects | Stay direct-row/source-artifact first; Almeida needs exact raster/export before row readiness can resume. |
| Pinned-dataset / aggregation blocked | Atomic-Clock Residuals | Do not use Pizzocaro as a benchmark row without harmonization; wait for admitted independent rows or an approved aggregation contract. |
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
- Do not run Textbook Formula Audit metrics until the selected formula has a
  source/baseline/holdout plan.

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
