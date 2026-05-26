# Current Missions

APL uses an **Agent First / Research First / Parallel Work** entrypoint.

The default path for a new coding agent is not "scan every file and pick
something small." The default path is:

```bash
python3 scripts/apl_mission.py --onboarding
```

Onboarding mode should explain the current scientific mission, show a few
`READY` options with estimated effort, recommend one, and wait before editing
files. For autonomous agent context after the user already understands the
flow, use:

```bash
python3 scripts/apl_mission.py --agent-prompt
```

Support, review, and closeout work remain explicit:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Mission policy and campaign guardrails live in
[`../missions/current.yaml`](../missions/current.yaml). Live task candidates
come from canonical `tasks/TASK-*.yaml` files through the mission script. For
lighter navigation than the full generated board, use:
[`research.md`](./task-views/research.md),
[`support.md`](./task-views/support.md),
[`release.md`](./task-views/release.md),
[`watchlist.md`](./task-views/watchlist.md), and
[`blocked.md`](./task-views/blocked.md).

## Recommended Mission Now

**Nuclear Mass Surface** remains the flagship validation surface.

Recommended default: start with the live `research` recommendation from
`python3 scripts/apl_mission.py --onboarding`. The best default work is not
more broad formula expansion; it is source-readiness, stress synthesis,
no-peek reveal discipline, domain-limit mapping, evidence packaging, and
negative-result preservation. At handoff, agents should route the output
through [`result-promotion-protocol.md`](./result-promotion-protocol.md): state
the verdict, destination, review tier, Gate A/B status, limitations, and
blockers.

If the Nuclear queue is saturated or a maintainer wants parallel breadth, the
next best surfaces are Quantum Size Effects, Atomic-Clock Residuals, and
Exoplanet Mass-Radius. Exoplanets has crossed into benchmark/failure-map work;
Quantum and Atomic should stay source- and protocol-first until direct rows are
ready.

## Current Mission Shape

APL currently has one flagship validation campaign and three fresh-data
surfaces that are intentionally moving more slowly. That mix is deliberate:
some agents can stress the strongest current evidence, while others build the
source discipline needed for future campaigns.

| Surface | Role right now | Good agent work |
| --- | --- | --- |
| [Nuclear Mass Surface](./campaigns/nuclear-mass-surface.md) | Flagship validation surface with baseline residuals, sandbox scouts, frozen predictions, no-leakage contract, and reveal-readiness blockers | no-leakage implementation planning, registry/reveal-readiness reporting, high-error cluster adversarial stability, negative-result preservation |
| [Exoplanet Mass-Radius](./campaigns/exoplanet-mass-radius.md) | Active catalog benchmark surface with a pinned snapshot, first baseline comparison, and inconclusive regime scout | residual failure-map packaging, true-mass slice audit, narrow matched-control regime follow-up |
| [Quantum Size Effects](./campaigns/quantum-size-effects.md) | Source-readiness campaign before any measurement benchmark | APS direct-table source artifact attempts, source-artifact packaging, digitization protocol review, readiness gates |
| [Atomic-Clock Residuals](./campaigns/atomic-clock-residuals.md) | High-precision fresh-data surface still in source/covariance/version-drift hardening | Beloy 2021 row curation only after source artifact, covariance, and version checks; otherwise preserve blockers |

Mature quality-floor tracks still matter: Pendulum, Dimensional Analysis, and
Particle Mass Relations keep the repository honest about exact references,
falsification, and overclaim resistance. They are not the default landing-page
focus unless the maintainer asks for replay, documentation, or benchmark
hygiene work.

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
- Do not start the Quantum baseline benchmark until direct measurement rows or
  an explicit weaker calibration-consistency scope is approved.
- Do not fit atomic-clock or anomaly-style campaigns before source and
  covariance semantics are reviewable.
- Do not present exoplanet regime scouts as corrections or planet-composition
  discoveries; the next public-safe artifact is a residual/failure map.

## Copy-Paste Agent Prompt

Generate the current prompt with:

```bash
python3 scripts/apl_mission.py --agent-prompt
```

Short onboarding version:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode with onboarding. Read AGENTS.md and
docs/agent-task-protocol.md, then run `python3 scripts/apl_mission.py --onboarding`.
Follow the printed onboarding instructions: explain the current research
mission, show READY options, recommend one, and wait for my choice before
editing files. Prefer a science-execution task over tooling or infrastructure
when a suitable READY option exists.
```
