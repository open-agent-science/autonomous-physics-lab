# Snapshot Strategy And Architecture Context Review

Task: `TASK-0632`

Verdict: `SNAPSHOT_CONTEXT_STRENGTHENED`

## Finding

`scripts/apl_snapshot.sh` already included a useful dynamic strategic front
page from `physics_lab/registry/snapshot.py`, including campaign-at-a-glance,
recent learnings, recommended parallel allocation, current queue, blocked work,
result tiers, predictions, and campaign output scorecard summaries.

The missing piece was source-file visibility: the snapshot named several
critical strategy files in the generated map, but did not include the full
contents of `docs/strategy.md`, `missions/current.yaml`, or campaign profile
files as first-class snapshot blocks. A strategy agent could therefore see a
summary but miss the authoritative source nuance.

## Change

The snapshot now includes a dedicated `Current Strategy And Mission Sources`
section with the full current strategy, mission, campaign profile catalog,
campaign profiles, curator guidance, Research Factory protocols, public-release
gate, and repository map.

It also includes an `Architecture Directory Structure` section: a compact,
noise-filtered tree of important repository surfaces. This is for architecture
planning only; it is not a committed static routing cache for agents.

## Guardrails

- The snapshot remains read-only.
- No validation, experiment, or workflow commands are run by snapshot generation.
- No new committed generated board or agent-facing static cache is added.
- Local/generated/cache directories are excluded from the architecture tree.

## Value

Strategy agents can now answer:

- What is the current strategy and mission source of truth?
- Which campaigns and profiles exist?
- What repository surfaces are architectural core versus scientific memory?
- Where should a future architecture cleanup or campaign-routing task point?

This should reduce duplicate strategic recommendations and make repository
architecture reviews less dependent on reconstructing context from scattered PRs.
