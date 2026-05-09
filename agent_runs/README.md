# Agent Runs

`agent_runs/` is the sandbox evidence area for autonomous research loop work.

It is intentionally separate from canonical scientific memory:

- not `results/`;
- not `claims/`;
- not `knowledge/`;
- not canonical `hypotheses/`;
- not canonical `experiments/`.

An agent run may collect proposal drafts, preflight output, metrics, reports,
limitations, and review summaries. It may not promote claims or create
canonical result artifacts.

## Layout

Use one directory per sandbox run:

```text
agent_runs/AGENT-RUN-0001/
  agent_run.yaml
  metrics.json
  report.md
  limitations.md
  preflight.md
  review_summary.md
```

The `agent_run.yaml` manifest is validated by
`physics_lab/schemas/agent_run.schema.json` and
`physics_lab.registry.agent_runs`.

## Proposal Inputs

Every agent run must point at:

- one file under `hypothesis_proposals/`;
- one file under `experiment_proposals/`;
- one campaign profile under `campaign_profiles/`.

Run preflight before sandbox execution:

```bash
python3 -m physics_lab.cli preflight-research-proposal hypothesis_proposals/HYP-PROPOSAL-0001.yaml
python3 -m physics_lab.cli preflight-research-proposal experiment_proposals/EXP-PROPOSAL-0001.yaml
python3 -m physics_lab.cli validate agent_runs/AGENT-RUN-0001/agent_run.yaml
```

## Review Boundary

Sandbox evidence can support a maintainer decision, but it cannot support a
public claim by itself. A later maintainer-reviewed task is required before any
canonical experiment, result, claim, or knowledge promotion.
