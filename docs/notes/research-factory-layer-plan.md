# Research Factory Layer Plan

## Purpose

APL is moving from one-lane-at-a-time hypothesis audits toward a reusable
Research Factory layer: deterministic workflows that campaign adapters can call
to generate many scoped candidates, apply locked controls, and route the
output into scientific memory without promoting claims automatically.

The first testbed is Nuclear Mass Surface. Exoplanet Mass-Radius is the second
reuse case, but the first executable sprint should stay Nuclear-first so the
flagship campaign gets a high-throughput residual-law test instead of more
single-lane audit churn.

## Design Principles

- Start with a reusable vertical slice, not a broad framework rewrite.
- Make the layer callable through a shared runner entrypoint plus
  campaign-specific adapters.
- Keep every factory bounded by campaign-approved feature families.
- Treat controls as mandatory, not as later review polish.
- Route outputs to `NEGATIVE_RESULT`, `INCONCLUSIVE`,
  `SHORTLIST_CANDIDATE`, `READY_FOR_REPLAY`, or `READY_FOR_PRED_FREEZE`.
- Do not create claims, prediction entries, or public discovery wording from
  a factory run.
- Preserve failed candidate families as useful negative memory.

## Intended Shape

The layer should eventually look like this:

- shared factory protocol and `factory_summary` artifact schema;
- shared runner/adapter interface under `physics_lab/factories/`;
- one command-style entrypoint such as `scripts/run_research_factory.py`;
- campaign adapters such as Nuclear residual-law and later Exoplanet residual
  factory adapters;
- campaign profile fields for `allowed_factory_families`,
  `required_factory_controls`, and `factory_stop_rules`.

The first implementation should prove the callable layer with a Nuclear smoke
run. It should not hard-code a Nuclear-only architecture that Exoplanets,
Quantum, Atomic, or Textbook Formula Audit cannot reuse.

## First Task Wave

- `TASK-0504` defines the bounded factory protocol, adapter contract, and the
  Nuclear-first sprint contract.
- `TASK-0505` adds the shared `factory_summary` artifact schema.
- `TASK-0506` implements the reusable Research Factory core plus the first
  Nuclear residual-law adapter and smoke run.
- `TASK-0507` runs the first Nuclear residual-law factory sprint over 50-100
  bounded candidates.
- `TASK-0508` defines Exoplanet factory reuse after the null-baseline and
  host-context gates, proving the second-campaign adapter path without
  stealing focus from Nuclear.

The wave is intentionally small: it creates a reusable research-factory layer
only as far as needed to run a real Nuclear sprint, then checks whether the
same contract can carry a second campaign.
