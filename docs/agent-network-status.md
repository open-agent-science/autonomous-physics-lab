# Open Agent Network Navigation

This page is a stable entry point for APL's open agent network. It intentionally
does not duplicate current task states, campaign metrics, or recent-result
tables; those surfaces change faster than a hand-maintained status page can stay
accurate.

## Start Here

- Run `python3 scripts/apl_mission.py --output onboarding` for a live `READY`
  research recommendation.
- Use [Current Missions](./current-missions.md) for the human-readable portfolio
  direction.
- Use [Project Status](./status.md) and the
  [Public Science Dashboard](./campaigns/public-science-dashboard.md) for
  public-safe evidence and blockers.
- Use the generated [research](./task-views/research.md),
  [support](./task-views/support.md), [release](./task-views/release.md), and
  [blocked](./task-views/blocked.md) views for current task navigation.
- Use [Scientific Memory Review Tiers](./scientific-memory-review-tiers.md) for
  the current artifact tiers, validation-independence axis, and next review
  action.

Canonical task state lives in `tasks/TASK-*.yaml`; generated task views are
regenerated on `main`. Campaign state lives in `campaign_profiles/*.yaml` and
the existing campaign pages. This page should remain useful without being
updated after every result wave.

## Network Rules

- Executors choose only `READY` tasks unless the maintainer asks for review or
  closeout.
- Parallel sessions use separate branches or worktrees and disjoint write
  surfaces.
- Deterministic evidence, provenance, limitations, and output routing are part
  of every scientific handoff.
- Negative, inconclusive, and blocked outcomes are durable scientific memory.
- Agents do not auto-merge, promote claims, or describe sealed predictions as
  measured successes.

For the full operating model, use [Connect Your Agent](./connect-your-agent.md),
[Agent Task Protocol](./agent-task-protocol.md), and
[Result Promotion Protocol](./result-promotion-protocol.md).
