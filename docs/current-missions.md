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
(`python3 scripts/apl_task_campaign_index.py`). For a curator view that ranks
campaigns by open-data availability and assigns each a bounded, parallel-safe
lane (open-data parallel leads: Materials and Stellar M-L), see the
[portfolio open-data lane map](reviews/portfolio-open-data-lane-map.md).

## Recommended Mission Now

**Exoplanet Mass-Radius Benchmark** remains the default near-term
public-safe benchmark story, but it is not currently a residual-scoring lane.
`TASK-0515` records `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY`, and the later
`EXO-0002` coverage gate did not reopen scoring. The active path is now
negative/control result-publication preflight, source-version monitoring, and
an `EXO-0003` acquisition trigger, not another current-snapshot residual pilot.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
science path is the post-gate data-to-benchmark wave: Materials `MD-0002`
acquisition and validation, Atomic Nemitz `ACR-0002` row curation, Stellar M-L
DEBCat Route 2 / row curation, and Quantum source-artifact handoff. Exoplanet
remains monitor-only until a material source-version trigger appears; do not
run another current-snapshot residual pilot.
At handoff, agents should route the output through
[`result-promotion-protocol.md`](./result-promotion-protocol.md): state the
verdict, destination, review tier, Gate A/B status, limitations, and blockers.

Nuclear Mass Surface remains the flagship validation challenge, but the latest
controls-first lanes landed as negative, inconclusive, diagnostic-only,
chain-local, or validation-regressing memory. The best Nuclear work now is
reveal-readiness, F2/factory result routing, and only tightly bounded
controls-first follow-up. Quantum Size Effects remains source-artifact gated:
Almeida and Vossmeyer are promising but still need checksum/source-copy
decisions before row curation. Atomic-Clock Residuals should now prioritize
Nemitz `ACR-0002`; the Pizzocaro PSD covariance artifact is useful diagnostic
evidence, but its row-admissibility gate preserved the aggregation blocker. New
campaign ideas should enter through source/schema/baseline scaffolds first,
not broad hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation campaign, one active secondary
benchmark surface, two source-readiness surfaces, one public-friendly
formula-audit scaffold, and one emerging reusable-dataset lane. That mix is
deliberate:
some agents can stress the strongest current evidence, others can build
source/baseline discipline, and curators can prepare new campaign lanes without
turning watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with baseline residuals, sandbox scouts, frozen predictions, no-leakage contract, reveal-readiness blockers, and several negative/control lanes | reveal-readiness matrix, F2/factory result routing, and new lanes only when controls and stop conditions are predeclared |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Public-safe benchmark surface with pinned snapshots, null-baseline controls, external-reviewer capsule, and closed current-snapshot residual scoring | preserve negative/control memory and define source-version or `EXO-0003` trigger work before any new residual audit |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign before any measurement benchmark; Vossmeyer and Almeida are promising but source-artifact blocked | Vossmeyer source-copy handoff, Almeida checksum/reuse decision, and direct-row readiness gates |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with Beloy rows, real-row loader, synthetic dry-run, Nemitz/Pizzocaro/Lange source surfaces, and covariance policy | Nemitz `ACR-0002` row curation first; Pizzocaro remains diagnostic-only unless an observable-harmonization contract lands |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | Public verifier lane with exact-reference fixtures and a Gate-B-validated Stefan-Boltzmann software/convention result; empirical audits remain gated | DEBCat Route 2 storage decision, normalized component rows, then Stellar M-L empirical audit |
| [Materials Property Residuals](./campaigns/materials-property-residuals.md) | Emerging reusable-dataset lane with `MD-0001`, independent replay, controls, split sensitivity, and authorized `MD-0002` acquisition | Execute `MD-0002` maintainer-gated acquisition, validate holdout binding, then run the formation-energy benchmark |

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
| Flagship validation challenge | Nuclear Mass Surface | Keep reveal scoring blocked until a no-peek source passes. Preserve local-curvature, pairing-asymmetry, magic-parity, mixed shell-axis transfer, factory no-shortlist, and broad-refit validation regression as negative/inconclusive memory unless a later review creates a narrower publication artifact. |
| Default public benchmark story | Exoplanet Mass-Radius | Preserve the current pinned-snapshot compact-radius surface as negative/control memory; continue source-version discipline and reopen residual audits only after a materially changed snapshot or approved trigger. |
| Prepare/source-readiness | Quantum Size Effects | Stay direct-row/source-artifact first before modeling or fitting; Vossmeyer and Almeida need source-copy/checksum decisions. |
| Pinned-dataset to benchmark-readiness | Atomic-Clock Residuals | Curate Nemitz `ACR-0002` or explicitly preserve the blocker; do not use Pizzocaro as a benchmark row without harmonization. |
| Public-friendly verifier lane | Textbook Formula Audit | Use exact-reference fixtures and DEBCat source gates first; Route 2 and row curation must land before empirical M-L metrics. |
| Emerging reusable-dataset lane | Materials Property Residuals | Treat `MD-0001` as source-pinned dataset memory; `MD-0002` is now the strongest near-term data-to-benchmark path. |
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
