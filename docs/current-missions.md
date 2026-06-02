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
[`campaigns/catalog.yaml`](../campaigns/catalog.yaml) (the canonical source) and
query the on-demand task-to-campaign index
(`python3 scripts/apl_task_campaign_index.py`).

## Recommended Mission Now

**Exoplanet Mass-Radius Benchmark** is the default near-term science-output
sprint. `TASK-0515` records `NO_GO_PRESERVE_NEGATIVE_CONTROL_MEMORY` for
another compact-radius residual or host-context pilot on the current pinned
snapshot. Reopen the residual lane only after a materially changed pinned
snapshot or explicitly revised coverage gate. The active path is now the
second-snapshot reopen gate plus a no-live-fetch ingestion dry-run, not another
current-snapshot residual pilot.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. Right now the strongest
default work is not another broad Nuclear hypothesis burst; it is preserving
the Exoplanet benchmark negative/control memory, frozen second-snapshot
discipline, and benchmark-only wording until a materially changed input surface
is reviewed.
At handoff, agents should route the output through
[`result-promotion-protocol.md`](./result-promotion-protocol.md): state the
verdict, destination, review tier, Gate A/B status, limitations, and blockers.

Nuclear Mass Surface remains the flagship validation challenge, but the latest
controls-first lanes landed as negative, inconclusive, or chain-local memory.
`TASK-0531` adds a sharper blocker: a simple `NMD-0003` broad-surface refit
improves train/full metrics but regresses on validation holdout. The best
Nuclear work now is baseline-family gating, F2 preflight, and reveal-source
readiness. Quantum Size Effects remains a source-readiness lane, while
Atomic-Clock Residuals is a pinned-source/covariance lane moving toward
benchmark readiness. New campaign ideas should enter through
source/schema/baseline scaffolds first, not broad hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation campaign, one active secondary
benchmark surface, two source-readiness surfaces, and one public-friendly
formula-audit scaffold. That mix is deliberate:
some agents can stress the strongest current evidence, others can build
source/baseline discipline, and curators can prepare new campaign lanes without
turning watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation challenge with baseline residuals, sandbox scouts, frozen predictions, no-leakage contract, and reveal-readiness blockers; local-curvature no-leakage is falsified, the residual-free cluster lane is inconclusive, pairing-asymmetry and magic-parity controls are negative, shell-axis transfer is mixed/chain-local, and the first `NMD-0003` refit regresses on validation holdout | baseline-family gate, F2 finer-taxonomy preflight, and reveal-source readiness; do not repeat completed weak lanes |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Default near-term science-output sprint with a pinned snapshot, baseline comparison, compact-radius matched-control diagnostic, null-baseline control panel, mass-quartile underpowered diagnostic, target-freeze protocol, external-reviewer capsule, landed host-context preflight, and `TASK-0515` no-go synthesis | Preserve negative/control memory; define the second-snapshot reopen gate and dry-run no-live-fetch ingestion before any new residual audit |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign before any measurement benchmark | APS direct-table source artifact attempts, source-artifact packaging, digitization protocol review, readiness gates |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface with Beloy 2021 pinned as sandbox-only rows, deterministic real-row loader, synthetic cross-source dry-run, Nemitz 2016 source artifact pinned but rows blocked, and first-benchmark covariance policy defined | fallback source triage, direct-vs-derived separation, then baseline-readiness gate |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | New scaffold for range-aware audits of famous formulas; Stefan-Boltzmann exact-reference fixture has landed, while empirical audits have not | Wien exact-reference fixture and empirical source/baseline planning before any real-source metrics |

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
| Flagship validation challenge | Nuclear Mass Surface | Keep reveal scoring blocked until a no-peek source passes. Preserve local-curvature, pairing-asymmetry, magic-parity, mixed shell-axis transfer, and the simple `NMD-0003` refit regression as negative/inconclusive memory unless a later review creates a narrower publication artifact. Run baseline-family gates before new fitting. |
| Default science-output sprint | Exoplanet Mass-Radius | Preserve the current pinned-snapshot compact-radius surface as negative/control memory; continue source discipline and reopen residual audits only after a materially changed snapshot or coverage gate plus dry-run ingestion. |
| Prepare/source-readiness | Quantum Size Effects | Stay direct-row/source-artifact first before modeling or fitting. |
| Pinned-dataset to benchmark-readiness | Atomic-Clock Residuals | Close second-source, loader, holdout/no-peek, and covariance-policy blockers before the first Yb/Sr consistency benchmark. |
| New public-friendly scaffold | Textbook Formula Audit | Use exact-reference fixtures first, then empirical source/baseline planning; no real-source metrics before source, schema, holdout, and verification gates. |
| Candidate new lanes | Materials Property Residuals | Scaffold source, baseline, and holdout rules before any hypothesis batches. |
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
