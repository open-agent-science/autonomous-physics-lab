# Autonomous Research PR Review Checklist

Use this checklist for PRs that package sandbox-only autonomous research runs.
It is a maintainer decision aid, not an automatic promotion path.

## Required Inputs

- [ ] PR references one canonical task, microtask, or proposal review surface.
- [ ] Agent-run manifest lives under `agent_runs/<id>/agent_run.yaml`.
- [ ] Hypothesis and experiment proposals are linked and pass preflight.
- [ ] Metrics, report, limitations, preflight, and review summary artifacts are present.
- [ ] The PR states `sandbox_only: true` and does not write canonical `results/` artifacts.

## Scientific Review

- [ ] Hypothesis summary is specific enough to falsify.
- [ ] Experiment summary names the deterministic method and baseline/reference.
- [ ] Metrics include the relevant pass/fail threshold or comparison target.
- [ ] Limitations are concrete and visible in the PR body.
- [ ] Failed or rejected alternatives are retained instead of hidden.
- [ ] Overclaim audit forbids public-success framing unless a later canonical review supports it.

## Allowed Maintainer Outcomes

- [ ] Reject the run as out of scope, overfit, under-specified, or unsafe.
- [ ] Retain it as negative or sandbox-only scientific memory.
- [ ] Promote a follow-up canonical task for reviewed implementation.
- [ ] Promote to canonical experiment/result only through a later reviewed task, reproducible run, and claim-promotion review.

## Prohibited Outcomes

- [ ] Do not auto-merge because the sandbox run passed.
- [ ] Do not promote a claim directly from sandbox evidence.
- [ ] Do not rewrite canonical result artifacts from this PR.
- [ ] Do not describe a sandbox result as a public success story.

## Helper Command

Generate PR-ready context from a sandbox run:

```bash
python3 scripts/apl_agent_run_pr_helper.py agent_runs/AGENT-RUN-0001/agent_run.yaml
```
