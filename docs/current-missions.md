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

## Recommended Mission Now

**Nuclear Mass Surface** remains the flagship validation surface.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --output onboarding`. The best default work is not
more broad formula expansion; it is source-readiness, stress synthesis,
no-peek reveal discipline, domain-limit mapping, evidence packaging, and
negative-result preservation. At handoff, agents should route the output
through [`result-promotion-protocol.md`](./result-promotion-protocol.md): state
the verdict, destination, review tier, Gate A/B status, limitations, and
blockers.

If the Nuclear queue is saturated or a maintainer wants parallel breadth, the
next best active surface is Exoplanet Mass-Radius. Quantum Size Effects and
Atomic-Clock Residuals remain valuable source-readiness lanes. New campaign
ideas should enter through source/schema/baseline scaffolds first, not broad
hypothesis batches.

## Current Mission Shape

APL currently has one flagship validation campaign, one active secondary
benchmark surface, two source-readiness surfaces, and one public-friendly
formula-audit scaffold. That mix is deliberate:
some agents can stress the strongest current evidence, others can build
source/baseline discipline, and curators can prepare new campaign lanes without
turning watchlist topics into formula-search work.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation surface with baseline residuals, sandbox scouts, frozen predictions, no-leakage contract, and reveal-readiness blockers; local-curvature no-leakage is now falsified under `TASK-0394` | local-curvature negative/preflight packaging, registry/reveal-readiness reporting, residual-free high-error cluster diagnostics, negative-result preservation |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Active catalog benchmark surface with a pinned snapshot, baseline comparison, failure-map/slice audits, compact-radius matched-control survivor, and `BENCHMARK_SUMMARY_ONLY` scorecard | independent compact-radius replay, normalized checksum cleanup, evidence-card packaging, second-snapshot no-live-fetch protocol |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign before any measurement benchmark | APS direct-table source artifact attempts, source-artifact packaging, digitization protocol review, readiness gates |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface still in source/covariance/version-drift hardening | Beloy 2021 row curation only after source artifact, covariance, and version checks; otherwise preserve blockers |
| [Textbook Formula Audit](./campaigns/textbook-formula-audit.md) | New scaffold for range-aware audits of famous formulas | Stellar Mass-Luminosity OOD source/baseline planning before any metrics |

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
| Active flagship | Nuclear Mass Surface | Keep reveal scoring blocked until a no-peek source passes. Preserve local-curvature as a falsified no-leakage lane unless a later review creates a narrower negative-result publication artifact. Continue bounded diagnostics and result-promotion preflights. |
| Active secondary | Exoplanet Mass-Radius | Continue pinned-snapshot residual maps, matched controls, selection-effect audits, result-promotion scoring, and future prediction-readiness work. |
| Prepare/source-readiness | Quantum Size Effects, Atomic-Clock Residuals | Stay source/covariance/direct-row first before modeling or fitting. |
| New public-friendly scaffold | Textbook Formula Audit | Start with Stellar Mass-Luminosity source/baseline planning; no metrics before source, schema, holdout, and verification gates. |
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
  discoveries; compact-radius is public-safe only as benchmark-summary wording
  with scorecard limitations attached.
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
